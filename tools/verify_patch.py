import sys, os, json, struct
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
orig=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
new=open(os.path.join(OUT,"Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
print("same size:", len(orig)==len(new))

# diff regions
diffs=[]
i=0; n=len(orig)
while i<n:
    if orig[i]!=new[i]:
        j=i
        while j<n and orig[j]!=new[j]: j+=1
        diffs.append((i,j)); i=j
    else: i+=1
print("diff runs:", len(diffs))
import collections
reg=collections.Counter()
for a,b in diffs:
    if a>=0x153680 and b<=0x153680+0x888c0: reg["font"]+=1
    elif 0x4000<=a<0x4000+0x127db8 and b<=0x4000+0x127db8: reg["arm9"]+=1
    elif 0x597be00<=a<0x5c0ec20 and b<=0x5c0ec20: reg["spc"]+=1
    else: reg["OTHER"]+=1
print(reg)
other=[(hex(a),hex(b)) for a,b in diffs if not (0x153680<=a<0x153680+0x888c0 or 0x4000<=a<0x4000+0x127db8 or 0x597be00<=a<0x5c0ec20)]
print("other regions:", other[:20])

# decode patched text
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
inv={}
for ch,c in CM["keepmap"].items(): inv[c]=ch
for item in CM["newchars"]: inv[item["code"]]=item["ch"]
def decode(bs):
    out=[]; i=0
    while i<len(bs):
        b=bs[i]
        if b==0: break
        if b<0x80: out.append(chr(b)); i+=1
        else:
            c=(b<<8)|bs[i+1]; i+=2
            out.append(inv.get(c, f"<{c:04x}>"))
    return "".join(out)
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
print("\n--- ARM9 verify (patched rom) ---")
for e in F["arm9"][:15]:
    off=0x4000+e["off"]
    got=decode(new[off:off+e["len"]+2])
    print(f'  {got!r}   (expected {e["ko"]!r})')
print("\n--- SPC verify ---")
SPC=0x597be00
d=new
cnt=struct.unpack_from("<I",d,SPC+0x34)[0]; hdr=struct.unpack_from("<I",d,SPC+0x38)[0]
idx={}
for i in range(cnt):
    o=SPC+hdr+i*0x18
    nm=d[o:o+16].split(b"\x00")[0].decode("ascii","replace")
    off,size=struct.unpack_from("<II",d,o+16); idx[nm]=(off,size)
for e in F["spc"][:8]:
    foff,_=idx[e["file"]]; off=SPC+foff+e["off"]
    print(f'  {decode(d[off:off+e["len"]+2])!r}   (expected {e["ko"]!r})')
