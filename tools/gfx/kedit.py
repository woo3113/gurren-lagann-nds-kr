import struct,sys
from PIL import Image
sys.path.insert(0,'/'+'/'.join(__file__.split('/')[1:-1]))
import kpc
def load(b):
    h,maps,tiles=kpc.parse(b); w=h['words']
    m,_=kpc.lz77(b,w[5]); t,_=kpc.lz77(b,w[0x60//4])
    po=w[0x84//4]; psz=w[0x80//4]
    pal=[(c&31,(c>>5)&31,(c>>10)&31) for c in struct.unpack_from('<%dH'%(psz//2),b,po)]
    return dict(h=h,w=w,m=list(struct.unpack('<%dH'%(len(m)//2),m)),t=t,pal=pal,pofs=po,psz=psz)
def tilepix(t,ti):
    o=ti*32; px=[]
    for y in range(8):
        r=[]
        for x in range(8):
            v=t[o+y*4+x//2]; r.append(v>>4 if x&1 else v&15)
        px.append(r)
    return px
def canvas(K):
    """absolute colour index (bank*16+idx) per pixel, 256x256"""
    W=32;H=32
    C=[[0]*256 for _ in range(256)]
    for ty in range(H):
        for tx in range(W):
            e=K['m'][ty*W+tx]; ti=e&0x3ff;hf=e>>10&1;vf=e>>11&1;pb=e>>12
            px=tilepix(K['t'],ti) if ti*32+32<=len(K['t']) else [[0]*8]*8
            for y in range(8):
                for x in range(8):
                    sx=7-x if hf else x; sy=7-y if vf else y
                    C[ty*8+sy][tx*8+sx]=pb*16+px[y][x]
    return C
def tobytes(px):
    out=bytearray()
    for y in range(8):
        for x in range(0,8,2): out.append(px[y][x]|(px[y][x+1]<<4))
    return bytes(out)
def lzenc(data):
    n=len(data)
    # optimal parse via DP over cost in bits
    idx={}
    INF=1<<60
    cost=[INF]*(n+1); cost[0]=0; choice=[None]*(n+1)
    # flag-bit cost approx: literal 9 bits, match 17 bits
    for i in range(n):
        if cost[i]>=INF: continue
        c=cost[i]+9
        if c<cost[i+1]: cost[i+1]=c; choice[i+1]=(i,1,0)
        if i+3<=n:
            best=0
            for p in reversed(idx.get(data[i:i+3],[])):
                d=i-p
                if d>4096: break
                if d<2: continue
                l=0
                while l<18 and i+l<n and data[p+l]==data[i+l]: l+=1
                for ll in range(3,l+1):
                    c=cost[i]+17
                    if c<cost[i+ll]: cost[i+ll]=c; choice[i+ll]=(i,ll,d)
                if l==18: break
            idx.setdefault(data[i:i+3],[]).append(i)
    seq=[];j=n
    while j>0:
        i,l,d=choice[j]; seq.append((i,l,d)); j=i
    seq.reverse()
    out=bytearray(b'\x10'+n.to_bytes(3,'little'))
    for g in range(0,len(seq),8):
        grp=seq[g:g+8]; fl=0; blk=bytearray()
        for k,(i,l,d) in enumerate(grp):
            if l>=3 and d:
                fl|=0x80>>k; v=((l-3)<<12)|(d-1); blk+=bytes([v>>8,v&255])
            else: blk.append(data[i])
        out.append(fl); out+=blk
    return bytes(out)
def rebuild(b,K,C,flipdedup=True):
    """C: 256x256 absolute idx. Banks per tile from K map (kept). returns new KPC bytes"""
    W=32;H=32; tiles={}; tl=[]; mp=[]
    def key(px): return tobytes(px)
    tiles[key([[0]*8]*8)]=0; tl.append(key([[0]*8]*8))
    for ty in range(H):
        for tx in range(W):
            e0=K['m'][ty*W+tx]; pb=e0>>12
            px=[[C[ty*8+y][tx*8+x]&15 for x in range(8)] for y in range(8)]
            # bank check
            found=None
            for hf in ([0,1] if flipdedup else [0]):
                for vf in ([0,1] if flipdedup else [0]):
                    q=[[px[(7-y) if vf else y][(7-x) if hf else x] for x in range(8)] for y in range(8)]
                    k=key(q)
                    if k in tiles: found=(tiles[k],hf,vf);break
                if found:break
            if not found:
                tiles[key(px)]=len(tl); tl.append(key(px)); found=(len(tl)-1,0,0)
            ti,hf,vf=found
            mp.append(ti|(hf<<10)|(vf<<11)|(pb<<12))
    if len(tl)>1024: raise Exception('too many tiles %d'%len(tl))
    mcomp=lzenc(struct.pack('<%dH'%len(mp),*mp)); tcomp=lzenc(b''.join(tl))
    w=list(K['w'])
    al=lambda x:(x+31)&~31
    mo=0xc0; to=al(mo+len(mcomp)); po=al(to+len(tcomp))
    w[4]=len(mcomp); w[5]=mo; w[0x5c//4]=len(tcomp); w[0x60//4]=to; w[0x84//4]=po
    out=bytearray(struct.pack('<45I',*w)); out+=b[len(out):0xc0]
    out+=mcomp; out+=b'\0'*(to-len(out)); out+=tcomp; out+=b'\0'*(po-len(out))
    out+=b[K['pofs']:K['pofs']+K['psz']]
    return bytes(out),len(tl)

from PIL import ImageFont,ImageDraw
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(sz): return ImageFont.truetype(FONT,sz,index=1)
def nearest(pal,rgb,cands):
    best=None
    for i in cands:
        c=pal[i]; d=sum((a-b)**2 for a,b in zip(c,rgb))
        if best is None or d<best[0]: best=(d,i)
    return best[1]
def bands(C,bg,x0=0,x1=256,y1=192):
    rows=[any(C[y][x]!=bg for x in range(x0,x1)) for y in range(y1)]; out=[];s=None
    for y,r in enumerate(rows+[False]):
        if r and s is None:s=y
        if not r and s is not None:
            xs=[x for yy in range(s,y) for x in range(x0,x1) if C[yy][x]!=bg]
            out.append((s,y-1,min(xs),max(xs)));s=None
    return out
def drawtext(C,K,text,x,ytop,size,maxw,fg,bgfun,cands,minsize=13,center=None,gamma=1.0):
    """fg rgb (0-31 scale); bgfun(x,y)->absolute idx currently there. returns used size"""
    while True:
        f=font(size); w=f.getlength(text)
        if w<=maxw or size<=minsize: break
        size-=1
    h=int(size*1.3)+2
    m=Image.new('L',(int(w)+8,h),0); ImageDraw.Draw(m).text((2,0),text,font=f,fill=255)
    bb=m.getbbox()
    if center is not None: x=int(center-w/2)
    # vertical: place so glyph body (hangul) top at ytop; use font ascent heuristic
    for yy in range(m.size[1]):
        for xx in range(m.size[0]):
            a=m.getpixel((xx,yy))/255
            if a<0.08: continue
            X=x+xx-2; Y=ytop+yy
            if not(0<=X<256 and 0<=Y<192): continue
            cur=bgfun(X,Y); bank=cur>>4
            bc=K['pal'][cur]; rgb=tuple(bc[i]*(1-a)+fg[i]*a for i in range(3))
            C[Y][X]=bank*16+nearest(K['pal'],rgb,[bank*16+c for c in cands])-bank*16 if False else nearest(K['pal'],rgb,[bank*16+c for c in cands])
    return size
