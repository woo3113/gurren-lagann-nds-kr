"""Core helpers for Gurren Lagann (NDS) Korean patch."""
import struct

# ---------- Shift-JIS helpers ----------
def is_lead(b):  return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC
def is_trail(b): return (0x40 <= b <= 0x7E) or (0x80 <= b <= 0xFC)

def iter_runs(buf, minjp=2, span=None):
    """Yield (offset, text_bytes) for maximal clean Shift-JIS runs with >=minjp japanese chars."""
    n=len(buf); i=0
    a = 0 if span is None else span[0]; b = n if span is None else span[1]
    i=a
    while i < b-1:
        if is_lead(buf[i]) and is_trail(buf[i+1]):
            j=i; s=bytearray()
            while j < b-1:
                c=buf[j]
                if is_lead(c) and is_trail(buf[j+1]): s+=buf[j:j+2]; j+=2
                else: break
            try: txt=bytes(s).decode("shift_jis")
            except Exception: i=j; continue
            jp=sum(1 for ch in txt if is_jp(ch))
            if jp>=minjp:
                yield (i, bytes(s))
            i=j; continue
        i+=1

def sjis_decode(bs):
    return bs.decode("shift_jis")

def sjis_split(bs):
    """split bytes into list of ints: 1-byte ascii, 2-byte packed"""
    out=[]; i=0
    while i < len(bs):
        b=bs[i]
        if b < 0x80 or b == 0x00:
            out.append(b); i+=1
        elif is_lead(b) and i+1 < len(bs):
            out.append((b<<8)|bs[i+1]); i+=2
        else:
            out.append(b); i+=1
    return out

def valid_sjis(bs):
    """True if the byte string decodes cleanly as Shift-JIS."""
    try:
        bs.decode("shift_jis")
        return True
    except Exception:
        return False

def is_jp(ch):
    o = ord(ch)
    return (0x3040 <= o <= 0x30FF) or (0x4E00 <= o <= 0x9FFF) or (0x3000 <= o <= 0x303F) or (0xFF01 <= o <= 0xFF60)

# ---------- SCRP (.SPC) script text ----------
TEXT_OP = 0x10

def plain_text_bytes(body):
    """True if body is plain text: printable ascii / tab / newline or SJIS chars, no control bytes."""
    for b in body:
        if b >= 0x80:
            continue
        if 0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D):
            continue
        return False
    return True

def iter_spc_text(buf, minlen=3, maxlen=0x600):
    """Yield (op_offset, length, text_bytes) for 0x10 <u16 len> <bytes+00>."""
    n=len(buf); i=0
    while i < n-3:
        if buf[i]==TEXT_OP:
            ln = buf[i+1] | (buf[i+2]<<8)
            if minlen <= ln <= maxlen and i+3+ln <= n:
                seg = bytes(buf[i+3:i+3+ln])
                if seg[-1]==0x00:
                    body = seg[:-1]
                    if body and plain_text_bytes(body) and valid_sjis(body):
                        if any(b>=0x80 for b in body):
                            yield (i, ln, body)
                            i += 3+ln
                            continue
        i += 1

# ---------- ARM9 string table ----------
def iter_arm9_strings(buf, minjp=2):
    """Yield (offset, total_len_incl_null, text_bytes) for null-terminated SJIS strings
    that start right after a 0x00 (pool style) and contain >=minjp japanese chars."""
    n=len(buf); i=0
    while i < n-1:
        if buf[i]!=0x00 and (i==0 or buf[i-1]==0x00):
            # try parse a string
            j=i; body=bytearray()
            ok=True
            while j < n and buf[j]!=0x00:
                b=buf[j]
                if b < 0x80:
                    if 0x09<=b<=0x7E or b in (0x0A,0x0D):
                        body.append(b); j+=1
                    else:
                        ok=False; break
                elif is_lead(b) and j+1<n and is_trail(buf[j+1]):
                    body.append(b); body.append(buf[j+1]); j+=2
                else:
                    ok=False; break
            if ok and j<n and buf[j]==0x00 and len(body)>=4:
                try:
                    txt = bytes(body).decode("shift_jis")
                except Exception:
                    txt=None
                if txt is not None:
                    jp = sum(1 for ch in txt if is_jp(ch))
                    if jp>=minjp:
                        yield (i, j-i+1, bytes(body))
            i = j+1
            continue
        i += 1
