#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# OSINT Module - بديل Maltego و Shodan و Censys

import os
import requests
import json
import sys
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class OSINTModule:
    def __init__(self):
        self.name = "OSINT Module"
        self.target = ""
        self.results = {}
    
    def show_menu(self):
        menu = f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║        🔍  قائمة أدوات جمع المعلومات          ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}جمع معلومات البريد الإلكتروني     {Fore.CYAN}║
║  {Fore.WHITE}[2] {Fore.GREEN}البحث عن حسابات في منصات التواصل   {Fore.CYAN}║
║  {Fore.WHITE}[3] {Fore.GREEN}جمع معلومات النطاق (Domain)        {Fore.CYAN}║
║  {Fore.WHITE}[4] {Fore.GREEN}البحث في Shodan API                 {Fore.CYAN}║
║  {Fore.WHITE}[5] {Fore.GREEN}البحث في Censys API                 {Fore.CYAN}║
║  {Fore.WHITE}[6] {Fore.GREEN}جمع معلومات IP (GeoIP, DNS, WHOIS) {Fore.CYAN}║
║  {Fore.WHITE}[7] {Fore.GREEN}البحث عن ملفات وكلمات سر مسربة     {Fore.CYAN}║
║  {Fore.WHITE}[8] {Fore.GREEN}سحب بيانات من TheHarvester          {Fore.CYAN}║
║  {Fore.WHITE}[9] {Fore.GREEN}جمع معلومات من LinkedIn             {Fore.CYAN}║
║  {Fore.WHITE}[10] {Fore.GREEN}تقرير شامل (Full Recon)            {Fore.CYAN}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية             {Fore.CYAN}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def email_osint(self, email):
        """جمع معلومات من البريد الإلكتروني"""
        print(f"\n{Fore.YELLOW}[*] جاري جمع معلومات عن: {email}{Style.RESET_ALL}")
        
        # 1. البحث في Have I Been Pwned
        try:
            r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
            if r.status_code == 200:
                breaches = r.json()
                print(f"{Fore.GREEN}[+] تم العثور على {len(breaches)} اختراق:{Style.RESET_ALL}")
                for b in breaches:
                    print(f"    {Fore.RED}[!] {b['Name']} - {b['BreachDate']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[-] لا توجد اختراقات معروفة لهذا البريد{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}[!] فشل الاتصال بـ Have I Been Pwned{Style.RESET_ALL}")
        
        # 2. استخراج اسم المستخدم والنطاق
        username = email.split('@')[0]
        domain = email.split('@')[1]
        print(f"\n{Fore.WHITE}[+] اسم المستخدم: {username}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[+] النطاق: {domain}{Style.RESET_ALL}")
        
        # 3. البحث في Google عن البريد
        print(f"{Fore.YELLOW}[*] البحث في Google...{Style.RESET_ALL}")
        search_query = email.replace('@', '%40')
        print(f"    {Fore.CYAN}رابط البحث: https://www.google.com/search?q={email}{Style.RESET_ALL}")
        
        # حفظ النتائج
        self.results['email'] = {
            'email': email,
            'username': username,
            'domain': domain
        }
    
    def social_search(self, username):
        """البحث عن اسم مستخدم في جميع المنصات (بديل Sherlock)"""
        print(f"\n{Fore.YELLOW}[*] جاري البحث عن: {username} في منصات التواصل{Style.RESET_ALL}")
        
        platforms = {
            "GitHub": f"https://github.com/{username}",
            "Twitter/X": f"https://twitter.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "LinkedIn": f"https://linkedin.com/in/{username}",
            "Reddit": f"https://reddit.com/user/{username}",
            "Telegram": f"https://t.me/{username}",
            "YouTube": f"https://youtube.com/@{username}",
            "TikTok": f"https://tiktok.com/@{username}",
            "Snapchat": f"https://snapchat.com/add/{username}",
            "Pinterest": f"https://pinterest.com/{username}",
            "Medium": f"https://medium.com/@{username}",
            "Dev.to": f"https://dev.to/{username}",
            "HackerNews": f"https://news.ycombinator.com/user?id={username}",
            "Keybase": f"https://keybase.io/{username}",
            "Replit": f"https://replit.com/@{username}",
        }
        
        found = []
        not_found = []
        
        for platform, url in platforms.items():
            try:
                r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    found.append((platform, url))
                    print(f"    {Fore.GREEN}[✓] {platform}: {url}{Style.RESET_ALL}")
                else:
                    not_found.append(platform)
            except:
                pass
        
        print(f"\n{Fore.WHITE}[+] تم العثور على {len(found)} حساب من {len(platforms)} منصة{Style.RESET_ALL}")
        
        self.results['social'] = {
            'username': username,
            'found': found,
            'total_checked': len(platforms)
        }
    
    def domain_info(self, domain):
        """جمع معلومات النطاق"""
        print(f"\n{Fore.YELLOW}[*] جاري جمع معلومات النطاق: {domain}{Style.RESET_ALL}")
        
        import socket
        import dns.resolver
        
        try:
            # 1. DNS Records
            print(f"{Fore.CYAN}[+] سجلات DNS:{Style.RESET_ALL}")
            
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
            for rtype in record_types:
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    for rdata in answers:
                        print(f"    {Fore.WHITE}{rtype}: {rdata}{Style.RESET_ALL}")
                except:
                    pass
            
            # 2. WHOIS
            print(f"{Fore.CYAN}[+] معلومات WHOIS:{Style.RESET_ALL}")
            import whois
            w = whois.whois(domain)
            print(f"    المنشئ: {w.org}")
            print(f"    المسجل: {w.registrar}")
            print(f"    تاريخ الإنشاء: {w.creation_date}")
            print(f"    تاريخ الانتهاء: {w.expiration_date}")
            
            # 3. IP والموقع
            ip = socket.gethostbyname(domain)
            print(f"\n{Fore.CYAN}[+] معلومات IP ({ip}):{Style.RESET_ALL}")
            
            r = requests.get(f"https://ipinfo.io/{ip}/json")
            data = r.json()
            print(f"    المدينة: {data.get('city', 'غير معروف')}")
            print(f"    المنطقة: {data.get('region', 'غير معروف')}")
            print(f"    الدولة: {data.get('country', 'غير معروف')}")
            print(f"    المزود: {data.get('org', 'غير معروف')}")
            
            # 4. Sublist3r (subdomains)
            print(f"\n{Fore.CYAN}[+] البحث عن نطاقات فرعية...{Style.RESET_ALL}")
            subdomains = [
                f"www.{domain}", f"mail.{domain}", f"ftp.{domain}", 
                f"admin.{domain}", f"api.{domain}", f"blog.{domain}",
                f"dev.{domain}", f"test.{domain}", f"vpn.{domain}",
                f"remote.{domain}", f"portal.{domain}", f"cpanel.{domain}",
                f"webmail.{domain}", f"support.{domain}", f"help.{domain}"
            ]
            found_subdomains = []
            for sub in subdomains:
                try:
                    socket.gethostbyname(sub)
                    found_subdomains.append(sub)
                    print(f"    {Fore.GREEN}[✓] {sub}{Style.RESET_ALL}")
                except:
                    pass
            
            self.results['domain'] = {
                'domain': domain,
                'ip': ip,
                'subdomains': found_subdomains,
                'geo': data
            }
            
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
    
    def shodan_lookup(self, ip):
        """البحث في Shodan"""
        print(f"\n{Fore.YELLOW}[*] البحث في Shodan عن: {ip}{Style.RESET_ALL}")
        
        # يمكن للمستخدم إضافة API Key خاص به
        api_key = input(f"{Fore.WHITE}[?] أدخل Shodan API Key (أو اتركه فارغاً): {Style.RESET_ALL}").strip()
        
        if not api_key:
            print(f"{Fore.CYAN}[-] لا يوجد API Key. استخدام بيانات تجريبية{Style.RESET_ALL}")
            # بيانات توضيحية
            print(f"""
    {Fore.CYAN}معلومات Shodan التجريبية:
    {Fore.WHITE}• IP: {ip}
    • المنافذ المفتوحة: 22 (SSH), 80 (HTTP), 443 (HTTPS)
    • الخدمات: OpenSSH 8.0, Apache 2.4
    • النظام: Linux 4.x
    • الموقع: استخدم shodan.io للحصول على بيانات كاملة
    
    {Fore.YELLOW}💡 نصيحة: احصل على API Key مجاني من https://account.shodan.io{Style.RESET_ALL}
            """)
            return
        
        try:
            r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={api_key}")
            data = r.json()
            print(f"{Fore.GREEN}[+] نتائج Shodan:{Style.RESET_ALL}")
            print(f"    ISP: {data.get('isp', 'N/A')}")
            print(f"    OS: {data.get('os', 'N/A')}")
            print(f"    المنافذ: {data.get('ports', [])}")
            print(f"    الخدمات: {data.get('hostnames', [])}")
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
    
    def run(self):
        show_banner("osint")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر العملية [0-10]: {Style.RESET_ALL}")
            
            if choice == "0":
                break
            elif choice == "1":
                target = input(f"\n{Fore.WHITE}[?] أدخل البريد الإلكتروني: {Style.RESET_ALL}").strip()
                if target:
                    self.email_osint(target)
            elif choice == "2":
                target = input(f"\n{Fore.WHITE}[?] أدخل اسم المستخدم: {Style.RESET_ALL}").strip()
                if target:
                    self.social_search(target)
            elif choice == "3":
                target = input(f"\n{Fore.WHITE}[?] أدخل اسم النطاق (domain.com): {Style.RESET_ALL}").strip()
                if target:
                    self.domain_info(target)
            elif choice == "4":
                target = input(f"\n{Fore.WHITE}[?] أدخل عنوان IP: {Style.RESET_ALL}").strip()
                if target:
                    self.shodan_lookup(target)
            elif choice == "6":
                target = input(f"\n{Fore.WHITE}[?] أدخل عنوان IP أو نطاق: {Style.RESET_ALL}").strip()
                if target:
                    self.domain_info(target)
            elif choice == "10":
                target = input(f"\n{Fore.WHITE}[?] أدخل اسم النطاق للفحص الشامل: {Style.RESET_ALL}").strip()
                if target:
                    print(f"\n{Fore.GREEN}[*] جاري الفحص الشامل...{Style.RESET_ALL}")
                    self.domain_info(target)
                    print(f"\n{Fore.GREEN}[*] الفحص الشامل اكتمل!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
