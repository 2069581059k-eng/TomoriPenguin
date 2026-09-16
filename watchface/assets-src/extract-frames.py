# -*- coding: utf-8 -*-
# 抽帧管线：从 gugugaga-penguin.mp4 截取循环段 -> 缩放 -> 自动裁剪含企鹅的 240x320 卡片段 -> 校验
import glob, os, re, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

VIDEO = r"D:\AGI\TraeCode\mp4\gugugaga-penguin.mp4"
WORK = r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\frames"
CARD_W, CARD_H = 240, 320
SS = 1.0          # 循环段起点（秒）
DUR = 4 / 3.0     # 16 帧 @ 12fps = 1.333s
FPS = 12
N = 16

os.makedirs(WORK, exist_ok=True)

# 1) 以 12fps 抽出整段（先保持原始 282x498，便于自动定位裁剪窗口）
raw = os.path.join(WORK, "raw")
os.makedirs(raw, exist_ok=True)
for f in glob.glob(os.path.join(raw, "*.png")):
    os.remove(f)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(SS), "-t", str(DUR),
                "-i", VIDEO, "-vf", f"fps={FPS}", os.path.join(raw, "r%02d.png")], check=True)

# 2) 帧间差分联合 bbox（在 56x32 网格上定位运动主体）
raws = sorted(glob.glob(os.path.join(raw, "r*.png")))
prev = None
minx, miny, maxx, maxy = 56, 32, 0, 0
for p in raws:
    img = Image.open(p).convert("L").resize((56, 32))
    if prev is not None:
        for y in range(32):
            for x in range(56):
                if abs(img.getpixel((x, y)) - prev.getpixel((x, y))) > 24:
                    minx, miny = min(minx, x), min(miny, y)
                    maxx, maxy = max(maxx, x), max(maxy, y)
    prev = img
print(f"motion bbox (56x32 grid): x {minx}-{maxx}, y {miny}-{maxy}")

# 3) 映射到 282x498 原始坐标 -> 缩放到 240 宽 -> 计算裁剪窗口
sx, sy = 282 / 56, 498 / 32
bx0, by0, bx1, by1 = minx * sx, miny * sy, (maxx + 1) * sx, (maxy + 1) * sy
scale = CARD_W / 282.0
scaled_h = round(498 * scale)
bx0, bx1 = bx0 * scale, bx1 * scale
by0, by1 = by0 * scale, by1 * scale
# 裁剪窗口（高 CARD_H）需完整包含运动区，垂直居中于运动区并夹在合法范围
cy = (by0 + by1) / 2
off = int(round(cy - CARD_H / 2))
off = max(0, min(scaled_h - CARD_H, off))
print(f"scaled: {CARD_W}x{scaled_h}, motion y {by0:.0f}-{by1:.0f}, crop y_off={off}")

# 4) 生成最终卡片帧
for f in glob.glob(os.path.join(WORK, "f*.png")):
    os.remove(f)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(SS), "-t", str(DUR),
                "-i", VIDEO, "-vf",
                f"fps={FPS},scale={CARD_W}:{scaled_h}:flags=lanczos,crop={CARD_W}:{CARD_H}:0:{off}",
                os.path.join(WORK, "f%02d.png")], check=True)

frames = sorted(glob.glob(os.path.join(WORK, "f*.png")))
print(f"generated {len(frames)} frames:")
for p in frames:
    im = Image.open(p)
    # 输出每帧亮度 ASCII 摘要（8x10 粗网格）确认主体在画面内
    g = im.convert("L").resize((10, 8))
    chars = " .:-=+*#%@"
    amp = ["".join(chars[min(9, g.getpixel((x, y)) * 10 // 256)] for x in range(10)) for y in range(8)]
    bright = sum(1 for y in range(8) for x in range(10) if g.getpixel((x, y)) > 170)
    print(f"  {os.path.basename(p)} {im.size} bright_cells={bright} " + "|".join(amp[i] for i in (2, 4)))
