#!/data/data/com.termux/files/usr/bin/bash
# Camoro Setup - Termux & Linux (Fixed)

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
echo "========================================"
echo "   CAMORO SETUP - Termux & Linux"
echo "========================================"
echo -e "${NC}"

# Detect python command
if command -v python3 >/dev/null 2>&1; then
    PY=python3
    PIP=pip3
elif command -v python >/dev/null 2>&1; then
    PY=python
    PIP=pip
else
    echo -e "${RED}[!] Python not found${NC}"
    exit 1
fi

# Install system packages
if [ -d "/data/data/com.termux" ]; then
    echo -e "${CYAN}[+] Termux detected${NC}"
    pkg update -y
    pkg install -y python git curl openssl libffi clang binutils
    $PY -m pip install --upgrade pip setuptools wheel
else
    echo -e "${CYAN}[+] Linux detected${NC}"
    if command -v sudo >/dev/null 2>&1; then
        sudo apt-get update -y
        sudo apt-get install -y python3 python3-pip git curl
    fi
    $PY -m pip install --upgrade pip setuptools wheel
fi

echo ""
echo -e "${YELLOW}[*] Installing Python packages one by one...${NC}"

# Core packages (must succeed)
for pkg in requests beautifulsoup4 colorama urllib3 certifi tqdm; do
    echo -e "${CYAN}[+] Installing $pkg ...${NC}"
    $PY -m pip install "$pkg" --no-cache-dir
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}    OK: $pkg${NC}"
    else
        echo -e "${RED}    FAIL: $pkg${NC}"
    fi
done

# Optional packages (ignore failures)
for pkg in pysocks httpx fake-useragent; do
    echo -e "${CYAN}[+] Installing optional $pkg ...${NC}"
    $PY -m pip install "$pkg" --no-cache-dir 2>/dev/null
done

# cryptography is optional and fails often on Termux
echo -e "${YELLOW}[*] Trying cryptography (optional)...${NC}"
$PY -m pip install cryptography --only-binary=:all: 2>/dev/null || \
$PY -m pip install cryptography 2>/dev/null || \
echo -e "${YELLOW}[!] cryptography skipped (tool still works)${NC}"

# Create data dirs
mkdir -p data/wordlists output/results output/profiles output/wordlists
touch data/proxies.txt

# Verify critical imports
echo ""
echo -e "${YELLOW}[*] Verifying install...${NC}"
$PY - <<'EOF'
import sys
ok = True
for m in ["requests", "bs4", "colorama"]:
    try:
        __import__(m if m != "bs4" else "bs4")
        print(f"  OK: {m}")
    except Exception as e:
        print(f"  FAIL: {m} -> {e}")
        ok = False
sys.exit(0 if ok else 1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[+] Installation completed!${NC}"
    echo -e "${GREEN}[+] Run: python camoro.py${NC}"
    echo -e "${GREEN}         or: python3 camoro.py${NC}"
else
    echo ""
    echo -e "${RED}[!] Some packages failed. Try manually:${NC}"
    echo -e "${YELLOW}    pip install requests beautifulsoup4 colorama${NC}"
fi
