import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
CM=json.load(open(os.path.join(OUT,"charmap.json"),encoding="utf-8"))
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
km={ch:c for ch,c in CM["keepmap"].items()}
nm={it["ch"]:it["code"] for it in CM["newchars"]}
def valid(c):
    hi=c>>8; lo=c&0xff
    return ((0x81<=hi<=0x9f) or (0xe0<=hi<=0xef)) and ((0x40<=lo<=0x7e) or (0x80<=lo<=0xfc))
bad=[]; inv=0
for e in F["arm9"]+F["spc"]:
    for ch in e["ko"]:
        o=ord(ch)
        if o<0x80: continue
        c=km.get(ch, nm.get(ch))
        if c is None: inv+=1; bad.append((e["text"][:20], ch, "no-code")); continue
        if not valid(c): bad.append((e["text"][:20], ch, hex(c)))
print("코드 없는 문자:", inv)
print("유효하지 않은 SJIS로 인코딩되는 항목:", len(bad))
for b in bad[:10]: print("   ", b)

# verify the actual patched ROM bytes decode as valid shift_jis everywhere we wrote
rom=open(os.path.join(OUT,"Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
def check(bs):
    i=0
    while i<len(bs):
        b=bs[i]
        if b==0: break
        if b<0x80: i+=1
        else:
            if i+1>=len(bs): return False
            c=(b<<8)|bs[i+1]; i+=2
            if not valid(c): return False
    return True
err=0
for kind,base in (("arm9",0x4000),):
    for e in F[kind]:
        off=base+e["off"]
        if not check(rom[off:off+e["len"]+2]): err+=1
import struct
SPC=0x597be00
cnt=struct.unpack_from("<I",rom,SPC+0x34)[0]; hdr=struct.unpack_from("<I",rom,SPC+0x38)[0]
idx={}
for i in range(cnt):
    o=SPC+hdr+i*0x18
    nmx=rom[o:o+16].split(b"\x00")[0].decode("ascii","replace")
    off,size=struct.unpack_from("<II",rom,o+16); idx[nmx]=(off,size)
for e in F["spc"]:
    foff,_=idx[e["file"]]; off=SPC+foff+e["off"]
    if not check(rom[off:off+e["len"]+2]): err+=1
print("패치 롬에서 유효하지 않은 SJIS 시퀀스가 있는 문자열:", err)
