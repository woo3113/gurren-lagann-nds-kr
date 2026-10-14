import sys, os, json
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from game import iter_spc_text, iter_arm9_strings, iter_runs, is_jp

ROOT = r"D:\20_게임\_한글패치\그랜라간"
ROM  = os.path.join(ROOT, "work", "Tengen Toppa Gurren Lagann (Japan).nds")
SPC  = os.path.join(ROOT, "work", "extract", "SPC.NFP")
rom=open(ROM,"rb").read()
ARM9 = rom[0x4000:0x4000+0x127db8]

# --- JP density per 4K page in ARM9 ---
out=open(os.path.join(ROOT,"out","arm9_density.txt"),"w",encoding="utf-8")
pages=[]
for p in range(0, len(ARM9), 0x1000):
    chunk=ARM9[p:p+0x1000]
    jp=0
    for off,tb in iter_runs(chunk,1):
        jp+=sum(1 for ch in tb.decode("shift_jis") if is_jp(ch))
    pages.append((jp,p))
pages.sort(reverse=True)
out.write("top density pages (jp chars per 4K):\n")
for jp,p in pages[:40]:
    out.write(f"  0x{p:06x}  {jp}\n")
out.close()

# --- SPC sample ---
with open(os.path.join(ROOT,"out","spc_sample.txt"),"w",encoding="utf-8") as fo:
    for fn in ("ADAI_01.SPC","SYS_230.SPC","MINI_01.SPC"):
        buf=open(os.path.join(SPC,fn),"rb").read()
        fo.write(f"===== {fn} =====\n")
        for off,ln,tb in list(iter_spc_text(buf))[:30]:
            fo.write(f"0x{off:x} len={ln} {tb.decode('shift_jis')!r}\n")
        fo.write("\n")
print("done")
