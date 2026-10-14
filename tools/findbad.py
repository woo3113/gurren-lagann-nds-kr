import sys, os, json, struct
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
rom=open(os.path.join(OUT,"Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
def valid(c):
    hi=c>>8; lo=c&0xff
    return ((0x81<=hi<=0x9f) or (0xe0<=hi<=0xef)) and ((0x40<=lo<=0x7e) or (0x80<=lo<=0xfc))
def find_bad(bs):
    i=0
    while i<len(bs):
        b=bs[i]
        if b==0: return None
        if b<0x80: i+=1
        else:
            if i+1>=len(bs): return (i,b,None)
            c=(b<<8)|bs[i+1]
            if not valid(c): return (i,hex(b),hex(bs[i+1]))
            i+=2
    return (-1,None,None)
bad=[]
for e in F["arm9"]:
    off=0x4000+e["off"]; r=find_bad(rom[off:off+e["len"]+2])
    if r and r[0]!=-1: bad.append(("arm9",e,r))
SPC=0x597be00
cnt=struct.unpack_from("<I",rom,SPC+0x34)[0]; hdr=struct.unpack_from("<I",rom,SPC+0x38)[0]
idx={}
for i in range(cnt):
    o=SPC+hdr+i*0x18
    nm=rom[o:o+16].split(b"\x00")[0].decode("ascii","replace")
    off,size=struct.unpack_from("<II",rom,o+16); idx[nm]=(off,size)
for e in F["spc"]:
    foff,_=idx[e["file"]]; off=SPC+foff+e["off"]; r=find_bad(rom[off:off+e["len"]+2])
    if r and r[0]!=-1: bad.append(("spc",e,r))
print("offending:", len(bad))
for k,e,r in bad[:20]:
    print(f"  [{k}] 0x{e['off']:x} len={e['len']} pos={r[0]} byte={r[1]} {e['text']!r} -> {e['ko']!r}")
