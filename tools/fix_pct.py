"""Fix: literal '%' that is not a valid game format specifier must be the full-width '％'."""
import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
VALID=re.compile(r'%[0-9]{0,3}m?[0-9]{0,3}[dscxX%]')

def fix(s):
    out=[]; i=0
    while i < len(s):
        if s[i]=="%":
            m=VALID.match(s,i)
            if m:
                out.append(m.group(0)); i=m.end(); continue
            out.append("\uFF05"); i+=1; continue   # full-width percent
        out.append(s[i]); i+=1
    return "".join(out)

n=0
for k in ("arm9","spc"):
    for e in F[k]:
        ko2=fix(e["ko"])
        if ko2!=e["ko"]:
            e["ko"]=ko2; n+=1
print("fixed entries:", n)
json.dump(F, open(os.path.join(OUT,"final.json"),"w",encoding="utf-8"), ensure_ascii=False)
print("wrote final.json")
