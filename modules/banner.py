#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from colorama import Fore, Style

BANNERS = {
    "osint": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║        🔍  جمع المعلومات - OSINT Module          ║
║     بديل مجاني لـ Maltego و Shodan و Censys       ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "scanner": f"""
{Fore.YELLOW}╔══════════════════════════════════════════════════╗
║        📡  فحص الثغرات - Scanner Module          ║
║      بديل مجاني لـ Burp Suite Enterprise          ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "exploit": f"""
{Fore.RED}╔══════════════════════════════════════════════════╗
║      💥  الاستغلال - Exploit Module             ║
║     بديل مجاني لـ Metasploit Pro و Cobalt Strike  ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "payload": f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════╗
║     🎯  توليد البايلودات - Payload Module        ║
║      بديل لـ Cobalt Strike و Brute Ratel          ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "network": f"""
{Fore.GREEN}╔══════════════════════════════════════════════════╗
║      🌐  هجمات الشبكة - Network Module           ║
║    بديل لـ WiFi Pineapple و Flipper Zero           ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "recon": f"""
{Fore.BLUE}╔══════════════════════════════════════════════════╗
║      🕵️  الاستطلاع - Reconnaissance Module       ║
║         بديل لـ Shodan و Censys المتقدم            ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "web": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║       🌍  فحص الويب - Web Application Module     ║
║       بديل مجاني لـ Burp Suite Enterprise          ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "c2": f"""
{Fore.RED}╔══════════════════════════════════════════════════╗
║     ☠️  نظام التحكم - C2 Command & Control      ║
║    بديل مجاني لـ Cobalt Strike و Brute Ratel       ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "flipper": f"""
{Fore.GREEN}╔══════════════════════════════════════════════════╗
║     🐬  محاكي Flipper Zero - GPIO & RFID         ║
║       محاكاة برمجية لجهاز Flipper Zero             ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""",
    "ducky": f"""
{Fore.YELLOW}╔══════════════════════════════════════════════════╗
║     🦆  Rubber Ducky Payload Generator           ║
║       توليد سكريبتات Ducky Script احترافية         ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
}

def show_banner(name):
    print(BANNERS.get(name, ""))
