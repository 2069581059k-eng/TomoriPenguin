# -*- coding: utf-8 -*-
# .fprj 设备码切换：MiWatchS3(362) -> Band 9 Pro(367)，控件尺寸 336x480
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

p = r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\fprj\TomoriPenguin.fprj"
s = open(p, encoding="utf-16").read()
before = s
s = s.replace('DeviceType="362"', 'DeviceType="367"')
s = s.replace('Width="466" Height="466"', 'Width="336" Height="480"')
if s == before:
    print("WARN: no replacement made")
open(p, "w", encoding="utf-16").write(s)
print(open(p, encoding="utf-16").read()[:260])
