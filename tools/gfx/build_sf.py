import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import kedit; from jobs_sf import SF
SRC=os.path.expanduser('~/mnt/그랜라간/work/extract/NFP2D.NFP/')
OUT=os.path.expanduser('~/mnt/그랜라간/work/gfxnew/'); os.makedirs(OUT,exist_ok=True)
def run(n,levels=None):
    b=open(SRC+n+'.KPC','rb').read();K=kedit.load(b);C=kedit.canvas(K)
    bs=[x for x in kedit.bands(C,1,y1=192)]
    lines=SF[n]; assert len(bs)==len(lines),(n,len(bs),len(lines))
    for y in range(192):
        for x in range(256): C[y][x]=1
    cands=list(range(1,16)) if not levels else levels
    for (y0,y1,x0,x1),t in zip(bs,lines):
        kedit.drawtext(C,K,t,x0,y0-4,19,250-x0,(31,31,31),lambda x,y:1,cands)
    nb,nt=kedit.rebuild(b,K,C)
    return nb,nt,C,K
if __name__=='__main__':
    from PIL import Image
    import render
    for n in SF:
        nb,nt,C,K=run(n)
        open(OUT+n+'.KPC','wb').write(nb)
        Image.frombytes('RGB',(256,192),bytes(v for row in C[:192] for x in row for v in [x*0]) ) if False else None
        render.render(nb).save(OUT+n+'.png'); print(n,len(nb),nt)
