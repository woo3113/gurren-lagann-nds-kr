import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import kedit,pixfont,build_box as B
SRC=B.SRC; OUT=B.OUT
def clear_sel(C,rect,sel,fill):
    x0,y0,x1,y1=rect
    for y in range(y0,y1):
        for x in range(x0,x1):
            if C[y][x] in sel: C[y][x]=fill
def stamp(C,s,cx,cy,color,adv=12):
    w,h,px=pixfont.text(s,0,adv,5); x0=int(cx-w/2); y0=int(cy-h/2)
    for x,y in px: C[y0+y][x0+x]=color
    return w
def com_b02():
    n='COM_B02'; b=open(SRC+n+'.KPC','rb').read();K=kedit.load(b);C=kedit.canvas(K)
    clear_sel(C,(16,52,58,70),{31},17)
    stamp(C,'본체',37,60,31)
    for i,(y0) in enumerate([88,114,140]):
        clear_sel(C,(49,y0,89,y0+16),{31},17)
        stamp(C,'서브%d'%(i+1),67,y0+8+1,31)
    return kedit.rebuild(b,K,C)
def arm_set():
    n='ARM_SET'; b=open(SRC+n+'.KPC','rb').read();K=kedit.load(b);C=kedit.canvas(K)
    sel=set(range(19,32)); rect=(28,0,61,192)
    bs=B.textbands.__wrapped__(C,rect) if False else None
    # bands
    rows=[y for y in range(192) if any(C[y][x] in sel for x in range(28,61))]
    groups=[];s=None;last=None
    for y in rows:
        if s is None or y!=last+1:
            if s is not None: groups.append((s,last))
            s=y
        last=y
    groups.append((s,last)); print('arm bands',groups)
    names=['머리','몸통','오른팔','왼팔','오른발','왼발']
    assert len(groups)==6,len(groups)
    clear_sel(C,rect,sel,17)
    for (a,bb),t in zip(groups,names):
        stamp(C,t,44,(a+bb)/2+0.5,31,adv=11 if len(t)>2 else 12)
    return kedit.rebuild(b,K,C)
if __name__=='__main__':
    import render
    for n,f in [('COM_B02',com_b02),('ARM_SET',arm_set)]:
        nb,nt=f(); open(OUT+n+'.KPC','wb').write(nb); render.render(nb).save(OUT+n+'.png'); print(n,len(nb),nt)
