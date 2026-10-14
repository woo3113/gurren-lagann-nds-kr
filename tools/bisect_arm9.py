"""Binary-search which ARM9 string patch causes the hang, using the melonDS auto-test harness."""
import sys, os, json, subprocess, re, time
sys.path.insert(0, r"D:\20_게임\_한글패치\그랜라간\tools")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\20_게임\_한글패치\그랜라간"
OUT = os.path.join(ROOT, "out")
EMU_PS = os.path.join(ROOT, "tools", "launch_test.ps1")
ASCII = r"C:\Users\woo31\AppData\Local\Temp\opencode\roms"
BROMA = os.path.join(ASCII, "kr_b.nds")
JAPAN = os.path.join(ROOT, "work", "Tengen Toppa Gurren Lagann (Japan).nds")

F = json.load(open(os.path.join(OUT, "final.json"), encoding="utf-8"))
CM = json.load(open(os.path.join(OUT, "charmap.json"), encoding="utf-8"))
km = {ch: c for ch, c in CM["keepmap"].items()}
nm = {it["ch"]: it["code"] for it in CM["newchars"]}
orig = open(JAPAN, "rb").read()
ARM9_OFF = 0x4000

def encode(s):
    o = bytearray()
    for ch in s:
        c = ord(ch)
        if c < 0x80: o.append(c)
        else:
            v = km.get(ch, nm.get(ch)); o.append(v >> 8); o.append(v & 0xFF)
    return bytes(o)

ARM = F["arm9"]
def build(idxs, path):
    r = bytearray(orig)
    for i in idxs:
        e = ARM[i]; off = ARM9_OFF + e["off"]; space = e["len"] + e["pad"]
        d = encode(e["ko"]) + b"\x00"
        r[off:off+len(d)] = d
        r[off+len(d):off+space] = b"\x00" * (space - len(d))
    open(path, "wb").write(r)

def run_test(path, samples=12, interval=4):
    p = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", EMU_PS,
                        "-Rom", path, "-Samples", str(samples), "-Interval", str(interval)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    ws = []
    for line in p.stdout.splitlines():
        m = re.search(r"white=([0-9.]+)", line)
        if m: ws.append(float(m.group(1)))
    if len(ws) < 8: return None, ws
    return ("HANG" if all(w > 0.5 for w in ws[-3:]) else "OK"), ws

def classify(idxs):
    if not idxs: return "OK", []
    build(idxs, BROMA)
    for attempt in range(3):
        verdict, ws = run_test(BROMA)
        if verdict: return verdict, ws
        print("   inconclusive, retry", flush=True)
    return "UNKNOWN", ws

print("=== sanity: original (no arm9 patch) ===", flush=True)
build([], BROMA)
v, ws = run_test(BROMA)
print("   original ->", v, ws, flush=True)

cur = list(range(len(ARM)))
print(f"=== bisect over {len(cur)} arm9 strings ===", flush=True)
step = 0
while len(cur) > 1:
    step += 1
    half = len(cur) // 2
    A, B = cur[:half], cur[half:]
    print(f"--- step {step}: testing {len(A)} of {len(cur)} (first half) ---", flush=True)
    va, wa = classify(A)
    print(f"    half A ({len(A)}) -> {va} {wa}", flush=True)
    if va == "HANG":
        cur = A
    else:
        print(f"--- step {step}: testing {len(B)} (second half) ---", flush=True)
        vb, wb = classify(B)
        print(f"    half B ({len(B)}) -> {vb} {wb}", flush=True)
        if vb == "HANG": cur = B
        else:
            print("!!! neither half hangs alone -> multiple causes, stopping"); break
    print(f"    narrowed to {len(cur)}", flush=True)

print("=== result ===", flush=True)
for i in cur:
    e = ARM[i]
    print(f"  idx={i} off=0x{e['off']:06x} len={e['len']} {e['text']!r} -> {e['ko']!r}", flush=True)
