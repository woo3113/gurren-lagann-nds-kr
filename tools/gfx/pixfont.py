import sys,os,json
sys.path.insert(0,os.path.expanduser('~/mnt/그랜라간/tools'))
from nft import Nft
ROM=os.path.expanduser('~/mnt/그랜라간/out/Tengen Toppa Gurren Lagann (Korea) v3.nds')
d=open(ROM,'rb').read()
F=Nft(bytearray(d[0x153680:0x153680+0x888C0]),0); CM=F.build_cmap()
cm=json.load(open(os.path.expanduser('~/mnt/그랜라간/out/charmap.json')))
MAP={e['ch']:e['code'] for e in cm['newchars']}; MAP.update(cm['keepmap'])
def code(ch):
    if ch in MAP: return MAP[ch]
    if ord(ch)<128: return ord(ch)
    return ch.encode('shift_jis')[0]<<8|ch.encode('shift_jis')[1]
def glyph(ch):
    g=CM.get(code(ch))
    if g is None and 33<=ord(ch)<127:
        g=CM.get(code(chr(ord(ch)+0xfee0)))
    if g is None: raise KeyError(ch)
    return F.render_glyph(g,11,11)
def text(s,space=0,adv=12,sp=6):
    px=set(); x=0
    for ch in s:
        if ch==' ': x+=sp; continue
        rows=glyph(ch)
        for y,r in enumerate(rows):
            for xx,v in enumerate(r):
                if v: px.add((x+xx,y))
        x+=adv+space
    return x-space,11,px
if __name__=='__main__':
    w,h,px=text('통신이 끊어졌습니다.A 버튼'); print(w,h)
    for y in range(h): print(''.join('#' if (x,y) in px else '.' for x in range(w)))
