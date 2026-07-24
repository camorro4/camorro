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
    ROTATE_EVERY,
    USER_AGENTS,
)


class ProxyRotator:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.attempts_on_current = 0
        self.blocked_proxies = {}
        self.lock = threading.Lock()
        self._load_proxies()

    def _load_proxies(self):
        self.proxies = []
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.proxies.append(line)
        print(f"    {len(self.proxies)} proxies loaded")

    def add_proxy(self, proxy_string):
        proxy_string = (proxy_string or "").strip()
        if not proxy_string:
            return False
        with self.lock:
            if proxy_string not in self.proxies:
                self.proxies.append(proxy_string)
                self._save()
                return True
        return False

    def remove_proxy(self, proxy_string):
        with self.lock:
            if proxy_string in self.proxies:
                self.proxies.remove(proxy_string)
                self._save()
                return True
        return False

    def _save(self):
        os.makedirs(os.path.dirname(PROXY_FILE), exist_ok=True)
        with open(PROXY_FILE, "w", encoding="utf-8") as f:
            for p in self.proxies:
                f.write(p + "\n")

    def list_proxies(self):
        return list(self.proxies)

    def get_next_proxy(self, force=False):
        with self.lock:
            now = time.time()
            for p, t in list(self.blocked_proxies.items()):
                if now - t >= COOLDOWN_PERIOD:
                    del self.blocked_proxies[p]
                    if p not in self.proxies:
                        self.proxies.append(p)

            need = force or self.attempts_on_current >= ROTATE_EVERY
            if need:
                self.current_proxy = None
                self.attempts_on_current = 0

            if not self.proxies:
                self.current_proxy = None
                return None

            if self.current_proxy and not need and self.current_proxy not in self.blocked_proxies:
                return self.current_proxy

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
            self.current_proxy = None
            self.attempts_on_current = 0

    def report_attempt(self):
        with self.lock:
            self.attempts_on_current += 1

    def should_rotate(self):
        with self.lock:
            return self.attempts_on_current >= ROTATE_EVERY

    def get_random_delay(self):
        return random.uniform(MIN_DELAY, MAX_DELAY)

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)
