"""Final compression pass: re-request very short DS translations for entries still over budget."""
import sys, os, json, re, time, sqlite3, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)
def budget(e,k): return (e["len"]+e.get("pad",0)-1) if k=="arm9" else (e["len"]-1)

targets={}
for k in ("arm9","spc"):
    for e in F[k]:
        if e["how"] in ("fit","tight"):
            b=budget(e,k); t=e["text"]
            if t not in targets or b<targets[t]: targets[t]=b
items=list(targets.items())
print("compression targets:", len(items))

def get_key():
    p=os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con=sqlite3.connect(p); cur=con.cursor()
    return json.loads(cur.execute("select value from credential where integration_id='deepseek' and active=1 order by time_updated desc limit 1").fetchone()[0])["key"]
KEY=get_key()

SYS="""너는 일본어→한국어 게임 번역가다. 게임「천원돌파 그렌라간」.
표기: シモン=시몬, カミナ=카미나, ヨーコ=요코, ニア=니아, ロシウ=로시우, キタン=키탄, ダヤッカ=다야카, ブータ=부타, ヴィラル=비랄,
ココ爺=코코 할아범, グレン=그렌, ラガン=라간, グレンラガン=그렌라간, アークグレン=아크그렌, ダイグレン=다이그렌, ガンメン=간멘, 獣人=수인,
螺旋力=나선력, アダイ村=아다이 마을, ジーハ村=지하 마을, グレンハウス=그렌하우스

[최우선 규칙] "max"는 출력 전체 바이트 상한이다(한글 1자=2, 영문/숫자/공백 1자=1). 절대 초과하지 마라.
- 명사구·장소·아이템 이름이면 핵심 명사(마지막 명사)는 반드시 남기고 앞의 수식어를 덜어낸다.
- 문장이면 핵심 의미만 남긴다.
- 줄바꿈(\\n) 개수는 유지한다. %s 등 포맷 지정자는 그대로.
- 출력은 JSON만: {"translations":[{"i":번호,"ko":"..."}, ...]}"""

def call(messages, max_tokens=4000):
    body=json.dumps({"model":"deepseek-chat","messages":messages,"temperature":0.9,
                     "max_tokens":max_tokens,"response_format":{"type":"json_object"}}).encode()
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    for a in range(5):
        try: return json.load(urllib.request.urlopen(req,timeout=240))["choices"][0]["message"]["content"]
        except Exception: time.sleep(2*(a+1))
    raise RuntimeError("fail")

CACHE=os.path.join(OUT,"strings_ko_ds2.json")
cache=json.load(open(CACHE,encoding="utf-8")) if os.path.exists(CACHE) else {}
todo=[t for t,_ in items if t not in cache]
print("todo:", len(todo))
bmap=dict(items)
BATCH=25
batches=[todo[i:i+BATCH] for i in range(0,len(todo),BATCH)]
lock=threading.Lock(); done=[0]; t0=time.time()

def work(batch):
    arr=[{"i":i,"ja":u,"max":bmap[u]} for i,u in enumerate(batch)]
    try:
        got=call([{"role":"system","content":SYS},
                  {"role":"user","content":"다음 항목을 max 이하로 짧게 번역해 JSON으로 출력.\n"+json.dumps(arr,ensure_ascii=False)}])
        got=re.sub(r'^```(json)?|```$','',got.strip(),flags=re.M).strip()
        d=json.loads(got)
        if isinstance(d,dict): d=d.get("translations") or next((v for v in d.values() if isinstance(v,list)),[])
        res={int(x["i"]):x["ko"] for x in d}
        with lock:
            for i,u in enumerate(batch):
                v=res.get(i)
                if v and v.strip(): cache[u]=v
    except Exception: pass
    with lock:
        done[0]+=len(batch)
        if done[0]%400<BATCH:
            json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
            print(f"  {done[0]}/{len(todo)} ({time.time()-t0:.0f}s)")
with ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(work,batches))
json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
print("compressed:", len(cache))
