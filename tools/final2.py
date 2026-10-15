import sys,os,re; sys.path.insert(0,os.path.expanduser('~/emu'))
import bspc
korea=open(os.path.expanduser("~/mnt/그랜라간/out/Tengen Toppa Gurren Lagann (Korea).nds"),"rb").read()
orig=bspc.orig
FO,FL=0x153680,0x888c0
base=bytearray(orig); base[FO:FO+FL]=korea[FO:FO+FL]
bspc.orig=bytes(base)
bspc.build(os.path.expanduser('~/emu/g1.nds'),'raw')      # SPC: all strings, correct offset
r=bytearray(open(os.path.expanduser('~/emu/g1.nds'),'rb').read())
JP=re.compile(r'[぀-ヿ一-鿿]')
def enc_arm9(e):
    t=e["text"]; ko=e["ko"]
    if not JP.search(t): return None                      # 전각 영문/기호뿐 -> 원문 유지
    allowed={c for c in t if ord(c)<0x80}|{'\n'}
    d=b''
    for c in ko:
        d+= bytes([ord(c)]) if (ord(c)<0x80 and c in allowed) else bspc.fw(c) if ord(c)<0x80 else bspc.code(c)
    return d
n=0; keep=0; skip=[]
FIX={'やるな…人間！':'제법이군…인간','くそっ！！罠か！！':'젠장! 함정이냐!'}
for e in bspc.F["arm9"]:
    e=dict(e,ko=FIX.get(e['text'],e['ko']))
    off=0x4000+e["off"]; space=e["len"]+e["pad"]
    d=enc_arm9(e)
    if d is None: keep+=1; continue
    ko=e["ko"]
    while len(d)+1>space and ' ' in ko:
        i=ko.rindex(' '); ko=ko[:i]+ko[i+1:]; e2=dict(e,ko=ko); d=enc_arm9(e2)
    if len(d)+1>space: skip.append((hex(e["off"]),e["text"],e["ko"],len(d)+1,space)); continue
    r[off:off+space]=d+b"\0"*(space-len(d)); n+=1
print("arm9 patched",n,"kept orig",keep,"skipped",skip)
open(os.path.expanduser('~/emu/g2.nds'),'wb').write(r)
