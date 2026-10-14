import json, os, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
entries=F["arm9"]+F["spc"]

JP=re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')
hangul=re.compile(r'[\uac00-\ud7a3]')

# 1. naming check
n_geul=sum(e["ko"].count("그렌라간") for e in entries)
n_grae=sum(e["ko"].count("그랜라간") for e in entries)
print(f'"그렌라간"(공식) 등장: {n_geul}   "그랜라간" 등장: {n_grae}')

# 2. entries with leftover japanese
leftover=[e for e in entries if JP.search(e["ko"])]
print(f"\n일본어가 남아있는 항목: {len(leftover)} / {len(entries)}")
c=collections.Counter(ch for e in leftover for ch in e["ko"] if JP.match(ch))
print("  남은 문자 상위:", c.most_common(20))

# 3. shortened entries
short=[e for e in entries if e["how"] in ("fit","tight")]
print(f"\n축약된 항목: {len(short)} / {len(entries)}")
ws=[e for e in entries if e["how"]=="ws"]
print(f"문장단위 재번역 사용: {len(ws)}")

# 4. write review files
with open(os.path.join(OUT,"review_leftover_japanese.txt"),"w",encoding="utf-8") as fh:
    fh.write(f"# 일본어가 남은 항목 {len(leftover)}건\n")
    for e in leftover:
        fh.write(f'{e.get("file","arm9")}\t{e["off"]}\t{e["text"]}\t{e["ko"]}\n')
with open(os.path.join(OUT,"review_shortened.txt"),"w",encoding="utf-8") as fh:
    fh.write(f"# 길이 때문에 축약된 항목 {len(short)}건\n")
    for e in short:
        fh.write(f'{e.get("file","arm9")}\t{e["off"]}\t{e["text"]}\t{e["ko"]}\n')
print("\nwrote out/review_leftover_japanese.txt, out/review_shortened.txt")

# unique shortened
uniq=len(set(e["text"] for e in short))
print(f"축약된 고유 문장 수: {uniq}")
