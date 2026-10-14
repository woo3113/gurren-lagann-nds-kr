import sys, os, json, collections
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
f=Nft(bytearray(open(os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT"),"rb").read()),0)
cmap=f.build_cmap()
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))

rec=collections.Counter()
zero=[]
for it in CM["newchars"]:
    g=cmap[it["code"]]
    r=f.hdwc_record(g)
    rec[r]+=1
    if r[0]==0 or r==(0,0,0): zero.append((it["ch"], hex(it["code"]), hex(g), r))
print("배정된 글리프의 '원본' HDWC 분포 (상위 15):")
for r,c in rec.most_common(15):
    print(f"   {r}: {c}")
print(f"\n폭이 0인 글리프: {len(zero)}")
for x in zero[:20]: print("   ", x)

# 어떤 코드에 배정했는지: 앞부분(낮은 주소대) 비율
codes=[it["code"] for it in CM["newchars"]]
lo=[c for c in codes if c<0x9900]
print(f"\n배정 코드 {len(codes)}개 중 0x889F~0x98FF(1수준 한자) 사용: {len(lo)}")
print("가장 낮은 10개:", [hex(c) for c in sorted(codes)[:10]])
print("가장 높은 10개:", [hex(c) for c in sorted(codes)[-10:]])
