import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
S=json.load(open(os.path.join(ROOT,"out","strings.json"),encoding="utf-8"))
def hasctl(s): return any(ord(c)<0x20 and c!='\n' for c in s)
print("=== SPC strings containing control chars ===")
n=0
for e in S["spc"]:
    if hasctl(e["text"]):
        n+=1
        if n<=30:
            print(f'{e["file"]} 0x{e["off"]:x} len={e["len"]} {[hex(ord(c)) for c in e["text"] if ord(c)<0x20]} {e["text"]!r}')
print("total SPC strings with ctl:", n)
print()
print("=== ARM9 strings containing control chars ===")
n=0
for e in S["arm9"]:
    if hasctl(e["text"]):
        n+=1
        if n<=30:
            print(f'{e["off"]:06x} len={e["len"]} {[hex(ord(c)) for c in e["text"] if ord(c)<0x20]} {e["text"]!r}')
print("total ARM9 strings with ctl:", n)
# strings with embedded NUL
print()
print("=== strings with embedded NUL (suspicious) ===")
n=0
for e in S["spc"]:
    if "\x00" in e["text"]:
        n+=1
        if n<=10: print(f'{e["file"]} 0x{e["off"]:x} {e["text"]!r}')
print("count:", n)
