import sys, os
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont

syll = "가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐기니디리미비시이지치키티피히시몬카미나요코니아글렌라간"
fonts = [
    (r"C:\Windows\Fonts\gulim.ttc", 0),
    (r"C:\Windows\Fonts\gulim.ttc", 1),
    (r"C:\Windows\Fonts\batang.ttc", 0),
    (r"C:\Windows\Fonts\malgun.ttf", 0),
    (r"C:\Windows\Fonts\NanumGothic.ttf", 0),
]
sizes = [10, 11, 12]
rows = []
for path,idx in fonts:
    for sz in sizes:
        try:
            f = ImageFont.truetype(path, sz, index=idx)
        except Exception as ex:
            print("fail", path, idx, sz, ex); continue
        n = len(syll)
        scale = 5
        img = Image.new("L", (n*12*scale, 13*scale), 255)
        for i,ch in enumerate(syll):
            tile = Image.new("L", (12,13), 255)
            d = ImageDraw.Draw(tile)
            d.text((0,0), ch, font=f, fill=0)
            # binarize + place in 11x11 cell
            px = tile.load()
            for y in range(11):
                for x in range(11):
                    if px[x,y] < 128:
                        for dy in range(scale):
                            for dx in range(scale):
                                img.putpixel((i*12*scale+x*scale+dx, y*scale+dy), 0)
        img.save(rf"D:\20_게임\_한글패치\그랜라간\work\fonttest_{os.path.basename(path)}_{idx}_{sz}.png")
        print("saved", path, idx, sz)
