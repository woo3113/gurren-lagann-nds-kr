import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

def is_lead(b): return 0x81<=b<=0x9F or 0xE0<=b<=0xFC
def is_trail(b): return (0x40<=b<=0x7E) or (0x80<=b<=0xFC)
def parse_seg(seg):
    if len(seg)<3: return None
    i=0; ok=True
    while i<len(seg):
        b=seg[i]
        if b<0x80:
            if 0x20<=b<=0x7E or b in (9,10,13): i+=1
            else: return None
        elif is_lead(b) and i+1<len(seg) and is_trail(seg[i+1]): i+=2
        else: return None
    return True

nul=[i for i,b in enumerate(ARM9) if b==0x00]
cover=bytearray(len(ARM9))
for a,b in zip(nul,nul[1:]):
    if b-a>1 and parse_seg(ARM9[a+1:b]):
        for k in range(a+1,b): cover[k]=1
# high coverage regions (>=0.9 in 256B windows), merged
flag=[sum(cover[p:p+0x100])/0x100>=0.85 for p in range(0,len(ARM9),0x100)]
regions=[]; st=None
for idx,f in enumerate(flag):
    if f and st is None: st=idx
    if (not f or idx==len(flag)-1) and st is not None:
        regions.append((st*0x100,min((idx+1)*0x100,len(ARM9)))); st=None
print("high-coverage text regions:")
for a,b in regions: print(f"   0x{a:06x}-0x{b:06x} ({b-a}B)")
def inside(o):
    return any(a<=o<b for a,b in regions)

outside=[e for e in F["arm9"] if not inside(e["off"])]
print(f"\nARM9 패치 {len(F['arm9'])}개 중 고밀도 텍스트 영역 밖: {len(outside)}")
for e in outside[:40]:
    print(f"   0x{e['off']:06x} len={e['len']} {e['text']!r}")
