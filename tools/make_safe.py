"""Rebuild the full patch but keep a given set of ARM9 offsets in Japanese; then auto-test."""
import sys, os, json, subprocess, re
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
from nft import Nft
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\20_게임\_한글패치\그랜라간"; OUT = os.path.join(ROOT, "out")
ASCII = r"C:\Users\woo31\AppData\Local\Temp\opencode\roms"
EMU_PS = os.path.join(ROOT, "tools", "launch_test.ps1")
JAPAN = os.path.join(ROOT, "work", "Tengen Toppa Gurren Lagann (Japan).nds")
FNT = os.path.join(ROOT, "work", "extract", "ETC.NFP", "GL_12FNT.NFT")
FNT_OFF = 0x153680; ARM9_OFF = 0x4000; SPC_NFP_OFF = 0x597be00

F = json.load(open(os.path.join(OUT, "final.json"), encoding="utf-8"))
CM = json.load(open(os.path.join(OUT, "charmap.json"), encoding="utf-8"))
km = {ch: c for ch, c in CM["keepmap"].items()}
nm = {it["ch"]: it["code"] for it in CM["newchars"]}
orig = open(JAPAN, "rb").read()

def encode(s):
    o = bytearray()
    for ch in s:
        c = ord(ch)
        if c < 0x80: o.append(c)
        else:
            v = km.get(ch, nm.get(ch)); o.append(v >> 8); o.append(v & 0xFF)
    return bytes(o)

def build(keep_jp_offsets, path):
    r = bytearray(orig)
    nf = bytearray(open(FNT, "rb").read())
    f = Nft(nf, 0); cmap = f.build_cmap()
    font = ImageFont.truetype(r"C:\Windows\Fonts\gulim.ttc", 11, index=0)
    def rb(ch):
        t = Image.new("L",(16,16),255); ImageDraw.Draw(t).text((0,0),ch,font=font,fill=0)
        px=t.load(); return [[1 if px[x,y]<128 else 0 for x in range(11)] for y in range(11)]
    def pack(bits):
        b = bytearray(16)
        for y in range(11):
            for x in range(11):
                if bits[y][x]: b[(y*11+x)//8] |= 0x80 >> ((y*11+x) % 8)
        return bytes(b)
    for it in CM["newchars"]:
        g = cmap[it["code"]]; f.set_glyph(g, pack(rb(it["ch"]))); f.set_hdwc(g,(11,12,1))
    r[FNT_OFF:FNT_OFF+len(nf)] = nf
    for e in F["arm9"]:
        if e["off"] in keep_jp_offsets: continue
        off = ARM9_OFF + e["off"]; space = e["len"] + e["pad"]
        d = encode(e["ko"]) + b"\x00"
        r[off:off+len(d)] = d; r[off+len(d):off+space] = b"\x00" * (space - len(d))
    cnt = int.from_bytes(r[SPC_NFP_OFF+0x34:SPC_NFP_OFF+0x38], "little")
    hdr = int.from_bytes(r[SPC_NFP_OFF+0x38:SPC_NFP_OFF+0x3c], "little")
    idx = {}
    for i in range(cnt):
        o = SPC_NFP_OFF + hdr + i*0x18
        nmx = bytes(r[o:o+16]).split(b"\x00")[0].decode("ascii","replace")
        off = int.from_bytes(r[o+16:o+20], "little")
        idx[nmx] = off
    for e in F["spc"]:
        off = SPC_NFP_OFF + idx[e["file"]] + e["off"]; space = e["len"]
        d = encode(e["ko"]) + b"\x00"
        r[off:off+len(d)] = d; r[off+len(d):off+space] = b"\x00" * (space - len(d))
    open(path, "wb").write(r)

def test(path, samples=12, interval=4):
    p = subprocess.run(["powershell","-ExecutionPolicy","Bypass","-File",EMU_PS,"-Rom",path,
                        "-Samples",str(samples),"-Interval",str(interval)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    ws = [float(m.group(1)) for m in re.finditer(r"white=([0-9.]+)", p.stdout)]
    if len(ws) < 8: return None
    return "HANG" if all(w > 0.5 for w in ws[-3:]) else "OK"

if __name__ == "__main__":
    keep = {0x11dbac}
    path = os.path.join(ASCII, "safe.nds")
    build(keep, path)
    print("built safe.nds with kept-japanese:", [hex(x) for x in keep])
    print("verdict:", test(path))
