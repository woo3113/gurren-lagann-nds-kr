import sys, os, json, struct
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from game import iter_spc_text, iter_arm9_strings, iter_runs, sjis_split

ROOT = r"D:\20_게임\_한글패치\그랜라간"
ROM  = os.path.join(ROOT, "work", "Tengen Toppa Gurren Lagann (Japan).nds")
FNT  = os.path.join(ROOT, "work", "extract", "ETC.NFP", "GL_12FNT.NFT")
SPC  = os.path.join(ROOT, "work", "extract", "SPC.NFP")
NFP2D= os.path.join(ROOT, "work", "extract", "NFP2D.NFP")

rom=open(ROM,"rb").read()
ARM9 = rom[0x4000:0x4000+0x127db8]
f1 = Nft(bytearray(open(FNT,"rb").read()), 0)
cmap = f1.build_cmap()

def is_cjk_code(c):
    hi=c>>8
    return (0x88<=hi<=0x9F) or (0xE0<=hi<=0xEA)

used=set()
# ARM9 runs + pools
for off,tb in iter_runs(ARM9, 2): 
    for c in sjis_split(tb): used.add(c)
for off,l,tb in iter_arm9_strings(ARM9,2):
    for c in sjis_split(tb): used.add(c)
arm_used=len(used)
# SPC runs + opcode text
for fn in os.listdir(SPC):
    if not fn.upper().endswith(".SPC"): continue
    buf=open(os.path.join(SPC,fn),"rb").read()
    for off,tb in iter_runs(buf,2):
        for c in sjis_split(tb): used.add(c)
    for off,ln,tb in iter_spc_text(buf):
        for c in sjis_split(tb): used.add(c)
print("used codes (conservative union):", len(used))

# NFP2D check for genuine text
hits=[]
for fn in os.listdir(NFP2D):
    p=os.path.join(NFP2D,fn)
    if os.path.getsize(p)>3*1024*1024: continue
    buf=open(p,"rb").read()
    for off,tb in iter_runs(buf, 6):
        hits.append((fn,off,tb)); break
print("NFP2D files with >=6-char clean JP runs:", len(hits))
for fn,off,tb in hits[:15]:
    try: t=tb.decode("shift_jis")
    except: t="?"
    print(f"   {fn:16s} 0x{off:x} {t[:50]}")

free=[c for c in cmap if c not in used]
free_cjk=[c for c in free if is_cjk_code(c)]
print("free codes:", len(free), " free CJK:", len(free_cjk))

json.dump({"used":sorted(used),"free_cjk":sorted(free_cjk),"cmap_count":len(cmap)},
          open(os.path.join(ROOT,"out","census.json"),"w"))
print("wrote out/census.json")
