import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yce,yedit
SRC=os.path.expanduser('~/mnt/그랜라간/work/extract/NFP2D.NFP/')
OUT=os.path.expanduser('~/mnt/그랜라간/work/gfxnew_yce/')
N8=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy]
def J(rect,tset,text,**kw):
    return lambda I,P: yedit.retext(I,P,rect,lambda i,P:i in tset,text,**kw)
def sys01():
    mk=lambda text,t: J((14,8,48,21),t,text)
    return 'SYS_01',[(0,mk('결정',{9,10})),(1,mk('결정',{14,15})),(2,mk('취소',{9,10})),(3,mk('취소',{14,15}))]
def com_s04():
    r=(10,8,86,23)
    a=lambda t: J(r,{11,12},t,fg=12,shadow=(11,[(1,1)]),period=3)
    b=lambda t: J(r,{11,12},t,fg=11,shadow=(12,[(1,1)]),period=3)
    y=lambda t: J(r,{11,12},t,fg=12,shadow=(11,[(1,1)]),period=3)
    return 'COM_S04',[(0,a('재대전')),(1,b('재대전')),(2,y('재대전')),(3,a('종료')),(4,b('종료')),(5,y('종료'))]
def save_s02():
    return 'SAVE_S02',[(0,J((30,3,128,22),{11,12},'스토리',fg=12,shadow=(11,[(1,0),(0,1),(1,1)]),adv=16)),
                       (1,J((30,3,128,22),{11,12},'통신대전',fg=12,shadow=(11,[(1,0),(0,1),(1,1)]),adv=15)),
                       (2,J((40,5,100,19),{15},'삭제',fg=15,outline=1,adv=16,extra=({1},N8))),
                       (3,J((40,5,96,19),{15,3},'삭제',fg=15,outline=3,adv=16))]
def mode_b():
    o=lambda t: J((11,8,77,24),{9,10,11,12},t,fg=9,shadow=(12,[(1,1)]),adv=12)
    c=lambda t: J((10,10,70,22),set(range(16)),t,fg=1,shadow=(6,[(1,1)]),adv=12,facefill=3,center=(40,16))
    return 'MODE_B',[(0,o('필살기 장비')),(1,c('필살기 장비')),(2,o('필살기 열람')),(3,c('필살기 열람')),(4,o('장갑 강화')),(5,c('장갑 강화'))]
def ttl_s01():
    def f(I,P):
        H=len(I);W=len(I[0]);from collections import deque
        q=deque((x,y) for y in range(H) for x in range(W) if I[y][x]==0 or (I[y][x] is None))
        seen=set(q);B=set()
        while q:
            x,y=q.popleft()
            for dx in(-1,0,1):
                for dy in(-1,0,1):
                    X,Y=x+dx,y+dy
                    if 0<=X<W and 0<=Y<H and (X,Y) not in seen and I[Y][X]==1:
                        seen.add((X,Y));B.add((X,Y));q.append((X,Y))
        for (x,y) in B: I[y][x]=99
        r=yedit.retext(I,P,(10,10,205,56),lambda i,P:1<=i<=14,'네 드릴로 하늘을 뚫어라!!',fg=1,kind='ttf',height=22,maxw=164,center=(108,33))
        for (x,y) in B: I[y][x]=1
        return r
    return 'TTL_S01',[(0,f)]

import pixfont
def redraw(I,P,xr,rows,clean_top,clean_bot,text,fg,outline,adv,center,sp=6):
    x0,x1=xr;y0,y1=rows
    mid=(y0+y1)//2
    for y in range(y0,y1+1):
        cy=clean_top if y<=mid else clean_bot
        for x in range(x0,x1):
            if I[y][x] is not None and I[cy][x] is not None: I[y][x]=I[cy][x]
    w,h,px=pixfont.text(text,0,adv,sp)
    ox=int(round(center[0]-w/2));oy=int(round(center[1]-h/2))
    M={(x+ox,y+oy) for x,y in px}
    if outline is not None:
        O={(x+dx,y+dy) for (x,y) in M for dx in(-1,0,1) for dy in(-1,0,1)}-M
        for (x,y) in O:
            if I[y][x] is not None: I[y][x]=outline
    for (x,y) in M:
        if I[y][x] is not None: I[y][x]=fg
    return True
def arm_end():
    return 'ARM_END',[(k,J((9,2,39,19),{15},'종료',fg=15,adv=12)) for k in range(5)]
def arm_slb():
    t=['설정을 반영하고 종료','설정을 되돌리고 종료','장갑 강화를 계속한다']
    return 'ARM_SLB',[(k,(lambda I,P,t=t[k//2]:redraw(I,P,(8,136),(7,23),4,26,t,15,1,12,(72,15),6))) for k in range(6)]


def btin_03():
    r=(16,10,64,24)
    return 'BTIN_03',[(0,J(r,{1,15},'출격',fg=15,outline=1,adv=16,center=(40,16.5))),
                      (1,J(r,{3,14},'출격',fg=3,outline=14,adv=16,center=(40,16.5)))]
def inbtl():
    r=(10,6,102,18)
    blk=lambda t: J(r,set(range(15)),t,fg=10,adv=12,center=(56,12))
    red=lambda t: J(r,{1,2,6,7,8,9,10,11,12,13,14,15},t,fg=10,outline=6,adv=12,period=2,center=(56,12))
    T=['재시도','설정변경','그만두기']
    return 'INBTLOBJ',[(3,blk(T[0])),(4,red(T[0])),(5,blk(T[1])),(6,red(T[1])),(7,blk(T[2])),(8,red(T[2]))]


import collections
def gradtext(I,P,text,pred,maxw,center=None,blob=None,blobr=2,plate=None,rect=None,height=None,thr=110,fixed_rows=None):
    H=len(I);W=len(I[0])
    rows={}
    for y in range(H):
        c=collections.Counter(I[y][x] for x in range(W) if I[y][x] is not None and pred(I[y][x]))
        if c: rows[y]=c.most_common(1)[0][0]
    ys=sorted(rows); y0,y1=ys[0],ys[-1]
    if fixed_rows: y0,y1=fixed_rows
    xs=[x for y in range(H) for x in range(W) if I[y][x] is not None and pred(I[y][x])]
    cx=(min(xs)+max(xs)+1)/2 if center is None else center
    col=lambda y: rows.get(min(max(y,ys[0]),ys[-1]),rows[ys[0]])
    rc={y:col(y) for y in range(y0,y1+1)}
    h=height or (y1-y0+1)
    # clear
    if plate is None:
        for y in range(H):
            for x in range(W):
                if I[y][x] is not None: I[y][x]=0
    else:
        rx0,ry0,rx1,ry1=rect
        for y in range(ry0,ry1):
            for x in range(rx0,rx1):
                if I[y][x] is not None: I[y][x]=plate
    w,h2,im=yedit.mask_ttf(text,h,maxw)
    ox=int(round(cx-w/2)); oy=y0
    M={(x+ox,y+oy) for y in range(h2) for x in range(w) if im.getpixel((x,y))>=thr}
    if blob is not None:
        B={(x+dx,y+dy) for (x,y) in M for dx in range(-blobr,blobr+1) for dy in range(-blobr,blobr+1)}
        for (x,y) in B:
            if 0<=y<H and 0<=x<W and I[y][x] is not None: I[y][x]=blob
    for (x,y) in M:
        if 0<=y<H and 0<=x<W and I[y][x] is not None: I[y][x]=rc.get(y, rc[y0] if y<y0 else rc[y1])
    return True
def st_chg():
    T=['조작 불능','이동 불능','이동속도 상승','이동속도 저하','공격력 상승','무적 실드 전개','선회속도 상승','선회속도 저하','차지속도 상승','차지속도 저하','필살기 게이지 리셋','필살기 게이지 최대','실드 전개','불가시']
    return 'ST_CHG',[(k,(lambda I,P,t=t:gradtext(I,P,t,lambda i:i not in(0,15),116,center=64,blob=15,blobr=2,fixed_rows=(9,23),height=15))) for k,t in enumerate(T)]
def bt_16():
    T=['머리','몸통','오른팔','왼팔','오른발','왼발']
    return 'BT_16',[(k,(lambda I,P,t=t+' 장갑 손상':gradtext(I,P,t,lambda i:i>=5,96,center=64,plate=1,rect=(16,8,112,25),fixed_rows=(10,21)))) for k,t in enumerate(T)]


def bt_15():
    N=['머리','몸통','오른팔','왼팔','오른발','왼발']
    red=[15,15,14,14,13,13,12]; grey=[11,10,9,8,7,5,3]
    def f(I,P,n):
        H=len(I);W=len(I[0])
        for y in range(H):
            for x in range(W):
                if I[y][x] is not None: I[y][x]=0
        Y0,Y1=7,53
        def draw(text,maxw,cx,pal):
            w,h,im=yedit.mask_ttf(text,Y1-Y0+1,maxw)
            ox=int(round(cx-w/2))
            return {(x+ox,y+Y0) for y in range(h) for x in range(w) if im.getpixel((x,y))>=110},pal
        parts=[draw(n,76,40,red),draw('장갑 대파!!',172,168,grey)]
        allm=set().union(*[p[0] for p in parts])
        for (x,y) in allm:
            for dx in range(-2,3):
                for dy in range(-2,3):
                    X,Y=x+dx,y+dy
                    if 0<=X<W and 0<=Y<H and I[Y][X] is not None: I[Y][X]=1
        for m,pal in parts:
            for (x,y) in m:
                if 0<=x<W and 0<=y<H and I[y][x] is not None:
                    I[y][x]=pal[min(len(pal)-1,(y-Y0)*len(pal)//(Y1-Y0+1))]
        return True
    return 'BT_15',[(k,(lambda I,P,n=n:f(I,P,n))) for k,n in enumerate(N)]


def rowmodes(I,pred):
    rows={}
    for y in range(len(I)):
        c=collections.Counter(v for v in I[y] if v is not None and pred(v))
        if c: rows[y]=c.most_common(1)[0][0]
    return rows
def gline(I,text,rows,y0,y1,cx,maxw,blob,blobr,thr=110,pix=False):
    H=len(I);W=len(I[0]);ys=sorted(rows)
    col=lambda y: rows[min(max(y,ys[0]),ys[-1])]
    if pix:
        for a in (12,11,10,9,8):
            w,h,px=pixfont.text(text,0,a,5)
            if w<=maxw: break
        ox=int(round(cx-w/2)); oy=y0+((y1-y0+1)-h)//2
        M={(x+ox,y+oy) for (x,y) in px}
    else:
        w,h,im=yedit.mask_ttf(text,y1-y0+1,maxw)
        ox=int(round(cx-w/2))
        M={(x+ox,y+y0) for y in range(h) for x in range(w) if im.getpixel((x,y))>=thr}
    for (x,y) in M:
        for dx in range(-blobr,blobr+1):
            for dy in range(-blobr,blobr+1):
                X,Y=x+dx,y+dy
                if 0<=X<W and 0<=Y<H and I[Y][X] is not None: I[Y][X]=blob
    for (x,y) in M:
        if 0<=x<W and 0<=y<H and I[y][x] is not None: I[y][x]=col(y)
def clear0(I):
    for y in range(len(I)):
        for x in range(len(I[0])):
            if I[y][x] is not None: I[y][x]=0
def bt_18():
    pr=lambda i:i not in(0,15)
    def one(t,cx,maxw,y0,y1):
        def f(I,P):
            r=rowmodes(I,pr);clear0(I);gline(I,t,r,y0,y1,cx,maxw,15,1,pix=True);return True
        return f
    def two(a,b):
        def f(I,P):
            r=rowmodes(I,pr);clear0(I)
            gline(I,a,r,3,13,32,52,15,1,pix=True);gline(I,b,r,18,28,32,52,15,1,pix=True);return True
        return f
    return 'BT_18',[(0,one('체력회복',32,58,3,13)),(1,one('공격력UP',32,58,3,13)),(2,two('필살기','속도UP')),(3,two('이동','속도UP')),(4,one('무적',16,28,3,13))]


def bt_10():
    T=['전투 개시','일시정지','격파!!','아이템 획득!']
    pal=[15,15,14,13,12,11,10,9]
    def f(I,P,t):
        H=len(I);W=len(I[0])
        for y in range(20,H):
            for x in range(W):
                if I[y][x] is not None: I[y][x]=0
        Y0,Y1=25,57
        w,h,im=yedit.mask_ttf(t,Y1-Y0+1,W-14)
        ox=int(round(W/2-w/2))
        M={(x+ox,y+Y0) for y in range(h) for x in range(w) if im.getpixel((x,y))>=110}
        for (x,y) in M:
            for dx in range(-3,4):
                for dy in range(-3,4):
                    X,Y=x+dx,y+dy
                    if Y>=20 and 0<=X<W and Y<H and I[Y][X] is not None: I[Y][X]=1
        for (x,y) in M:
            if I[y][x] is not None: I[y][x]=pal[min(len(pal)-1,(y-Y0)*len(pal)//(Y1-Y0+1))]
        return True
    return 'BT_10',[(k,(lambda I,P,t=t:f(I,P,t))) for k,t in enumerate(T)]


def mode_f():
    T=['정비실','필살기 장비','필살기 열람','장갑 강화']
    b0=open(SRC+'MODE_F.YCE','rb').read();F0=yce.parse(b0)
    I0=yce.idxcanvas(b0,F0[0])[4]
    mode=lambda y,xa,xb:collections.Counter(I0[y][x] for x in range(xa,xb)).most_common(1)[0][0]
    C={y:(mode(y,14,30),mode(y,118,130)) for y in range(6,34)}
    pal=[15,14,14,13,13,12,12,11,11,10,10,9]
    def f(I,P,t):
        for y in range(6,34):
            for x in range(8,137):
                if I[y][x] is not None: I[y][x]=I0[y][x] if (x<16 or x>=126) and I0[y][x] is not None else (C[y][0] if x<72 else C[y][1])
        Y0,Y1=8,31
        w,h,im=yedit.mask_ttf(t,Y1-Y0+1,106)
        ox=int(round(72-w/2))
        M={(x+ox,y+Y0) for y in range(h) for x in range(w) if im.getpixel((x,y))>=110}
        for (x,y) in M:
            for dx in range(-1,3):
                for dy in range(-1,3):
                    X,Y=x+dx,y+dy
                    if I[Y][X] is not None: I[Y][X]=2
        for (x,y) in M:
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    X,Y=x+dx,y+dy
                    if I[Y][X]==2 and (dx<=0 and dy<=0 or dx==0 or dy==0): pass
        for (x,y) in M:
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    X,Y=x+dx,y+dy
                    if I[Y][X] is not None and (X,Y) not in M: I[Y][X]=3 if not(dx>0 and dy>0) else 2
        for (x,y) in M:
            if I[y][x] is not None: I[y][x]=pal[min(len(pal)-1,(y-Y0)*len(pal)//(Y1-Y0+1))]
        return True
    return 'MODE_F',[(k,(lambda I,P,t=t:f(I,P,t))) for k,t in enumerate(T)]


def eq_yn():
    r=(16,9,48,21)
    f=lambda t:J(r,{9,10},t,fg=10,shadow=(9,[(1,1)]),adv=12,center=(33,15))
    g=lambda t:J(r,{14,15},t,fg=15,shadow=(11,[(1,1)]),adv=12,center=(33,15))
    return 'EQ_YN',[(0,f('결정')),(1,g('결정')),(2,f('취소')),(3,g('취소'))]
def eq_ctg():
    T=['전체 표시',None,'공격력','수동/자동','장비 부위','사이트','록온 수','공격/보조']
    jobs=[]
    for i,t in enumerate(T):
        if t is None: continue
        for k in (2*i,2*i+1):
            jobs.append((k,J((1,6,60,17),{12},t,fg=12,adv=12,center=(32,11.5))))
    for k,t in ((62,'공'),(63,'공'),(64,'보'),(65,'보')):
        jobs.append((k,J((7,3,18,14),{11},t,fg=11,adv=11,period=3,center=(12.5,8.5))))
    return 'EQ_CTG',jobs


def gl_compnl():
    r=(10,6,102,18)
    blk=lambda t: J(r,set(range(2,16)),t,fg=2,adv=12,center=(56,12))
    red=lambda t: J(r,set(range(0,16))-{5,7,9,1},t,fg=2,outline=12,adv=12,period=2,center=(56,12))
    dim=lambda t: J(r,{10,11},t,fg=10,shadow=(11,[(1,1)]),adv=12,center=(56,12))
    return 'GL_COMPNL',[(0,blk('재시도')),(1,red('재시도')),(2,dim('재시도')),(3,blk('그만두기')),(4,red('그만두기')),(5,dim('그만두기'))]

JOBS=[gl_compnl,eq_yn,eq_ctg,mode_f,bt_10,bt_18,bt_15,st_chg,bt_16,btin_03,inbtl,arm_end,arm_slb,sys01,com_s04,save_s02,mode_b,ttl_s01]
if __name__=='__main__':
    names=sys.argv[1:]
    for fnc in JOBS:
        if names and fnc.__name__ not in names: continue
        n,j=fnc(); yedit.apply(SRC,OUT,n,j); print('ok',n)
