import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
E=F["arm9"]+F["spc"]

# game format dialect seen: %s %c %d %md %m02d %03md ...
VALID=re.compile(r'%[0-9]{0,3}m?[0-9]{0,3}[dscxX%]')
bad=[]
for e in E:
    ko=e["ko"]; i=0
    while True:
        j=ko.find("%",i)
        if j<0: break
        m=VALID.match(ko,j)
        if not m:
            bad.append((e, j, ko[max(0,j-8):j+8]))
            break
        i=m.end()
print("KO에 '잘못된 % 토큰'이 있는 항목:", len(bad))
for e,j,ctx in bad[:40]:
    print(f"   {e['text']!r} -> {e['ko']!r}   (ctx ...{ctx}...)")

# also count literal % occurrences in the japanese source (to see if % is normally escaped)
print("\nJA에 '%' 포함 항목 수:", sum(1 for e in E if "%" in e["text"]))
print("KO에 '%' 포함 항목 수:", sum(1 for e in E if "%" in e["ko"]))
