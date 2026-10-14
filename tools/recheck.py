import sys, os, json
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from game import iter_runs, iter_spc_text, sjis_split
ROOT=r"D:\20_게임\_한글패치\그랜라간"
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
f=Nft(bytearray(open(os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT"),"rb").read()),0)
cmap=f.build_cmap()
def cjk(c):
    h=c>>8; return (0x88<=h<=0x9F) or (0xE0<=h<=0xEA)
used=set()
for minjp in (1,):
    for off,tb in iter_runs(ARM9,minjp):
        for c in sjis_split(tb): used.add(c)
    SPC=os.path.join(ROOT,"work","extract","SPC.NFP")
    for fn in os.listdir(SPC):
        if not fn.upper().endswith(".SPC"): continue
        buf=open(os.path.join(SPC,fn),"rb").read()
        for off,tb in iter_runs(buf,minjp):
            for c in sjis_split(tb): used.add(c)
        for off,ln,tb in iter_spc_text(buf):
            for c in sjis_split(tb): used.add(c)
free=[c for c in cmap if c not in used and cjk(c)]
print("minjp=1 -> used:", len(used), " free cjk:", len(free))
