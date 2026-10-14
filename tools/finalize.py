import sys, os, json, csv
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))

# translation table for human revisers
with open(os.path.join(OUT,"translation_table.csv"),"w",encoding="utf-8-sig",newline="") as fh:
    w=csv.writer(fh)
    w.writerow(["type","file","offset","japanese","korean_mt","fit"])
    for e in F["arm9"]:
        w.writerow(["arm9","", f'{e["off"]:06x}', e["text"], e["ko"], e["how"]])
    for e in F["spc"]:
        w.writerow(["spc", e["file"], f'{e["off"]:06x}', e["text"], e["ko"], e["how"]])
print("wrote translation_table.csv")

n=len(F["arm9"])+len(F["spc"])
ok=sum(1 for e in F["arm9"]+F["spc"] if e["how"]=="ok")
print(f"entries: {n}  direct-fit: {ok} ({ok/n*100:.1f}%)  shortened: {n-ok}")
