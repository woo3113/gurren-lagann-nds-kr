import sys, os, json
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from game import iter_spc_text, is_lead, is_trail, is_jp

ROOT = r"D:\20_게임\_한글패치\그랜라간"
ROM  = os.path.join(ROOT, "work", "Tengen Toppa Gurren Lagann (Japan).nds")
SPC  = os.path.join(ROOT, "work", "extract", "SPC.NFP")
rom=open(ROM,"rb").read()
ARM9 = rom[0x4000:0x4000+0x127db8]

def parse_segment(seg):
    """seg: bytes between NULs. return decoded text or None."""
    if len(seg) < 3: return None
    i=0; txt=[]
    while i < len(seg):
        b=seg[i]
        if b < 0x80:
            if 0x20<=b<=0x7E or b in (0x09,0x0A,0x0D):
                txt.append(chr(b)); i+=1
            else:
                return None
        elif is_lead(b) and i+1<len(seg) and is_trail(seg[i+1]):
            try: txt.append(seg[i:i+2].decode("shift_jis"))
            except Exception: return None
            i+=2
        else:
            return None
    s="".join(txt)
    if sum(1 for ch in s if is_jp(ch))==0: return None
    return s

nul=[i for i,b in enumerate(ARM9) if b==0x00]
segs=[]
for a,b in zip(nul, nul[1:]):
    if b-a>1:
        s=parse_segment(ARM9[a+1:b])
        if s: segs.append((a+1,b,s))
print("candidate segments:", len(segs))

# text regions (coverage analysis; see coverage.py)
REGIONS = [(0x10f500,0x11eb00)]
def in_region(a,b):
    return any(r0<=a and b<=r1 for r0,r1 in REGIONS)

segs.sort()
keep=[seg for seg in segs if in_region(seg[0],seg[1])]
print("segments inside text regions:", len(keep))

arm=[]
for st,en,s in keep:
    pad=0
    while en+pad < len(ARM9) and ARM9[en+pad]==0x00 and pad<16: pad+=1
    arm.append({"off":st,"len":en-st,"pad":pad,"text":s})
print("ARM9 translatable:", len(arm), "bytes:", sum(a["len"] for a in arm))

spc=[]
for fn in sorted(os.listdir(SPC)):
    if not fn.upper().endswith(".SPC"): continue
    buf=open(os.path.join(SPC,fn),"rb").read()
    for off,ln,tb in iter_spc_text(buf):
        spc.append({"file":fn,"off":off,"len":ln,"text":tb.decode("shift_jis")})
print("SPC translatable:", len(spc), "bytes:", sum(s["len"] for s in spc))

json.dump({"arm9":arm,"spc":spc}, open(os.path.join(ROOT,"out","strings.json"),"w",encoding="utf-8"), ensure_ascii=False)
print("wrote out/strings.json")
print("total chars:", sum(len(a['text']) for a in arm)+sum(len(s['text']) for s in spc))

with open(os.path.join(ROOT,"out","arm9_sample.txt"),"w",encoding="utf-8") as fo:
    for a in arm[:200]:
        fo.write(f'{a["off"]:06x} len={a["len"]:3d} pad={a["pad"]} {a["text"]!r}\n')
with open(os.path.join(ROOT,"out","arm9_sample2.txt"),"w",encoding="utf-8") as fo:
    for a in arm[500:660]:
        fo.write(f'{a["off"]:06x} len={a["len"]:3d} pad={a["pad"]} {a["text"]!r}\n')
