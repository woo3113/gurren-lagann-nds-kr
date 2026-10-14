import sys, os, json, collections, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
E=F["spc"]
print("SPC 문자열:", len(E))

# 1) command-marker-like leading chars
LEAD=collections.Counter(e["text"][0] for e in E if e["text"])
odd=[(c,n) for c,n in LEAD.items() if not (0x3040<=ord(c)<=0x30FF or 0x4E00<=ord(c)<=0x9FFF or 0x3000<=ord(c)<=0x303F or 0xFF01<=ord(c)<=0xFF60 or ord(c)<0x80)]
print("일반적이지 않은 첫 글자:", odd[:40])

# 2) strings containing marker-ish symbols
MARK="＠＃＊★☆◆●■□♪｜/\\[]{}<>＝=＋+"
mk=[e for e in E if any(ch in e["text"] for ch in MARK)]
print(f"\n마커성 기호 포함 문자열: {len(mk)}")
for e in mk[:40]:
    print(f"   {e['file']} 0x{e['off']:x} {e['text']!r} -> {e['ko']!r}")

# 3) short strings that look like identifiers (no kana, has ascii/digits)
ident=[e for e in E if re.fullmatch(r'[A-Za-z0-9_%\.\-]+', e["ko"].strip()) ]
print(f"\n출력이 영숫자/기호만인 문자열: {len(ident)}")
for e in ident[:20]:
    print(f"   {e['file']} {e['text']!r} -> {e['ko']!r}")

# 4) strings whose KO is much shorter than the japanese (severe truncation)
short=[e for e in E if len(e["ko"])*2 < len(e["text"]) ]
print(f"\n심하게 축약된 문자열: {len(short)}")
for e in short[:25]:
    print(f"   {e['text']!r} -> {e['ko']!r}")
