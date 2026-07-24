# InstaCrackAI 🔥

**Advanced Instagram Security Assessment Tool**
— OSINT Reconnaissance + AI Password Generation + Login Attack

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-green)
![License](https://img.shields.io/badge/license-MIT-red)

## 📌 Features

- **🔍 OSINT Recon**: Profile info, followers, bio analysis, engagement rate, hashtags, mentions
- **🧠 AI Password Generator**: Builds personalized wordlists from target's personal data
- **⚡ Login Attack**: Full Instagram login flow with libsodium password encryption
- **🌐 Proxy Support**: Rotate proxies to avoid rate limiting
- **📊 Reports**: JSON/CSV export, colored terminal output

## ⚙️ Installation

### Linux (Kali / Ubuntu / Debian)
```bash
git clone https://github.com/YOUR_USERNAME/InstaCrackAI.git
cd InstaCrackAI
pip install -r requirements.txt

# For password encryption:
pip install pysodium
# OR
pip install pynacl
