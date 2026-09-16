# -*- coding: utf-8 -*-
# 帧内容分析：背景色 / 色块网格 / 亮度ASCII / 帧间差分运动区域
import glob, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

files = sorted(glob.glob(r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\dense\f*.png"),
               key=lambda p: int(re.search(r"f(\d+)", p).group(1)))
if not files:
    files = sorted(glob.glob(r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\full-*.png"))
print(f"frames: {len(files)}")

def grid_colors(img, cw, ch):
    w, h = img.size
    rows = []
    for gy in range(ch):
        row = []
        for gx in range(cw):
            box = (gx*w//cw, gy*h//ch, (gx+1)*w//cw, (gy+1)*h//ch)
            r, g, b = img.crop(box).resize((1, 1)).getpixel((0, 0))[:3]
            row.append(f"{r:02X}{g:02X}{b:02X}")
        rows.append(" ".join(row))
    return rows

def ascii_lum(img, cw, ch):
    g = img.convert("L").resize((cw, ch))
    chars = " .:-=+*#%@"
    out = []
    for y in range(ch):
        out.append("".join(chars[min(9, g.getpixel((x, y)) * 10 // 256)] for x in range(cw)))
    return out

prev = None
for i, f in enumerate(files):
    img = Image.open(f).convert("RGB")
    w, h = img.size
    corners = [img.getpixel(p) for p in [(2,2),(w-3,2),(2,h-3),(w-3,h-3),(w//2,2),(w//2,h-3)]]
    cs = " ".join(f"{r:02X}{g:02X}{b:02X}" for r,g,b in corners)
    print(f"\n=== [{i}] {f.split(chr(92))[-1]} {w}x{h} corners: {cs}")
    if i in (0, len(files)//2) or (len(files) <= 6):
        for r in grid_colors(img, 8, 12): print("  C", r)
        for r in ascii_lum(img, 44, 20): print("  A", r)
    if prev is not None:
        pg = prev.convert("L").resize((56, 32))
        cg = img.convert("L").resize((56, 32))
        diff = [abs(cg.getpixel((x,y)) - pg.getpixel((x,y))) for y in range(32) for x in range(56)]
        changed = [d for d in diff if d > 24]
        pct = 100*len(changed)/len(diff)
        xs = [i%56 for i,d in enumerate(diff) if d>24]; ys=[i//56 for i,d in enumerate(diff) if d>24]
        bbox = (min(xs),min(ys),max(xs),max(ys)) if xs else None
        amap = []
        for y in range(32):
            amap.append("".join("#" if diff[y*56+x] > 24 else "." for x in range(56)))
        print(f"  DIFF pct={pct:.1f}% bbox(56x32)={bbox}")
        for r in amap[::2]: print("  D", r)
    prev = img
