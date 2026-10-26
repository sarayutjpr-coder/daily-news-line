import os, re, sys, urllib.request, urllib.error, json
from pathlib import Path

# LINE Notify was discontinued in March 2025, so this uses the LINE Messaging API push endpoint.
TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
TO = os.environ.get("LINE_TO", "").strip()
if not TOKEN or not TO:
    print("LINE secrets not set (LINE_CHANNEL_ACCESS_TOKEN / LINE_TO) - skipping LINE notification")
    sys.exit(0)

files = sorted(Path("briefings").glob("*.md"))
content = files[-1].read_text(encoding="utf-8")
date = re.search(r'\d{4}-\d{2}-\d{2}', str(files[-1])).group()

SECTION_ICONS = {"AI & Technology": "🤖", "World & Economy": "🌍", "Thailand": "🇹🇭", "สรุป": "📝"}

def md_to_text(text):
    out = []
    for line in text.strip().split('\n'):
        if line.startswith('# '):
            continue
        if line.startswith('## '):
            title = line[3:].strip()
            if out: out.append('')
            out.append(SECTION_ICONS.get(title, "▪️") + " " + title)
        elif line.startswith('- ') or line.startswith('* '):
            out.append("• " + re.sub(r'\*\*(.+?)\*\*', r'\1', line[2:]))
        elif line.strip():
            out.append(re.sub(r'\*\*(.+?)\*\*', r'\1', line))
    return '\n'.join(out)

# A LINE text message holds at most 5000 characters and a push request at most 5 messages.
MAX_LEN = 4900
def split_chunks(text):
    chunks, cur = [], ""
    for para in text.split('\n'):
        while len(para) > MAX_LEN:
            if cur: chunks.append(cur); cur = ""
            chunks.append(para[:MAX_LEN]); para = para[MAX_LEN:]
        if len(cur) + len(para) + 1 > MAX_LEN:
            chunks.append(cur); cur = para
        else:
            cur = cur + '\n' + para if cur else para
    if cur: chunks.append(cur)
    return chunks[:5]

text = "☀️ Daily Briefing " + date + "\nGood morning Khun Yut!\n\n" + md_to_text(content)
messages = [{"type": "text", "text": c} for c in split_chunks(text)]

payload = json.dumps({"to": TO, "messages": messages}).encode()
req = urllib.request.Request("https://api.line.me/v2/bot/message/push", data=payload,
    headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req) as r:
        print("LINE SUCCESS:", r.status, len(messages), "message(s)")
except urllib.error.HTTPError as e:
    print("LINE HTTP Error", e.code, ":", e.read().decode())
    sys.exit(1)
except Exception as e:
    print("LINE Error:", str(e))
    sys.exit(1)
