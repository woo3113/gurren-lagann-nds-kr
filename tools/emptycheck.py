import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
E=F["spc"]+F["arm9"]
empty=[e for e in E if not e["ko"].strip()]
print("빈 문자열로 번역된 항목:", len(empty))
for e in empty[:20]:
    print(f"   {e.get('file','arm9')} {e['text']!r} -> {e['ko']!r} (len={e['len']})")

punct=[e for e in E if e["ko"].strip() and not re.search(r'[가-힣A-Za-z0-9]', e["ko"])]
print(f"\n한글/영숫자 없이 기호만 남은 항목: {len(punct)}")
for e in punct[:25]:
    print(f"   {e['text']!r} -> {e['ko']!r}")

# ko with leading/trailing spaces or only spaces+symbols
ws=[e for e in E if e["ko"]!=e["ko"].strip()]
print(f"\n앞뒤 공백 있는 항목: {len(ws)}")

# \n 이 KO에 남아있는데 원문과 개수가 다른 경우
nl=[e for e in E if e["ko"].count("\n") != e["text"].count("\n")]
print(f"\n줄바꿈 개수가 원문과 다른 항목: {len(nl)}")
for e in nl[:15]:
    print(f"   {e['text']!r} -> {e['ko']!r}")
