"""Assemble final Korean text per entry, compacting to fit the original byte budget."""
import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
LONG=json.load(open(os.path.join(OUT,"lines_ko.json"),encoding="utf-8"))
SHORT=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))

def enc_len(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

def compact(s):
    s=s.replace("...","…").replace(" ...","…").replace("... ","…")
    s=re.sub(r'\s*([,.!?…、。」』）)~·:;])\s*', r'\1', s)
    s=re.sub(r'([!?])\1+', r'\1', s)
    s=re.sub(r'\s{2,}',' ',s)
    s=re.sub(r'^\s+|\s+$','',s)
    return s

PART = ["에서는","으로는","에게는","이라고","이라는","이지만","이라도","에서","으로","에게","까지","부터","처럼","보다","라고","이나","라도","에는","에도","로는","이란","이라","으로써",
        "를","을","이","가","은","는","도","에","로","와","과","의","만","께","서","나"]
END = [("것 같습니다","듯"),("것 같아","듯"),("것입니다","이다"),("입니다","이다"),("습니다","다"),("합니다","한다"),
       ("됩니다","된다"),("있습니다","있다"),("없습니다","없다"),("하겠습니다","한다"),("주세요","줘"),("입니다만","지만")]

def fit_line(s, budget):
    if enc_len(s)<=budget: return s,"ok"
    c=compact(s)
    if enc_len(c)<=budget: return c,"compact"
    # ending shortening
    for a,b in END:
        if a in c:
            cc=c.replace(a,b)
            if enc_len(cc)<=budget: return cc,"ending"
    # remove trailing particle(s) of the last word
    toks=c.split(" ")
    for rep in range(3):
        if not toks: break
        w=toks[-1]
        for p in PART:
            if w.endswith(p) and len(w)>len(p):
                nw=w[:-len(p)]
                cand=" ".join(toks[:-1]+[nw])
                if enc_len(cand)<=budget: return cand,"particle"
    # progressively drop trailing tokens
    toks=c.split(" ")
    while len(toks)>1:
        toks=toks[:-1]
        cand=" ".join(toks)
        if enc_len(cand)<=budget: return cand,"dropword"
    # drop chars
    cand=""
    for ch in c:
        if enc_len(cand+ch)>budget: break
        cand+=ch
    return cand,"truncate"

stats={}; result=[]
for kind in ("arm9","spc"):
    for e in S[kind]:
        budget=(e["len"]+e.get("pad",0)-1) if kind=="arm9" else e["len"]-1
        ja_lines=e["text"].split("\n")
        picks=[]
        for ln in ja_lines:
            a=SHORT.get(ln,ln); b=LONG.get(ln,ln)
            picks.append(a if enc_len(a)<=enc_len(b) else b)
        ko="\n".join(picks)
        how="ok"
        if enc_len(ko)>budget:
            tot=enc_len(ko); over=tot-budget
            shares=[max(2,int((enc_len(l)-over*(enc_len(l)/max(tot,1)))//2*2)) for l in picks]
            out=[]
            for l,sh in zip(picks,shares):
                r,h=fit_line(l,sh); out.append(r)
            ko="\n".join(out)
            if enc_len(ko)>budget:
                # tighten whole again
                extra=enc_len(ko)-budget
                i=len(out)-1
                while extra>0 and i>=0:
                    r,h=fit_line(out[i], max(2,enc_len(out[i])-extra-2))
                    extra-=enc_len(out[i])-enc_len(r); out[i]=r; i-=1
                ko="\n".join(out)
            how="fit"
        stats[how]=stats.get(how,0)+1
        rec=dict(e); rec["ko"]=ko; rec["how"]=how
        result.append((kind,rec))

print("methods:",stats)
arm=[r for k,r in result if k=="arm9"]; spc=[r for k,r in result if k=="spc"]
json.dump({"arm9":arm,"spc":spc}, open(os.path.join(OUT,"final.json"),"w",encoding="utf-8"), ensure_ascii=False)
bad=sum(1 for k,r in result if enc_len(r["ko"])>((r["len"]+r.get("pad",0)-1) if k=="arm9" else r["len"]-1))
print("over budget:", bad)
print("wrote out/final.json")
