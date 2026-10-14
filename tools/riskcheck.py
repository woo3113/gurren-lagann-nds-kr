import sys, os, json, re, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
rom=open(os.path.join(ROOT,"work","Tengen Toppa Gurren Lagann (Japan).nds"),"rb").read()
ARM9=rom[0x4000:0x4000+0x127db8]
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

KANA=re.compile(r'[\u3040-\u30ff]')
KANJI=re.compile(r'[\u4e00-\u9fff]')

nokana=[]; odd=[]
for e in F["arm9"]:
    t=e["text"]
    if not KANA.search(t):
        nokana.append(e)
    # odd: very high kanji ratio and short, or repeated same char
    if len(t)>=4 and len(set(t))<=2:
        odd.append(e)
print(f"ARM9 문자열 {len(F['arm9'])}개 중")
print(f"  가나 없는 문자열(한자/기호만): {len(nokana)}")
for e in nokana[:40]:
    kana=len(KANA.findall(e['text'])); kan=len(KANJI.findall(e['text']))
    print(f"    0x{e['off']:06x} len={e['len']:3d} kanji={kan:2d} {e['text']!r}")
print(f"  반복 문자만 있는 문자열: {len(odd)}")
for e in odd[:20]:
    print(f"    0x{e['off']:06x} {e['text']!r}")

# density check window around each patched arm9 string
low=[]; 
for e in F["arm9"]:
    a,b=e["off"], e["off"]+e["len"]+e["pad"]
    lo=max(0,a-32); hi=min(len(ARM9),b+32)
    win=ARM9[lo:hi]
    ok=sum(1 for c in win if 0x20<=c<=0x7e or c>=0x80 or c==0)
    low.append((ok/len(win), e["off"], e["len"]))
low.sort()
print("\n주변 바이트가 텍스트스럽지 않은 상위 (낮을수록 위험):")
for f,off,ln in low[:10]:
    print(f"    frac={f:.2f} off=0x{off:06x} len={ln}")
print("\n평균 텍스트 비율:", sum(x[0] for x in low)/len(low))
