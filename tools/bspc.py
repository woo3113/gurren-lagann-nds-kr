import json,sys,struct,os
R=os.path.expanduser("~/mnt/그랜라간")
F=json.load(open(R+"/out/final.json",encoding="utf-8")); CM=json.load(open(R+"/out/charmap.json",encoding="utf-8"))
km=CM["keepmap"]; nm={i["ch"]:i["code"] for i in CM["newchars"]}
orig=open(os.path.expanduser("~/emu/orig.nds"),"rb").read()
SPC=0x597be00
def idx():
    cnt=struct.unpack_from("<I",orig,SPC+0x34)[0]; hdr=struct.unpack_from("<I",orig,SPC+0x38)[0]; d={}
    for i in range(cnt):
        o=SPC+hdr+i*0x18; n=orig[o:o+16].split(b"\0")[0].decode(); d[n]=struct.unpack_from("<II",orig,o+16)
    return d
def code(ch):
    o=ord(ch)
    if o<0x80: return bytes([o])
    v=km.get(ch,nm.get(ch)); return bytes([v>>8,v&255])
def fw(ch):
    if ch==' ': return b'\x81\x40'
    o=ord(ch)
    if 0x21<=o<=0x7e:
        try: return chr(o+0xFEE0).encode('cp932')
        except: return bytes([o])
    return code(ch)
def build(path, mode, filt=None):
    """mode: 'raw' (as before) | 'fw' (fullwidth for strings whose original has no ASCII)"""
    r=bytearray(orig); ix=idx(); n=0
    for e in F["spc"]:
        if filt and not filt(e): continue
        foff,_=ix[e["file"]]; off=SPC+foff+e["off"]; space=e["len"]
        ko=e["ko"]; jp_ascii=any(ord(c)<0x80 for c in e["text"])
        if mode=='fw' and not jp_ascii:
            d=b''.join(fw(c) for c in ko)
            while len(d)+1>space and ' ' in ko:   # drop spaces from the end until fits
                i=ko.rindex(' '); ko=ko[:i]+ko[i+1:]; d=b''.join(fw(c) for c in ko)
        else:
            d=b''.join(code(c) for c in ko)
        d+=b"\0"
        if len(d)>space: d=d[:space-1]; d=d[:len(d)-(len(d)%2)] if mode=='fw' else d; d+=b"\0"
        r[off:off+space]=d+b"\0"*(space-len(d)); n+=1
    open(path,"wb").write(r); return n
if __name__=="__main__":
    print(build(sys.argv[1],sys.argv[2]))
