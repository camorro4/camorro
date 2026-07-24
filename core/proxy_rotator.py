#!/usr/bin/env python3
import os
import random
import threading
import time

from .config import (
    COOLDOWN_PERIOD,
    MAX_ATTEMPTS_PER_IP,
    MAX_DELAY,
    MIN_DELAY,
    PROXY_FILE,
    USER_AGENTS,
)
from .info_gather import format_proxy


class ProxyRotator:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.attempts_on_current = 0
        self.blocked_proxies = {}
        self.lock = threading.Lock()
        self._load_proxies()

    def _load_proxies(self):
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, "r", encoding="utf-8", errors="ignore") as f:
                self.proxies = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
        else:
            self.proxies = []
        print(f"    {len(self.proxies)} proxies loaded")

    def add_proxy(self, proxy_string):
        proxy_string = (proxy_string or "").strip()
        if not proxy_string:
            return False
        with self.lock:
            if proxy_string not in self.proxies:
                self.proxies.append(proxy_string)
                self._save_proxies()
                return True
        return False

    def remove_proxy(self, proxy_string):
        with self.lock:
            if proxy_string in self.proxies:
                self.proxies.remove(proxy_string)
                self._save_proxies()
                return True
        return False

    def _save_proxies(self):
        os.makedirs(os.path.dirname(PROXY_FILE), exist_ok=True)
        with open(PROXY_FILE, "w", encoding="utf-8") as f:
            for proxy in self.proxies:
                f.write(proxy + "\n")

    def get_next_proxy(self):
        with self.lock:
            now = time.time()
            cooled = [
                p
                for p, t in list(self.blocked_proxies.items())
                if now - t >= COOLDOWN_PERIOD
            ]
            for p in cooled:
                del self.blocked_proxies[p]
                if p not in self.proxies:
                    self.proxies.append(p)

            if self.attempts_on_current >= MAX_ATTEMPTS_PER_IP:
                self._rotate()

            if not self.proxies:
                self.current_proxy = None
                self.attempts_on_current = 0
                return None

            available = [p for p in self.proxies if p not in self.blocked_proxies]
            if not available:
                self.blocked_proxies.clear()
                available = list(self.proxies)

            self.current_proxy = random.choice(available)
            self.attempts_on_current = 0
            return self.current_proxy

    def mark_blocked(self, proxy=None):
        with self.lock:
            proxy = proxy or self.current_proxy
            if proxy and proxy in self.proxies:
                self.proxies.remove(proxy)
                self.blocked_proxies[proxy] = time.time()
            self._rotate()

    def _rotate(self):
        self.current_proxy = None
        self.attempts_on_current = 0

    def report_attempt(self):
        with self.lock:
            self.attempts_on_current += 1

    def get_random_delay(self):
        return random.uniform(MIN_DELAY, MAX_DELAY) + min(
            self.attempts_on_current * 0.3, 5.0
        )

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def format_proxy_for_requests(self, proxy_string):
        return format_proxy(proxy_string)

    def list_proxies(self):
        return list(self.proxies)
