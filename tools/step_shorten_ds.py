"""Second DS pass: shorten over-budget lines, then assemble the final Korean text."""
import sys, os, json, re, time, sqlite3, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
DS=json.load(open(os.path.join(OUT,"lines_ko_ds.json"),encoding="utf-8"))
GO=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))

def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

share={}
for kind in ("arm9","spc"):
    for e in S[kind]:
        B=(e["len"]+e.get("pad",0)-1) if kind=="arm9" else (e["len"]-1)
        lines=e["text"].split("\n"); lbs=[max(2,blen(l)) for l in lines]; tot=sum(lbs)
        for l,lb in zip(lines,lbs):
            share[l]=min(share.get(l,10**9), max(4,int(B*lb/tot)))

shorten=[u for u in DS if u in share and blen(DS[u])>share[u]]
print("lines needing shortening:", len(shorten))

def get_key():
    p=os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con=sqlite3.connect(p); cur=con.cursor()
    return json.loads(cur.execute("select value from credential where integration_id='deepseek' and active=1 order by time_updated desc limit 1").fetchone()[0])["key"]
KEY=get_key()

GLOSS="""シモン=시몬, カミナ=카미나, ヨーコ=요코, ニア=니아, ロシウ=로시우, キタン=키탄, ダヤッカ=다야카, ブータ=부타, ヴィラル=비랄,
グレンラガン=그렌라간, グレン=그렌, ラガン=라간, アークグレン=아크그렌, ダイグレン=다이그렌, 대그렌단, ガンメン=간멘, 獣人=수인,
アンチスパイラル=안티 스파이럴, 螺旋力=나선력, ドリル=드릴, アダイ村=아다이 마을, ジーハ村=지하 마을"""
SYS=("너는 일본어→한국어 게임 번역가다. 게임「천원돌파 그렌라간」. 표기: "+GLOSS+
     "\n주어진 한국어 번역문을 의미와 말투를 유지하면서 더 짧게 다듬어라. "
     "각 항목의 \"max\"는 출력 바이트 상한이다(한글 1자=2, 영문/숫자/공백/기호 1자=1). 반드시 지켜라. "
     "줄바꿈과 포맷 지정자(%s 등)는 그대로 둔다. 출력은 JSON만: {\"translations\":[{\"i\":번호,\"ko\":\"...\"}, ...]}")

def call(messages, max_tokens=4000):
    body=json.dumps({"model":"deepseek-chat","messages":messages,"temperature":1.0,
                     "max_tokens":max_tokens,"response_format":{"type":"json_object"}}).encode()
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    for a in range(5):
        try: return json.load(urllib.request.urlopen(req,timeout=180))["choices"][0]["message"]["content"]
        except Exception: time.sleep(2*(a+1))
    raise RuntimeError("fail")

CACHE=os.path.join(OUT,"lines_ko_ds2.json")
cache=json.load(open(CACHE,encoding="utf-8")) if os.path.exists(CACHE) else {}
todo=[u for u in shorten if u not in cache]
print("todo:", len(todo))

BATCH=30
batches=[todo[i:i+BATCH] for i in range(0,len(todo),BATCH)]
lock=threading.Lock(); done=[0]; t0=time.time()
def work(batch):
    arr=[{"i":i,"ja":u,"ko":DS[u],"max":share[u]} for i,u in enumerate(batch)]
    try:
        got=call([{"role":"system","content":SYS},
                  {"role":"user","content":"다음 항목들의 ko를 max 이하로 더 짧게 다듬어 JSON으로 출력.\n"+json.dumps(arr,ensure_ascii=False)}])
        got=re.sub(r'^```(json)?|```$','',got.strip(),flags=re.M).strip()
        d=json.loads(got)
        if isinstance(d,dict):
            d=d.get("translations") or next((v for v in d.values() if isinstance(v,list)),[])
        res={int(x["i"]):x["ko"] for x in d}
        with lock:
            for i,u in enumerate(batch):
                v=res.get(i)
                if v and len(v.strip()): cache[u]=v
    except Exception:
        pass
    with lock:
        done[0]+=len(batch)
        if done[0]%600<BATCH:
            json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
            print(f"  {done[0]}/{len(todo)} ({time.time()-t0:.0f}s)")
with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(work,batches))
json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
print("shortened:", len(cache))
