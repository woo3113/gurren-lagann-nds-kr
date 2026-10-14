import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
entries=F["arm9"]+F["spc"]
JP=re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')
left=[e for e in entries if JP.search(e["ko"])]
u=collections.OrderedDict()
for e in left:
    kmap={}
    u.setdefault(e["text"], e["ko"])
print("unique leftover source lines:", len(u))
for ja,ko in u.items():
    print(f"{ja!r}\n    -> {ko!r}")
