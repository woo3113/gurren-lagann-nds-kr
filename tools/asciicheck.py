import sys, os, json, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"; OUT=os.path.join(ROOT,"out")
F=json.load(open(os.path.join(OUT,"final.json"),encoding="utf-8"))
E=F["arm9"]+F["spc"]
ja_ascii=collections.Counter(); ko_ascii=collections.Counter()
for e in E:
    for ch in e["text"]:
        if ord(ch)<0x80: ja_ascii[ch]+=1
    for ch in e["ko"]:
        if ord(ch)<0x80: ko_ascii[ch]+=1
new=sorted(set(ko_ascii)-set(ja_ascii))
print("KO에만 등장하는 ASCII 문자:", [(repr(c), ko_ascii[c]) for c in new])
# halfwidth katakana in output?
hw=sum(1 for e in E for ch in e["ko"] if 0xFF61<=ord(ch)<=0xFF9F)
print("출력 내 반각 카타카나 수:", hw)
# control chars other than \n \t
ctl=collections.Counter(ch for e in E for ch in e["ko"] if ord(ch)<0x20 and ch not in "\n\t")
print("제어문자:", ctl)
# strings whose ko has 0x5c backslash
bs=[e for e in E if "\\" in e["ko"]]
print("백슬래시 포함:", len(bs), [ (e['text'],e['ko']) for e in bs[:5] ])
