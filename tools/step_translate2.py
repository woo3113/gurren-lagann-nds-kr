"""Second pass: translate with a 'short/casual' hint to fit the fixed byte budget."""
import sys, os, json, re, time, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))

SPEC=re.compile(r'%[-+ #0]*[0-9]*(?:\.[0-9]+)?[diouxXeEfgGcs%]')
def protect(s):
    toks=[]
    def r(m):
        toks.append(m.group(0)); return f"[[{len(toks)-1}]]"
    return SPEC.sub(r,s), toks
def restore(s,toks):
    for i,t in enumerate(toks):
        s=s.replace(f"[[{i}]]",t).replace(f"[[{i} ]]",t).replace(f"[[ {i}]]",t)
    return s

MARK=re.compile(r'^\s*(짧게|짧고|간단히|반말로|쉽게)\s*(로|하게)?\s*[:：]\s*')
def strip_mark(s):
    m=MARK.match(s)
    return s[m.end():] if m else s

units=set()
for e in S["arm9"]+S["spc"]:
    for ln in e["text"].split("\n"):
        units.add(ln)
units=[u for u in units if u.strip()]
units.sort()
print("units:", len(units))

cache_path=os.path.join(OUT,"lines_ko_short.json")
cache=json.load(open(cache_path,encoding="utf-8")) if os.path.exists(cache_path) else {}
UA={"User-Agent":"Mozilla/5.0"}
def request(batch):
    q="\n".join(batch)
    url="https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=ko&dt=t&q="+urllib.parse.quote(q)
    for a in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30))
            return "".join(seg[0] for seg in d[0])
        except Exception:
            time.sleep(1.5*(a+1))
    raise RuntimeError("fail")

todo=[u for u in units if u not in cache]
print("todo:",len(todo))
BATCH=60; i=0; done=0; t0=time.time()
while i<len(todo):
    chunk=todo[i:i+BATCH]
    prot=[protect(c) for c in chunk]
    srcs=["짧게: "+p[0] for p in prot]
    try:
        res=request(srcs); parts=res.split("\n")
        if len(parts)!=len(chunk): raise RuntimeError("mismatch")
        for orig,(p,toks),ko in zip(chunk,prot,parts):
            ko=restore(ko,toks); ko=strip_mark(ko)
            cache[orig]=ko
    except Exception:
        for orig,(p,toks) in zip(chunk,prot):
            try:
                ko=restore(request(["짧게: "+p]),toks); cache[orig]=strip_mark(ko)
            except Exception:
                cache[orig]=orig
    i+=BATCH; done+=len(chunk)
    if done%1200==0 or i>=len(todo):
        json.dump(cache,open(cache_path,"w",encoding="utf-8"),ensure_ascii=False)
        print(f"  {done}/{len(todo)} ({time.time()-t0:.0f}s)")
    time.sleep(0.05)
json.dump(cache,open(cache_path,"w",encoding="utf-8"),ensure_ascii=False)
print("cached:",len(cache))
