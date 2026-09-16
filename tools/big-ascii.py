# -*- coding: utf-8 -*-
# 高分辨率 ASCII 转储（用于辨认屏幕内容结构）
import sys, io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

img = Image.open(sys.argv[1]).convert("RGB")
w, h = img.size
COLS, ROWS = 88, 44
g = img.convert("L").resize((COLS, ROWS), Image.BOX)
chars = " .:-=+*#%@"
for y in range(ROWS):
    print("".join(chars[min(9, g.getpixel((x, y)) * 10 // 256)] for x in range(COLS)))
