import sys
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
import struct

p = r"D:\20_게임\_한글패치\그랜라간\work\extract\ETC.NFP\GL_12FNT.NFT"
d = open(p,"rb").read()
DATA=0x3c; BPG=16; N=(0x1b2a0-0x10)//16
print("nglyphs", N)

def read_glyph(idx, gw, gh, msb=True):
    base=DATA+idx*BPG
    rows=[]
    for y in range(gh):
        row=[]
        for x in range(gw):
            bit=y*gw+x
            byte=base+bit//8
            v = (d[byte] & ((0x80>>(bit%8)) if msb else (1<<(bit%8)))) if byte<len(d) else 0
            row.append(1 if v else 0)
        rows.append(row)
    return rows

# empirical ink bbox stats for a range of glyphs, per dims
def stats(gw,gh,lo,hi):
    minx=[99]*gw; maxx=[-1]*gw; miny=[99]*gh; maxy=[-1]*gh
    for idx in range(lo,hi):
        rows=read_glyph(idx,gw,gh)
        for y in range(gh):
            for x in range(gw):
                if rows[y][x]:
                    minx[x]=min(minx[x],y)  # unused
    # simpler: count ink per row and per column
    rowink=[0]*gh; colink=[0]*gw; tot=0
    for idx in range(lo,hi):
        rows=read_glyph(idx,gw,gh)
        for y in range(gh):
            for x in range(gw):
                if rows[y][x]:
                    rowink[y]+=1; colink[x]+=1; tot+=1
    return rowink,colink,tot

for gw,gh in ((11,11),(11,12),(12,11),(12,12),(10,12)):
    r,c,t=stats(gw,gh,3000,4000)
    print(f"{gw}x{gh}: total={t}")
    print("   rowink:", [f"{v*100//max(t,1)}" for v in r])
    print("   colink:", [f"{v*100//max(t,1)}" for v in c])
