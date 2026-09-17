# -*- coding: utf-8 -*-
# v4 素材管线：全屏视频底图（参考 相变临界/哥伦比亚 技法）
# 抽帧 → 满屏裁剪 → 顶部渐变暗区烘焙（信息区不遮素材的解法）→ I8 .bin
import os, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

VIDEO = r"D:\AGI\TraeCode\mp4\gugugaga-penguin.mp4"
WORK = r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\frames-v4"
W, H = 336, 480
SS, DUR, FPS, N = 0.5, 2.0, 10, 20        # 2 秒循环段

os.makedirs(WORK, exist_ok=True)
for f in os.listdir(WORK):
    if f.endswith(".png"):
        os.remove(os.path.join(WORK, f))

# 1) 抽帧：原比例放大到宽 336（282x498 → 336x594），再裁 480 高
#    企鹅主体在原 y≈47-466 → 放大后 y≈56-555，取窗口偏移 57（主体略偏下保留）
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(SS), "-t", str(DUR), "-i", VIDEO,
                "-vf", f"fps={FPS},scale={W}:594:flags=lanczos,crop={W}:{H}:0:57",
                os.path.join(WORK, "f%02d.png")], check=True)

# 2) 顶部渐变暗区烘焙：海军蓝 scrim（alpha 200 → 0，y=0→132）+ 底部轻 vignette
frames = sorted(f for f in os.listdir(WORK) if f.startswith("f") and f.endswith(".png"))
print(f"frames: {len(frames)}")
for f in frames:
    img = Image.open(os.path.join(WORK, f)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    for y in range(H):
        if y < 74:
            a = 235
        elif y < 170:
            a = int(235 * (1 - (y - 74) / 96) ** 1.6)
        elif y > H - 36:
            a = int(90 * ((y - (H - 36)) / 36) ** 1.5)
        else:
            continue
        for x in range(W):
            px[x, y] = (15, 20, 32, a)
    Image.alpha_composite(img, ov).convert("RGB").save(os.path.join(WORK, f))
print("scrim baked")
