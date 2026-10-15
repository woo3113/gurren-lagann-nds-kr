import sys,glob,re
from PIL import Image,ImageDraw
sys.path.insert(0,'/'+'/'.join(__file__.split('/')[1:-1]))
import render
out=sys.argv[1]; names=sys.argv[2:]
ims=[]
for n in names:
    try:
        im=render.render(open(n,'rb').read())
        # crop trailing black rows
        ims.append((n,im))
    except Exception as e:
        print('FAIL',n,e)
cols=3; cw=256; 
rows=[]
Wd=cols*(cw+4); 
y=0;pos=[]
rh=0;x=0
for n,im in ims:
    w,h=im.size
    if x+w>Wd and x>0: y+=rh+14;x=0;rh=0
    pos.append((n,im,x,y)); x+=w+4; rh=max(rh,h)
sheet=Image.new('RGB',(max(Wd,x),y+rh+14),(60,60,60))
d=ImageDraw.Draw(sheet)
for n,im,x,y in pos:
    sheet.paste(im,(x,y+12)); d.text((x,y),n,fill=(255,255,0))
sheet.save(out)
