#!/usr/bin/env python3
import hashlib
import json
import re
import time
import uuid

import requests

from .config import INSTAGRAM_ENDPOINTS, REQUEST_TIMEOUT, get_random_headers
from .info_gather import format_proxy


class InstagramSession:
    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.csrf_token = None
        self.session_id = None
        self.mid = None
        self.logged_in = False
        self.current_username = None
        self.proxy = proxy
        px = format_proxy(proxy)
        if px:
            self.session.proxies.update(px)
        self._initialize_session()

    def _initialize_session(self):
        try:
            headers = get_random_headers()
            resp = self.session.get(
                "https://www.instagram.com/",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            self._extract_csrf(resp)
            self._set_device_fingerprint()
        except requests.RequestException:
            if not self.csrf_token:
                self.csrf_token = hashlib.md5(str(time.time()).encode()).hexdigest()[
                    :32
                ]

    def _extract_csrf(self, response=None):
        csrf = self.session.cookies.get("csrftoken")
        if csrf:
            self.csrf_token = csrf
            return
        if response is not None and getattr(response, "text", None):
            match = re.search(r'"csrf_token":"([^"]+)"', response.text)
            if match:
                self.csrf_token = match.group(1)
                return
        if not self.csrf_token:
            self.csrf_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:32]

    def _set_device_fingerprint(self):
        device_id = str(uuid.uuid4()).upper()
        self.session.cookies.set("ig_did", device_id, domain=".instagram.com")
        self.session.cookies.set(
            "mid",
            f"Z{hashlib.md5(device_id.encode()).hexdigest()[:16]}",
            domain=".instagram.com",
        )

    def _build_enc_password(self, password):
        ts = int(time.time())
        return f"#PWD_INSTAGRAM_BROWSER:0:{ts}:{password}"

    def attempt_login(self, username, password):
        if not self.csrf_token:
            self._initialize_session()

        login_url = INSTAGRAM_ENDPOINTS["login"]
        headers = get_random_headers()
        headers.update(
            {
                "X-CSRFToken": self.csrf_token or "",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.instagram.com/accounts/login/",
                "Origin": "https://www.instagram.com",
            }
        )

        data = {
            "username": username,
            "enc_password": self._build_enc_password(password),
            "queryParams": "{}",
            "optIntoOneTap": "false",
            "stopDeletionNonce": "",
            "trustedDeviceRecords": "{}",
        }

        try:
            response = self.session.post(
                login_url,
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
            self._extract_csrf(response)

            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {"message": "unknown_error", "status": "fail"}

            if response.status_code == 429:
                return False, {"error": "rate_limited", "message": "HTTP 429"}

            if result.get("authenticated") or result.get("user"):
                self.logged_in = True
                self.current_username = username
                return True, result

            message = str(result.get("message", "") or "")
            low = message.lower()
            if "checkpoint" in low or result.get("checkpoint_url"):
                return False, {
                    "error": "checkpoint_required",
                    "message": "checkpoint/2FA",
                }
            if "rate" in low or "block" in low or "wait" in low:
                return False, {"error": "rate_limited", "message": message}
            if "invalid" in low or "incorrect" in low or "password" in low:
                return False, {
                    "error": "invalid_credentials",
                    "message": "invalid password",
                }
            if response.status_code in (401, 403):
                return False, {
                    "error": "rate_limited",
                    "message": f"HTTP {response.status_code}",
                }
            return False, result
        except requests.RequestException as e:
            return False, {"error": "network_error", "message": str(e)}

    def reset_session(self):
        try:
            self.session.close()
        except Exception:
            pass
        self.session = requests.Session()
        px = format_proxy(self.proxy)
        if px:
            self.session.proxies.update(px)
        self.csrf_token = None
        self.logged_in = False
        self._initialize_session()
