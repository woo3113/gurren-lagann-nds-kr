import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

for off in (0x11bc70, 0x11bcb0, 0x11b9c0, 0x11b564):
    a=max(0,off-48); b=off+96
    seg=ARM9[a:b]
    print(f"===== 0x{off:06x} =====")
    for i in range(0,len(seg),16):
        ch=seg[i:i+16]
        print(f"{a+i:06x}  "+" ".join(f"{x:02x}" for x in ch)+"  "+"".join(chr(x) if 32<=x<127 else "." for x in ch))
    print()

# find the entry whose off matches, print its translation
for e in F["arm9"]:
    if e["off"] in (0x11bc70,0x11bcb0,0x11b9c0,0x11b564):
        print(f"0x{e['off']:06x} len={e['len']} JA={e['text']!r}\n        KO={e['ko']!r}\n")

# M2_12UTF usage context
i=ARM9.find(b"M2_12UTF.NFT")
print("=== around M2_12UTF.NFT ref 0x%x ===" % (i-64))
seg=ARM9[i-96:i+96]
for k in range(0,len(seg),16):
    ch=seg[k:k+16]
    print(f"{i-96+k:06x}  "+" ".join(f"{x:02x}" for x in ch)+"  "+"".join(chr(x) if 32<=x<127 else "." for x in ch))
