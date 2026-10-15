import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import render
from PIL import Image,ImageDraw
out=sys.argv[1]; sc=float(sys.argv[2]); names=sys.argv[3:]
ims=[]
for n in names:
    try: im=render.render(open(n,'rb').read()).crop((0,0,256,192))
    except Exception as e: continue
    ims.append((n,im.resize((int(256*sc),int(192*sc)))))
cw=int(256*sc)+4; ch=int(192*sc)+12; cols=max(1,1500//cw)
S=Image.new('RGB',(cols*cw,((len(ims)+cols-1)//cols)*ch),(70,70,70)); d=ImageDraw.Draw(S)
for i,(n,im) in enumerate(ims):
    x=(i%cols)*cw;y=(i//cols)*ch; d.text((x,y),n.replace('.KPC',''),fill=(255,255,0)); S.paste(im,(x,y+11))
S.save(out); print(out,S.size,len(ims))
