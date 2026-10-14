import json, os, sys, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
F=json.load(open(os.path.join(ROOT,"out","final.json"),encoding="utf-8"))
cand=[e for e in F["arm9"] if re.search(r'[A-Za-z0-9_]', e["text"])]
print("ARM9 패치 항목 중 ASCII 영숫자 포함:", len(cand))
for e in cand[:70]:
    print(f"  0x{e['off']:06x} len={e['len']:3d} {e['text']!r} -> {e['ko']!r}")
print()
# region 0x119c00-0x119e00 (filename table area)
print("=== 0x119c00-0x119f00 ARM9 패치 항목 ===")
for e in F["arm9"]:
    if 0x119800 <= e["off"] < 0x11a000:
        print(f"  0x{e['off']:06x} {e['text']!r} -> {e['ko']!r}")
