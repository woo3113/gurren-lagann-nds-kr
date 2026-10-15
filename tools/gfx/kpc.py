"""KPC (2CPK) parser: header 0xB4, LZ77(0x10) sections. Rendering helper."""
import struct
def lz77(b, off):
    assert b[off]==0x10, hex(b[off])
    n=b[off+1]|(b[off+2]<<8)|(b[off+3]<<16); i=off+4; out=bytearray()
    while len(out)<n:
        fl=b[i]; i+=1
        for k in range(8):
            if len(out)>=n: break
            if fl&(0x80>>k):
                x=(b[i]<<8)|b[i+1]; i+=2
                ln=(x>>12)+3; disp=(x&0xfff)+1
                for _ in range(ln): out.append(out[-disp])
            else:
                out.append(b[i]); i+=1
    return bytes(out[:n]), i
def hdr(b):
    return dict(flags=b[4:0x10].hex(' '), w=struct.unpack_from("<h",b,0xc)[0], h=struct.unpack_from("<h",b,0xe)[0],
                nsec=b[6], npal=b[7], f8=b[8], f9=b[9], comp=b[0xa], f0b=b[0xb],
                words=struct.unpack_from("<45I",b,0))

def parse(b):
    h=hdr(b); w=h['words']; assert w[0]==0x4b504332
    secs=[]
    # section entries (size, offset) at 0x10.. step 0x14 for nsec ; tile entries at 0x5c step 8 for npal(count)
    maps=[(w[4+5*i],w[5+5*i]) for i in range(h['nsec'])]
    tiles=[(w[0x5c//4+2*i],w[0x60//4+2*i]) for i in range(h['npal'])]
    return h,maps,tiles
def pal16(b, off, n=16):
    return [((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3) for c in struct.unpack_from("<%dH"%n,b,off)]
