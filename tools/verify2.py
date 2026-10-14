import sys
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
import struct

p = r"D:\20_게임\_한글패치\그랜라간\work\extract\ETC.NFP\GL_12FNT.NFT"
d = open(p,"rb").read()

# cmap from nft
from nft import Nft
f = Nft(bytearray(d), 0)
cm = f.build_cmap()

text = "ここだ発射"
seq=[]
b=text.encode("shift_jis"); i=0
while i<len(b):
    c=b[i]
    if c<0x80: seq.append(c); i+=1
    else: seq.append(b[i]<<8|b[i+1]); i+=2
glyphs=[cm[c] for c in seq]

def read_glyph(data_off, bpg, idx, gw, gh, msb, rowpad=False):
    rows=[]
    base=data_off+idx*bpg
    for y in range(gh):
        off = base + (y*((gw+7)//8) if rowpad else 0)
        row=[]
        for x in range(gw):
            if rowpad:
                bit=x
                byte=off+bit//8
            else:
                bit=y*gw+x
                byte=base+bit//8
            if byte>=len(d): row.append(0); continue
            v = d[byte] & ((0x80>>(bit%8)) if msb else (1<<(bit%8)))
            row.append(1 if v else 0)
        rows.append(row)
    return rows

cands=[]
for data_off in (0x34,0x38,0x3c,0x40,0x44,0x48):
    for bpg,gw,gh in ((16,11,11),(18,12,12),(24,12,12),(16,8,16),(16,16,8),(12,8,12),(14,7,16),(16,11,12)):
        cands.append((data_off,bpg,gw,gh))

scale=4
CW=len(seq)*max(g for _,_,g,_ in cands)*scale+40
CH=16*scale+20
cols=2; rows=(len(cands)+cols-1)//cols
img=Image.new("RGB",(cols*CW, rows*CH),(255,255,255)); dr=ImageDraw.Draw(img)
for i,(data_off,bpg,gw,gh) in enumerate(cands):
    cx=(i%cols)*CW; cy=(i//cols)*CH
    dr.text((cx+2,cy+2), f"off=0x{data_off:x} bpg={bpg} {gw}x{gh} MSB", fill=(255,0,0))
    for k,g in enumerate(glyphs):
        rowsx=read_glyph(data_off,bpg,g,gw,gh,True)
        for y in range(gh):
            for x in range(gw):
                if rowsx[y][x]:
                    for dy in range(scale):
                        for dx in range(scale):
                            px_x=cx+k*gw*scale+x*scale+dx; px_y=cy+16+y*scale+dy
                            if 0<=px_x<img.width and 0<=px_y<img.height:
                                img.putpixel((px_x,px_y),(0,0,0))
img.save(r"D:\20_게임\_한글패치\그랜라간\work\verify_montage.png")
print("saved", len(cands))
