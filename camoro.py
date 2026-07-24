#!/usr/bin/env python3
"""
camoro - Instagram Profile Information Gathering Tool
Author: [Your Name]
GitHub: [Your GitHub]
"""

import requests
import json
import re
import sys
import os
import textwrap
from datetime import datetime

# ==================== COLORS ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    BG_BLACK = '\033[40m'

def cprint(text, color=Colors.WHITE, bold=False):
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")

# ==================== CAMORO CLASS ====================
class Camoro:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                'Version/14.0 Mobile/15E148 Safari/604.1'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        })
        # Try to load cookies if exists
        self.cookie_file = os.path.expanduser('~/.camoro_cookies')
        self._load_cookies()

    def _load_cookies(self):
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r') as f:
                    cookies = json.load(f)
                    for cookie in cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])
            except:
                pass

    def _save_cookies(self):
        try:
            cookies = []
            for cookie in self.session.cookies:
                cookies.append({'name': cookie.name, 'value': cookie.value})
            with open(self.cookie_file, 'w') as f:
                json.dump(cookies, f)
        except:
            pass

    def fetch_profile(self, username):
        """
        Fetch Instagram profile using multiple fallback methods.
        Returns dict with profile info or None.
        """
        username = username.strip().replace('@', '')

        # Method 1: Public GraphQL JSON endpoint (?__a=1)
        cprint("[*] Trying public JSON endpoint...", Colors.CYAN)
        data = self._try_json_endpoint(username)
        if data:
            return data

        # Method 2: HTML scraping with window._sharedData
        cprint("[*] Trying HTML scraping method...", Colors.CYAN)
        data = self._try_html_scrape(username)
        if data:
            return data

        # Method 3: Alternative JSON endpoint
        cprint("[*] Trying alternative endpoint...", Colors.CYAN)
        data = self._try_alternative_endpoint(username)
        if data:
            return data

        return None

    def _try_json_endpoint(self, username):
        """Try the classic ?__a=1 JSON endpoint."""
        try:
            url = f"https://www.instagram.com/{username}/?__a=1&__d=1"
            resp = self.session.get(url, timeout=15, allow_redirects=True)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    user = data.get('graphql', {}).get('user', {})
                    if user:
                        self._save_cookies()
                        return self._parse_user(user)
                except json.JSONDecodeError:
                    pass
        except requests.RequestException:
            pass
        return None

    def _try_html_scrape(self, username):
        """Scrape HTML for window._sharedData JSON blob."""
        try:
            url = f"https://www.instagram.com/{username}/"
            resp = self.session.get(url, timeout=15, allow_redirects=True)

            if resp.status_code != 200:
                return None

            html = resp.text

            # Pattern 1: window._sharedData
            patterns = [
                r'window\._sharedData\s*=\s*({.*?});\s*</script>',
                r'<script[^>]*>window\._sharedData\s*=\s*({.*?});</script>',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        # Navigate the data structure
                        user = None
                        if 'entry_data' in data:
                            profile = data['entry_data'].get('ProfilePage', [{}])
                            if profile:
                                user = profile[0].get('graphql', {}).get('user')
                        elif 'config' in data:
                            user = data.get('config', {}).get('viewer')
                        elif 'user' in data:
                            user = data.get('user')

                        if user:
                            self._save_cookies()
                            return self._parse_user(user)
                    except (json.JSONDecodeError, KeyError):
                        continue

            # Pattern 2: csrf_token check - detect login wall
            if '"csrf_token"' in html and 'LoginAndSignupPage' in html:
                cprint("[!] Instagram is asking for login. The profile may be private or rate-limited.", Colors.YELLOW)

        except requests.RequestException:
            pass
        return None

    def _try_alternative_endpoint(self, username):
        """Try the i.instagram.com API endpoint."""
        try:
            url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = {
                'X-IG-App-ID': '936619743392459',
                'User-Agent': 'Instagram 219.0.0.12.117 Android',
            }
            resp = self.session.get(url, timeout=15, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                user = data.get('data', {}).get('user', {})
                if user:
                    self._save_cookies()
                    return self._parse_user_alt(user)
        except (requests.RequestException, json.JSONDecodeError):
            pass
        return None

    def _parse_user(self, user):
        """Parse user data from GraphQL format."""
        return {
            'username': user.get('username', 'N/A'),
            'full_name': user.get('full_name', 'N/A'),
            'bio': user.get('biography', ''),
            'followers': user.get('edge_followed_by', {}).get('count', 0),
            'following': user.get('edge_follow', {}).get('count', 0),
            'posts': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
            'is_private': user.get('is_private', False),
            'is_verified': user.get('is_verified', False),
            'is_business': user.get('is_business_account', False),
            'profile_pic_hd': user.get('profile_pic_url_hd', ''),
            'profile_pic': user.get('profile_pic_url', ''),
            'external_url': user.get('external_url', ''),
            'category': user.get('category_name', 'N/A'),
            'id': user.get('id', 'N/A'),
            'highlight_reel_count': user.get('highlight_reel_count', 0),
        }

    def _parse_user_alt(self, user):
        """Parse user data from i.instagram.com API format."""
        return {
            'username': user.get('username', 'N/A'),
            'full_name': user.get('full_name', 'N/A'),
            'bio': user.get('biography', ''),
            'followers': user.get('edge_followed_by', {}).get('count', 0) or user.get('follower_count', 0),
            'following': user.get('edge_follow', {}).get('count', 0) or user.get('following_count', 0),
            'posts': user.get('edge_owner_to_timeline_media', {}).get('count', 0) or user.get('media_count', 0),
            'is_private': user.get('is_private', False),
            'is_verified': user.get('is_verified', False),
            'is_business': user.get('is_business_account', False),
            'profile_pic_hd': user.get('profile_pic_url_hd', user.get('profile_pic_url', '')),
            'profile_pic': user.get('profile_pic_url', ''),
            'external_url': user.get('external_url', ''),
            'category': user.get('category_name', 'N/A'),
            'id': user.get('id', user.get('pk', 'N/A')),
            'highlight_reel_count': user.get('highlight_reel_count', 0),
        }

    def _format_number(self, num):
        """Format large numbers with commas."""
        if num is None:
            return 'N/A'
        return f"{num:,}"

    def display_profile(self, data):
        """Beautiful terminal display of profile information."""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')

        # Banner
        banner = f"""
    {Colors.PURPLE}╔══════════════════════════════════════════════════╗
    ║              {Colors.BOLD}C A M O R O  v1.0{Colors.RESET}{Colors.PURPLE}                  ║
    ║         Instagram Profile Scanner               ║
    ╚══════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)

        # Status badges
        is_private = f"{Colors.RED}PRIVATE 🔒{Colors.RESET}" if data['is_private'] else f"{Colors.GREEN}PUBLIC 🌐{Colors.RESET}"
        is_verified = f"{Colors.BLUE}VERIFIED ✓{Colors.RESET}" if data['is_verified'] else ""
        is_business = f"{Colors.YELLOW}BUSINESS{Colors.RESET}" if data['is_business'] else ""

        status_line = f"  Status: {is_private}"
        if is_verified:
            status_line += f" | {is_verified}"
        if is_business:
            status_line += f" | {is_business}"
        print(status_line)
        print()

        # Profile header
        print(f"  {Colors.BOLD}{Colors.CYAN}╔══ Profile Information ═══════════════════════════╗{Colors.RESET}")

        rows = [
            ("📛 Username", data['username']),
            ("👤 Full Name", data['full_name']),
            ("🆔 User ID", str(data['id'])),
            ("📂 Category", data['category']),
            ("👥 Followers", self._format_number(data['followers'])),
            ("🔗 Following", self._format_number(data['following'])),
            ("📸 Posts", self._format_number(data['posts'])),
            ("🌟 Highlights", str(data['highlight_reel_count'])),
        ]

        for label, value in rows:
            print(f"  {Colors.GREEN}{label}{Colors.RESET}: {Colors.WHITE}{value}{Colors.RESET}")

        # Bio
        if data['bio']:
            print(f"\n  {Colors.BOLD}{Colors.YELLOW}📝 Bio:{Colors.RESET}")
            bio_lines = textwrap.wrap(data['bio'], width=46)
            for line in bio_lines:
                print(f"  {Colors.WHITE}{line}{Colors.RESET}")

        # External URL
        if data['external_url']:
            print(f"\n  {Colors.BOLD}{Colors.CYAN}🔗 External URL:{Colors.RESET}")
            print(f"  {Colors.WHITE}{data['external_url']}{Colors.RESET}")

        # Profile picture
        if data['profile_pic_hd']:
            print(f"\n  {Colors.BOLD}{Colors.PURPLE}🖼️  Profile Picture:{Colors.RESET}")
            print(f"  {Colors.WHITE}{data['profile_pic_hd']}{Colors.RESET}")

        print(f"\n  {Colors.CYAN}╚══════════════════════════════════════════════════╝{Colors.RESET}")
        print()

        # Save option
        cprint(f"  [💾] Data ready for export", Colors.YELLOW)


# ==================== MAIN ====================
def show_banner():
    banner = f"""
{Colors.PURPLE}{Colors.BOLD}
   ▄████████  ▄▄▄▄███▄▄▄▄    ▄▄▄▄███▄▄▄▄   ▄██████▄   ▄████████    ▄████████ 
  ███    ███ ▄██▀▀▀███▀▀▀██▄ ▄██▀▀▀███▀▀▀██▄ ███    ███ ███    ███   ███    ███ 
  ███    █▀  ███   ███   ███ ███   ███   ███ ███    ███ ███    █▀    ███    ███ 
  ███        ███   ███   ███ ███   ███   ███ ███    ███ ███         ▄███▄▄▄▄██▀ 
  ███        ███   ███   ███ ███   ███   ███ ███    ███ ███        ▀▀███▀▀▀▀▀   
  ███    █▄  ███   ███   ███ ███   ███   ███ ███    ███ ███    █▄  ▀███████████ 
  ███    ███ ███   ███   ███ ███   ███   ███ ███    ███ ███    ███   ███    ███ 
  ████████▀   ▀█   ███   █▀   ▀█   ███   █▀   ▀██████▀  ████████▀    ███    ███ 
{Colors.RESET}
{Colors.CYAN}{Colors.BOLD}     Instagram Profile Information Gathering Tool
{Colors.RESET}{Colors.WHITE}                    Version 1.0 | By [YourName]
{Colors.RESET}
    """
    print(banner)

def save_to_file(data, username):
    """Save profile data to JSON file."""
    filename = f"camoro_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    show_banner()

    camoro = Camoro()

    while True:
        try:
            # Get target username
            username = input(f"\n{Colors.GREEN}[?]{Colors.RESET} {Colors.BOLD}Enter target Instagram username{Colors.RESET} {Colors.WHITE}(or 'exit' to quit){Colors.RESET}: ").strip()

            if username.lower() in ['exit', 'quit', 'q', 'خروج']:
                cprint("\n[!] Goodbye! 👋", Colors.PURPLE)
                sys.exit(0)

            if not username:
                cprint("[!] Username cannot be empty!", Colors.RED)
                continue

            # Remove @ if present
            username = username.replace('@', '')

            cprint(f"\n[*] Fetching profile for: @{username}", Colors.CYAN)
            print(f"{Colors.WHITE}{'─'*50}{Colors.RESET}")

            # Fetch profile data
            data = camoro.fetch_profile(username)

            if data is None:
                cprint(f"\n[✗] Failed to fetch profile for @{username}", Colors.RED)
                cprint("[!] Possible reasons:", Colors.YELLOW)
                print("    • Account is private or doesn't exist")
                print("    • Instagram rate-limited the request")
                print("    • Network connectivity issue")
                print("    • Instagram changed their API structure")
                continue

            # Display the profile
            camoro.display_profile(data)

            # Ask to save
            save_choice = input(f"\n{Colors.GREEN}[?]{Colors.RESET} Save results to file? {Colors.WHITE}(y/n){Colors.RESET}: ").strip().lower()
            if save_choice in ['y', 'yes', 'نعم']:
                filename = save_to_file(data, username)
                cprint(f"[✓] Data saved to: {filename}", Colors.GREEN)

            # Ask to scan another
            again = input(f"\n{Colors.GREEN}[?]{Colors.RESET} Scan another profile? {Colors.WHITE}(y/n){Colors.RESET}: ").strip().lower()
            if again not in ['y', 'yes', 'نعم']:
                cprint("\n[!] Goodbye! 👋", Colors.PURPLE)
                sys.exit(0)

        except KeyboardInterrupt:
            cprint("\n\n[!] Interrupted by user. Goodbye! 👋", Colors.YELLOW)
            sys.exit(0)
        except Exception as e:
            cprint(f"\n[✗] Unexpected error: {e}", Colors.RED)
            continue

if __name__ == "__main__":
    main()
