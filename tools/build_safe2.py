"""Build a guaranteed-working Korean ROM: SPC script translation + Korean font only (ARM9 left japanese)."""
import sys, os, json, re, subprocess
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image, ImageDraw, ImageFont

ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
JAPAN=os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds")
FNT=os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT")
OUTROM=os.path.join(OUT,"Tengen Toppa Gurren Lagann (Korea).nds")
FNT_OFF=0x153680; ARM9_OFF=0x4000; SPC_NFP_OFF=0x597be00

F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

# % fix (real bug that would break the script text at runtime)
VALID=re.compile(r'%[0-9]{0,3}m?[0-9]{0,3}[dscxX%]')
def fixpct(s):
    out=[];i=0
    while i<len(s):
        if s[i]=="%":
            m=VALID.match(s,i)
            if m: out.append(m.group(0)); i=m.end(); continue
            out.append("\uFF05"); i+=1; continue
        out.append(s[i]); i+=1
    return "".join(out)
n=0
for k in ("arm9","spc"):
    for e in F[k]:
        v=fixpct(e["ko"])
        if v!=e["ko"]: e["ko"]=v; n+=1
print("percent fixed:", n)
json.dump(F, open(os.path.join(OUT,"final.json"),"w",encoding="utf-8"), ensure_ascii=False)

subprocess.run([sys.executable, os.path.join(ROOT,"tools","step_hangul.py")], check=True)
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
km={ch:c for ch,c in CM["keepmap"].items()}
nm={it["ch"]:it["code"] for it in CM["newchars"]}
orig=open(JAPAN,"rb").read()
def encode(s):
    o=bytearray()
    for ch in s:
        c=ord(ch)
        if c<0x80: o.append(c)
        else:
            v=km.get(ch,nm.get(ch)); o.append(v>>8); o.append(v&0xFF)
    return bytes(o)

r=bytearray(orig)
nf=bytearray(open(FNT,"rb").read()); f=Nft(nf,0); cmap=f.build_cmap()
font=ImageFont.truetype(r"C:\Windows\Fonts\gulim.ttc",11,index=0)
def rb(ch):
    t=Image.new("L",(16,16),255); ImageDraw.Draw(t).text((0,0),ch,font=font,fill=0)
    px=t.load(); return [[1 if px[x,y]<128 else 0 for x in range(11)] for y in range(11)]
def pack(bits):
    b=bytearray(16)
    for y in range(11):
        for x in range(11):
            if bits[y][x]: b[(y*11+x)//8] |= 0x80>>((y*11+x)%8)
    return bytes(b)
for it in CM["newchars"]:
    g=cmap[it["code"]]; f.set_glyph(g,pack(rb(it["ch"]))); f.set_hdwc(g,(11,12,1))
r[FNT_OFF:FNT_OFF+len(nf)]=nf
print("font glyphs:", len(CM["newchars"]))

# SPC only (ARM9 left untouched)
cnt=int.from_bytes(r[SPC_NFP_OFF+0x34:SPC_NFP_OFF+0x38],"little")
hdr=int.from_bytes(r[SPC_NFP_OFF+0x38:SPC_NFP_OFF+0x3c],"little")
idx={}
for i in range(cnt):
    o=SPC_NFP_OFF+hdr+i*0x18
    nmx=bytes(r[o:o+16]).split(b"\x00")[0].decode("ascii","replace")
    idx[nmx]=int.from_bytes(r[o+16:o+20],"little")
for e in F["spc"]:
    off=SPC_NFP_OFF+idx[e["file"]]+e["off"]; space=e["len"]
    d=encode(e["ko"])+b"\x00"
    r[off:off+len(d)]=d; r[off+len(d):off+space]=b"\x00"*(space-len(d))
print("spc patched:", len(F["spc"]))
open(OUTROM,"wb").write(r)
print("wrote", OUTROM, hex(len(r)))
