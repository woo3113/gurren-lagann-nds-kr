import struct,sys,os,glob
# usage: patch_gfx2.py src dst dir1 [dir2...]   (KPC: replace within gap; YCE: diff-apply vs extracted original)
src,dst=sys.argv[1:3]; dirs=sys.argv[3:]
d=bytearray(open(src,'rb').read())
base=0x178200
cnt=struct.unpack_from("<I",d,base+0x34)[0];hs=struct.unpack_from("<I",d,base+0x38)[0]
ents={}
for i in range(cnt):
    o=hs+i*0x18
    nm=bytes(d[base+o:base+o+16]).split(b"\0")[0].decode();off,sz=struct.unpack_from("<II",d,base+o+16);ents[nm]=off
offs=sorted(ents.values())
ex=os.path.join(os.path.dirname(__file__),'..','..','work','extract','NFP2D.NFP')
for dr in dirs:
  for p in sorted(glob.glob(dr+'/*')):
    nm=os.path.basename(p)
    if nm not in ents: continue
    off=ents[nm]; nb=open(p,'rb').read()
    nx=min(o for o in offs if o>off); gap=nx-off
    if nm.endswith('.KPC'):
        assert len(nb)<=gap,(nm,len(nb),gap)
        d[base+off:base+nx]=nb+b'\0'*(gap-len(nb)); print('KPC',nm,len(nb),'/',gap)
    else:
        ob=open(os.path.join(ex,nm),'rb').read()
        assert len(nb)==len(ob),(nm,len(nb),len(ob))
        n=0
        for i in range(len(ob)):
            if nb[i]!=ob[i]: d[base+off+i]=nb[i]; n+=1
        print('YCE',nm,n,'bytes')
open(dst,'wb').write(d)
