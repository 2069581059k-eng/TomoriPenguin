# -*- coding: utf-8 -*-
# 表盘自定义工具发布图生成：真实截图 + 海报合成（清冷夜色风）
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"D:\AGI\TraeCode\Watchface-TomoriPenguin"
SHOT = os.path.join(ROOT, "qa", "native-shot3.png")
OUT = os.path.join(ROOT, "watchface", "assets-src", "release-poster.png")

W, H = 1000, 750
F = "C:\\Windows\\Fonts\\msyhbd.ttc"
FR = "C:\\Windows\\Fonts\\msyh.ttc"

# 画布：深夜渐变底（呼应表盘 bg #0F1420）
img = Image.new("RGB", (W, H), (13, 17, 28))
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    img.putpixel((0, y), (0, 0, 0))  # noop 保持模式
for y in range(H):
    t = y / H
    r = int(13 + 10 * t); g = int(17 + 14 * t); b = int(28 + 18 * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# 远景光斑（表盘同款氛围）
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for (x, y, r, c) in [(-60, -80, 180, (27, 58, 92, 60)), (W+40, 120, 140, (23, 69, 75, 50)),
                      (W-120, H-60, 200, (35, 32, 74, 55)), (-40, H-140, 150, (20, 49, 78, 45))]:
    od.ellipse((x, y, x + r * 2, y + r * 2), fill=c)
ov = ov.filter(ImageFilter.GaussianBlur(40))
img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(img)

# 左侧：表盘实拍（相纸卡片风：白边+阴影+悬浮）
shot = Image.open(SHOT).convert("RGB")
CARD_X, CARD_Y, SH_W = 90, 105, 300
SH_H = int(SH_W * 480 / 336)  # 428
# 阴影
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sd.rounded_rectangle((CARD_X + 10, CARD_Y + 18, CARD_X + 10 + SH_W + 24, CARD_Y + 18 + SH_H + 24),
                    radius=16, fill=(0, 0, 0, 110))
sh = sh.filter(ImageFilter.GaussianBlur(14))
img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
d = ImageDraw.Draw(img)
# 相纸白边（老照片质感，呼应表盘内相纸元素）
d.rounded_rectangle((CARD_X, CARD_Y, CARD_X + SH_W + 24, CARD_Y + SH_H + 24),
                    radius=12, fill=(244, 246, 249), outline=(221, 227, 234), width=2)
img.paste(shot, (CARD_X + 12, CARD_Y + 12))
d = ImageDraw.Draw(img)
# 胶带装饰（手帐感）
tape = Image.new("RGBA", (90, 26), (142, 212, 239, 150))
tape = tape.rotate(-8, expand=True)
img.paste(tape, (CARD_X + 118, CARD_Y - 12), tape)
d = ImageDraw.Draw(img)

# 右侧文字区
TX = 480
C_INK = (234, 240, 247)
C_DIM = (159, 179, 200)
C_ACCENT = (142, 212, 239)

# 标题
f_title = ImageFont.truetype(F, 44)
d.text((TX, 120), "咕咕嘎嘎臭企鹅", font=f_title, fill=C_INK)
# 副标题
f_sub = ImageFont.truetype(FR, 20)
d.text((TX, 186), "高松灯企鹅 · 全屏动画动态表盘", font=f_sub, fill=C_ACCENT)
# 分隔线
d.line([(TX, 232), (W - 90, 232)], fill=(60, 76, 100), width=2)

# 特性列表
f_item = ImageFont.truetype(FR, 22)
f_num = ImageFont.truetype(F, 22)
feats = [
    ("动态视频底图", "20 帧全屏手绘动画 10fps 循环"),
    ("原生控件引擎", "真机动画流畅 · 表盘库长按管理"),
    ("图片字形信息", "时间 · 中文日期 · 星期 · 电量"),
    ("清冷夜色设计", "信息区收纳顶部暗区 · 不遮主体"),
]
y = 268
for i, (t, s) in enumerate(feats, 1):
    d.ellipse((TX, y + 2, TX + 30, y + 32), outline=C_ACCENT, width=2)
    tw = d.textbbox((0, 0), str(i), font=f_num)[2]
    d.text((TX + 15 - tw // 2, y + 4), str(i), font=f_num, fill=C_ACCENT)
    d.text((TX + 46, y), t, font=f_item, fill=C_INK)
    d.text((TX + 46, y + 34), s, font=ImageFont.truetype(FR, 18), fill=C_DIM)
    y += 88

# 底部适配信息
d.line([(TX, y + 10), (W - 90, y + 10)], fill=(60, 76, 100), width=2)
f_foot = ImageFont.truetype(FR, 18)
d.text((TX, y + 26), "适配：小米手环 9 Pro / 10 Pro（336×480）", font=f_foot, fill=C_DIM)
d.text((TX, y + 54), "体积 4.6MB · 原生 .bin · v2.0", font=f_foot, fill=(90, 105, 125))

img.save(OUT)
print(f"saved {OUT} {img.size}")

# 同时生成一张纯竖版展示图（社区帖常用：截图+简单标题）
W2, H2 = 420, 620
img2 = Image.new("RGB", (W2, H2), (13, 17, 28))
d2 = ImageDraw.Draw(img2)
for y in range(H2):
    t = y / H2
    d2.line([(0, y), (W2, y)], fill=(int(13 + 10 * t), int(17 + 14 * t), int(28 + 18 * t)))
# 光斑
ov2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
od2 = ImageDraw.Draw(ov2)
od2.ellipse((-40, -60, 200, 200), fill=(27, 58, 92, 60))
od2.ellipse((W2 - 120, H2 - 160, W2 + 60, H2 + 20), fill=(35, 32, 74, 55))
ov2 = ov2.filter(ImageFilter.GaussianBlur(30))
img2 = Image.alpha_composite(img2.convert("RGBA"), ov2).convert("RGB")
d2 = ImageDraw.Draw(img2)
# 截图（居中，带描边）
s2 = Image.open(SHOT).convert("RGB").resize((336, 480), Image.LANCZOS)
d2.rounded_rectangle((38, 112, 38 + 344, 112 + 488), radius=10, outline=(142, 212, 239), width=2)
img2.paste(s2, (42, 116))
d2 = ImageDraw.Draw(img2)
f2t = ImageFont.truetype(F, 30)
t = "咕咕嘎嘎臭企鹅"
tw = d2.textbbox((0, 0), t, font=f2t)[2]
d2.text(((W2 - tw) // 2, 34), t, font=f2t, fill=(234, 240, 247))
f2s = ImageFont.truetype(FR, 16)
s = "全屏动画 · 原生引擎 · 9 Pro / 10 Pro"
sw = d2.textbbox((0, 0), s, font=f2s)[2]
d2.text(((W2 - sw) // 2, 78), s, font=f2s, fill=(142, 212, 239))
OUT2 = os.path.join(ROOT, "watchface", "assets-src", "release-card.png")
img2.save(OUT2)
print(f"saved {OUT2} {img2.size}")
