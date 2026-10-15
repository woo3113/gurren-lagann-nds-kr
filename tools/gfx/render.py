import struct,sys
from PIL import Image
sys.path.insert(0,'.')
import kpc
def render(b):
    h,maps,tiles=kpc.parse(b)
    w=h['words']
    ms,mo=maps[0]; ts,to=tiles[0]
    m,_=kpc.lz77(b,mo); t,_=kpc.lz77(b,to)
    pofs=w[0x84//4]; psz=w[0x80//4]
    pal=kpc.pal16(b,pofs,psz//2)
    W=h['w'];H=h['h']
    img=Image.new('RGB',(W*8,H*8),(255,0,255))
    for ty in range(H):
        for tx in range(W):
            e=struct.unpack_from('<H',m,(ty*W+tx)*2)[0] if (ty*W+tx)*2+2<=len(m) else 0
            ti=e&0x3ff;hf=e>>10&1;vf=e>>11&1;pb=(e>>12)*16
            for y in range(8):
                for x in range(8):
                    o=ti*32+y*4+x//2
                    if o>=len(t): continue
                    v=t[o]>>4 if x&1 else t[o]&15
                    sx=7-x if hf else x; sy=7-y if vf else y
                    c=pal[(pb+v)%len(pal)] if pb+v<len(pal) else (255,0,255)
                    if v==0: c=(0,0,0)
                    img.putpixel((tx*8+sx,ty*8+sy),c)
    return img
if __name__=='__main__':
    for n in sys.argv[2:]:
        b=open(n,'rb').read()
        render(b).save(sys.argv[1]+'/'+n.split('/')[-1]+'.png')
