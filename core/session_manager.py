#!/usr/bin/env python3
import hashlib
import json
import random
import re
import time
import uuid

import requests

from .config import LOGIN_ENDPOINTS, REQUEST_TIMEOUT, get_random_headers
from .info_gather import format_proxy


class InstagramSession:
    def __init__(self, proxy=None, endpoint=None):
        self.session = requests.Session()
        self.csrf_token = None
        self.logged_in = False
        self.current_username = None
        self.proxy = proxy
        self.endpoint = endpoint or random.choice(LOGIN_ENDPOINTS)
        self.device_id = str(uuid.uuid4())
        px = format_proxy(proxy)
        if px:
            self.session.proxies.update(px)
        self._initialize_session()

    def _initialize_session(self):
        try:
            r = self.session.get(
                "https://www.instagram.com/accounts/login/",
                headers=get_random_headers(),
                timeout=REQUEST_TIMEOUT,
            )
            self._extract_csrf(r)
            self.session.cookies.set("ig_did", self.device_id.upper(), domain=".instagram.com")
            mid = "Z" + hashlib.md5(self.device_id.encode()).hexdigest()[:16]
            self.session.cookies.set("mid", mid, domain=".instagram.com")
        except requests.RequestException:
            if not self.csrf_token:
                self.csrf_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:32]

    def _extract_csrf(self, response=None):
        csrf = self.session.cookies.get("csrftoken")
        if csrf:
            self.csrf_token = csrf
            return
        if response is not None and getattr(response, "text", None):
            m = re.search(r'"csrf_token"\s*:\s*"([^"]+)"', response.text)
            if m:
                self.csrf_token = m.group(1)
                return
        if not self.csrf_token:
            self.csrf_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:32]

    def _enc_password(self, password):
        # صيغة المتصفح العامة (#PWD_INSTAGRAM_BROWSER:0:timestamp:password)
        ts = int(time.time())
        return f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{password}"

    def attempt_login(self, username, password):
        if not self.csrf_token:
            self._initialize_session()

        headers = get_random_headers(username)
        headers.update(
            {
                "X-CSRFToken": self.csrf_token or "",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.instagram.com/accounts/login/",
                "Origin": "https://www.instagram.com",
                "X-Instagram-AJAX": str(random.randint(1000000000, 9999999999)),
                "X-IG-WWW-Claim": "0",
            }
        )

        data = {
            "username": username,
            "enc_password": self._enc_password(password),
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "trustedDeviceRecords": "{}",
        }

        try:
            r = self.session.post(
                self.endpoint,
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
            self._extract_csrf(r)

            if r.status_code == 429:
                return False, {"error": "rate_limited", "message": "HTTP 429", "http": 429}
            if r.status_code in (401, 403):
                return False, {
                    "error": "rate_limited",
                    "message": f"HTTP {r.status_code}",
                    "http": r.status_code,
                }

            try:
                result = r.json()
            except json.JSONDecodeError:
                return False, {"error": "bad_response", "message": (r.text or "")[:120], "http": r.status_code}

            if result.get("authenticated") or result.get("user") is True:
                self.logged_in = True
                self.current_username = username
                return True, result

            msg = str(result.get("message", "") or "")
            low = msg.lower()
            if "checkpoint" in low or result.get("checkpoint_url"):
                return False, {"error": "checkpoint_required", "message": msg}
            if any(x in low for x in ("rate", "wait", "block", "spam")):
                return False, {"error": "rate_limited", "message": msg}
            if result.get("status") == "fail" or "password" in low or "invalid" in low:
                return False, {"error": "invalid_credentials", "message": msg or "wrong"}

            return False, {"error": "unknown", "message": msg, "raw": result}
        except requests.RequestException as e:
            return False, {"error": "network_error", "message": str(e)}

    def reset_session(self, proxy=None, endpoint=None):
        try:
            self.session.close()
        except Exception:
            pass
        self.session = requests.Session()
        self.csrf_token = None
        self.logged_in = False
        self.proxy = proxy if proxy is not None else self.proxy
        self.endpoint = endpoint or random.choice(LOGIN_ENDPOINTS)
        self.device_id = str(uuid.uuid4())
        px = format_proxy(self.proxy)
        if px:
            self.session.proxies.update(px)
        self._initialize_session()
