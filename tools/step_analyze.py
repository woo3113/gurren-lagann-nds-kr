import sys, os, json, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
LONG=json.load(open(os.path.join(OUT,"lines_ko.json"),encoding="utf-8"))
SHORT=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))
def enc_len(s): return sum(1 if ord(c)<0x80 else 2 for c in s)
def rebuild(e,t): return "\n".join(t.get(ln,ln) for ln in e["text"].split("\n"))

hist=collections.Counter()
both_over=0; short_worse=0; tot_over=0
examples=[]
for e in S["spc"]:
    bud=e["len"]-1
    ks=enc_len(rebuild(e,SHORT)); kl=enc_len(rebuild(e,LONG))
    ov=min(ks,kl)-bud
    if ov>0:
        tot_over+=1
        cls=collections.Counter()
        hist[min(ov,20)]+=1
        if ks>bud and kl>bud: both_over+=1
        if len(examples)<40 and ov>=6:
            examples.append((ov,bud,e["text"],rebuild(e,SHORT)))
print("total over:", tot_over, " both_long_and_short_over:", both_over)
print("overflow amount histogram (capped 20):")
for k in sorted(hist): print(f"   {k:2d}: {hist[k]}")
print("\nexamples (over>=6):")
for ov,bud,ja,ko in sorted(examples,reverse=True)[:40]:
    print(f" over={ov} bud={bud} JA={ja!r} KO={ko!r}")
