import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import kedit,pixfont
SRC=os.path.expanduser('~/mnt/그랜라간/work/extract/NFP2D.NFP/')
OUT=os.path.expanduser('~/mnt/그랜라간/work/gfxnew/')
SEL={13,14,15}
def textbands(C,rect):
    x0,y0,x1,y1=rect; rows={}
    for y in range(y0,y1):
        xs=[x for x in range(x0,x1) if C[y][x] in SEL]
        if xs: rows[y]=(min(xs),max(xs))
    out=[];s=None;last=None
    for y in sorted(rows):
        if s is None or y!=last+1:
            if s is not None: out.append((s,last))
            s=y
        last=y
    if s is not None: out.append((s,last))
    return [(a,b,min(rows[y][0] for y in range(a,b+1) if y in rows),max(rows[y][1] for y in range(a,b+1) if y in rows)) for a,b in out]
def clear(C,rect):
    x0,y0,x1,y1=rect
    for y in range(y0,y1):
        for x in range(x0,x1):
            if C[y][x] in SEL:
                v=None
                for xx in range(x,x0-1,-1):
                    if C[y][xx] not in SEL: v=C[y][xx];break
                if v is None:
                    for xx in range(x,x1):
                        if C[y][xx] not in SEL: v=C[y][xx];break
                C[y][x]=v
def put(C,s,cx,cy,color=15,space=0,adv=12,sp=6):
    w,h,px=pixfont.text(s,space,adv,sp); x0=int(cx-w/2); y0=int(cy-h/2)
    for (x,y) in px: C[y0+y][x0+x]=color
    return w
def small(C,s,cx,cy,color=15):
    # tighter pitch for long lines
    for adv in (12,11,10):
        w,h,px=pixfont.text(s,0,adv,5)
        if w<=228: break
    return put(C,s,cx,cy,color,0,adv,5)
JOBS={
 'COM_B04':((14,75,242,116),[('통신이 끊어졌습니다.',None),('화면을 터치하거나 A버튼을 눌러 주세요',None)]),
 'COM_B05':((50,76,206,116),[('통신을 종료하시겠습니까?',None)]),
 'COM_B06':((14,75,242,116),[('본체와 접속하지 못했습니다.',None),('화면을 터치하거나 A버튼을 눌러 주세요',None)]),
 'EQ_M01':((14,75,242,116),[('필살기를 장비할 버튼을',None),('터치해 주세요.',None)]),
 'EQ_M02':((14,75,242,116),[('선택한 버튼의 장비를 변경합니다.',None),('괜찮으면 한 번 더 터치해 주세요.',None)]),
 'EQ_M04':((14,72,242,118),[('상세 정보를 보려는 필살기를',None),('터치해 주세요.',None)]),
 'EQ_M05':((14,72,242,125),[('강화할 부위에 칩을 슬라이드해서',None),('끼워 주세요.',None),('칩은 몇 번이든 탈착할 수 있습니다.',None)]),
 'EQ_M08':((14,72,242,118),[('장비된 필살기가 하나도 없습니다.',None)]),
 'EQ_M03':((14,75,242,116),[('장비할 필살기를 터치해 주세요.',None)]),
}
def run(n):
    b=open(SRC+n+'.KPC','rb').read();K=kedit.load(b);C=kedit.canvas(K)
    rect,lines=JOBS[n]; bs=textbands(C,rect)
    print(n,bs)
    assert len(bs)==len(lines),(n,len(bs))
    clear(C,rect)
    for (a,bb,x0,x1),(t,_) in zip(bs,lines):
        small(C,t,(x0+x1)/2 if n!='EQ_M03' else 128,(a+bb)/2+0.5)
    return kedit.rebuild(b,K,C)
if __name__=='__main__':
    import render
    for n in JOBS:
        nb,nt=run(n); open(OUT+n+'.KPC','wb').write(nb); render.render(nb).save(OUT+n+'.png'); print(n,len(nb),nt)
