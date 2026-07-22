#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Recon Module - بديل Shodan و Censys المتقدم

import os
import subprocess
import json
import dns.resolver
import socket
import requests
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class ReconModule:
    def __init__(self):
        self.name = "Recon Module"
    
    def show_menu(self):
        menu = f"""
{Fore.BLUE}╔══════════════════════════════════════════════╗
║        🕵️  قائمة أدوات الاستطلاع             ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}جمع النطاقات الفرعية (Subdomains)    {Fore.BLUE}║
║  {Fore.WHITE}[2] {Fore.GREEN}فحص DNS Records كامل                {Fore.BLUE}║
║  {Fore.WHITE}[3] {Fore.GREEN}جمع معلومات IP (GeoIP, ASN, ISP)    {Fore.BLUE}║
║  {Fore.WHITE}[4] {Fore.GREEN}فحص Web Technologies                {Fore.BLUE}║
║  {Fore.WHITE}[5] {Fore.GREEN}فحص SSL/TLS Certificate              {Fore.BLUE}║
║  {Fore.WHITE}[6] {Fore.GREEN}جمع URL من Internet Archive (Wayback){Fore.BLUE}║
║  {Fore.WHITE}[7] {Fore.GREEN}Google Dorking (بحث متقدم)           {Fore.BLUE}║
║  {Fore.WHITE}[8] {Fore.GREEN}فحص GitHub للبيانات المسربة          {Fore.BLUE}║
║  {Fore.WHITE}[9] {Fore.GREEN}تقرير استطلاع كامل (Full Recon)      {Fore.BLUE}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية             {Fore.BLUE}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def subdomain_scan(self, domain):
        """جمع النطاقات الفرعية"""
        print(f"\n{Fore.YELLOW}[*] جاري جمع النطاقات الفرعية لـ: {domain}{Style.RESET_ALL}")
        
        # قائمة موسعة للنطاقات الفرعية الشائعة
        subdomains = [
            "www", "mail", "ftp", "admin", "api", "blog", "dev", "test",
            "vpn", "remote", "portal", "cpanel", "webmail", "support",
            "help", "ssh", "smtp", "pop3", "imap", "mysql", "db",
            "database", "backup", "beta", "stage", "staging", "prod",
            "production", "app", "mobile", "m", "shop", "store", "cdn",
            "static", "assets", "img", "images", "upload", "download",
            "media", "video", "tv", "radio", "forum", "chat", "community",
            "wiki", "docs", "documentation", "helpdesk", "ticket",
            "status", "stats", "analytics", "monitor", "logs", "git",
            "svn", "jenkins", "jira", "confluence", "wiki", "board",
            "meet", "call", "phone", "fax", "server", "host", "hosting",
            "cloud", "ns1", "ns2", "ns3", "mx1", "mx2", "dns", "dhcp",
            "gateway", "router", "switch", "proxy", "firewall", "waf",
            "sso", "oauth", "auth", "login", "register", "signup",
            "password", "reset", "recovery", "verify", "confirm",
            "whm", "reseller", "client", "customer", "user", "member",
            "partner", "affiliate", "vendor", "supplier", "internal",
            "external", "corp", "office", "hq", "global", "local"
        ]
        
        found = []
        for sub in subdomains:
            try:
                full_domain = f"{sub}.{domain}"
                ip = socket.gethostbyname(full_domain)
                found.append((full_domain, ip))
                print(f"    {Fore.GREEN}[✓] {full_domain:30s} -> {ip}{Style.RESET_ALL}")
            except socket.gaierror:
                pass
        
        print(f"\n{Fore.WHITE}[+] تم العثور على {len(found)} نطاق فرعي من {len(subdomains)}{Style.RESET_ALL}")
        
        # حفظ النتائج
        with open(f"subdomains_{domain}.txt", "w") as f:
            for sub, ip in found:
                f.write(f"{sub},{ip}\n")
        print(f"{Fore.GREEN}[+] تم حفظ النتائج في subdomains_{domain}.txt{Style.RESET_ALL}")
    
    def dns_enum(self, domain):
        """فحص كامل لسجلات DNS"""
        print(f"\n{Fore.YELLOW}[*] فحص سجلات DNS لـ: {domain}{Style.RESET_ALL}")
        
        record_types = {
            'A': 'IPv4 Address',
            'AAAA': 'IPv6 Address',
            'MX': 'Mail Exchange',
            'NS': 'Name Servers',
            'TXT': 'Text Records',
            'SOA': 'Start of Authority',
            'CNAME': 'Canonical Name',
            'SRV': 'Service Records',
            'PTR': 'Pointer Records',
            'CAA': 'Certification Authority'
        }
        
        for rtype, desc in record_types.items():
            try:
                answers = dns.resolver.resolve(domain, rtype)
                print(f"\n{Fore.CYAN}[+] {rtype} ({desc}):{Style.RESET_ALL}")
                for rdata in answers:
                    print(f"    {Fore.WHITE}{rdata}{Style.RESET_ALL}")
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                print(f"\n{Fore.CYAN}[+] {rtype}: {Fore.RED}غير موجود{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.CYAN}[+] {rtype}: {Fore.YELLOW}خطأ: {e}{Style.RESET_ALL}")
    
    def web_tech_detect(self, url):
        """كشف تقنيات الموقع"""
        print(f"\n{Fore.YELLOW}[*] فحص تقنيات الموقع: {url}{Style.RESET_ALL}")
        
        try:
            r = requests.get(url, timeout=10, 
                           headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
            
            headers = r.headers
            
            techs = {
                'Server': headers.get('Server', 'غير معروف'),
                'X-Powered-By': headers.get('X-Powered-By', 'غير متاح'),
                'Content-Type': headers.get('Content-Type', 'غير متاح'),
                'Set-Cookie': 'مستخدم' if 'Set-Cookie' in headers else 'غير مستخدم',
                'X-Frame-Options': headers.get('X-Frame-Options', 'غير موجود - خطر Clickjacking'),
                'X-XSS-Protection': headers.get('X-XSS-Protection', 'غير موجود'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'غير موجود'),
                'Content-Security-Policy': 'مستخدم' if 'Content-Security-Policy' in headers else 'غير مستخدم',
                'Strict-Transport-Security': 'مستخدم' if 'Strict-Transport-Security' in headers else 'غير مستخدم'
            }
            
            print(f"\n{Fore.GREEN}[+] معلومات الرأس (Headers):{Style.RESET_ALL}")
            for key, val in techs.items():
                color = Fore.GREEN if 'غير' not in str(val) and 'غير موجود' not in str(val) else Fore.YELLOW
                if 'خطر' in str(val):
                    color = Fore.RED
                print(f"    {color}{key}: {val}{Style.RESET_ALL}")
            
            # تحليل الـ HTML
            if 'WordPress' in r.text[:2000]:
                print(f"\n    {Fore.GREEN}[✓] الموقع يستخدم WordPress{Style.RESET_ALL}")
            if 'wp-content' in r.text:
                print(f"    {Fore.GREEN}[✓] تم اكتشاف مسار WordPress{Style.RESET_ALL}")
            if 'Joomla' in r.text[:2000]:
                print(f"    {Fore.GREEN}[✓] الموقع يستخدم Joomla{Style.RESET_ALL}")
            if 'Drupal' in r.text[:2000]:
                print(f"    {Fore.GREEN}[✓] الموقع يستخدم Drupal{Style.RESET_ALL}")
            if 'Laravel' in r.text or 'csrf-token' in r.text:
                print(f"    {Fore.GREEN}[✓] الموقع يستخدم Laravel{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}[!] فشل الاتصال: {e}{Style.RESET_ALL}")
    
    def wayback_urls(self, domain):
        """جمع URLs من Internet Archive"""
        print(f"\n{Fore.YELLOW}[*] جلب URLs من Wayback Machine لـ: {domain}{Style.RESET_ALL}")
        
        try:
            r = requests.get(f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey")
            if r.status_code == 200:
                urls = r.json()
                print(f"{Fore.GREEN}[+] تم العثور على {len(urls)} URL{Style.RESET_ALL}")
                
                # تصفية URLs مهمة
                interesting = ['admin', 'login', 'api', 'config', 'backup', 'db', 'sql', 'password', 'secret', 'key', 'token', 'auth']
                found_interesting = []
                
                for url in urls[1:]:  # تخطي الرأس
                    url_str = url[0] if isinstance(url, list) else url
                    for keyword in interesting:
                        if keyword in url_str.lower():
                            found_interesting.append(url_str)
                            break
                
                if found_interesting:
                    print(f"\n{Fore.YELLOW}[!] URLs مهمة تم العثور عليها:{Style.RESET_ALL}")
                    for url in found_interesting[:20]:
                        print(f"    {Fore.RED}{url}{Style.RESET_ALL}")
                    
                    # حفظ النتائج
                    with open(f"wayback_{domain}.txt", "w") as f:
                        for url in found_interesting:
                            f.write(f"{url}\n")
                    print(f"\n{Fore.GREEN}[+] تم حفظ {len(found_interesting)} URL في wayback_{domain}.txt{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[-] لا توجد نتائج{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
    
    def run(self):
        show_banner("recon")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر العملية [0-9]: {Style.RESET_ALL}")
            
            if choice == "0":
                break
            elif choice == "1":
                domain = input(f"\n{Fore.WHITE}[?] النطاق (example.com): {Style.RESET_ALL}").strip()
                if domain:
                    self.subdomain_scan(domain)
            elif choice == "2":
                domain = input(f"\n{Fore.WHITE}[?] النطاق: {Style.RESET_ALL}").strip()
                if domain:
                    self.dns_enum(domain)
            elif choice == "4":
                url = input(f"\n{Fore.WHITE}[?] الرابط (https://example.com): {Style.RESET_ALL}").strip()
                if url:
                    self.web_tech_detect(url)
            elif choice == "6":
                domain = input(f"\n{Fore.WHITE}[?] النطاق: {Style.RESET_ALL}").strip()
                if domain:
                    self.wayback_urls(domain)
            elif choice == "9":
                domain = input(f"\n{Fore.WHITE}[?] النطاق للفحص الشامل: {Style.RESET_ALL}").strip()
                if domain:
                    print(f"\n{Fore.GREEN}[*] بدء الفحص الشامل...{Style.RESET_ALL}")
                    self.dns_enum(domain)
                    self.subdomain_scan(domain)
                    self.web_tech_detect(f"https://{domain}")
                    self.wayback_urls(domain)
                    print(f"\n{Fore.GREEN}[✓] اكتمل الفحص الشامل!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
