import sys, os, json, collections
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
f=Nft(bytearray(open(os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT"),"rb").read()),0)
cmap=f.build_cmap()

cnt=collections.Counter()
for e in F["arm9"]+F["spc"]:
    for ch in e["ko"]:
        if ord(ch)>=0x80: cnt[ch]+=1
print("distinct non-ascii chars in korean text:", len(cnt))

hd=[]; sjis_ok=[]; other=[]
for ch,c in cnt.items():
    if 0xAC00<=ord(ch)<=0xD7A3: hd.append((ch,c))
    else:
        try:
            b=ch.encode("shift_jis")
            code = b[0] if len(b)==1 else (b[0]<<8)|b[1]
            if code in cmap: sjis_ok.append((ch,c,hex(code)))
            else: other.append((ch,c,"not-in-cmap",b.hex()))
        except Exception:
            other.append((ch,c,"not-sjis",""))
print("hangul syllables:", len(hd), "total occurrences:", sum(c for _,c in hd))
print("non-hangul reusing existing font codes:", len(sjis_ok))
print("   ", [(ch,c,cd) for ch,c,cd in sjis_ok[:60]])
print("others (need handling):", len(other))
print("   ", other)
