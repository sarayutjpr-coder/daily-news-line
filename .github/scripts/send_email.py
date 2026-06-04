import os, re, urllib.request, urllib.error, json
from pathlib import Path

files = sorted(Path("briefings").glob("*.md"))
content = files[-1].read_text(encoding="utf-8")
date = re.search(r'\d{4}-\d{2}-\d{2}', str(files[-1])).group()

def md_to_html(text):
    lines = text.strip().split('\n')
    html = []
    in_ul = False
    for line in lines:
        if line.startswith('## '):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<h3 style="color:#A6E3A1;margin:20px 0 8px">{line[3:]}</h3>')
        elif line.startswith('- ') or line.startswith('* '):
            if not in_ul: html.append('<ul style="color:#e0e0e0;padding-left:20px">'); in_ul = True
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#FFA500">\1</strong>', line[2:])
            html.append(f'<li style="margin:6px 0">{item}</li>')
        elif line.strip() and not line.startswith('#'):
            if in_ul: html.append('</ul>'); in_ul = False
            html.append(f'<p style="color:#e0e0e0">{line}</p>')
    if in_ul: html.append('</ul>')
    return '\n'.join(html)

body = md_to_html(content)
html = f"""<html><body style="margin:0;padding:0;background:#f0f2f5;font-family:Arial,sans-serif">
<div style="max-width:620px;margin:30px auto;background:#1e1e2e;border-radius:16px;padding:25px">
<h1 style="color:#FFA500">Daily Briefing {date}</h1>
<p style="color:#89DCEB">Good morning Khun Yut!</p>
{body}
<p style="color:#585b70;font-size:12px">Sent by Claude Agent</p>
</div></body></html>"""

key = os.environ.get('RESEND_API_KEY', '').strip()
print(f"Key length: {len(key)}, starts with: {key[:8]}")

payload = json.dumps({"from":"onboarding@resend.dev","to":["sarayut.jpr@gmail.com","K_lalana@hotmail.com"],"subject":f"Daily Briefing {date}","html":html}).encode()
req = urllib.request.Request("https://api.resend.com/emails",data=payload,
    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
try:
    with urllib.request.urlopen(req) as r:
        print("SUCCESS:", json.loads(r.read()))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")