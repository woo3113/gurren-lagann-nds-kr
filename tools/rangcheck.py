import sys, os, json, collections
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from game import iter_runs, iter_spc_text, sjis_split
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]

# codes actually used by the ORIGINAL japanese text
orig_used=collections.Counter()
for off,tb in iter_runs(ARM9,2):
    for c in sjis_split(tb): orig_used[c]+=1
SPC=os.path.join(ROOT,"work","extract","SPC.NFP")
for fn in os.listdir(SPC):
    if not fn.upper().endswith(".SPC"): continue
    buf=open(os.path.join(SPC,fn),"rb").read()
    for off,tb in iter_runs(buf,2):
        for c in sjis_split(tb): orig_used[c]+=1
    for off,ln,tb in iter_spc_text(buf):
        for c in sjis_split(tb): orig_used[c]+=1

CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
mine=[it["code"] for it in CM["newchars"]]
print("원본 텍스트가 실제로 쓰는 2바이트 코드 수:", len([c for c in orig_used if c>0xff]))
print("내가 배정한 코드 수:", len(mine))
# how many of mine does the original text use? (should be 0 -> they were free)
print("내 코드 중 원본 텍스트가 쓰는 것:", sum(1 for c in mine if orig_used.get(c,0)>0))

# range histogram of original text codes vs mine
def bucket(c):
    hi=c>>8
    if hi<0x81: return "ascii"
    if 0x81<=hi<=0x83: return "sym/kana"
    if 0x84<=hi<=0x87: return "row84-87"
    if 0x88<=hi<=0x9f: return "kanjiL1"
    if 0xa0<=hi<=0xdf: return "singlebyte-kana"
    if 0xe0<=hi<=0xea: return "kanjiL2"
    return f"other({hi:02x})"
oh=collections.Counter(bucket(c) for c in orig_used)
mh=collections.Counter(bucket(c) for c in mine)
print("\n원본 텍스트 코드 분포:", dict(oh))
print("내 배정 코드 분포:    ", dict(mh))

# 어떤 SJIS 코드가 '행 끝 0x7F'인지 = 무효 (2차 확인)
def valid(c):
    hi=c>>8; lo=c&0xff
    return ((0x81<=hi<=0x9f) or (0xe0<=hi<=0xef)) and ((0x40<=lo<=0x7e) or (0x80<=lo<=0xfc))
print("\n내 코드 중 무효 SJIS:", sum(1 for c in mine if not valid(c)))
# check the japanese original text never contains any of my assigned codes' BYTES by accident
