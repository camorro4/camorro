#!/usr/bin/env python3
"""CAMORRO recon — public Instagram OSINT with multi-fallback + debug."""
import json
import re
import time
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from modules.utils import ensure_dirs, BASE, clean_username

console = Console()

# Mobile UA = softer anti-bot bucket
UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1"
)
APP_ID = "936619743392459"


class Recon:
    def __init__(self, username: str, proxies: dict = None, timeout: int = 25, debug: bool = True):
        self.username = clean_username(username)
        self.proxies = proxies or {}
        self.timeout = timeout
        self.debug = debug
        self.data = {}
        self.last_error = ""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "X-IG-App-ID": APP_ID,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "Origin": "https://www.instagram.com",
            "Connection": "keep-alive",
        })

    def _log(self, msg: str):
        if self.debug:
            console.print(f"[dim][DEBUG] {msg}[/dim]")

    def _get(self, url: str, **kw):
        headers = kw.pop("headers", {})
        h = dict(self.session.headers)
        h.update(headers)
        return self.session.get(
            url,
            timeout=self.timeout,
            proxies=self.proxies,
            headers=h,
            allow_redirects=True,
            **kw,
        )

    def _warmup(self) -> bool:
        """Get csrftoken / mid cookies — required for API."""
        try:
            r = self._get("https://www.instagram.com/", headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            })
            self._log(f"homepage HTTP {r.status_code} cookies={list(self.session.cookies.keys())}")
            csrf = self.session.cookies.get("csrftoken")
            if csrf:
                self.session.headers["X-CSRFToken"] = csrf
            # touch profile page (IG often needs this before API)
            r2 = self._get(
                f"https://www.instagram.com/{self.username}/",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer": "https://www.instagram.com/",
                },
            )
            self._log(f"profile page HTTP {r2.status_code} len={len(r2.text)}")
            csrf = self.session.cookies.get("csrftoken") or csrf
            if csrf:
                self.session.headers["X-CSRFToken"] = csrf
            if r.status_code >= 400 and r2.status_code >= 400:
                self.last_error = f"Instagram blocked warmup ({r.status_code}/{r2.status_code})"
                return False
            return True
        except Exception as e:
            self.last_error = f"warmup failed: {e}"
            self._log(self.last_error)
            return False

    def _is_login_wall(self, html: str) -> bool:
        markers = [
            "loginForm",
            '"login_form"',
            "Log in to Instagram",
            "Create an account",
            "accounts/login",
        ]
        # real profile pages still mention login sometimes; require weak signal + no og:description
        has_login = sum(1 for m in markers if m.lower() in html.lower()) >= 2
        has_og = 'property="og:description"' in html or "og:description" in html
        return has_login and not has_og

    def _is_not_found(self, html: str, status: int) -> bool:
        if status == 404:
            return True
        bad = [
            "Sorry, this page isn't available",
            "page isn't available",
            "The link you followed may be broken",
        ]
        return any(b.lower() in html.lower() for b in bad)

    # ── Method 1: web_profile_info ──────────────────────────
    def _via_web_profile_info(self) -> dict:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        try:
            r = self._get(url, headers={
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"https://www.instagram.com/{self.username}/",
                "X-IG-App-ID": APP_ID,
            })
            self._log(f"web_profile_info HTTP {r.status_code} body={r.text[:120]!r}")
            if r.status_code == 200:
                j = r.json()
                user = (j.get("data") or {}).get("user")
                if user:
                    return self._parse_user(user)
            if r.status_code in (401, 403, 429):
                self.last_error = f"API blocked HTTP {r.status_code} (bad IP — use VPN/proxy)"
            else:
                self.last_error = f"API HTTP {r.status_code}"
        except Exception as e:
            self.last_error = f"API error: {e}"
            self._log(self.last_error)
        return {}

    # ── Method 2: i.instagram.com (same payload, mobile host) ─
    def _via_i_host(self) -> dict:
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        try:
            r = self._get(url, headers={
                "Accept": "*/*",
                "X-IG-App-ID": APP_ID,
                "Referer": f"https://www.instagram.com/{self.username}/",
            })
            self._log(f"i.instagram API HTTP {r.status_code}")
            if r.status_code == 200:
                j = r.json()
                user = (j.get("data") or {}).get("user")
                if user:
                    return self._parse_user(user)
        except Exception as e:
            self._log(f"i.instagram failed: {e}")
        return {}

    # ── Method 3: embedded JSON in HTML ─────────────────────
    def _via_html_json(self, html: str) -> dict:
        # Pattern A: window._sharedData
        m = re.search(r"window\._sharedData\s*=\s*(\{.+?\});</script>", html, re.S)
        if m:
            try:
                sd = json.loads(m.group(1))
                user = (
                    sd.get("entry_data", {})
                    .get("ProfilePage", [{}])[0]
                    .get("graphql", {})
                    .get("user")
                )
                if user:
                    self._log("parsed _sharedData")
                    return self._parse_user(user)
            except Exception as e:
                self._log(f"_sharedData parse fail: {e}")

        # Pattern B: Professional / Relay prefetched
        for pat in [
            r'"user"\s*:\s*(\{[^']{200,}?"edge_followed_by"[^']{50,}?\})\s*[,}]',
            r'ProfilePage["\']\s*,\s*(\{.+?\})\s*\]\s*,\s*["\']http',
        ]:
            m = re.search(pat, html, re.S)
            if not m:
                continue
            try:
                chunk = m.group(1)
                # try load as json
                if not chunk.strip().startswith("{"):
                    continue
                # sometimes truncated — find edge_followed_by block
            except Exception:
                pass

        # Pattern C: "biography":"...","edge_followed_by":{"count":N}
        bio_m = re.search(r'"biography":"(.*?)"\s*,', html)
        fol_m = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
        eng_m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
        posts_m = re.search(r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
        name_m = re.search(r'"full_name"\s*:\s*"(.*?)"', html)
        id_m = re.search(r'"id"\s*:\s*"(\d+)"', html)
        priv_m = re.search(r'"is_private"\s*:\s*(true|false)', html)
        if fol_m or bio_m:
            def unesc(s):
                if not s:
                    return ""
                try:
                    return json.loads(f'"{s}"')
                except Exception:
                    return s.encode().decode("unicode_escape", errors="ignore")

            self._log("parsed loose JSON fields from HTML")
            return {
                "username": self.username,
                "full_name": unesc(name_m.group(1)) if name_m else "",
                "userid": id_m.group(1) if id_m else "",
                "followers": int(fol_m.group(1)) if fol_m else 0,
                "following": int(eng_m.group(1)) if eng_m else 0,
                "posts": int(posts_m.group(1)) if posts_m else 0,
                "biography": unesc(bio_m.group(1)) if bio_m else "",
                "is_private": (priv_m.group(1) == "true") if priv_m else False,
                "is_verified": '"is_verified":true' in html,
                "is_business": '"is_business_account":true' in html,
                "category": "",
                "external_url": "",
                "profile_pic": "",
                "emails": [],
                "phones": [],
                "keywords": [],
                "source": "html_json",
            }
        return {}

    # ── Method 4: OpenGraph meta ────────────────────────────
    def _via_og(self, html: str) -> dict:
        def meta(prop):
            m = re.search(
                rf'(?:property|name)="{re.escape(prop)}"\s+content="([^"]*)"',
                html, re.I,
            )
            if not m:
                m = re.search(
                    rf'content="([^"]*)"\s+(?:property|name)="{re.escape(prop)}"',
                    html, re.I,
                )
            return (m.group(1) if m else "").replace("&amp;", "&")

        title = meta("og:title")
        desc = meta("og:description")
        image = meta("og:image")
        if not desc and not title:
            return {}

        # formats: "1,234 Followers, 56 Following, 78 Posts - See Instagram photos..."
        nums = re.findall(
            r"([\d,.]+)\s*(Followers|Following|Posts)",
            desc,
            re.I,
        )
        mapped = {}
        for v, k in nums:
            try:
                mapped[k.lower()] = int(v.replace(",", "").replace(".", ""))
            except ValueError:
                pass

        full_name = title.split("(")[0].strip() if title else ""
        # strip "• Instagram photos and videos"
        full_name = re.sub(r"\s*[•|].*$", "", full_name).strip()

        self._log(f"parsed OG title={title[:40]!r} followers={mapped.get('followers')}")
        bio = desc
        return {
            "username": self.username,
            "full_name": full_name,
            "userid": "",
            "followers": mapped.get("followers", 0),
            "following": mapped.get("following", 0),
            "posts": mapped.get("posts", 0),
            "biography": bio,
            "is_private": "This Account is Private" in html or "is private" in desc.lower(),
            "is_verified": False,
            "is_business": False,
            "category": "",
            "external_url": meta("og:url"),
            "profile_pic": image,
            "emails": re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", bio),
            "phones": re.findall(r"\+?\d{8,15}", bio),
            "keywords": self._keywords(bio + " " + full_name),
            "source": "og_meta",
        }

    def gather(self) -> dict:
        console.print(Panel.fit(
            f"[bold cyan]🔍 CAMORRO RECON → @{self.username}[/bold cyan]",
            border_style="cyan",
        ))

        if not self._warmup():
            console.print(f"[red][✗] {self.last_error or 'Cannot reach Instagram'}[/red]")
            console.print("[yellow]→ فعّل VPN (WARP/Proton) أو حط proxy صالح فـ proxies.txt[/yellow]")
            return {}

        # Method 1
        console.print("[*] Trying API web_profile_info ...")
        self.data = self._via_web_profile_info()
        if self._has_useful(self.data):
            self._finish_ok("web_profile_info")
            return self.data

        # Method 2
        console.print("[*] Trying i.instagram.com API ...")
        self.data = self._via_i_host()
        if self._has_useful(self.data):
            self._finish_ok("i.instagram")
            return self.data

        # HTML dump
        console.print("[*] Trying HTML parse ...")
        try:
            r = self._get(
                f"https://www.instagram.com/{self.username}/",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer": "https://www.instagram.com/",
                },
            )
            html = r.text
            self._log(f"HTML HTTP {r.status_code} len={len(html)}")

            if self._is_not_found(html, r.status_code):
                console.print(f"[red][✗] الحساب @{self.username} غير موجود[/red]")
                return {}

            if self._is_login_wall(html) or r.status_code in (401, 403, 429):
                console.print("[red][✗] Instagram رجّع Login Wall / Block على IP ديالك[/red]")
                console.print("[yellow]الحل:[/yellow]")
                console.print("  1) pkg install cloudflared  أو تطبيق WARP/VPN")
                console.print("  2) proxies.txt → proxy سكني (residential) HTTP")
                console.print("  3) عاود من شبكة Wi‑Fi/4G أخرى")
                # save sample for debug
                ensure_dirs()
                dump = BASE / "reports" / f"debug_html_{self.username}.html"
                dump.write_text(html[:50000], encoding="utf-8", errors="ignore")
                console.print(f"[dim]HTML dump: {dump}[/dim]")
                return {}

            self.data = self._via_html_json(html)
            if not self._has_useful(self.data):
                self.data = self._via_og(html)

            if self._has_useful(self.data):
                self._finish_ok(self.data.get("source", "html"))
                return self.data

            console.print("[red][✗] الصفحة ترجعات بلا بيانات مفيدة[/red]")
            console.print(f"[dim]title sample: {html[html.find('<title>'):html.find('<title>')+80] if '<title>' in html else 'n/a'}[/dim]")
            return {}
        except Exception as e:
            console.print(f"[red][✗] Recon failed: {e}[/red]")
            return {}

    def _has_useful(self, d: dict) -> bool:
        if not d:
            return False
        if d.get("followers") or d.get("biography") or d.get("full_name") or d.get("userid"):
            return True
        if d.get("profile_pic"):
            return True
        return False

    def _finish_ok(self, source: str):
        self.data["source"] = source
        self.data.setdefault("keywords", self._keywords(
            (self.data.get("biography") or "") + " " + (self.data.get("full_name") or "")
        ))
        console.print(f"[green][✓] Recon OK via [bold]{source}[/bold][/green]")
        # soft enrich hashtags
        try:
            r = self._get(f"https://www.instagram.com/{self.username}/")
            tags = set(re.findall(r"#([A-Za-z0-9_\u0600-\u06FF]{2,})", r.text))
            self.data["page_hashtags"] = sorted(tags)[:30]
        except Exception:
            pass

    def _parse_user(self, u: dict) -> dict:
        bio = u.get("biography") or ""
        pic = u.get("profile_pic_url_hd") or u.get("profile_pic_url") or ""
        return {
            "username": u.get("username", self.username),
            "full_name": u.get("full_name") or "",
            "userid": str(u.get("id") or u.get("pk") or ""),
            "followers": (u.get("edge_followed_by") or {}).get("count")
                or u.get("follower_count")
                or 0,
            "following": (u.get("edge_follow") or {}).get("count")
                or u.get("following_count")
                or 0,
            "posts": (u.get("edge_owner_to_timeline_media") or {}).get("count")
                or u.get("media_count")
                or 0,
            "biography": bio,
            "is_private": bool(u.get("is_private")),
            "is_verified": bool(u.get("is_verified")),
            "is_business": bool(u.get("is_business_account") or u.get("is_business")),
            "category": u.get("category_name") or u.get("business_category_name") or "",
            "external_url": u.get("external_url") or "",
            "profile_pic": pic,
            "emails": re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", bio),
            "phones": re.findall(r"\+?\d{8,15}", bio),
            "keywords": self._keywords(bio + " " + (u.get("full_name") or "")),
            "source": "api",
        }

    def _keywords(self, text: str) -> list:
        words = re.findall(r"[A-Za-z0-9\u0600-\u06FF]{3,}", text or "")
        stop = {
            "the", "and", "for", "with", "from", "instagram", "photos", "videos",
            "see", "followers", "following", "posts", "this", "that",
            "من", "على", "في", "الى", "هذا", "هذه", "كان", "التي",
        }
        return sorted({w for w in words if w.lower() not in stop})[:40]

    def exists(self) -> bool:
        """Best-effort public existence check."""
        d = self.gather()
        return bool(d)

    def download_avatar(self) -> str:
        ensure_dirs()
        url = (self.data or {}).get("profile_pic")
        if not url:
            console.print("[yellow][!] No profile pic URL[/yellow]")
            return ""
        try:
            r = self.session.get(url, timeout=self.timeout, proxies=self.proxies)
            path = BASE / "avatars" / f"{self.username}.jpg"
            path.write_bytes(r.content)
            console.print(f"[green][✓] Avatar saved: {path}[/green]")
            return str(path)
        except Exception as e:
            console.print(f"[red][✗] Avatar failed: {e}[/red]")
            return ""

    def display(self):
        if not self.data:
            console.print("[yellow]لا توجد بيانات للعرض[/yellow]")
            return
        t = Table(title=f"🎯 @{self.data.get('username')}", show_header=True)
        t.add_column("Field", style="cyan")
        t.add_column("Value", style="green")
        # always show core fields even if 0
        core = [
            "username", "full_name", "userid", "followers", "following", "posts",
            "biography", "is_private", "is_verified", "category", "external_url",
            "emails", "phones", "keywords", "source",
        ]
        shown = set()
        for k in core:
            if k not in self.data:
                continue
            v = self.data[k]
            shown.add(k)
            if isinstance(v, list):
                v = ", ".join(map(str, v)) if v else "-"
            if v in ("", None):
                v = "-"
            t.add_row(k.replace("_", " ").title(), str(v))
        for k, v in self.data.items():
            if k in shown or k == "profile_pic":
                continue
            if v in ("", None, [], {}):
                continue
            if isinstance(v, list):
                v = ", ".join(map(str, v))
            t.add_row(k.replace("_", " ").title(), str(v)[:200])
        console.print(t)

    def export(self, path: str = None) -> str:
        ensure_dirs()
        path = path or str(BASE / "reports" / f"recon_{self.username}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        console.print(f"[green][✓] Saved: {path}[/green]")
        return path
