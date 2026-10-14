import sys, os, json, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT=r"D:\20_게임\_한글패치\그랜라간"
S=json.load(open(os.path.join(ROOT,"out","strings.json"),encoding="utf-8"))
ctl=collections.Counter()
for e in S["spc"]:
    for ch in e["text"]:
        if ord(ch)<0x20: ctl[hex(ord(ch))]+=1
for e in S["arm9"]:
    for ch in e["text"]:
        if ord(ch)<0x20: ctl[hex(ord(ch))]+=1
print("control chars in extracted text:", ctl)
lines=set()
nlines=0
for e in S["spc"]+S["arm9"]:
    for ln in e["text"].split("\n"):
        nlines+=1; lines.add(ln)
print("total lines:", nlines, "unique lines:", len(lines))
chars=sum(len(l) for l in lines)
print("unique line chars:", chars)
# how many lines are pure punct/space
import re
pure=sum(1 for l in lines if not re.search(r'[ぁ-んァ-ヶ一-龠]', l))
print("lines with no kana/kanji:", pure)
