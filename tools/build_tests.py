"""Build isolation test ROMs: font-only / arm9-only to find what causes the hang."""
import sys, os, json, struct
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image, ImageDraw, ImageFont

ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
ROM=os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds")
FNT=os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT")
FNT_OFF=0x153680; ARM9_OFF=0x4000; SPC_NFP_OFF=0x597be00
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
orig=open(ROM,"rb").read()

def encode(s):
    km={ch:c for ch,c in CM["keepmap"].items()}
    nm={it["ch"]:it["code"] for it in CM["newchars"]}
    out=bytearray()
    for ch in s:
        o=ord(ch)
        if o<0x80: out.append(o)
        else:
            c=km.get(ch, nm.get(ch))
            if c is None: raise ValueError(ch)
            out.append(c>>8); out.append(c&0xff)
    return bytes(out)

def font_patch(rom):
    nf=bytearray(open(FNT,"rb").read())
    f=Nft(nf,0); cmap=f.build_cmap()
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
    rom[FNT_OFF:FNT_OFF+len(nf)]=nf
    return rom

def arm9_patch(rom):
    for e in F["arm9"]:
        off=ARM9_OFF+e["off"]; space=e["len"]+e["pad"]
        d=encode(e["ko"])+b"\x00"
        rom[off:off+len(d)]=d; rom[off+len(d):off+space]=b"\x00"*(space-len(d))
    return rom

def spc_patch(rom):
    cnt=struct.unpack_from("<I",rom,SPC_NFP_OFF+0x34)[0]
    hdr=struct.unpack_from("<I",rom,SPC_NFP_OFF+0x38)[0]
    idx={}
    for i in range(cnt):
        o=SPC_NFP_OFF+hdr+i*0x18
        nm=rom[o:o+16].split(b"\x00")[0].decode("ascii","replace")
        off,size=struct.unpack_from("<II",rom,o+16); idx[nm]=(off,size)
    for e in F["spc"]:
        foff,_=idx[e["file"]]; off=SPC_NFP_OFF+foff+e["off"]; space=e["len"]
        d=encode(e["ko"])+b"\x00"
        rom[off:off+len(d)]=d; rom[off+len(d):off+space]=b"\x00"*(space-len(d))
    return rom

for name, fn in (("test_font", font_patch), ("test_arm9", arm9_patch), ("test_spc", spc_patch)):
    r=bytearray(orig)
    fn(r)
    open(os.path.join(OUT,name+".nds"),"wb").write(r)
    print("wrote", name+".nds")
