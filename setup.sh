#!/bin/bash
# camoro - Setup Script for Termux / Linux / iSH

echo -e "\033[95m╔══════════════════════════════════════════╗"
echo -e "║       CAMORO - Setup & Install           ║"
echo -e "╚══════════════════════════════════════════╝\033[0m"
echo ""

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo -e "\033[91m[!] Python3 not found! Installing...\033[0m"
    if command -v apt &> /dev/null; then
        apt update && apt install python3 -y
    elif command -v pkg &> /dev/null; then
        pkg update && pkg install python3 -y
    elif command -v apk &> /dev/null; then
        apk add python3
    else
        echo "Please install Python3 manually"
        exit 1
    fi
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "\033[91m[!] pip3 not found! Installing...\033[0m"
    if command -v apt &> /dev/null; then
        apt install python3-pip -y
    elif command -v pkg &> /dev/null; then
        pkg install python-pip -y
    fi
fi

# Install requirements
echo -e "\033[96m[*] Installing Python dependencies...\033[0m"
pip3 install -r requirements.txt

# Make camoro.py executable
chmod +x camoro.py

echo ""
echo -e "\033[92m[✓] Installation complete!\033[0m"
echo -e "\033[93m[*] Run: python3 camoro.py\033[0m"
