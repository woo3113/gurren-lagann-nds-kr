"""Build Korean glyphs (11x11 1bpp) and assign free Shift-JIS codes."""
import sys, os, json, collections
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from game import iter_runs, iter_spc_text, iter_arm9_strings, sjis_split
from PIL import Image, ImageDraw, ImageFont

ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
FNT=os.path.join(ROOT,"work","extract","ETC.NFP","GL_12FNT.NFT")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
fnt=bytearray(open(FNT,"rb").read())
f=Nft(fnt,0)
cmap=f.build_cmap()

# ---- 1. characters needing glyphs ----
need=set()
for e in F["arm9"]+F["spc"]:
    for ch in e["ko"]:
        if ord(ch)>=0x80: need.add(ch)

def is_cjk_code(c):
    hi=c>>8
    return (0x88<=hi<=0x9F) or (0xE0<=hi<=0xEA)

def valid_sjis(c):
    """True only for a real, decodable Shift-JIS double-byte code."""
    hi=c>>8; lo=c&0xFF
    lead = (0x81<=hi<=0x9F) or (0xE0<=hi<=0xEF)
    trail = (0x40<=lo<=0x7E) or (0x80<=lo<=0xFC)
    return lead and trail

def code_of(ch):
    try:
        b=ch.encode("shift_jis")
    except Exception:
        return None
    c = b[0] if len(b)==1 else (b[0]<<8)|b[1]
    return c if c in cmap else None

newchars=[]      # chars to add (no existing code)
keepmap={}       # char -> existing code
for ch in sorted(need):
    c=code_of(ch)
    if c is not None: keepmap[ch]=c
    else: newchars.append(ch)
print("reuse existing codes:", len(keepmap), " new glyphs needed:", len(newchars))

# ---- 2. recompute used codes (source japanese + korean reused codes) ----
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
used=set(keepmap.values())
for off,tb in iter_runs(ARM9,1):
    for c in sjis_split(tb): used.add(c)
SPC=os.path.join(ROOT,"work","extract","SPC.NFP")
for fn in os.listdir(SPC):
    if not fn.upper().endswith(".SPC"): continue
    buf=open(os.path.join(SPC,fn),"rb").read()
    for off,tb in iter_runs(buf,1):
        for c in sjis_split(tb): used.add(c)
    for off,ln,tb in iter_spc_text(buf):
        for c in sjis_split(tb): used.add(c)
print("used codes:", len(used))

free=[c for c in sorted(cmap) if c not in used and is_cjk_code(c) and valid_sjis(c)]
print("free cjk codes:", len(free))
bad=[c for c in free if not valid_sjis(c)]
assert not bad, bad
# also confirm none of the previously assigned codes were invalid
print("free codes that are invalid sjis:", len(bad))
assert len(free)>=len(newchars), "not enough free codes"

# ---- 3. assign codes (deterministic) ----
code2char={}
for ch,c in zip(newchars, free):
    code2char[ch]=c

# ---- 4. render glyphs ----
FPATH=r"C:\Windows\Fonts\gulim.ttc"
font=ImageFont.truetype(FPATH, 11, index=0)

def render_bits(ch):
    tile=Image.new("L",(16,16),255)
    d=ImageDraw.Draw(tile)
    d.text((0,0), ch, font=font, fill=0)
    px=tile.load()
    return [[1 if px[x,y]<128 else 0 for x in range(11)] for y in range(11)]

def pack(bits):
    buf=bytearray(16)
    for y in range(11):
        for x in range(11):
            if bits[y][x]:
                bit=y*11+x
                buf[bit//8] |= (0x80>>(bit%8))
    return bytes(buf)

glyph_map={}
preview_chars=list(newchars)
for ch in preview_chars:
    code=code2char[ch]
    g=cmap[code]
    glyph_map[ch]={"code":code,"glyph":g,"bits":render_bits(ch)}

# preview sheet
scale=4; cols=40
rows=(len(preview_chars)+cols-1)//cols
img=Image.new("L",(cols*12*scale, rows*13*scale),255)
for i,ch in enumerate(preview_chars):
    b=glyph_map[ch]["bits"]
    cx=(i%cols)*12*scale; cy=(i//cols)*13*scale
    for y in range(11):
        for x in range(11):
            if b[y][x]:
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((cx+x*scale+dx, cy+y*scale+dy),0)
img.save(os.path.join(ROOT,"work","hangul_preview.png"))
print("saved hangul_preview.png", len(preview_chars), "glyphs")

out={"newchars":[{"ch":ch,"code":code2char[ch]} for ch in newchars],
     "keepmap":{ch:c for ch,c in keepmap.items()}}
json.dump(out, open(os.path.join(OUT,"charmap.json"),"w",encoding="utf-8"), ensure_ascii=False)
print("wrote out/charmap.json")
