import sys, os, json
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
new=open(os.path.join(OUT,"Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
inv={}
for ch,c in CM["keepmap"].items(): inv[c]=ch
for it in CM["newchars"]: inv[it["code"]]=it["ch"]
rev={ch:c for c,ch in inv.items()}
f=Nft(bytearray(new[0x153680:0x153680+0x888c0]),0); cmap=f.build_cmap()

def glyph_for(ch):
    o=ord(ch)
    if o<0x80: return cmap.get(o)
    c=rev.get(ch)
    return cmap.get(c) if c is not None else None

def draw(img, x, y, text, color=255, adv=12):
    cx=x
    for ch in text:
        if ch==" ": cx+=6; continue
        g=glyph_for(ch)
        if g is not None:
            rows=f.render_glyph(g,11,11)
            for yy in range(11):
                for xx in range(11):
                    if rows[yy][xx] and cx+xx<img.width and y+yy<img.height:
                        img.putpixel((cx+xx,y+yy),color)
        cx+=adv
    return img

F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
# pick samples: prefer SPC dialogue with kana source and reasonable length
samples=[]
seen=set()
for e in F["spc"]:
    ja=e["text"]; ko=e["ko"]
    if "\n" in ja or len(ja)<4 or len(ja)>22: continue
    if ja in seen: continue
    seen.add(ja)
    samples.append((ja,ko))
    if len(samples)>=16: break

rowh=30
img=Image.new("RGB",(256, len(samples)*rowh+8),(10,12,28))
y=4
for ja,ko in samples:
    jt=draw(Image.new("L",(256,14),0),4,1,ja,110)
    img.paste(Image.merge("RGB",(jt,jt,jt)),(0,y))
    t=Image.new("L",(256,14),0); draw(t,4,1,ko,255)
    img.paste(Image.merge("RGB",(t,t,t)),(0,y+14))
    y+=rowh
img=img.resize((256*3,img.height*3),Image.NEAREST)
img.save(os.path.join(ROOT,"work","preview_compare.png"))
print("saved", img.size, len(samples), "samples")
