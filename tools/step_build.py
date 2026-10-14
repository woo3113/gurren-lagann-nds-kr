"""Build the Korean-patched ROM (in-place, same-size patch)."""
import sys, os, json, struct
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image, ImageDraw, ImageFont

ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
ROM=os.path.join(ROOT,"work","Tengen Toppa Gurrell Lagann (Japan).nds")
ROM=os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds")
OUTROM=os.path.join(ROOT,"out","Tengen Toppa Gurren Lagann (Korea).nds")
SPC_NFP_OFF=0x597be00     # SPC.NFP absolute offset in ROM

F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))

rom=bytearray(open(ROM,"rb").read())
print("rom size", hex(len(rom)))

# ---------- 1. font ----------
fnt_off=0x153680   # GL_12FNT.NFT absolute offset in ROM (from NFP FAT)
FNT=os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT")
nf=bytearray(open(FNT,"rb").read())
f=Nft(nf,0)
cmap=f.build_cmap()

font=ImageFont.truetype(r"C:\Windows\Fonts\gulim.ttc", 11, index=0)
def render_bits(ch):
    tile=Image.new("L",(16,16),255); ImageDraw.Draw(tile).text((0,0),ch,font=font,fill=0)
    px=tile.load()
    return [[1 if px[x,y]<128 else 0 for x in range(11)] for y in range(11)]
def pack(bits):
    buf=bytearray(16)
    for y in range(11):
        for x in range(11):
            if bits[y][x]:
                bit=y*11+x; buf[bit//8]|=(0x80>>(bit%8))
    return bytes(buf)

nwritten=0
for item in CM["newchars"]:
    ch=item["ch"]; code=item["code"]; g=cmap[code]
    f.set_glyph(g, pack(render_bits(ch)))
    f.set_hdwc(g,(11,12,1))
    nwritten+=1
print("font glyphs written:", nwritten)

# patch font bytes back into ROM (keep original file length)
assert len(nf)==0x888c0
# we only modified glyph data + hdwc inside the file; write whole file
rom[fnt_off:fnt_off+len(nf)]=nf

# ---------- 2. text encoder ----------
keepmap={ch:c for ch,c in CM["keepmap"].items()}
newmap={item["ch"]:item["code"] for item in CM["newchars"]}
def encode(s):
    out=bytearray()
    for ch in s:
        o=ord(ch)
        if o<0x80:
            out.append(o)
        else:
            c=keepmap.get(ch, newmap.get(ch))
            if c is None: raise ValueError(f"no code for {ch!r}")
            out.append(c>>8); out.append(c&0xff)
    return bytes(out)

# ---------- 3. patch ARM9 ----------
ARM9_OFF=0x4000
n_arm=0
for e in F["arm9"]:
    off=ARM9_OFF+e["off"]
    space=e["len"]+e["pad"]
    data=encode(e["ko"])+b"\x00"
    assert len(data)<=space, (e["text"], e["ko"], len(data), space)
    rom[off:off+len(data)]=data
    rom[off+len(data):off+space]=b"\x00"* (space-len(data))
    n_arm+=1
print("ARM9 strings patched:", n_arm)

# ---------- 4. patch SPC ----------
# build NFP index for SPC.NFP
def nfp_index(base):
    d=rom
    cnt=struct.unpack_from("<I", d, base+0x34)[0]
    hdr=struct.unpack_from("<I", d, base+0x38)[0]
    idx={}
    for i in range(cnt):
        o=base+hdr+i*0x18
        nm=d[o:o+16].split(b"\x00")[0].decode("ascii","replace")
        off,size=struct.unpack_from("<II", d, o+16)
        idx[nm]=(off,size)
    return idx
spc_idx=nfp_index(SPC_NFP_OFF)
n_spc=0
for e in F["spc"]:
    foff,fsize=spc_idx[e["file"]]
    off=SPC_NFP_OFF+foff+e["off"]
    space=e["len"]
    data=encode(e["ko"])+b"\x00"
    assert len(data)<=space, (e["text"], e["ko"], len(data), space)
    rom[off:off+len(data)]=data
    rom[off+len(data):off+space]=b"\x00"*(space-len(data))
    n_spc+=1
print("SPC strings patched:", n_spc)

open(OUTROM,"wb").write(rom)
print("wrote", OUTROM, hex(len(rom)))
