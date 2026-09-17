# -*- coding: utf-8 -*-
# 原生表盘素材生成：时钟数字/日期数字/星期/汉字/电量（延续 v4 清冷夜色 + 顶部暗区设计）
# 输出: watchface/native/images/
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> watchface/
OUT = os.path.join(ROOT, "native", "images")
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "C:\\Windows\\Fonts\\msyhbd.ttc"
FONT_REG = "C:\\Windows\\Fonts\\msyh.ttc"

# v4 配色
C_INK = (234, 240, 247, 255)      # 大时间 近白
C_DIM = (201, 214, 228, 255)      # 日期 浅蓝灰
C_ACCENT = (142, 212, 239, 255)    # 电量 浅青

def render_text(text, font, color, canvas_w, canvas_h, glow=True, glow_alpha=110):
    """居中渲染文字 + 柔和发光（夜色氛围）"""
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (canvas_w - tw) // 2 - bbox[0]
    y = (canvas_h - th) // 2 - bbox[1]
    if glow:
        glow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.text((x, y), text, font=font, fill=(color[0], color[1], color[2], glow_alpha))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(img, glow_layer)
    d = ImageDraw.Draw(img)
    d.text((x, y), text, font=font, fill=color)
    return img

def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  {name} {img.size}")

# 1) 时钟数字 0-9（38px Medium 近白 + 轻发光，画布 26×44——轻量化，不抢企鹅戏）
f_hero = ImageFont.truetype(FONT_REG, 38)
for i in range(10):
    save(render_text(str(i), f_hero, C_INK, 26, 44, glow=True, glow_alpha=70), f"n{i}.png")
save(render_text(":", f_hero, C_INK, 13, 44, glow=False), "colon.png")

# 2) 日期数字 0-9（15px Regular 浅蓝灰，画布 12×18）
f_date = ImageFont.truetype(FONT_REG, 15)
for i in range(10):
    save(render_text(str(i), f_date, C_DIM, 12, 18, glow=False), f"d{i}.png")

# 3) 汉字：月 日 周（15px 浅蓝灰）
for ch, fn in [("月", "t_month.png"), ("日", "t_day.png"), ("周", "t_week.png")]:
    save(render_text(ch, f_date, C_DIM, 16, 18, glow=False), fn)

# 4) 星期 0-6（15px 浅青，ImageList 周几帧：0=周日）
f_week = ImageFont.truetype(FONT_REG, 15)
for i, ch in enumerate(["日", "一", "二", "三", "四", "五", "六"]):
    save(render_text(ch, f_week, C_ACCENT, 16, 18, glow=False), f"w{i}.png")

# 5) 电量数字 0-9（13px 浅青，画布 10×16）+ % 符号
f_bat = ImageFont.truetype(FONT_REG, 13)
for i in range(10):
    save(render_text(str(i), f_bat, C_ACCENT, 10, 16, glow=False), f"b{i}.png")
save(render_text("%", f_bat, C_ACCENT, 10, 16, glow=False), "t_pct.png")

# 6) 复制 20 帧全屏背景（已烘焙 scrim 暗区）→ 转 256 色共享调色板
#    （索引色 PNG 使 Compiler 走 rle=0x10 索引路径，体积从 9.4MB 减半到 4.9MB）
frames_src = os.path.join(ROOT, "assets-src", "frames-v4")
frames = [Image.open(os.path.join(frames_src, f"f{i:02d}.png")).convert("RGB")
          for i in range(1, 21) if os.path.exists(os.path.join(frames_src, f"f{i:02d}.png"))]
if frames:
    pal = frames[0].quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    for i, img in enumerate(frames, 1):
        img.quantize(palette=pal, dither=Image.Dither.NONE).save(os.path.join(OUT, f"f{i:02d}.png"))
print(f"  背景帧 {len(frames)}/20（256 色共享调色板）")

# 7) 市场预览图 230×328（第一帧缩放）
f1 = Image.open(os.path.join(OUT, "f01.png")).convert("RGB")
f1.resize((230, 328), Image.LANCZOS).save(os.path.join(OUT, "preview.png"))
print("  preview.png 230x328")
print(f"DONE -> {OUT}")
