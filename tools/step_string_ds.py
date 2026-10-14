"""Whole-string DeepSeek translation for entries that were shortened (line-splitting lost meaning)."""
import sys, os, json, re, time, sqlite3, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

def budget(e, kind): return (e["len"]+e.get("pad",0)-1) if kind=="arm9" else (e["len"]-1)

# unique (text,budget) that currently needed shortening
targets={}
for kind in ("arm9","spc"):
    for e in F[kind]:
        b=budget(e,kind)
        t=e["text"]
        cur=targets.get(t)
        if cur is None or b<cur[0]:
            targets[t]=[b, e["how"]]
items=[(t,v[0]) for t,v in targets.items() if v[1]!="ok" or "\n" in t]
print("whole-string targets:", len(items))

def get_key():
    p=os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con=sqlite3.connect(p); cur=con.cursor()
    return json.loads(cur.execute("select value from credential where integration_id='deepseek' and active=1 order by time_updated desc limit 1").fetchone()[0])["key"]
KEY=get_key()

SYS="""너는 일본어→한국어 게임 번역가다. 닌텐도 DS 게임 「천원돌파 그렌라간(天元突破グレンラガン)」을 번역한다.
[고유명사 표기 - 반드시 준수]
シモン=시몬, カミナ=카미나, ヨーコ=요코, ニア=니아, ロシウ=로시우, キタン=키탄, ダヤッカ=다야카, ブータ=부타, ヴィラル=비랄,
ココ爺=코코 할아범, リーロン=리론, キヨウ=쿄, キヤル=키얄, ギミー=기미, ダリー=다리, アディーネ=아디네, ロージェノム=로제놈,
グレン=그렌, ラガン=라간, グレンラガン=그렌라간, アークグレン=아크그렌, ダイグレン=다이그렌, 超銀河ダイグレン=초은하 다이그렌,
ガンメン=간멘, 獣人=수인, 大グレン団=대그렌단, アンチスパイラル=안티 스파이럴, 螺旋力=나선력, 螺旋王=나선왕, 四天王=사천왕,
アダイ村=아다이 마을, ジーハ村=지하 마을, グレンハウス=그렌하우스, リットナー村=리트나 마을, カミナシティ=카미나 시티, テッペリン=테페린

[규칙]
1. 자연스러운 한국어 구어체(반말). 메뉴/설명문은 간결한 문어체.
2. 줄바꿈(\\n) 개수와 위치를 반드시 유지한다. 각 줄을 짧게 나눠 총 길이를 줄여라.
3. %s, %d, %03d 등 포맷 지정자는 그대로.
4. "max"는 출력 전체의 바이트 상한이다(한글 1자=2, 영문/숫자/공백 1자=1). 반드시 지켜라.
   의미를 유지하되 조사·수식어를 덜어내어 짧게 만들어라.
5. 출력은 JSON만: {"translations":[{"i":번호,"ko":"번역문"}, ...]}"""

def call(messages, max_tokens=4000):
    body=json.dumps({"model":"deepseek-chat","messages":messages,"temperature":1.0,
                     "max_tokens":max_tokens,"response_format":{"type":"json_object"}}).encode()
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    for a in range(5):
        try: return json.load(urllib.request.urlopen(req,timeout=240))["choices"][0]["message"]["content"]
        except Exception: time.sleep(2*(a+1))
    raise RuntimeError("fail")

CACHE=os.path.join(OUT,"strings_ko_ds.json")
cache=json.load(open(CACHE,encoding="utf-8")) if os.path.exists(CACHE) else {}
todo=[t for t,_ in items if t not in cache]
print("todo:", len(todo))
bmap={t:b for t,b in items}

BATCH=25
batches=[todo[i:i+BATCH] for i in range(0,len(todo),BATCH)]
lock=threading.Lock(); done=[0]; t0=time.time()
def work(batch):
    arr=[{"i":i,"ja":u,"max":bmap[u]} for i,u in enumerate(batch)]
    try:
        got=call([{"role":"system","content":SYS},
                  {"role":"user","content":"다음 항목을 번역해 JSON으로 출력.\n"+json.dumps(arr,ensure_ascii=False)}])
        got=re.sub(r'^```(json)?|```$','',got.strip(),flags=re.M).strip()
        d=json.loads(got)
        if isinstance(d,dict): d=d.get("translations") or next((v for v in d.values() if isinstance(v,list)),[])
        res={int(x["i"]):x["ko"] for x in d}
        with lock:
            for i,u in enumerate(batch):
                v=res.get(i)
                if v and v.strip(): cache[u]=v
    except Exception:
        pass
    with lock:
        done[0]+=len(batch)
        if done[0]%400<BATCH:
            json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
            print(f"  {done[0]}/{len(todo)} ({time.time()-t0:.0f}s)")
with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(work,batches))
json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
print("whole-string translations:", len(cache))
