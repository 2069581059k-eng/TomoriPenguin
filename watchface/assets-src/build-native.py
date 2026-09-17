# -*- coding: utf-8 -*-
# 最终原生表盘构建：工程 XML + 素材 + 编译（一站式）
import subprocess, sys, io, os, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

ROOT = r"D:\AGI\TraeCode\Watchface-TomoriPenguin"
NAT = os.path.join(ROOT, "watchface", "native")
IMG = os.path.join(NAT, "images")
OUT = os.path.join(NAT, "output")
COMPILER = os.path.join(ROOT, "watchface", "tools", "Compiler-4.22.exe")

# 1) 工程目录净化（关键：根目录只能有一个 .fprj，output 清空）
for f in glob.glob(os.path.join(NAT, "*.fprj")):
    os.remove(f)
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*")):
    os.remove(f)

# 2) 素材齐备校验
need = ([f"f{i:02d}.png" for i in range(1, 21)] + [f"n{i}.png" for i in range(10)] +
        [f"d{i}.png" for i in range(10)] + [f"w{i}.png" for i in range(7)] +
        [f"b{i}.png" for i in range(10)] +
        ["colon.png", "t_month.png", "t_day.png", "t_week.png", "t_pct.png", "preview.png"])
missing = [f for f in need if not os.path.exists(os.path.join(IMG, f))]
if missing:
    print("MISSING:", missing)
    sys.exit(1)
print(f"images ok: {len(need)} files")

NUM11 = '|'.join([f"n{i}.png" for i in range(10)] + ["n0.png"])   # 官方模板：11 张（末尾重复首图）
DATE11 = '|'.join([f"d{i}.png" for i in range(10)] + ["d0.png"])
BAT11 = '|'.join([f"b{i}.png" for i in range(10)] + ["b0.png"])
F20I = "|".join(f"({i}):f{i+1:02d}.png" for i in range(20))
W7I = "|".join(f"({i}):w{i}.png" for i in range(7))

# 3) 最终工程 XML（utf-16 + 无 @Id + anim_[0@100] 动画格式）
xml = f'''<?xml version="1.0" encoding="utf-16"?>
<FaceProject DeviceType="367">
<Screen Title="TomoriPenguin" Bitmap="preview.png">
<Widget Shape="31" Name="anim_[0@100]" X="0" Y="0" Width="336" Height="480" Alpha="255" Alignment="0" DefaultIndex="0" Index_Src="0" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{F20I}" />
<Widget Shape="32" Name="clock_hour" X="22" Y="28" Width="26" Height="44" Alpha="255" Digits="2" Alignment="0" Value_Src="0811" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{NUM11}" />
<Widget Shape="30" Name="clock_colon" X="76" Y="28" Width="13" Height="44" Alpha="255" Visible_Src="0" Bitmap="colon.png" />
<Widget Shape="32" Name="clock_minute" X="90" Y="28" Width="26" Height="44" Alpha="255" Digits="2" Alignment="0" Value_Src="1011" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{NUM11}" />
<Widget Shape="32" Name="date_month" X="22" Y="78" Width="12" Height="18" Alpha="255" Digits="2" Alignment="0" Value_Src="1012" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{DATE11}" />
<Widget Shape="30" Name="date_t_month" X="46" Y="78" Width="16" Height="18" Alpha="255" Visible_Src="0" Bitmap="t_month.png" />
<Widget Shape="32" Name="date_day" X="66" Y="78" Width="12" Height="18" Alpha="255" Digits="2" Alignment="0" Value_Src="1812" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{DATE11}" />
<Widget Shape="30" Name="date_t_day" X="90" Y="78" Width="16" Height="18" Alpha="255" Visible_Src="0" Bitmap="t_day.png" />
<Widget Shape="30" Name="date_t_week" X="112" Y="78" Width="16" Height="18" Alpha="255" Visible_Src="0" Bitmap="t_week.png" />
<Widget Shape="31" Name="date_weekday" X="128" Y="78" Width="16" Height="18" Alpha="255" Alignment="0" DefaultIndex="0" Index_Src="2012" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{W7I}" />
<Widget Shape="32" Name="batt_num" X="280" Y="30" Width="10" Height="16" Alpha="255" Digits="2" Alignment="0" Value_Src="0841" Spacing="0" Blanking="0" Visible_Src="0" BitmapList="{BAT11}" />
<Widget Shape="30" Name="batt_pct" X="300" Y="30" Width="10" Height="16" Alpha="255" Visible_Src="0" Bitmap="t_pct.png" />
</Screen>
</FaceProject>
'''
fprj = os.path.join(NAT, "TomoriPenguin.fprj")
with open(fprj, "w", encoding="utf-16") as f:
    f.write(xml)

# 4) 编译
r = subprocess.run([COMPILER, "-b", fprj, OUT, "TomoriPenguinNative.face", "491552737"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print((r.stdout or "") + (r.stderr or ""))
face = os.path.join(OUT, "TomoriPenguinNative.face")
if os.path.exists(face):
    print(f"\nFACE: {os.path.getsize(face):,} bytes")
