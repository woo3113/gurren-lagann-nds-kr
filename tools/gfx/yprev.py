import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yce
from PIL import Image
W=os.path.expanduser('~/mnt/그랜라간/work/')
def prev(names,out,scale=3,maxfr=6):
    rows=[]
    for n in names:
        for d in ('extract/NFP2D.NFP/','gfxnew_yce/'):
            b=open(W+d+n+'.YCE','rb').read();F=yce.parse(b)
            ims=[yce.render(b,f) for f in F[:maxfr]]; ims=[i for i in ims if i]
            rows.append(ims)
    wmax=max(sum(i.width+4 for i in r) for r in rows)*scale; 
    hs=[max(i.height for i in r)*scale+4 for r in rows]
    S=Image.new('RGB',(wmax,sum(hs)),(70,70,70)); y=0
    for r,h in zip(rows,hs):
        x=0
        for i in r:
            i2=i.resize((i.width*scale,i.height*scale),Image.NEAREST); S.paste(i2,(x,y)); x+=i2.width+4*scale
        y+=h
    S.save(W+'gfxout/'+out); print(S.size)
if __name__=='__main__':
    prev(sys.argv[3:],sys.argv[1],int(sys.argv[2]))
