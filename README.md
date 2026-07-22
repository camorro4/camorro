# 🏴 Camorro - Advanced Penetration Testing Framework

![Version](https://img.shields.io/badge/version-2.0.0-red)
![Platform](https://img.shields.io/badge/platform-Termux-brightgreen)
![Language](https://img.shields.io/badge/language-Python-blue)

**Camorro** هو إطار عمل متكامل لاختبار الاختراق يعمل على Termux، يجمع أفضل الأدوات مفتوحة المصدر في واجهة واحدة موحدة.

## 📋 الميزات

| الوحدة | الوصف | البديل لـ |
|--------|-------|-----------|
| 🔍 OSINT | جمع المعلومات | Maltego, Shodan, Censys |
| 📡 Scanner | فحص الثغرات | Burp Suite, Nessus |
| 💥 Exploit | الاستغلال | Metasploit Pro, Cobalt Strike |
| 🎯 Payload | توليد البايلودات | Cobalt Strike, Brute Ratel |
| 🌐 Network | هجمات الشبكة | WiFi Pineapple |
| 🕵️ Recon | الاستطلاع | Shodan Pro, Censys |
| 🌍 Web | فحص الويب | Burp Suite Enterprise |
| ☠️ C2 | نظام التحكم | Cobalt Strike, Covenant |
| 🐬 Flipper | محاكي Flipper Zero | Flipper Zero |
| 🦆 Ducky | Rubber Ducky | Rubber Ducky |

## ⚡ التثبيت

```bash
# 1. تأكد من وجود Termux محدث
pkg update && pkg upgrade

# 2. Clone المشروع
git clone [https://github.com/camorro3/camorro.git]

# 3. تشغيل سكريبت التثبيت
chmod +x install.sh
./install.sh

# 4. تشغيل الأداة
python camorro.py
