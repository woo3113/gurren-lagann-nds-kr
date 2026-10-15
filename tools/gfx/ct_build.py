import sys,os,collections;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yce,yedit,pixfont
from ct_ko import ko
from ct_names import CT
SRC=os.path.expanduser('~/mnt/그랜라간/work/extract/NFP2D.NFP/')
OUT=os.path.expanduser('~/mnt/그랜라간/work/gfxnew_yce/'); os.makedirs(OUT,exist_ok=True)
R0,R1,C0,C1=3,14,5,67
def mask_for(text):
    for adv in (12,11,10):
        w,h,px=pixfont.text(text,0,adv,5)
        if w<=62: return w,{(x,y) for x,y in px}
    tw,th,im=yedit.mask_ttf(text,10,62)
    return tw,{(x,y+1) for y in range(th) for x in range(tw) if im.getpixel((x,y))>=140}
def runlen(I,k):
    runs=[]
    for y in range(R0,R1):
        c=0
        for x in range(C0,C1):
            if I[y][x]==k: c+=1
            elif c: runs.append(c);c=0
        if c: runs.append(c)
    return sum(runs)/len(runs) if runs else 99
def detect(I,P):
    cnt=collections.Counter(I[y][x] for y in range(R0,R1) for x in range(C0,C1))
    cands=[k for k,v in cnt.items() if 12<=v<=330 and runlen(I,k)<2.6]
    if not cands: return None
    st=max(cands,key=lambda k:yedit.luma(P[k]))
    if yedit.luma(P[st])<30: return None
    sh=[k for k in cands if k!=st]
    sh=min(sh,key=lambda k:yedit.luma(P[k])) if sh else None
    return st,sh
def run(i):
    n='CT_%03d'%i; b=open(SRC+n+'.YCE','rb').read(); F=yce.parse(b)
    text=ko(i); w,T0=mask_for(text); nb=b; stats=[]
    for fi,f in enumerate(F):
        x0,y0,W,H,I,S=yce.idxcanvas(nb,f)
        if (W,H)!=(72,16) or fi>=(12 if len(F)>=16 else 4): stats.append('s');continue
        P=yce.pal(nb,f); d=detect(I,P)
        if not d: stats.append('-');continue
        st,sh=d
        I0=[r[:] for r in I]
        stroke={(x,y) for y in range(R0,R1) for x in range(C0,C1) if I[y][x]==st}
        old=set(stroke)
        if sh is not None:
            for y in range(R0,R1):
                for x in range(C0,C1):
                    if I[y][x]==sh and ((x-1,y) in stroke or (x-1,y-1) in stroke or (x,y-1) in stroke): old.add((x,y))
        xs=[x for x,y in stroke];ys=[y for x,y in stroke]
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
        yedit.clear(I,(C0,R0,C1,R1),old) if False else None
        # clear: row-nearest non-old fill
        for y in range(R0,R1):
            for x in range(C0,C1):
                if (x,y) in old:
                    v=None
                    for xx in range(x-1,C0-1,-1):
                        if (xx,y) not in old: v=I[y][xx];break
                    if v is None:
                        for xx in range(x+1,C1):
                            if (xx,y) not in old: v=I[y][xx];break
                    I[y][x]=v
        # draw
        ox=int(round(cx-w/2)); oy=int(round(cy-5.5))
        T={(x+ox,y+oy) for x,y in T0}
        for (x,y) in T:
            if C0<=x<C1 and R0<=y<R1: I[y][x]=st
        if sh is not None:
            for (x,y) in T:
                if (x+1,y) not in T and C0<=x+1<C1 and R0<=y<R1: I[y][x+1]=sh
        nb=yce.write(nb,f,I0,I,S); stats.append('o')
    open(OUT+n+'.YCE','wb').write(nb)
    return text,''.join(stats)
if __name__=='__main__':
    ids=[int(a) for a in sys.argv[1:]] or sorted(CT)
    for i in ids: print(i,*run(i))
