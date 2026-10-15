import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yce,pixfont
from PIL import Image,ImageDraw,ImageFont
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def luma(c): return 0.3*c[0]+0.59*c[1]+0.11*c[2]
def analyze(I,rect,pal,margin=4):
    x0,y0,x1,y1=rect
    bgset=set()
    for y in range(y0,y1):
        for x in list(range(x0,x0+margin))+list(range(x1-margin,x1)):
            if I[y][x] is not None: bgset.add(I[y][x])
    import collections
    cnt=collections.Counter(I[y][x] for y in range(y0,y1) for x in range(x0+margin,x1-margin) if I[y][x] is not None and I[y][x] not in bgset)
    return bgset,cnt
def textbbox(I,rect,textset):
    x0,y0,x1,y1=rect; xs=[];ys=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            if I[y][x] in textset: xs.append(x);ys.append(y)
    return (min(xs),min(ys),max(xs),max(ys)) if xs else None
def clear(I,rect,textset):
    x0,y0,x1,y1=rect
    for y in range(y0,y1):
        for x in range(x0,x1):
            if I[y][x] in textset:
                v=None
                for xx in range(x-1,x0-1,-1):
                    if I[y][xx] not in textset: v=I[y][xx];break
                if v is None:
                    for xx in range(x+1,x1):
                        if I[y][xx] not in textset: v=I[y][xx];break
                I[y][x]=v
def mask_pix(text,maxw):
    for adv in (12,11,10,9):
        w,h,px=pixfont.text(text,0,adv,5)
        if w<=maxw: break
    return w,h,px
def mask_ttf(text,height,maxw,bold=True):
    # render at 4x, fit to (<=maxw,height), return binary pixels set
    sz=height*4
    f=ImageFont.truetype(FONT,sz,index=1)
    l,t,r,b=f.getbbox(text); w=r-l;h=b-t
    im=Image.new('L',(w+8,h+8),0); ImageDraw.Draw(im).text((4-l,4-t),text,font=f,fill=255)
    bb=im.getbbox(); im=im.crop(bb)
    tw=min(maxw,max(1,round(im.width/4))); th=height
    im=im.resize((tw,th),Image.LANCZOS)
    return tw,th,im
def stamp_mask(I,w,h,px,cx,cy,fg):
    x0=int(round(cx-w/2)); y0=int(round(cy-h/2))
    for (x,y) in px:
        if 0<=y0+y<len(I) and 0<=x0+x<len(I[0]) and I[y0+y][x0+x] is not None: I[y0+y][x0+x]=fg
def stamp_alpha(I,im,cx,cy,fg,bgfn=None,mid=None,thr=0.5):
    w,h=im.size; x0=int(round(cx-w/2)); y0=int(round(cy-h/2))
    for y in range(h):
        for x in range(w):
            a=im.getpixel((x,y))/255
            Y=y0+y;X=x0+x
            if not(0<=Y<len(I) and 0<=X<len(I[0])) or I[Y][X] is None: continue
            if a>=thr: I[Y][X]=fg
            elif mid is not None and a>=0.3: I[Y][X]=mid

import collections
def rgbmatch(P,idx,rgbs,tol=24):
    c=P[idx]; return any(all(abs(c[i]-r[i])<=tol for i in range(3)) for r in rgbs)
def retext(I,P,rect,is_text,text,fg=None,outline=None,outline_mode=8,period=1,center=None,maxw=None,kind='pix',adv=None,dx=0,dy=0,height=None,keep_old_if_none=True,shadow=None,extra=None,facefill=None):
    """I: idx canvas (modified in place). rect=(x0,y0,x1,y1). is_text(idx,P)->bool.
    fg: idx for strokes (None -> most common text idx); outline: idx for 1px outline (or None).
    returns True if changed"""
    x0,y0,x1,y1=rect
    T={(x,y) for y in range(y0,y1) for x in range(x0,x1) if I[y][x] is not None and is_text(I[y][x],P)}
    if extra:
        eset,eoffs=extra
        for (x,y) in list(T):
            for (ex,ey) in eoffs:
                xx,yy=x+ex,y+ey
                if x0<=xx<x1 and y0<=yy<y1 and I[yy][xx] in eset: T.add((xx,yy))
    if not T: return False
    cnt=collections.Counter(I[y][x] for (x,y) in T)
    xs=[x for x,y in T];ys=[y for x,y in T]
    bc=((min(xs)+max(xs)+1)/2,(min(ys)+max(ys)+1)/2) if center is None else center
    if facefill is not None:
        for y in range(y0,y1):
            for x in range(x0,x1):
                if I[y][x] is not None: I[y][x]=facefill
        T=set()
    # fill
    for (x,y) in sorted(T):
        v=None
        for k in range(1,40):
            for s in (-1,1):
                xx=x+s*k*period
                if x0<=xx<x1 and (xx,y) not in T and I[y][xx] is not None: v=I[y][xx];break
            if v is not None:break
        if v is None:
            for k in range(1,12):
                for s in (-1,1):
                    yy=y+s*k
                    if y0<=yy<y1 and (x,yy) not in T and I[yy][x] is not None: v=I[yy][x];break
                if v is not None:break
        if v is not None: I[y][x]=v
    if fg is None: fg=cnt.most_common(1)[0][0]
    # mask
    mw=maxw or (x1-x0)
    if kind=='pix':
        ww=mw
        for a in ([adv] if adv else (12,11,10,9)):
            w,h,px=pixfont.text(text,0,a,5)
            if w<=mw: break
        M=set(px)
    else:
        w,h,im=mask_ttf(text,height or 11,mw)
        M={(x,y) for y in range(h) for x in range(w) if im.getpixel((x,y))>=128}
    ox=int(round(bc[0]-w/2))+dx; oy=int(round(bc[1]-h/2))+dy
    M={(x+ox,y+oy) for x,y in M}
    if outline is not None:
        O=set()
        for (x,y) in M:
            for ddx in (-1,0,1):
                for ddy in (-1,0,1):
                    if outline_mode==4 and ddx and ddy: continue
                    if (x+ddx,y+ddy) not in M: O.add((x+ddx,y+ddy))
        for (x,y) in O:
            if x0<=x<x1 and y0<=y<y1 and I[y][x] is not None: I[y][x]=outline
    if shadow is not None:
        sidx,offs=shadow if isinstance(shadow,tuple) else (shadow,[(1,1)])
        for (x,y) in M:
            for (ox_,oy_) in offs:
                if (x+ox_,y+oy_) not in M and x0<=x+ox_<x1 and y0<=y+oy_<y1 and I[y+oy_][x+ox_] is not None: I[y+oy_][x+ox_]=sidx
    for (x,y) in M:
        if x0<=x<x1 and y0<=y<y1 and I[y][x] is not None: I[y][x]=fg
    return True
def apply(srcdir,outdir,name,jobs):
    """jobs: list of (frame_index, fn(I,P)->None)"""
    b=open(srcdir+name+'.YCE','rb').read();F=yce.parse(b);nb=b
    for fi,fn in jobs:
        f=F[fi]; x0,y0,W,H,I,S=yce.idxcanvas(nb,f); I0=[r[:] for r in I]; P=yce.pal(nb,f)
        fn(I,P); nb=yce.write(nb,f,I0,I,S)
    open(outdir+name+'.YCE','wb').write(nb)
