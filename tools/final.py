import sys,os,json; sys.path.insert(0,os.path.expanduser('~/emu'))
import bspc,fixkeys
H=fixkeys.H
korea=open(os.path.expanduser("~/mnt/그랜라간/out/Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
orig=bspc.orig
# base = original + font from Korea build
FO,FL=0x153680,0x888c0
base=bytearray(orig); base[FO:FO+FL]=korea[FO:FO+FL]
bspc.orig=bytes(base)
bspc.build(os.path.expanduser('~/emu/f1.nds'),'fw',lambda e:e["text"] not in H)
r=bytearray(open(os.path.expanduser('~/emu/f1.nds'),'rb').read())
# ARM9: fullwidth rule
A=bspc.F["arm9"]; n=0; skip=0
for e in A:
    off=0x4000+e["off"]; space=e["len"]+e["pad"]
    ko=e["ko"]; jp_ascii=any(ord(c)<0x80 for c in e["text"])
    if not jp_ascii:
        d=b''.join(bspc.fw(c) for c in ko)
        while len(d)+1>space and ' ' in ko:
            i=ko.rindex(' '); ko=ko[:i]+ko[i+1:]; d=b''.join(bspc.fw(c) for c in ko)
    else:
        d=b''.join(bspc.code(c) for c in ko)
    if len(d)+1>space: skip+=1; continue
    r[off:off+space]=d+b"\0"*(space-len(d)); n+=1
print("arm9 patched",n,"skipped(too long)",skip)
open(os.path.expanduser('~/emu/f2.nds'),'wb').write(r)
