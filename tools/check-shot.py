# -*- coding: utf-8 -*-
# 截图内容分析：与设计稿比对
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

img = Image.open(sys.argv[1]).convert("RGB")
w, h = img.size
print(f"{sys.argv[1]}: {w}x{h}")

print("— 色块网格 8x12 —")
for gy in range(12):
    row = []
    for gx in range(8):
        box = (gx*w//8, gy*h//12, (gx+1)*w//8, (gy+1)*h//12)
        r, g, b = img.crop(box).resize((1, 1)).getpixel((0, 0))
        row.append(f"{r:02X}{g:02X}{b:02X}")
    print(" ".join(row))

print("— 亮度 ASCII 44x20 —")
g = img.convert("L").resize((44, 20))
chars = " .:-=+*#%@"
for y in range(20):
    print("".join(chars[min(9, g.getpixel((x, y)) * 10 // 256)] for x in range(44)))

# 采样关键点
pts = {
    "bg左上(10,10)": (10, 10), "bg右下(326,470)": (326, 470),
    "时间区(168,70)": (168, 70), "日期区(30,25)": (30, 25),
    "卡内(168,280)": (168, 280), "相纸边(50,120)": (50, 120),
    "字幕区(168,455)": (168, 455),
}
print("— 关键点 —")
for k, (x, y) in pts.items():
    print(f"{k}: #{img.getpixel((x, y))[0]:02X}{img.getpixel((x, y))[1]:02X}{img.getpixel((x, y))[2]:02X}")
