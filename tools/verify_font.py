import sys, struct
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image

p = r"D:\20_게임\_한글패치\그랜라간\work\extract\ETC.NFP\GL_12FNT.NFT"
data = bytearray(open(p,"rb").read())

# font1 starts at 0
f = Nft(data, 0)
print("font1: glyph_info", [hex(x) if isinstance(x,int) else x for x in f.glyph_info()])
print("hdwc", f.hdwc_info())
cm = f.build_cmap()
print("cmap entries:", len(cm), "max glyph:", max(cm.values()))
print("glyph_of_code(0x829f)=", f.glyph_of_code(0x829f))
print("hdwc rec for glyph 0xd1:", f.hdwc_record(0xd1))
print("hdwc rec for glyph 0x256:", f.hdwc_record(0x256))

text = "ここだ発射！！"
codes = list(text.encode("shift_jis"))
# split into 2-byte codes
seq = []
i = 0
while i < len(codes):
    c = codes[i]
    if c < 0x80:
        seq.append(c); i += 1
    else:
        seq.append(codes[i]<<8 | codes[i+1]); i += 2
print("codes:", [hex(c) for c in seq], "glyphs:", [f.glyph_of_code(c) for c in seq])

# render
gw, gh = 11, 11
scale = 6
im = Image.new("L", (len(seq)*gw*scale, gh*scale), 255); px = im.load()
for k, code in enumerate(seq):
    g = f.glyph_of_code(code)
    if g is None: continue
    rows = f.render_glyph(g, gw, gh)
    for y in range(gh):
        for x in range(gw):
            if rows[y][x]:
                for dy in range(scale):
                    for dx in range(scale):
                        px[(k*gw+x)*scale+dx, y*scale+dy] = 0
im.save(r"D:\20_게임\_한글패치\그랜라간\work\verify_str.png")
print("saved verify_str.png")
