import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
S=json.load(open(os.path.join(OUT,"strings.json"),encoding="utf-8"))
LONG=json.load(open(os.path.join(OUT,"lines_ko.json"),encoding="utf-8"))
SHORT=json.load(open(os.path.join(OUT,"lines_ko_short.json"),encoding="utf-8"))

def enc_len(s): return sum(1 if ord(c)<0x80 else 2 for c in s)
def rebuild(entry, table):
    return "\n".join(table.get(ln,ln) for ln in entry["text"].split("\n"))

# marker leakage check
leak=[k for k,v in SHORT.items() if v.startswith("짧게") or v.startswith("반말")]
print("marker leaks:", len(leak), [SHORT[k][:30] for k in leak[:5]])
empty=[k for k,v in SHORT.items() if not v.strip()]
print("empty outputs:", len(empty))

def fit_stats(table, name):
    fs=0; ov=0
    for e in S["spc"]:
        ko=rebuild(e,table)
        if enc_len(ko)<=e["len"]-1: fs+=1
        else: ov+=1
    fs2=0; ov2=0
    for e in S["arm9"]:
        ko=rebuild(e,table)
        if enc_len(ko)<=e["len"]+e["pad"]-1: fs2+=1
        else: ov2+=1
    print(f"{name}: SPC fits={fs} over={ov} ({fs/(fs+ov)*100:.1f}%) | ARM9 fits={fs2} over={ov2}")

fit_stats(LONG,"plain")
fit_stats(SHORT,"short")

print("\n--- sample short translations ---")
for e in S["arm9"][:15]:
    print(f"JA:{e['text']!r}\nKO:{rebuild(e,SHORT)!r}\n")
