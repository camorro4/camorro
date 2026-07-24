from pathlib import Path
from datetime import datetime
from modules.utils import ensure_dirs, BASE


def export_html(username: str, recon: dict, wordlist_count: int = 0,
                attack: dict = None, out_name: str = None) -> str:
    ensure_dirs()
    attack = attack or {}
    out_name = out_name or f"report_{username}_{datetime.now():%Y%m%d_%H%M%S}.html"
    path = BASE / "reports" / out_name

    rows = ""
    for k, v in (recon or {}).items():
        if v in ("", None, [], {}):
            continue
        if isinstance(v, list):
            v = ", ".join(map(str, v))
        rows += f"<tr><td>{k}</td><td>{v}</td></tr>"

    found = attack.get("found") or "—"
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<title>CAMORRO Report — @{username}</title>
<style>
body{{font-family:Segoe UI,Tahoma,sans-serif;background:#0b1220;color:#e8eefc;margin:0;padding:24px}}
.card{{background:#121a2b;border:1px solid #24344f;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 10px 30px rgba(0,0,0,.35)}}
h1,h2{{margin:0 0 12px}}
.badge{{display:inline-block;background:#1f6feb;padding:4px 10px;border-radius:999px;font-size:12px}}
table{{width:100%;border-collapse:collapse}}
td,th{{border-bottom:1px solid #24344f;padding:10px;text-align:right}}
.ok{{color:#3fb950}} .bad{{color:#f85149}} .muted{{color:#8b9bb4}}
</style>
</head>
<body>
  <div class="card">
    <h1>⚡ CAMORRO Report</h1>
    <div class="badge">@{username}</div>
    <p class="muted">{datetime.now():%Y-%m-%d %H:%M:%S}</p>
  </div>
  <div class="card">
    <h2>🔍 Recon</h2>
    <table>{rows or "<tr><td colspan=2>No data</td></tr>"}</table>
  </div>
  <div class="card">
    <h2>🧠 Wordlist</h2>
    <p>Generated passwords: <b>{wordlist_count}</b></p>
  </div>
  <div class="card">
    <h2>⚡ Attack</h2>
    <p>Tried: <b>{attack.get('tried', 0)}</b></p>
    <p>Rate-limits: <b>{attack.get('rate_hits', 0)}</b></p>
    <p>Result: <b class="{'ok' if attack.get('found') else 'bad'}">{found}</b></p>
  </div>
</body></html>"""
    path.write_text(html, encoding="utf-8")
    return str(path)
