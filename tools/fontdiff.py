import sys, os, struct
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
o=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
n=open(os.path.join(ROOT,"out","Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
FNTO=0x153680; FNT_END=FNTO+0x888c0
# regions inside GL_12FNT.NFT (offsets relative to fnt)
GLYPH=(0x3c, 0x1b2cc)          # font1 glyph bitmaps
HDWC=(0x1b2cc, 0x20458)        # font1 metrics
CMAP=(0x20458, 0x22224)        # font1 cmap blocks
HDR=(0x0,0x3c)
bad=[]
for i in range(FNTO, FNT_END):
    if o[i]!=n[i]:
        r=i-FNTO
        if not (GLYPH[0]<=r<GLYPH[1] or HDWC[0]<=r<HDWC[1]):
            bad.append(r)
print("font diffs outside glyph/metrics regions:", len(bad), [hex(x) for x in bad[:20]])
# count diffs per region
def cnt(a,b): return sum(1 for r in range(a,b) if o[FNTO+r]!=n[FNTO+r])
print("header diffs:", cnt(*HDR), " cmap diffs:", cnt(*CMAP))
print("glyph diffs:", cnt(*GLYPH), " hdwc diffs:", cnt(*HDWC))
# glyph diff alignment: should be multiples of 16 within glyph data
g=[r-GLYPH[0] for r in range(*GLYPH) if o[FNTO+r]!=n[FNTO+r]]
print("glyph diff byte range:", hex(min(g)), hex(max(g)), "mod16 set:", sorted(set(x%16 for x in g))[:20])
h=[r-HDWC[0] for r in range(*HDWC) if o[FNTO+r]!=n[FNTO+r]]
print("hdwc diff byte range:", hex(min(h)), hex(max(h)), "mod3 set:", sorted(set(x%3 for x in h)))
