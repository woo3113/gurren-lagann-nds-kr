import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
E=F["arm9"]+F["spc"]

# 1) JA contains fullwidth colon but KO lost it
lost=[e for e in E if "：" in e["text"] and "：" not in e["ko"]]
print("JA에 '：'가 있는데 KO에 없는 항목:", len(lost))
for e in lost[:30]:
    print(f"   0x{e['off']:x} {e['text']!r} -> {e['ko']!r}")

# 2) strings that consist of number + colon pattern
pat=re.compile(r'^\s*[%0-9m]{0,8}[：:]')
num=[e for e in E if pat.match(e["text"])]
print(f"\n숫자/포맷 + 콜론으로 시작하는 항목: {len(num)}")
for e in num[:25]:
    print(f"   0x{e['off']:x} {e['text']!r} -> {e['ko']!r}")

# 3) JA fully-width chars vs KO ascii where it matters
conv=[e for e in E if any(ch in e["text"] for ch in "％＃＋－／") ]
print(f"\n전각 기호 포함 항목: {len(conv)}")
for e in conv[:15]:
    print(f"   0x{e['off']:x} {e['text']!r} -> {e['ko']!r}")
