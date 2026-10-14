import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
DS=json.load(open(os.path.join(OUT,"lines_ko_ds.json"),encoding="utf-8"))
GO=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))
GOP=json.load(open(os.path.join(OUT,"lines_ko.json"),encoding="utf-8"))
def blen(s): return sum(1 if ord(c)<0x80 else 2 for c in s)

# per-line share (min over occurrences)
share={}
for kind in ("arm9","spc"):
    for e in S[kind]:
        B=(e["len"]+e.get("pad",0)-1) if kind=="arm9" else (e["len"]-1)
        lines=e["text"].split("\n"); lbs=[max(2,blen(l)) for l in lines]; tot=sum(lbs)
        for l,lb in zip(lines,lbs):
            share[l]=min(share.get(l,10**9), max(4,int(B*lb/tot)))

def fits(table):
    n=0; over=0
    for k,v in table.items():
        if k in share:
            if blen(v)<=share[k]: n+=1
            else: over+=1
    return n,over
print("DS   per-line fits:", fits(DS))
print("GOOG per-line fits:", fits(GO))
# string-level, DS
def strfit(table):
    n=0; over=0; tot=0
    for kind in ("arm9","spc"):
        for e in S[kind]:
            B=(e["len"]+e.get("pad",0)-1) if kind=="arm9" else (e["len"]-1)
            ko="\n".join(table.get(l,l) for l in e["text"].split("\n"))
            tot+=1
            if blen(ko)<=B: n+=1
            else: over+=1
    return n,over
print("DS string-level fits:", strfit(DS))
