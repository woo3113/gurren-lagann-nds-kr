"""Machine-translate all extracted lines to Korean (Google gtx endpoint), cached to disk."""
import sys, os, json, re, time, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\20_게임\_한글패치\그랜라간"
OUT  = os.path.join(ROOT, "out")
S = json.load(open(os.path.join(OUT,"strings.json"), encoding="utf-8"))

SPEC = re.compile(r'%[-+ #0]*[0-9]*(?:\.[0-9]+)?[diouxXeEfgGcs%]')

def protect(s):
    toks = []
    def repl(m):
        toks.append(m.group(0))
        return f"[[{len(toks)-1}]]"
    s2 = SPEC.sub(repl, s)
    return s2, toks

def restore(s, toks):
    for i,t in enumerate(toks):
        s = s.replace(f"[[{i}]]", t)
        s = s.replace(f"[[{i} ]]", t); s = s.replace(f"[[ {i}]]", t)
    return s

# ---- build unique units (lines) ----
units = set()
for e in S["arm9"] + S["spc"]:
    for ln in e["text"].split("\n"):
        units.add(ln)
units = [u for u in units if u.strip()]
units.sort()
print("unique units:", len(units), "chars:", sum(len(u) for u in units))

cache_path = os.path.join(OUT, "lines_ko.json")
cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
print("cached:", len(cache))

UA = {"User-Agent":"Mozilla/5.0"}

def request(batch):
    q = "\n".join(batch)
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=ja&tl=ko&dt=t&q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
            return "".join(seg[0] for seg in d[0])
        except Exception as ex:
            time.sleep(1.5*(attempt+1))
    raise RuntimeError("translate failed")

todo = [u for u in units if u not in cache]
print("todo:", len(todo))

BATCH = 60
i = 0
done = 0
t0 = time.time()
while i < len(todo):
    chunk = todo[i:i+BATCH]
    prot = [protect(c) for c in chunk]
    try:
        res = request([p[0] for p in prot])
        parts = res.split("\n")
        if len(parts) != len(chunk):
            raise RuntimeError(f"line count mismatch {len(parts)} vs {len(chunk)}")
        for src, (p, toks), ko in zip(chunk, prot, parts):
            cache[src] = restore(ko, toks)
    except Exception as ex:
        # fallback: one by one
        for src, (p, toks) in zip(chunk, prot):
            try:
                ko = request([p])
                cache[src] = restore(ko, toks)
            except Exception:
                cache[src] = src
    i += BATCH
    done += len(chunk)
    if done % 600 == 0 or i >= len(todo):
        json.dump(cache, open(cache_path,"w",encoding="utf-8"), ensure_ascii=False)
        print(f"  {done}/{len(todo)}  ({time.time()-t0:.0f}s)")
    time.sleep(0.05)

json.dump(cache, open(cache_path,"w",encoding="utf-8"), ensure_ascii=False)
print("total cached:", len(cache))
