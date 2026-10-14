"""Nitro NFTR (NFT) font parser/patcher for "Tengen Toppa Gurren Lagann" (NOBORI engine).

Font file layout (verified against GL_12FNT.NFT):
  RTFN header (0x10)
  blocks...  FNIF / PLGC(glyph bitmaps) / HDWC(metrics) / PAMC(cmap)*
Each PAMC (cmap) block:
   magic 'PAMC'(4) size(4) first(u16) last(u16) method(u32)
   method 0 : sequential -> glyph = base + (code - first);  base = u32 @ block+0x14   (size==0x18)
   method 1 : lookup table of u16 @ block+0x14 ; 0xffff = undefined            (size>0x18)
"""
import struct

class Nft:
    def __init__(self, data, base=0):
        self.d = data
        self.base = base
        self.parse()

    def parse(self):
        d = self.d; b = self.base
        assert d[b:b+4] == b"RTFN"
        self.size = struct.unpack_from("<I", d, b+8)[0]
        hsz = struct.unpack_from("<H", d, b+0xc)[0]
        nblk = struct.unpack_from("<H", d, b+0xe)[0]
        self.blocks = []
        off = b + hsz
        for i in range(nblk):
            magic = d[off:off+4]
            sz = struct.unpack_from("<I", d, off+4)[0]
            self.blocks.append({"off": off, "magic": magic, "size": sz})
            if sz == 0:
                break
            off += sz
        self.end = off
        self.fnif = [x for x in self.blocks if x["magic"] == b"FNIF"]
        self.cglp = [x for x in self.blocks if x["magic"] == b"PLGC"]
        self.hdwc = [x for x in self.blocks if x["magic"] == b"HDWC"]
        self.cmap = [x for x in self.blocks if x["magic"] == b"PAMC"]

    # ---- glyph bitmaps ----
    def glyph_info(self):
        """returns (glyph_data_off, glyph_w, glyph_h, bytes_per_glyph, nglyphs)"""
        c = self.cglp[0]
        o = c["off"]; d = self.d
        # tileW/H bytes at +0x34? -> use fields: +8 tileW(u8) +9 tileH(u8) +0xa bpg(u16)
        tileW = d[o+8]; tileH = d[o+9]
        bpg = struct.unpack_from("<H", d, o+0xa)[0]
        data_off = o + 0x10           # header size (verified)
        n = (c["size"] - 0x10) // bpg
        return data_off, tileW, tileH, bpg, n

    def glyph(self, idx):
        data_off, w, h, bpg, n = self.glyph_info()
        if idx >= n: return None
        return self.d[data_off+idx*bpg: data_off+(idx+1)*bpg]

    def set_glyph(self, idx, bits):
        data_off, w, h, bpg, n = self.glyph_info()
        assert len(bits) == bpg and idx < n
        self.d[data_off+idx*bpg: data_off+(idx+1)*bpg] = bits

    def render_glyph(self, idx, gw=None, gh=None, msb=True):
        data_off, w, h, bpg, n = self.glyph_info()
        gw = gw or w; gh = gh or h
        buf = self.d[data_off+idx*bpg: data_off+(idx+1)*bpg]
        rows = []
        for y in range(gh):
            row = []
            for x in range(gw):
                bit = y*gw+x
                byte = buf[bit//8]
                v = byte & ((0x80 >> (bit % 8)) if msb else (1 << (bit % 8)))
                row.append(1 if v else 0)
            rows.append(row)
        return rows

    # ---- cmap ----
    def build_cmap(self):
        if getattr(self, "_cmap", None) is not None:
            return self._cmap
        d = self.d
        m = {}
        for c in self.cmap:
            o = c["off"]; sz = c["size"]
            first, last = struct.unpack_from("<HH", d, o+8)
            method = struct.unpack_from("<I", d, o+0xc)[0]
            if sz <= 0x18:                       # method 0 (sequential)
                base = struct.unpack_from("<I", d, o+0x14)[0]
                for code in range(first, last+1):
                    g = base + (code - first)
                    if g < 0xffff:
                        m[code] = g
            else:                                # method 1 (table)
                n = (sz - 0x14)//2
                for i in range(n):
                    g = struct.unpack_from("<H", d, o+0x14+i*2)[0]
                    if g != 0xffff:
                        m[first+i] = g
        self._cmap = m
        return m

    def glyph_of_code(self, code):
        return self.build_cmap().get(code)

    # ---- HDWC metrics ----
    def hdwc_info(self):
        c = self.hdwc[0]
        return c["off"], c["size"]

    def hdwc_record(self, idx):
        o, sz = self.hdwc_info()
        return tuple(self.d[o+0xe+idx*3: o+0xe+idx*3+3])

    def set_hdwc(self, idx, rec):
        o, sz = self.hdwc_info()
        assert o+0xe+idx*3+3 <= o+sz
        self.d[o+0xe+idx*3: o+0xe+idx*3+3] = bytes(rec)


def fnt_to_bytes(f):
    """Return a bytes-like containing all blocks (the whole NFT file)."""
    return f.d[:f.end]
