import sys, os
sys.stdout.reconfigure(encoding="utf-8")
p=r"D:\20_게임\_한글패치\그랜라간\work\extract\SPC.NFP\SYS_230.SPC"
d=open(p,"rb").read()
def dump(off,ln=0x30):
    for i in range(0,ln,16):
        c=d[off+i:off+i+16]
        print(f"{off+i:08x}  "+" ".join(f"{b:02x}" for b in c)+"  "+"".join(chr(b) if 32<=b<127 else "." for b in c))
print("file size", hex(len(d)))
for t in (0x36, 0xe35, 0xe59, 0x425c, 0x472b, 0x4765):
    print(f"--- offset 0x{t:x} ---")
    dump(t)
# count 22 00 patterns
import re
cnt=len(re.findall(rb"\x22\x00", d))
print("occurrences of 22 00:", cnt)
# what values follow?
vals=[]
i=0
while True:
    j=d.find(b"\x22\x00", i)
    if j<0: break
    if j+6<=len(d):
        v=int.from_bytes(d[j+2:j+6],"little")
        vals.append(v)
    i=j+1
vals=[v for v in vals if v<len(d)]
print("22 00 u32 < filesize count:", len(vals), "min", hex(min(vals)), "max", hex(max(vals)))
import collections
print("sample vals:", [hex(v) for v in vals[:40]])
