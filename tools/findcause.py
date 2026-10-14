import sys, os, json, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

# where is ロードファイル選択 ?
tgt="ロードファイル選択".encode("shift_jis")
i=0
while True:
    j=ARM9.find(tgt,i)
    if j<0: break
    print(f"ロードファイル選択 at arm9 0x{j:06x}")
    i=j+1

# 1) same japanese source -> different korean translations (key/comparison hazard)
bytext=collections.defaultdict(set)
for e in F["arm9"]+F["spc"]:
    bytext[e["text"]].add(e["ko"])
diff=[(t,v) for t,v in bytext.items() if len(v)>1]
print(f"\n같은 원문인데 번역이 다른 경우: {len(diff)}")
for t,v in diff[:25]:
    print(f"   {t!r} -> {list(v)}")

# 2) arm9 strings containing % or path-ish chars
print("\nARM9 문자열 중 '%' 또는 '/' 포함:")
n=0
for e in F["arm9"]:
    if "%" in e["text"] or "/" in e["text"] or "\\" in e["text"]:
        print(f"   0x{e['off']:06x} {e['text']!r} -> {e['ko']!r}")
        n+=1
        if n>60: break
print("count:", n)

# 3) strings in the load-screen neighbourhood (0x114300-0x115a00)
print("\n0x114d00-0x115a00 근처 문자열:")
for e in F["arm9"]:
    if 0x114d00<=e["off"]<0x115a00:
        print(f"   0x{e['off']:06x} {e['text']!r} -> {e['ko']!r}")
