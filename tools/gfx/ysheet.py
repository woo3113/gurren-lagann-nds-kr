import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yce
from PIL import Image,ImageDraw
def sheet(out,names,maxfr=4,W=1000,scale=1):
    items=[]
    for n in names:
        try:
            b=open(n,'rb').read(); F=yce.parse(b); ims=[]
            for f in F[:maxfr]:
                im=yce.render(b,f)
                if im: ims.append(im)
            items.append((os.path.basename(n),len(F),ims))
        except Exception as e: items.append((os.path.basename(n)+' ERR '+str(e)[:30],0,[]))
    y=0;x=0;rowh=0;pos=[]
    for nm,nf,ims in items:
        w=sum(i.width+4 for i in ims)*scale+4; h=(max([i.height for i in ims]+[8]))*scale+12
        w=max(w,len(nm)*6+4)
        if x+w>W and x>0: y+=rowh;x=0;rowh=0
        pos.append((nm,nf,ims,x,y)); x+=w+6; rowh=max(rowh,h+2)
    S=Image.new('RGB',(W,y+rowh+4),(70,70,70)); d=ImageDraw.Draw(S)
    for nm,nf,ims,x,y in pos:
        d.text((x,y),'%s(%d)'%(nm,nf),fill=(255,255,0)); xx=x
        for im in ims:
            im2=im.resize((im.width*scale,im.height*scale),Image.NEAREST) if scale>1 else im
            S.paste(im2,(xx,y+11)); xx+=im2.width+4
    S.save(out); print(out,S.size)
if __name__=='__main__':
    sheet(sys.argv[1],sys.argv[2:])
