#!/data/data/com.termux/files/usr/bin/bash
# -*- coding: utf-8 -*-
# Camorro - Installation Script for Termux

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

clear
echo -e "${RED}"
echo " ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗ ██████╗ ██████╗ "
echo "██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗"
echo "██║     ███████║██╔████╔██║██║   ██║██████╔╝██████╔╝██████╔╝"
echo "██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██╔══██╗"
echo "╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║██████╔╝"
echo " ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ "
echo -e "${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "${CYAN}    Camorro Pentesting Framework Installer      ${NC}"
echo -e "${GREEN}==============================================${NC}"
echo ""

# التحقق من وجود Termux
echo -e "${YELLOW}[*] التحقق من البيئة...${NC}"
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}[!] هذا السكريبت مخصص لـ Termux على Android${NC}"
    exit 1
fi

# تحديث Termux
echo -e "${YELLOW}[*] تحديث Termux...${NC}"
pkg update -y && pkg upgrade -y

# تثبيت المتطلبات الأساسية
echo -e "${YELLOW}[*] تثبيت المتطلبات الأساسية...${NC}"

# أدوات Python
echo -e "${CYAN}[+] تثبيت Python والمكتبات...${NC}"
pkg install -y python python-pip git wget curl

# أدوات الشبكات
echo -e "${CYAN}[+] تثبيت أدوات الشبكات...${NC}"
pkg install -y nmap net-tools dnsutils traceroute hydra

# أدوات الاختراق
echo -e "${CYAN}[+] تثبيت أدوات الاختراق...${NC}"
pkg install -y metasploit sqlmap hydra

# أدوات إضافية
echo -e "${CYAN}[+] تثبيت أدوات إضافية...${NC}"
pkg install -y termux-api jq openssh

# تثبيت مكتبات Python
echo -e "${CYAN}[+] تثبيت مكتبات Python...${NC}"
pip install colorama requests dnspython python-whois

# إنشاء المجلدات
echo -e "${CYAN}[+] إنشاء هيكل المشروع...${NC}"
mkdir -p modules tools/config 2>/dev/null
mkdir -p tools/custom_payloads 2>/dev/null

# ضبط الصلاحيات
chmod +x camorro.py 2>/dev/null

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       ✅  تم التثبيت بنجاح!              ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                          ║${NC}"
echo -e "${GREEN}║  ${WHITE}للتشغيل:${NC}                               ${GREEN}║${NC}"
echo -e "${GREEN}║  ${CYAN}python camorro.py${NC}                        ${GREEN}║${NC}"
echo -e "${GREEN}║                                          ║${NC}"
echo -e "${GREEN}║  ${WHITE}أو اجعله executable:${NC}                    ${GREEN}║${NC}"
echo -e "${GREEN}║  ${CYAN}chmod +x camorro.py${NC}                      ${GREEN}║${NC}"
echo -e "${GREEN}║  ${CYAN}./camorro.py${NC}                             ${GREEN}║${NC}"
echo -e "${GREEN}║                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
