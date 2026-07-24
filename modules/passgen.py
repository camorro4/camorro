import itertools
import json
from pathlib import Path
from rich.console import Console
from modules.utils import ensure_dirs, BASE, clean_username

console = Console()


class PassGen:
    SUFFIXES = [
        "", "1", "12", "123", "1234", "12345", "123456", "123456789",
        "!", "@", "#", "$", "!!", "@@", ".", "_",
        "2020", "2021", "2022", "2023", "2024", "2025", "2026",
        "00", "01", "07", "10", "11", "99", "007",
        "Insta", "instagram", "ig", "Ig",
    ]
    PREFIXES = ["", "!", "@", "#", "1", "12", "a"]
    LEET = str.maketrans({
        "a": "@", "A": "4", "e": "3", "E": "3",
        "i": "1", "I": "1", "o": "0", "O": "0",
        "s": "$", "S": "5", "t": "7", "T": "7",
    })

    def ask_personal_info(self, username: str = "") -> dict:
        console.print("\n[bold yellow]═══ معلومات الهدف ═══[/bold yellow]")
        console.print("[dim]Enter للتخطي | load:اسم_ملف لتحميل بروفايل محفوظ[/dim]\n")

        # feature: load saved profile
        first = input("  الاسم الشخصي (أو load:filename): ").strip()
        if first.lower().startswith("load:"):
            return self.load_profile(first.split(":", 1)[1].strip() or username)

        info = {"first_name": first}
        keys = [
            ("last_name", "اسم العائلة"),
            ("nickname", "الكنية / username"),
            ("birth_day", "يوم الميلاد (1-31)"),
            ("birth_month", "شهر الميلاد (1-12)"),
            ("birth_year", "سنة الميلاد"),
            ("phone_last4", "آخر 4 أرقام هاتف"),
            ("city", "المدينة"),
            ("school", "مدرسة / جامعة"),
            ("pet", "اسم حيوان أليف"),
            ("partner", "اسم الشريك"),
            ("club", "فريق / نادي"),
            ("extra", "كلمات إضافية (فاصلة)"),
        ]
        for k, label in keys:
            info[k] = input(f"  {label}: ").strip()

        # auto save profile
        if username:
            self.save_profile(username, info)
        return info

    def save_profile(self, username: str, info: dict) -> str:
        ensure_dirs()
        path = BASE / "sessions" / f"profile_{clean_username(username)}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        console.print(f"[green][✓] Profile saved: {path.name}[/green]")
        return str(path)

    def load_profile(self, name: str) -> dict:
        ensure_dirs()
        name = clean_username(name)
        cand = [
            BASE / "sessions" / f"profile_{name}.json",
            BASE / "sessions" / name,
            Path(name),
        ]
        for p in cand:
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                console.print(f"[green][✓] Loaded profile: {p}[/green]")
                return data
        console.print("[red][✗] Profile not found[/red]")
        return {}

    def seed_from_recon(self, info: dict, recon: dict, username: str) -> dict:
        info = dict(info or {})
        info["nickname"] = info.get("nickname") or username
        parts = [
            info.get("extra", ""),
            recon.get("full_name", ""),
            ",".join(recon.get("keywords", [])[:20]),
            ",".join(recon.get("page_hashtags", [])[:15]),
            ",".join(recon.get("emails", [])),
            ",".join(recon.get("phones", [])),
        ]
        info["extra"] = ",".join(x for x in parts if x)
        return info

    def generate(self, info: dict, username: str = "", target: int = 18000) -> list:
        console.print("\n[cyan]🧠 توليد القاموس الذكي...[/cyan]")
        bases = set()

        def add(*vals):
            for v in vals:
                v = (v or "").strip()
                if len(v) < 2:
                    continue
                # strip email domain for base
                if "@" in v and "." in v:
                    v = v.split("@")[0]
                bases.add(v)
                bases.add(v.lower())
                bases.add(v.upper())
                bases.add(v.capitalize())
                bases.add(v.translate(self.LEET))

        first = info.get("first_name", "")
        last = info.get("last_name", "")
        nick = info.get("nickname", "") or username
        add(first, last, nick, username,
            info.get("city"), info.get("pet"), info.get("partner"),
            info.get("school"), info.get("club"))

        if first and last:
            add(f"{first}{last}", f"{first}_{last}", f"{first}.{last}",
                f"{first[0]}{last}", f"{last}{first}", f"{first[0]}.{last}")

        try:
            d = int(info.get("birth_day") or 0)
            m = int(info.get("birth_month") or 0)
            y = int(info.get("birth_year") or 0)
        except ValueError:
            d = m = y = 0

        if y:
            add(str(y), str(y)[2:])
        if d and m:
            add(f"{d:02d}{m:02d}", f"{m:02d}{d:02d}", f"{d}{m}")
        if first and y:
            add(f"{first}{y}", f"{first}{str(y)[2:]}", f"{first.capitalize()}{y}")
        if nick and y:
            add(f"{nick}{y}", f"{nick}{str(y)[2:]}")
        if first and d and m:
            add(f"{first}{d:02d}{m:02d}", f"{first.capitalize()}{d:02d}{m:02d}")
        if d and m and y:
            add(f"{d:02d}{m:02d}{y}", f"{d:02d}{m:02d}{str(y)[2:]}")

        if info.get("phone_last4"):
            add(info["phone_last4"])

        for x in (info.get("extra") or "").split(","):
            add(x.strip())

        add("password", "qwerty", "iloveyou", "instagram", "admin",
            "123456", "12345678", "111111", "camorro", username)

        out = set()
        for b in list(bases):
            for pre, suf in itertools.product(self.PREFIXES, self.SUFFIXES):
                out.add(f"{pre}{b}{suf}")
                if len(out) >= target * 3:
                    break
            if len(out) >= target * 3:
                break

        # prioritize likely human passwords
        def score(p: str) -> tuple:
            special = 1 if any(c in p for c in "!@#$") else 0
            digit = 1 if any(c.isdigit() for c in p) else 0
            return (abs(len(p) - 10), -special, -digit, p)

        result = sorted(out, key=score)[:target]
        console.print(f"[green][✓] Generated {len(result)} passwords[/green]")
        return result

    def save(self, passwords: list, username: str) -> str:
        ensure_dirs()
        path = BASE / "wordlists" / f"wordlist_{clean_username(username)}.txt"
        path.write_text("\n".join(passwords), encoding="utf-8")
        console.print(f"[green][✓] Wordlist: {path}[/green]")
        return str(path)
