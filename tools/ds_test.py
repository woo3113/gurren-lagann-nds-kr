import sqlite3, os, json, urllib.request

def get_key(integration="deepseek"):
    p = os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con = sqlite3.connect(p); cur = con.cursor()
    row = cur.execute("select value from credential where integration_id=? and active=1 order by time_updated desc limit 1",(integration,)).fetchone()
    if not row: raise SystemExit("no credential for "+integration)
    v = json.loads(row[0])
    return v.get("key") or v.get("value")

key = get_key()
print("key loaded:", key[:6] + "..." + key[-4:], "len", len(key))

def chat(messages, model="deepseek-chat", temperature=1.0, max_tokens=2000):
    body = json.dumps({"model":model,"messages":messages,"temperature":temperature,"max_tokens":max_tokens}).encode()
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+key})
    r = urllib.request.urlopen(req, timeout=120)
    return json.load(r)

res = chat([{"role":"system","content":"너는 일본어→한국어 게임 번역가다. 'グレンラガン'은 '그렌라간', 'シモン'은 '시몬', 'カミナ'은 '카미나'로 표기한다."},
            {"role":"user","content":"다음 일본어를 자연스러운 한국어 구어체로 번역해라. 번역문만 출력.\nここだ発射！！\n俺は、お前みたいに…"}])
print("---")
print(res["choices"][0]["message"]["content"])
print("usage:", res.get("usage"))
