# 🚀 Camoro - AI-Powered Instagram Security Testing Framework

> **Version:** 2.0.0  
> **Platform:** Termux | Linux  
> **Language:** Python 3.9+

---

## ⚠️ Legal Disclaimer

This tool is designed **exclusively for authorized security testing**. Users must have explicit permission from the account owner before use. Unauthorized access to accounts is illegal and unethical.

---

## 🔥 Features

- **AI-Powered Password Generation** - Generates 18,000+ intelligent password combinations based on:
  - Profile intelligence (bio, username, full name)
  - Personal information (birth date, girlfriend, pet, nickname)
  - Pattern mutations (leet speak, dates, common patterns)
  - Contextual AI analysis

- **Smart Proxy Rotation** - Automatic proxy switching to avoid detection:
  - Rotates after configurable attempt thresholds
  - Cooldown management for blocked proxies
  - Multi-format proxy support (HTTP, SOCKS5, with auth)

- **Anti-Detection System**:
  - User-Agent rotation pool
  - Header fingerprint randomization
  - CSRF token management
  - Device ID rotation
  - Randomized delays between attempts

- **Multi-Threaded Attacks** - Configurable concurrent workers
- **Profile Intelligence Gathering** - Extracts actionable intel from Instagram profiles
- **Interactive CLI** - Beautiful terminal interface with Rich library
- **Result Logging** - All successful credentials saved securely

---

## 📦 Installation

### Termux
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/YOUR_USERNAME/camoro.git
cd camoro
bash setup.sh
