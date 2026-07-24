#!/usr/bin/env python3
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PROXIES_FILE = os.path.join(DATA_DIR, "proxies.txt")

# رموز خاصة لكلمات المرور (مطلوبة من password_engine)
SPECIAL_CHARS = list("!@#$%^&*()_+-=[]{}|;:',.<>?/~`")
NUMBERS = list("0123456789")
YEARS = [str(y) for y in range(1980, 2027)]
COMMON_NUMBERS = [
    "123", "1234", "12345", "123456", "1234567", "12345678", "123456789",
    "00", "01", "07", "10", "11", "12", "13", "21", "22", "69", "77", "88", "99",
    "100", "200", "1000", "2000", "2020", "2021", "2022", "2023", "2024", "2025", "2026",
]

COMMON_PASSWORDS = [
    "password", "Password", "PASSWORD", "pass", "Pass123", "password1",
    "123456", "12345678", "123456789", "1234567890", "qwerty", "qwerty123",
    "abc123", "iloveyou", "admin", "welcome", "monkey", "dragon", "master",
    "letmein", "login", "princess", "football", "baseball", "soccer",
    "instagram", "insta", "insta123", "love", "lovely", "baby", "angel",
    "shadow", "sunshine", "princess1", "hello", "hello123", "freedom",
    "whatever", "qazwsx", "trustno1", "batman", "zaq1zaq1", "password123",
]

NAME_SUFFIXES = [
    "123", "1234", "12345", "1", "12", "01", "07", "10", "11",
    "!", "@", "#", "!!", "@@", "01!", "123!", "2020", "2021", "2022",
    "2023", "2024", "2025", "2026", "69", "007", "99", "88", "77",
]

LEET_MAP = {
    "a": ["a", "A", "4", "@"],
    "e": ["e", "E", "3"],
    "i": ["i", "I", "1", "!"],
    "o": ["o", "O", "0"],
    "s": ["s", "S", "5", "$"],
    "t": ["t", "T", "7"],
    "l": ["l", "L", "1"],
    "g": ["g", "G", "9"],
    "b": ["b", "B", "8"],
}

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Instagram 192.0.0.37.107 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 301484483)",
    "Instagram 306.0.0.0.0 Android (31/12; 480dpi; 1080x2340; Xiaomi; M2101K6G; sweet; qcom; en_US; 541635890)",
]

IG_APP_ID = "936619743392459"
MAX_ATTEMPTS_PER_PROXY = 5
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_ATTEMPTS = (2.0, 5.0)

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_random_headers():
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "X-IG-App-ID": IG_APP_ID,
        "Origin": "https://www.instagram.com",
        "Referer": "https://www.instagram.com/",
    }

def load_proxies():
    proxies = []
    if not os.path.isfile(PROXIES_FILE):
        return proxies
    try:
        with open(PROXIES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    proxies.append(line)
    except OSError:
        pass
    return proxies
