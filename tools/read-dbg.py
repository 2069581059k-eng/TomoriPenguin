# -*- coding: utf-8 -*-
# 放大读取截图底部调试条带
import sys, io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

img = Image.open(sys.argv[1]).convert("L")
w, h = img.size
box = (0, h - 30, w, h)
strip = img.crop(box).resize((w * 2, 60), Image.LANCZOS)
# 自适应阈值二值化
px = strip.load()
vals = [px[x, y] for y in range(60) for x in range(w * 2)]
thr = (max(vals) + min(vals)) // 2
chars = " .:-=+*#%@"
for y in range(0, 60, 2):
    line = ""
    for x in range(0, w * 2, 2):
        v = px[x, y]
        line += "#" if v > thr else " "
    print(line)
