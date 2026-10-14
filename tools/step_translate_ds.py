"""Re-translate all lines with the DeepSeek chat API, primed with a Gurren Lagann glossary."""
import sys, os, json, re, time, sqlite3, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\20_게임\_한글패치\그랜라간"; OUT = os.path.join(ROOT, "out")
S = json.load(open(os.path.join(OUT, "strings.json"), encoding="utf-8"))

# ---------------- API key ----------------
def get_key(integration="deepseek"):
    p = os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con = sqlite3.connect(p); cur = con.cursor()
    row = cur.execute("select value from credential where integration_id=? and active=1 order by time_updated desc limit 1",(integration,)).fetchone()
    return json.loads(row[0])["key"]
KEY = get_key()

# ---------------- glossary / system prompt ----------------
GLOSSARY = """
[인물]
シモン=시몬, カミナ=카미나, ヨーコ=요코, ヨーコ・リットナー=요코 리트나, ニア=니아, ロシウ=로시우, ロシウ・アダイ=로시우 아다이,
キタン=키탄, ダヤッカ=다야카, ブータ=부타, ココ爺=코코 할아범, リーロン=리론, キヨウ=쿄, キヤル=키얄, ギミー=기미, ダリー=다리,
ヴィラル=비랄, アディーネ=아디네, チミルフ=치미르프, ロージェノム=로제놈, ナンティー=난티, ヨマコ=요마코, マッハ=마하

[기체・세력]
グレン=그렌, ラガン=라간, グレンラガン=그렌라간, アークグレン=아크그렌, ダイグレン=다이그렌, 超銀河ダイグレン=초은하 다이그렌,
グレンウィング=그렌윙, 大グレン団=대그렌단, グレン団=그렌단, ガンメン=간멘, 獣人=수인, アンチスパイラル=안티 스파이럴,
螺旋王=나선왕, 四天王=사천왕, テッペリン=테페린, 天元突破=천원돌파

[장소]
アダイ村=아다이 마을, ジーハ村=지하 마을, グレンハウス=그렌하우스, リットナー村=리트나 마을, カミナシティ=카미나 시티, 獣人島=수인섬

[용어]
螺旋力=나선력, 螺旋=나선, ドリル=드릴, コアドリル=코어 드릴, 必殺技=필살기, 技ゲージ=기술 게이지, 装甲=장갑, 装備=장비
"""

SYSTEM = f"""너는 일본어→한국어 게임 번역가다. 닌텐도 DS 게임 「천원돌파 그렌라간(天元突破グレンラガン)」을 번역한다.
아래 고유명사 표기를 반드시 그대로 사용한다. (교육된 용어집)

{GLOSSARY}

[번역 규칙]
1. 자연스러운 한국어 구어체(반말)로 번역한다. 인물의 말투와 상황을 살린다.
2. 메뉴/시스템/설명/튜토리얼 문구는 간결한 문어체로 번역한다.
3. 원문의 줄바꿈(\\n) 개수와 위치를 그대로 유지한다.
4. %s, %d, %03d, %c 같은 포맷 지정자는 절대 변형하거나 삭제하지 않는다.
5. 각 항목의 "max"는 출력 바이트 상한이다. 계산법: 한글/한자 1자=2, 영문/숫자/공백/기호 1자=1.
   반드시 max 이하여야 한다. 초과할 것 같으면 의미를 유지한 채 더 짧게 의역한다.
6. 이미 한국어인 항목, 숫자/기호만 있는 항목은 그대로 둔다.
7. 출력은 반드시 JSON 오브젝트 하나만: {{\"translations\":[{{\"i\":번호,\"ko\":\"번역문\"}}, ...]}}. 설명·인사말·코드블록 금지."""

def make_user(items):
    arr = [{"i": i, "ja": ja, "max": mx} for i, (ja, mx) in enumerate(items)]
    return ("다음 항목들을 번역해 JSON으로 출력해라. 형식: {{\"translations\":[{{\"i\":번호,\"ko\":\"번역문\"}}, ...]}}\n"
            + json.dumps(arr, ensure_ascii=False))

def call_ds(messages, max_tokens=4000, temperature=1.1):
    body = json.dumps({"model":"deepseek-chat","messages":messages,"temperature":temperature,
                       "max_tokens":max_tokens,"response_format":{"type":"json_object"}}).encode()
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    for a in range(5):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            return r["choices"][0]["message"]["content"]
        except Exception as ex:
            time.sleep(2*(a+1))
    raise RuntimeError("deepseek failed")

# ---------------- length targets ----------------
def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)
budget = {}
for kind in ("arm9","spc"):
    for e in S[kind]:
        B = (e["len"]+e["pad"]-1) if kind=="arm9" else (e["len"]-1)
        lines = e["text"].split("\n")
        lbs = [max(2, blen(ln)) for ln in lines]
        tot = sum(lbs)
        for ln, lb in zip(lines, lbs):
            share = max(4, int(B*lb/tot))
            budget[ln] = min(budget.get(ln, 10**9), share)

units = [u for u in budget if u.strip() and re.search(r'[ぁ-んァ-ヶ一-龥ぁ-ん]', u)]
print("unique translatable lines:", len(units))

CACHE = os.path.join(OUT, "lines_ko_ds.json")
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
todo = [u for u in units if u not in cache]
print("todo:", len(todo))

BATCH = 40
batches = [todo[i:i+BATCH] for i in range(0, len(todo), BATCH)]
lock = threading.Lock()
done = [0]; t0 = time.time()

def work(batch):
    items = [(u, budget[u]) for u in batch]
    try:
        content = call_ds([{"role":"system","content":SYSTEM},{"role":"user","content":make_user(items)}])
        content = re.sub(r'^```(json)?|```$', '', content.strip(), flags=re.M).strip()
        data = json.loads(content)
        if isinstance(data, dict):
            data = data.get("translations") or data.get("items") or next((v for v in data.values() if isinstance(v, list)), [])
        res = {int(d["i"]): d["ko"] for d in data}
        with lock:
            for i,u in enumerate(batch):
                cache[u] = res.get(i, cache.get(u, u))
    except Exception as ex:
        with lock:
            for u in batch: cache.setdefault(u, u)
    with lock:
        done[0]+=len(batch)
        if done[0] % 800 < BATCH:
            json.dump(cache, open(CACHE,"w",encoding="utf-8"), ensure_ascii=False)
            print(f"  {done[0]}/{len(todo)} ({time.time()-t0:.0f}s)")

with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(work, batches))

json.dump(cache, open(CACHE,"w",encoding="utf-8"), ensure_ascii=False)
print("translated:", len(cache))
