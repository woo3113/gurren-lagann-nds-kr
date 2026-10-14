import sys, os, json
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image
ROOT=r"D:\20_게임\_한글패치\그랜라간"
f=Nft(bytearray(open(os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT"),"rb").read()),0)
dio,w,h,bpg,n=f.glyph_info()
print(f"data_off=0x{dio:x} tile={w}x{h} bpg={bpg} nglyph={n}")

def render(g, gw=11, gh=11, scale=8):
    rows=f.render_glyph(g,gw,gh)
    img=Image.new("L",(gw*scale,gh*scale),255)
    for y in range(gh):
        for x in range(gw):
            if rows[y][x]:
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x*scale+dx,y*scale+dy),0)
    return img

# 'あ' code 0x82a0 -> glyph, '漢' etc
tests=[("あ",0x82a0),("漢",0x8abf),("！",0x8149),("。",0x8142)]
imgs=[]
for ch,code in tests:
    g=f.glyph_of_code(code)
    print(ch, hex(code), "glyph", g)
    imgs.append(render(g))
W=sum(i.width for i in imgs)+30; H=max(i.height for i in imgs)
canvas=Image.new("L",(W,H),255); x=0
for i in imgs:
    canvas.paste(i,(x,0)); x+=i.width+10
canvas.save(os.path.join(ROOT,"work","glyph_check.png"))
print("saved")

# HDWC sample for kanji glyph slots
print("\nHDWC records for kanji glyphs 0x256..0x270:")
for g in range(0x256,0x270):
    print(f"  {g:04x}: {f.hdwc_record(g)}")
print("\nunique HDWC records over 3000 glyphs:")
import collections
c=collections.Counter(f.hdwc_record(g) for g in range(3000,6000))
print(c.most_common(10))
