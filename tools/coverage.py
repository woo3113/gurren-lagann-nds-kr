import sys, os
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from game import is_lead, is_trail, is_jp
ROOT=r"D:\20_게임\_한글패치\그랜라간"
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]

def parse_segment(seg):
    if len(seg)<3: return False
    i=0; jp=0
    while i<len(seg):
        b=seg[i]
        if b<0x80:
            if 0x20<=b<=0x7E or b in (0x09,0x0A,0x0D): i+=1
            else: return False
        elif is_lead(b) and i+1<len(seg) and is_trail(seg[i+1]):
            try:
                ch=seg[i:i+2].decode("shift_jis")
                if is_jp(ch): jp+=1
            except Exception: return False
            i+=2
        else: return False
    return jp>0

nul=[i for i,b in enumerate(ARM9) if b==0x00]
cover=bytearray(len(ARM9))
for a,b in zip(nul,nul[1:]):
    if b-a>1 and parse_segment(ARM9[a+1:b]):
        for k in range(a+1,b): cover[k]=1

# 256-byte windows
out=open(os.path.join(ROOT,"out","arm9_cover.txt"),"w",encoding="utf-8")
regions=[]
cur=None
for p in range(0,len(ARM9),0x100):
    c=sum(cover[p:p+0x100])
    frac=c/0x100
    # print interesting windows
    if frac>0.3:
        out.write(f"0x{p:06x} {frac:.2f}\n")
out.close()
# contiguous regions with frac>0.3
flag=[sum(cover[p:p+0x100])/0x100>0.3 for p in range(0,len(ARM9),0x100)]
start=None
for idx,f in enumerate(flag):
    if f and start is None: start=idx
    if (not f or idx==len(flag)-1) and start is not None:
        regions.append((start*0x100, min((idx+1)*0x100,len(ARM9))))
        start=None
print("regions with coverage>0.3:")
for a,b in regions:
    print(f"   0x{a:06x} .. 0x{b:06x}   ({b-a} bytes)")
