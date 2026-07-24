"""Utilities: proxy, user-agent rotation, rate-limit handling, logging."""

import os
import random
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# ── User-Agent rotation (mobile + desktop) ──────────────────────────
USER_AGENTS = [
    # iOS Instagram
    "Instagram 273.0.0.21.113 (iPhone13,3; iOS 16_5; en_US; en-US; scale=3.00; 1170x2532; 444542477)",
    "Instagram 275.0.0.28.115 (iPhone14,5; iOS 16_6; en_GB; en-GB; scale=3.00; 1170x2532; 448723612)",
    # Android Instagram
    "Instagram 274.1.0.26.104 (Android 13; 320dpi; 1080x2400; samsung; SM-S908B; g0s; g0s; en_US; 448723612)",
    "Instagram 276.0.0.18.110 (Android 14; 420dpi; 1440x3120; Google; Pixel 8 Pro; husky; husky; en_US; 450123789)",
    # Desktop Chrome / Firefox
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

# ── Proxy support ───────────────────────────────────────────────────
def load_proxies(proxy_file: Optional[str] = None) -> list:
    """Load HTTP/HTTPS proxies from file (one per line: http://user:pass@host:port)."""
    proxies = []
    if proxy_file and os.path.isfile(proxy_file):
        with open(proxy_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    proxies.append(line)
    return proxies


def get_random_ua() -> str:
    return random.choice(USER_AGENTS)


def get_session(proxy: Optional[str] = None) -> 'requests.Session':
    import requests
    s = requests.Session()
    s.headers.update({
        "User-Agent": get_random_ua(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "*/*",
        "X-IG-App-ID": "936619743392459",
    })
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


# ── Simple logger ───────────────────────────────────────────────────
def setup_logger(name: str = "instacrack") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(f"instacrack_{datetime.now():%Y%m%d_%H%M%S}.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
