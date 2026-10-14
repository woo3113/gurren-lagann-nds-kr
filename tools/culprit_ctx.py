import sys, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
tgt="ロードファイル選択".encode("shift_jis")
i=0; hits=[]
while True:
    j=rom.find(tgt,i)
    if j<0: break
    hits.append(j); i=j+1
print("전체 롬에서 'ロードファイル選択' 발견 위치:", [hex(h) for h in hits])
for h in hits:
    print(f"--- 0x{h:x} ---")
    for k in range(-32, tgt.__len__()+32, 16):
        a=h+k; ch=rom[a:a+16]
        print(f"{a:08x}  "+" ".join(f"{b:02x}" for b in ch)+"  "+"".join(chr(b) if 32<=b<127 else "." for b in ch))

print()
print("=== ARM9 0x11db80-0x11dbe0 (주변) ===")
A=0x4000
for a in range(0x11db80, 0x11dbf0, 16):
    ch=rom[A+a:A+a+16]
    print(f"{a:08x}  "+" ".join(f"{b:02x}" for b in ch)+"  "+"".join(chr(b) if 32<=b<127 else "." for b in ch))

# other menu-label-like strings nearby
import json
F=json.load(open(os.path.join(ROOT,"out","final.json"),encoding="utf-8"))
print("\n0x11db00-0x11e400 구간 ARM9 항목:")
for e in F["arm9"]:
    if 0x11db00<=e["off"]<0x11e400:
        print(f"  0x{e['off']:06x} len={e['len']:3d} {e['text']!r} -> {e['ko']!r}")
