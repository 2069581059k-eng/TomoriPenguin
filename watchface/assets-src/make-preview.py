# -*- coding: utf-8 -*-
# 生成表盘市场缩略图 preview.png（336×480 设计稿快照）
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont

W, H = 336, 480
img = Image.new("RGB", (W, H), 0x0F1420)

F_ARIAL = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", s)
F_YH = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", s)

# 远景光斑（半透明叠层）
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
for (x, y, r, c) in [(-44,-56,92,(27,58,92,72)), (W-36,-34,64,(23,69,75,72)),
                     (W-70,H-48,104,(35,32,74,72)), (-30,H-90,72,(20,49,78,72))]:
    d.ellipse((x, y, x+r*2, y+r*2), fill=c)
img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(img)

# 顶部：日期 / 电量
d.text((20, 16), "9月16日 周二", font=F_YH(17), fill=0x8FA3BB)
d.text((246, 17), "82%", font=F_ARIAL(15), fill=0x8FA3BB)
d.rounded_rectangle((288, 19, 316, 33), radius=7, outline=0x8FA3BB, width=2)
d.rounded_rectangle((290, 21, 290+18, 31), radius=5, fill=0x8ED4EF)

# 大时间
t = "21:47"
f = F_ARIAL(64)
bb = d.textbbox((0, 0), t, font=f)
d.text(((W-(bb[2]-bb[0]))//2, 46), t, font=f, fill=0xEAF0F7)

# 卡片：阴影 + 相纸 + 帧 + 字幕
CX, CY, MW, MH = 42, 116, 252, 352
sh = Image.new("RGBA", (W, H), (0,0,0,0))
ds = ImageDraw.Draw(sh)
ds.rounded_rectangle((CX+6, CY+12, CX+6+MW, CY+12+MH), radius=18, fill=(0,0,0,90))
img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
d = ImageDraw.Draw(img)
d.rounded_rectangle((CX, CY, CX+MW, CY+MH), radius=10, fill=0xF4F6F9, outline=0xDDE3EA, width=2)

frame = Image.open(r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\frames\f01.png").convert("RGB")
img.paste(frame, (CX+6, CY+6))
d = ImageDraw.Draw(img)

fc = "咕咕嘎嘎"
ff = F_YH(16)
bb = d.textbbox((0, 0), fc, font=ff)
d.text(((W-(bb[2]-bb[0]))//2, CY+MH-24), fc, font=ff, fill=0x5C6678)

# 雪（近景）
for (x, y, r) in [(30,300,4),(310,180,3),(120,420,4),(260,40,3),(70,120,3)]:
    d.ellipse((x, y, x+r*2, y+r*2), fill=(234,243,251,255) if r==3 else (234,243,251))

# 保存设计稿 + Band 9 Pro 预览缩略图（230×328，Compiler 对 DeviceType=367 的要求）
img.save(r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\assets-src\preview-design.png")
img.resize((230, 328), Image.LANCZOS).save(r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\fprj\images\preview.png")
print("preview.png saved 230x328")
