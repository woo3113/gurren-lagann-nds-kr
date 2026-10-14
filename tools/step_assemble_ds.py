"""Assemble final Korean text from DeepSeek translations, fitting the byte budget."""
import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
DS=json.load(open(os.path.join(OUT,"lines_ko_ds.json"),encoding="utf-8"))
DS2=json.load(open(os.path.join(OUT,"lines_ko_ds2.json"),encoding="utf-8"))
GOS=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))
WS=json.load(open(os.path.join(OUT,"strings_ko_ds.json"),encoding="utf-8"))
WS2=json.load(open(os.path.join(OUT,"strings_ko_ds2.json"),encoding="utf-8"))
FIX=json.load(open(os.path.join(OUT,"strings_ko_fix.json"),encoding="utf-8"))

HIRA=re.compile(r'[\u3041-\u309f]')          # hiragana: never valid in korean output
def sanitize(s):
    s=HIRA.sub("", s)                        # drop leftover hiragana (ね, ぞ, ことかな ...)
    s=s.replace("\u30fc","~")                # long vowel mark -> tilde
    s=s.replace("\u30fb","\u00b7")           # katakana middle dot -> korean middle dot
    s=re.sub(r'~~+','~',s)
    s=re.sub(r'\s{2,}',' ',s)
    s=re.sub(r'\s+([,.!?…、。」』）)])', r'\1', s)
    return s.strip()

def enc_len(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

def compact(s):
    s=s.replace("...","…").replace(" ...","…").replace("... ","…")
    s=re.sub(r'\s*([,.!?…、。」』）)~·:;])\s*', r'\1', s)
    s=re.sub(r'([!?])\1+', r'\1', s)
    s=re.sub(r'\s{2,}',' ',s)
    return s.strip()

PART=["에서는","으로는","에게는","이라고","이라는","이지만","이라도","에서","으로","에게","까지","부터","처럼","보다",
      "라고","이나","라도","에는","에도","로는","이란","이라","를","을","이","가","은","는","도","에","로","와","과","의","만","께","서","나"]
END=[("것 같습니다","듯"),("것 같아","듯"),("것입니다","이다"),("입니다","이다"),("습니다","다"),("합니다","한다"),
     ("됩니다","된다"),("있습니다","있다"),("없습니다","없다"),("하겠습니다","한다"),("주세요","줘"),("해 주세요","해줘")]

def fit_line(s, budget):
    if enc_len(s)<=budget: return s,"ok"
    c=compact(s)
    if enc_len(c)<=budget: return c,"compact"
    for a,b in END:
        if a in c:
            cc=c.replace(a,b)
            if enc_len(cc)<=budget: return cc,"ending"
    toks=c.split(" ")
    for rep in range(3):
        if not toks: break
        w=toks[-1]
        for p in PART:
            if w.endswith(p) and len(w)>len(p):
                cand=" ".join(toks[:-1]+[w[:-len(p)]])
                if enc_len(cand)<=budget: return cand,"particle"
    toks=c.split(" ")
    while len(toks)>1:
        toks=toks[:-1]
        cand=" ".join(toks)
        if enc_len(cand)<=budget: return cand,"dropword"
    cand=""
    for ch in c:
        if enc_len(cand+ch)>budget: break
        cand+=ch
    return cand,"truncate"

stats={}; result=[]
for kind in ("arm9","spc"):
    for e in S[kind]:
        budget=(e["len"]+e.get("pad",0)-1) if kind=="arm9" else (e["len"]-1)
        # whole-string DS translation takes priority when it fits (compressed version first)
        wsv=next((x for x in (FIX.get(e["text"]), WS2.get(e["text"]), WS.get(e["text"])) if x and enc_len(x)<=budget), None)
        if wsv:
            stats["ws"]=stats.get("ws",0)+1
            rec=dict(e); rec["ko"]=sanitize(wsv); rec["how"]="ws"; result.append((kind,rec)); continue
        lines=e["text"].split("\n"); lbs=[max(2,enc_len(l)) for l in lines]; tot=sum(lbs)
        picks=[]; hows=[]
        for ln,lb in zip(lines,lbs):
            if not ln.strip():
                picks.append(ln); hows.append("ok"); continue
            share=max(4,int(budget*lb/tot))
            # never fall back to the japanese source; shorten the korean instead
            cands=[x for x in (FIX.get(ln), DS2.get(ln), DS.get(ln)) if x]
            if not cands:
                picks.append(ln); hows.append("ok"); continue
            best=None
            for c in cands:
                if enc_len(c)<=share: best=c; break
            if best is None:
                best=min(cands, key=enc_len)
            r,h=fit_line(best, share); picks.append(r); hows.append(h)
        ko="\n".join(picks)
        if enc_len(ko)>budget:
            over=enc_len(ko)-budget
            out=list(picks)
            i=len(out)-1
            while over>0 and i>=0:
                r,h=fit_line(out[i], max(2,enc_len(out[i])-over-2))
                over-=enc_len(out[i])-enc_len(r); out[i]=r; i-=1
            ko="\n".join(out)
            how="tight"
        else:
            how="ok" if all(h=="ok" for h in hows) else "fit"
        ko=sanitize(ko)
        stats[how]=stats.get(how,0)+1
        rec=dict(e); rec["ko"]=ko; rec["how"]=how
        result.append((kind,rec))

print("methods:", stats)
arm=[r for k,r in result if k=="arm9"]; spc=[r for k,r in result if k=="spc"]
json.dump({"arm9":arm,"spc":spc}, open(os.path.join(OUT,"final.json"),"w",encoding="utf-8"), ensure_ascii=False)
bad=sum(1 for k,r in result if enc_len(r["ko"])>((r["len"]+r.get("pad",0)-1) if k=="arm9" else r["len"]-1))
print("over budget:", bad, " wrote out/final.json")
