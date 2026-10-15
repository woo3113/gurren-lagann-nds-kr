import struct
from PIL import Image
SZ={1:[(16,8),(32,8),(32,16),(64,32)],2:[(8,16),(8,32),(16,32),(32,64)],0:[(8,8),(16,16),(32,32),(64,64)]}
def parse(b):
    assert b[:4]==b'ECNY'
    hs=struct.unpack_from('<I',b,0x10)[0]; nf=struct.unpack_from('<I',b,0x1c)[0]
    offs=struct.unpack_from('<%dI'%nf,b,0x20)
    frames=[]
    for o in offs:
        c=o+hs
        size,hl,nrec,toff,tsz,poff,npal=struct.unpack_from('<7I',b,c)
        recs=[]
        for i in range(nrec):
            r=c+hl+i*0x14
            x,y,_a,_b,sh,tile=struct.unpack_from('<hhIIII',b,r)
            shape=sh&0xff;sz=(sh>>8)&0xff
            recs.append((x,y,shape,sz,tile,struct.unpack_from('<5I',b,r)))
        frames.append(dict(c=c,size=size,hl=hl,nrec=nrec,toff=toff,tsz=tsz,poff=poff,npal=npal,recs=recs))
    return frames
def pal(b,f):
    c=f['c']; n=(f['size']-f['poff'])//2
    return [((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3) for v in struct.unpack_from('<%dH'%n,b,c+f['poff'])]
def render(b,f,maxw=400):
    P=pal(b,f); td=f['c']+f['toff']; tile=lambda i:b[td+i*32:td+i*32+32]
    sp=[]
    for (x,y,shape,sz,t,raw) in f['recs']:
        if shape>2 or sz>3: continue
        w,h=SZ[shape][sz]; sp.append((x,y,w,h,t))
    if not sp: return None
    x0=min(s[0] for s in sp);y0=min(s[1] for s in sp);x1=max(s[0]+s[2] for s in sp);y1=max(s[1]+s[3] for s in sp)
    im=Image.new('RGB',(x1-x0,y1-y0),(255,0,255)); px=im.load()
    for (x,y,w,h,t) in sp:
        for ty in range(h//8):
            for tx in range(w//8):
                d=tile(t+ty*(w//8)+tx)
                if len(d)<32: continue
                for yy in range(8):
                    for xx in range(8):
                        v=d[yy*4+xx//2]; v=v>>4 if xx&1 else v&15
                        if v: px[x-x0+tx*8+xx,y-y0+ty*8+yy]=P[v] if v<len(P) else (255,0,0)
    return im

def idxcanvas(b,f):
    """returns (x0,y0,w,h,I,src) where I[y][x]=palette idx (None where empty) and src[y][x]=byte offset of the byte, nibble"""
    td=f['c']+f['toff']; sp=[]
    for (x,y,shape,sz,t,raw) in f['recs']:
        if shape>2 or sz>3: continue
        w,h=SZ[shape][sz]; sp.append((x,y,w,h,t))
    x0=min(s[0] for s in sp);y0=min(s[1] for s in sp);x1=max(s[0]+s[2] for s in sp);y1=max(s[1]+s[3] for s in sp)
    W=x1-x0;H=y1-y0
    I=[[None]*W for _ in range(H)]; S=[[None]*W for _ in range(H)]
    for (x,y,w,h,t) in sp:
        for ty in range(h//8):
            for tx in range(w//8):
                base=td+(t+ty*(w//8)+tx)*32
                for yy in range(8):
                    for xx in range(8):
                        o=base+yy*4+xx//2; v=b[o]; v=v>>4 if xx&1 else v&15
                        I[y-y0+ty*8+yy][x-x0+tx*8+xx]=v; S[y-y0+ty*8+yy][x-x0+tx*8+xx]=(o,xx&1)
    return x0,y0,W,H,I,S
def write(b,f,I0,I,S):
    nb=bytearray(b)
    for y in range(len(I)):
        for x in range(len(I[0])):
            if I[y][x]!=I0[y][x] and S[y][x] is not None:
                o,hi=S[y][x]
                nb[o]=(nb[o]&0x0f)|(I[y][x]<<4) if hi else (nb[o]&0xf0)|I[y][x]
    return bytes(nb)
def asc(I,pal=None):
    for r in I: print(''.join('.' if v is None else '%x'%v for v in r))
