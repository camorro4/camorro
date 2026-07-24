#!/usr/bin/env python3
import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup

from .config import get_random_headers, USER_AGENTS
from .banner import C, RE, Y, G, R

class InstagramInfoGatherer:
    APP_ID = "936619743392459"

    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.proxy = proxy
        if proxy:
            self.session.proxies = self._format_proxy(proxy)
        # cookies أساسية تساعد على قبول الطلب
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": self.APP_ID,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        })

    def _format_proxy(self, proxy_string):
        if not proxy_string:
            return None
        if "://" in proxy_string:
            return {"http": proxy_string, "https": proxy_string}
        parts = str(proxy_string).split(":")
        if len(parts) == 2:
            url = f"http://{proxy_string}"
            return {"http": url, "https": url}
        if len(parts) == 4:
            ip, port, user, pwd = parts
            url = f"http://{user}:{pwd}@{ip}:{port}"
            return {"http": url, "https": url}
        return None

    def _empty_data(self, username):
        return {
            "username": username,
            "full_name": "",
            "biography": "",
            "followers": 0,
            "following": 0,
            "posts": 0,
            "verified": False,
            "is_business": False,
            "is_private": False,
            "profile_pic_url": "",
            "external_url": "",
            "category": "",
            "user_id": "",
            "extracted_names": [],
            "extracted_dates": [],
            "extracted_keywords": [],
            "source": "none",
        }

    def _parse_count(self, count_str):
        if count_str is None:
            return 0
        if isinstance(count_str, (int, float)):
            return int(count_str)
        s = str(count_str).replace(",", "").strip().upper()
        mult = 1
        if s.endswith("K"):
            mult, s = 1000, s[:-1]
        elif s.endswith("M"):
            mult, s = 1000000, s[:-1]
        elif s.endswith("B"):
            mult, s = 1000000000, s[:-1]
        try:
            return int(float(s) * mult)
        except ValueError:
            return 0

    def extract_profile_data(self, username):
        username = (username or "").strip().lstrip("@")
        print(f"\n{C}[*] Gathering intelligence on @{username}...{RE}")
        data = self._empty_data(username)

        # 1) الطريقة الأهم حالياً
        ok = self._method_web_profile_info(username, data)
        if ok:
            print(f"{G}[+] Profile via web_profile_info{RE}")
        else:
            # 2) HTML meta / shared data
            print(f"{Y}[*] Trying HTML fallback...{RE}")
            ok = self._method_html(username, data)
            if ok:
                print(f"{G}[+] Profile via HTML parse{RE}")
            else:
                # 3) oEmbed (محدود لكنه يعطي full_name أحياناً)
                print(f"{Y}[*] Trying oEmbed fallback...{RE}")
                ok = self._method_oembed(username, data)
                if ok:
                    print(f"{G}[+] Profile via oEmbed (limited){RE}")
                else:
                    print(f"{R}[!] Could not fetch profile data{RE}")
                    print(f"{Y}[!] Instagram may be blocking this IP, or the account is private/invalid{RE}")
                    print(f"{Y}[!] Tip: add residential proxies in data/proxies.txt and retry{RE}")

        data = self._extract_intelligence(data)
        if data.get("full_name") or data.get("followers") or data.get("biography"):
            print(f"{G}[+] Collected for @{username}: "
                  f"{data.get('followers', 0)} followers | "
                  f"{data.get('following', 0)} following | "
                  f"{data.get('posts', 0)} posts{RE}")
        return data

    def _method_web_profile_info(self, username, data):
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "X-IG-App-ID": self.APP_ID,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": f"https://www.instagram.com/{username}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        try:
            # زيارة الصفحة أولاً لأخذ cookies
            try:
                self.session.get(
                    f"https://www.instagram.com/{username}/",
                    headers=get_random_headers(),
                    timeout=15,
                )
                time.sleep(random.uniform(0.5, 1.2))
            except requests.RequestException:
                pass

            resp = self.session.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                print(f"    {Y}[!] web_profile_info HTTP {resp.status_code}{RE}")
                return False

            payload = resp.json()
            user = (payload.get("data") or {}).get("user") or {}
            if not user:
                return False

            data["username"] = user.get("username") or username
            data["full_name"] = user.get("full_name") or ""
            data["biography"] = user.get("biography") or ""
            data["followers"] = int((user.get("edge_followed_by") or {}).get("count") or 0)
            data["following"] = int((user.get("edge_follow") or {}).get("count") or 0)
            data["posts"] = int((user.get("edge_owner_to_timeline_media") or {}).get("count") or 0)
            data["verified"] = bool(user.get("is_verified", False))
            data["is_business"] = bool(user.get("is_business_account", False))
            data["is_private"] = bool(user.get("is_private", False))
            data["profile_pic_url"] = user.get("profile_pic_url_hd") or user.get("profile_pic_url") or ""
            data["external_url"] = user.get("external_url") or ""
            data["category"] = user.get("category_name") or ""
            data["user_id"] = str(user.get("id") or "")
            data["source"] = "web_profile_info"
            return True
        except Exception as e:
            print(f"    {R}[!] web_profile_info error: {e}{RE}")
            return False

    def _method_html(self, username, data):
        try:
            headers = get_random_headers()
            headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            resp = self.session.get(
                f"https://www.instagram.com/{username}/",
                headers=headers,
                timeout=20,
            )
            if resp.status_code != 200 or not resp.text:
                print(f"    {Y}[!] HTML HTTP {getattr(resp, 'status_code', '?')}{RE}")
                return False

            html = resp.text
            found = False

            # shared data / additionalDataLoaded
            patterns = [
                r"window\._sharedData\s*=\s*(\{.+?\});</script>",
                r"window\.__additionalDataLoaded\([^,]+,\s*(\{.+?\})\);</script>",
                r'"user"\s*:\s*(\{.+?"edge_followed_by".+?\})\s*,\s*"status"',
            ]
            for pat in patterns:
                m = re.search(pat, html, re.DOTALL)
                if not m:
                    continue
                try:
                    blob = json.loads(m.group(1))
                    user = None
                    if "entry_data" in blob:
                        pages = blob.get("entry_data", {}).get("ProfilePage") or []
                        if pages:
                            user = ((pages[0] or {}).get("graphql") or {}).get("user")
                    elif "graphql" in blob:
                        user = (blob.get("graphql") or {}).get("user")
                    elif "data" in blob:
                        user = (blob.get("data") or {}).get("user")
                    elif "edge_followed_by" in blob:
                        user = blob

                    if user:
                        data["full_name"] = user.get("full_name") or data["full_name"]
                        data["biography"] = user.get("biography") or data["biography"]
                        data["followers"] = int((user.get("edge_followed_by") or {}).get("count") or data["followers"] or 0)
                        data["following"] = int((user.get("edge_follow") or {}).get("count") or data["following"] or 0)
                        data["posts"] = int((user.get("edge_owner_to_timeline_media") or {}).get("count") or data["posts"] or 0)
                        data["verified"] = bool(user.get("is_verified", data["verified"]))
                        data["is_business"] = bool(user.get("is_business_account", data["is_business"]))
                        data["is_private"] = bool(user.get("is_private", data["is_private"]))
                        data["external_url"] = user.get("external_url") or data["external_url"]
                        data["user_id"] = str(user.get("id") or data.get("user_id") or "")
                        data["source"] = "html_json"
                        found = True
                        break
                except Exception:
                    continue

            # meta tags fallback
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all("meta"):
                prop = (tag.get("property") or tag.get("name") or "").lower()
                content = tag.get("content") or ""
                if not content:
                    continue
                if prop == "og:title" and not data.get("full_name"):
                    # "Name (@user) • Instagram photos..."
                    name = content.split("(@")[0].strip()
                    name = re.sub(r"\s*[•|].*$", "", name).strip()
                    if name and name.lower() != "instagram":
                        data["full_name"] = name
                        found = True
                elif prop in ("og:description", "description"):
                    # "1,234 Followers, 56 Following, 78 Posts - Bio"
                    fm = re.search(r"([\d,.]+[KMB]?)\s*Followers", content, re.I)
                    gm = re.search(r"([\d,.]+[KMB]?)\s*Following", content, re.I)
                    pm = re.search(r"([\d,.]+[KMB]?)\s*Posts", content, re.I)
                    if fm:
                        data["followers"] = self._parse_count(fm.group(1))
                        found = True
                    if gm:
                        data["following"] = self._parse_count(gm.group(1))
                        found = True
                    if pm:
                        data["posts"] = self._parse_count(pm.group(1))
                        found = True
                    if " - " in content and not data.get("biography"):
                        bio = content.split(" - ", 1)[-1].strip()
                        # تنظيف نهاية الوصف
                        bio = re.sub(r"\s*See Instagram photos and videos.*$", "", bio, flags=re.I).strip()
                        if bio:
                            data["biography"] = bio
                            found = True
                elif prop == "og:image" and not data.get("profile_pic_url"):
                    data["profile_pic_url"] = content
                    found = True

            # regex counts if meta failed
            if not data.get("followers"):
                m = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
                if m:
                    data["followers"] = int(m.group(1))
                    found = True
            if not data.get("following"):
                m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
                if m:
                    data["following"] = int(m.group(1))
                    found = True
            if not data.get("posts"):
                m = re.search(r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
                if m:
                    data["posts"] = int(m.group(1))
                    found = True
            if not data.get("full_name"):
                m = re.search(r'"full_name"\s*:\s*"([^"]*)"', html)
                if m:
                    data["full_name"] = m.group(1).encode().decode("unicode_escape") if "\\" in m.group(1) else m.group(1)
                    found = True
            if not data.get("biography"):
                m = re.search(r'"biography"\s*:\s*"((?:\\.|[^"\\])*)"', html)
                if m:
                    try:
                        data["biography"] = bytes(m.group(1), "utf-8").decode("unicode_escape")
                    except Exception:
                        data["biography"] = m.group(1)
                    found = True

            if found and data.get("source") == "none":
                data["source"] = "html_meta"
            return found
        except Exception as e:
            print(f"    {R}[!] HTML error: {e}{RE}")
            return False

    def _method_oembed(self, username, data):
        try:
            url = f"https://www.instagram.com/api/v1/oembed/?url=https://www.instagram.com/{username}/"
            resp = self.session.get(url, headers=get_random_headers(), timeout=15)
            if resp.status_code != 200:
                return False
            j = resp.json()
            title = j.get("title") or j.get("author_name") or ""
            if title:
                data["full_name"] = title
                data["source"] = "oembed"
                return True
            return False
        except Exception:
            return False

    def _extract_intelligence(self, data):
        full_name = data.get("full_name", "") or ""
        if full_name:
            names = full_name.split()
            data["extracted_names"] = [n.lower() for n in names if len(n) > 1]
            data["extracted_names"].append(full_name.lower().replace(" ", ""))
            data["extracted_names"].append(full_name.lower().replace(" ", "_"))

        bio = data.get("biography", "") or ""
        if bio:
            data["extracted_dates"].extend(re.findall(r"\b(?:19|20)\d{2}\b", bio))
            for d in re.findall(r"\b(\d{1,2})[/\-.](\d{1,2})\b", bio):
                data["extracted_dates"].extend(list(d))
            data["extracted_keywords"] = [k.replace("#", "") for k in re.findall(r"#[a-zA-Z0-9_]+", bio)]
            data["extracted_keywords"].extend(re.findall(r"@(\w+)", bio))

        username = data.get("username", "") or ""
        if username:
            data["extracted_keywords"].append(re.sub(r"[._\-]", "", username).lower())
            data["extracted_keywords"].extend(
                [w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[a-z]+", username) if len(w) > 1]
            )

        external_url = data.get("external_url", "") or ""
        if external_url:
            domain = re.sub(r"https?://(www\.)?", "", external_url).split("/")[0]
            if domain:
                data["extracted_keywords"].append(domain.split(".")[0])

        data["extracted_names"] = list(set([x for x in data["extracted_names"] if x]))
        data["extracted_dates"] = list(set([x for x in data["extracted_dates"] if x]))
        data["extracted_keywords"] = list(set([x for x in data["extracted_keywords"] if x]))
        return data
