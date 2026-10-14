import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
L=json.load(open(os.path.join(OUT,"lines_ko.json"),encoding="utf-8"))

def trans(text):
    return "\n".join(L.get(ln, ln) for ln in text.split("\n"))
def enc_len(s):
    return sum(1 if ord(c)<0x80 else 2 for c in s)

fits=0; over=0; tot=0
overs=[]
for e in S["spc"]:
    ko=trans(e["text"]); tot+=1
    if enc_len(ko) <= e["len"]-1: fits+=1
    else:
        over+=1
        overs.append((enc_len(ko)-(e["len"]-1), e["len"], e["text"], ko, "spc", e["file"], e["off"]))
print(f"SPC: fits={fits} over={over} / {tot}")
fits2=0; over2=0
for e in S["arm9"]:
    ko=trans(e["text"]); tot+=1
    if enc_len(ko) <= e["len"]+e["pad"]-1: fits2+=1
    else:
        over2+=1
        overs.append((enc_len(ko)-(e["len"]+e["pad"]-1), e["len"]+e["pad"], e["text"], ko, "arm9", "", e["off"]))
print(f"ARM9: fits={fits2} over={over2} / {len(S['arm9'])}")

overs.sort(reverse=True)
print("\n--- worst overflow examples ---")
for o in overs[:25]:
    print(f"[{o[4]}] over={o[0]} budget={o[1]} JA={o[2]!r} KO={o[3]!r}")
print("\n--- sample translations ---")
for e in S["arm9"][:12]:
    print(f"JA: {e['text']!r}\nKO: {trans(e['text'])!r}\n")
