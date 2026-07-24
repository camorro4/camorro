#!/usr/bin/env python3
"""
Camoro Banner & UI Module
"""

import os
import sys
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

init(autoreset=True)
console = Console()

# ─── Color Aliases ──────────────────────────────────
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
B = Fore.BLUE
W = Fore.WHITE
RE = Style.RESET_ALL

def clear_screen():
    """Clear terminal screen."""
    os.system("clear" if os.name != "nt" else "cls")

def show_banner():
    """Display the main Camoro banner."""
    clear_screen()
    banner = f"""
{R}   ▄████████  ▄████████    ▄▄▄▄███▄▄▄▄   ▄██████▄   ████████▄     ▄████████ 
{R}  ███    ███ ███    ███  ▄██▀▀▀███▀▀▀██▄ ███    ███  ███   ▀███   ███    ███ 
{R}  ███    █▀  ███    ███  ███   ███   ███ ███    ███  ███    ███   ███    █▀  
{R}  ███        ███    ███  ███   ███   ███ ███    ███  ███    ███  ▄███▄▄▄     
{R}  ███        ███    ███  ███   ███   ███ ███    ███  ███    ███ ▀▀███▀▀▀     
{R}  ███    █▄  ███    ███  ███   ███   ███ ███    ███  ███    ███   ███    █▄  
{R}  ███    ███ ███    ███  ███   ███   ███ ███    ███  ███   ▄███   ███    ███ 
{R}  ████████▀  ████████▀    ▀█   ███   █▀   ▀██████▀   ████████▀    ██████████ 
    
{W}  ╔══════════════════════════════════════════════════════════════════════╗
{W}  ║  {C}AI-Powered Instagram Password Security Testing Framework {G}v2.0    {W}║
{W}  ║  {M}Author: Camoro Team  {W}|  {Y}Termux & Linux Support                     {W}║
{W}  ╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def show_menu():
    """Display interactive main menu."""
    table = Table(title=f"{C}[ CAMORO MAIN MENU ]{RE}", 
                  title_style="bold cyan",
                  border_style="red",
                  show_header=True,
                  header_style="bold yellow")
    
    table.add_column("Option", style="cyan", justify="center", width=8)
    table.add_column("Function", style="white", width=35)
    table.add_column("Description", style="green")
    
    table.add_row("[1]", "Target Information Gathering", "Fetch Instagram profile data")
    table.add_row("[2]", "AI Password Generation", "Generate 18,000+ intelligent passwords")
    table.add_row("[3]", "Full Attack Mode", "Info gathering + Password gen + Brute force")
    table.add_row("[4]", "Brute Force Only", "Test existing wordlist against target")
    table.add_row("[5]", "Proxy Configuration", "Add/rotate/manage proxy list")
    table.add_row("[6]", "View Results", "Show successful credentials")
    table.add_row("[7]", "Settings & Config", "Adjust attack parameters")
    table.add_row("[0]", "Exit", "Close Camoro")
    
    console.print(table)
    print(f"\n{Y}[*] Select option [0-7]: {RE}", end="")

def show_info_panel(username, data):
    """Display gathered information about target."""
    if not data:
        console.print(Panel(f"{R}Could not retrieve information for @{username}", 
                           title="Error"))
        return
    
    info_text = f"""
{G}Username:{W}        @{username}
{G}Full Name:{W}       {data.get('full_name', 'N/A')}
{G}Bio:{W}            {data.get('biography', 'N/A')[:100]}
{G}Followers:{W}      {data.get('followers', 'N/A'):,}
{G}Following:{W}      {data.get('following', 'N/A'):,}
{G}Posts:{W}          {data.get('posts', 'N/A')}
{G}Verified:{W}       {data.get('verified', False)}
{G}Business:{W}       {data.get('is_business', False)}
{G}Private:{W}        {data.get('is_private', False)}
{G}External URL:{W}   {data.get('external_url', 'N/A')}
"""
    console.print(Panel(info_text, title=f"[cyan]Target Profile: @{username}[/cyan]", 
                        border_style="green"))

def show_password_stats(passwords):
    """Show password generation statistics."""
    table = Table(title="Password Generation Stats", border_style="magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="yellow", justify="right")
    table.add_column("Example", style="green")
    
    # Categorize passwords
    categories = {
        "Basic mutations": [],
        "Date combos": [],
        "Name variants": [],
        "Leet speak": [],
        "Complex mixes": [],
    }
    
    leet_chars = set('43015789')
    date_patterns = set('0123456789-_')
    
    sample_size = min(500, len(passwords))
    for pwd in passwords[:sample_size]:
        if any(c in leet_chars for c in pwd) and any(c.isalpha() for c in pwd):
            categories["Leet speak"].append(pwd)
        elif any(c.isdigit() for c in pwd) and any(c.isalpha() for c in pwd):
            if sum(1 for c in pwd if c in '0123456789') >= 4:
                categories["Date combos"].append(pwd)
            else:
                categories["Complex mixes"].append(pwd)
        elif pwd.isalpha():
            categories["Name variants"].append(pwd)
        else:
            categories["Basic mutations"].append(pwd)
    
    for cat, pwds in categories.items():
        if pwds:
            table.add_row(cat, str(len(pwds)), pwds[0] if pwds else "N/A")
    
    table.add_row(f"{G}TOTAL", f"{G}{len(passwords):,}", "")
    console.print(table)

def show_progress_bar():
    """Return a Rich Progress bar for brute-force operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[cyan]{task.completed:,}/{task.total:,}"),
        TextColumn("[yellow]{task.fields[speed]}"),
    )
