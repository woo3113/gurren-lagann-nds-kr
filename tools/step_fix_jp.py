"""Targeted fix pass: remove leftover Japanese (kana / hanja words / long-vowel mark) in Korean output."""
import sys, os, json, re, time, sqlite3, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
JP=re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')
def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

targets={}
for k in ("arm9","spc"):
    for e in F[k]:
        if JP.search(e["ko"]):
            b=(e["len"]+e.get("pad",0)-1) if k=="arm9" else (e["len"]-1)
            if e["text"] not in targets or b<targets[e["text"]]:
                targets[e["text"]]=b
print("targets:", len(targets))

def get_key():
    p=os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
    con=sqlite3.connect(p); cur=con.cursor()
    return json.loads(cur.execute("select value from credential where integration_id='deepseek' and active=1 order by time_updated desc limit 1").fetchone()[0])["key"]
KEY=get_key()

SYS="""너는 일본어→한국어 게임 번역가다. 게임「천원돌파 그렌라간」.

[고유명사 표기]
シモン=시몬, カミナ=카미나, ヨーコ=요코, ニア=니아, ロシウ=로시우, キタン=키탄, ダヤッカ=다야카, ブータ=부타, ヴィラル=비랄,
ココ爺=코코 할아범, リーロン=리론, キヨウ=쿄, ギミー=기미, ダリー=다리, アディーネ=아디네, ロージェノム=로제놈,
グレン=그렌, ラガン=라간, グレンラガン=그렌라간, アークグレン=아크그렌, ダイグレン=다이그렌, ガンメン=간멘, 獣人=수인,
螺旋力=나선력, アダイ村=아다이 마을, ジーハ村=지하 마을, グレンハウス=그렌하우스,
ギガンチョ=기가초, ギャンザ=갼자, ザウレッグ=자우레그, トビダマ=토비다마, サル=원숭이

[절대 규칙]
1. 출력에 히라가나·가타카나·한자를 절대 남기지 마라. 고유명사도 완전히 한글로 음차한다.
   (나쁜 예: 「갸ンザ」, 「기가ンチョ」, 「웅姿」, 「출番」 → 좋은 예: 「갼자」, 「기가초」, 「위용」, 「등장」)
2. 일본식 한자어(出番, 雄姿, 懲りない 등)를 그대로 쓰지 말고 한국어로 번역한다.
3. 장음 기호 'ー'는 쓰지 마라. 늘임은 '~' 또는 모음 반복(아아, 오오)으로 표현한다.
4. "max"는 출력 전체 바이트 상한(한글 1자=2, 영문/숫자/공백 1자=1). 반드시 지켜라.
5. 줄바꿈(\\n) 개수 유지. %s 등 포맷 지정자 그대로.
6. 출력은 JSON만: {"translations":[{"i":번호,"ko":"..."}, ...]}"""

def call(messages, max_tokens=4000):
    body=json.dumps({"model":"deepseek-chat","messages":messages,"temperature":1.0,
                     "max_tokens":max_tokens,"response_format":{"type":"json_object"}}).encode()
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=body,
        headers={"Content-Type":"application/json","Authorization":"Bearer "+KEY})
    for a in range(5):
        try: return json.load(urllib.request.urlopen(req,timeout=180))["choices"][0]["message"]["content"]
        except Exception: time.sleep(2*(a+1))
    raise RuntimeError("fail")

CACHE=os.path.join(OUT,"strings_ko_fix.json")
cache=json.load(open(CACHE,encoding="utf-8")) if os.path.exists(CACHE) else {}
todo=[t for t in targets if t not in cache]
print("todo:", len(todo))
BATCH=25
batches=[todo[i:i+BATCH] for i in range(0,len(todo),BATCH)]
lock=threading.Lock()
def work(batch):
    arr=[{"i":i,"ja":u,"max":targets[u]} for i,u in enumerate(batch)]
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
    except Exception: pass
with ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(work,batches))
json.dump(cache,open(CACHE,"w",encoding="utf-8"),ensure_ascii=False)
print("fixed:", len(cache))
for t,v in list(cache.items())[:25]:
    print(f"  {t!r} -> {v!r}")
