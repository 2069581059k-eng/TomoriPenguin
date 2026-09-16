# -*- coding: utf-8 -*-
# 控制台文字放大读取：裁剪 + 3x 放大 + 二值化 ASCII
import sys, io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

img = Image.open(sys.argv[1]).convert("L")
w, h = img.size
# 控制台文本区：约 x 78-250, y 20-440
region = img.crop((74, 18, 258, 444))
rw, rh = region.size
# 3x 放大
big = region.resize((rw * 3, rh * 3), Image.LANCZOS)
bw, bh = big.size
px = big.load()
vals = sorted(px[x, y] for y in range(0, bh, 4) for x in range(0, bw, 4))
thr = (vals[len(vals) // 10] + vals[len(vals) * 9 // 10]) // 2
# 每个字符格约 4.2px 高（14px 字体）放大后 ~12px；按行扫描输出
step = 3
for y in range(0, bh, step):
    line = ""
    for x in range(0, bw, step):
        # 3x3 采样
        v = max(px[x + dx, y + dy] for dx in (0, 1, 2) for dy in (0, 1, 2) if x + dx < bw and y + dy < bh)
        line += "#" if v > thr else " "
    print(line)
