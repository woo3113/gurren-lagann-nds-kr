import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
F=json.load(open(os.path.join(ROOT,"out","final.json"),encoding="utf-8"))
seen=set(); n=0
for e in F["spc"]+F["arm9"]:
    if e["how"] in ("fit","tight") and e["text"] not in seen:
        seen.add(e["text"])
        print("[%s] JA: %r" % (e["how"], e["text"]))
        print("        KO: %r" % e["ko"])
        n+=1
        if n>=30: break
