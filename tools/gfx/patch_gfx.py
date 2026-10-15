import struct,sys,os,glob
src,dst,newdir=sys.argv[1:4]
d=bytearray(open(src,'rb').read())
base=0x178200
cnt=struct.unpack_from("<I",d,base+0x34)[0];hs=struct.unpack_from("<I",d,base+0x38)[0]
ents=[]
for i in range(cnt):
    o=hs+i*0x18
    nm=bytes(d[base+o:base+o+16]).split(b"\0")[0].decode();off,sz=struct.unpack_from("<II",d,base+o+16);ents.append((off,sz,nm))
offs=sorted(e[0] for e in ents)
for p in sorted(glob.glob(newdir+'/*.KPC')):
    nm=os.path.basename(p); e=[x for x in ents if x[2]==nm][0]
    nx=min(o for o in offs if o>e[0]); gap=nx-e[0]
    nb=open(p,'rb').read()
    assert len(nb)<=gap,(nm,len(nb),gap)
    d[base+e[0]:base+nx]=nb+b'\0'*(gap-len(nb))
    print('patched',nm,len(nb),'/',gap)
open(dst,'wb').write(d)
