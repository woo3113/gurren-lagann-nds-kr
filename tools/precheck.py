import sys, os, re, json
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]

# 1) which font files does the arm9 reference?
for name in (b"GL_12FNT.NFT", b"M2_12UTF.NFT", b".NFT"):
    idx=[]; i=0
    while True:
        j=ARM9.find(name,i)
        if j<0: break
        idx.append(j); i=j+1
    print(f"{name}: {len(idx)} refs at {[hex(x) for x in idx[:6]]}")

# 2) sanity: are the patched arm9 strings inside a dense string pool?
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
def txt_frac(a,b):
    seg=ARM9[a:b]; ok=0
    i=0
    while i<len(seg):
        c=seg[i]
        if 0x20<=c<=0x7e: ok+=1; i+=1
        elif c>=0x81 and i+1<len(seg) and (0x40<=seg[i+1]<=0xfc): ok+=2; i+=2
        else: break
    return ok/max(1,len(seg))

# for each patched arm9 string, examine 64 bytes before and after
bad=[]
for e in F["arm9"]:
    a,b=e["off"], e["off"]+e["len"]+e["pad"]
    lo=max(0,a-64); hi=min(len(ARM9),b+64)
    # neighbours: count null-terminated text tokens in window
    win=ARM9[lo:hi]
    nl=win.count(0)
    bad.append((nl, e["off"], e["len"]))
bad.sort()
print("\npatched arm9 strings with fewest NUL neighbours (suspicious?):")
for nl,off,ln in bad[:12]:
    print(f"  off=0x{off:06x} len={ln} nuls_in_128B={nl}")

# 3) does any patched arm9 range look like ARM code? (check for high byte density typical of code)
