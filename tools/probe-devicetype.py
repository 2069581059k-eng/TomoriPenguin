# DeviceType 探针：用 Compiler.exe 枚举有效设备码（极小探针工程，秒级/个）
# 原理：Compiler 对每个 DeviceType 校验 preview 尺寸——有效码会输出 "Watch: <名称>"
#       或报 "expected: WxH"；无效码直接报错。目标：找出 Band 10 Pro 专属码。
import os, re, subprocess, sys, io, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

ROOT = r"D:\AGI\TraeCode\Temp\dtprobe"
COMPILER = r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\tools\Compiler.exe"
PREVIEW = r"D:\AGI\TraeCode\Watchface-TomoriPenguin\watchface\fprj\images\preview.png"  # 230x328

shutil.rmtree(ROOT, ignore_errors=True)
os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "app", "lua"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
shutil.copy(PREVIEW, os.path.join(ROOT, "images", "preview.png"))
open(os.path.join(ROOT, "app", "lua", "main.lua"), "w", encoding="utf-8").write(
    'local app_module = "app.probe"\nlocal project_name = "probe"\n')

FPRJ = """<?xml version="1.0" encoding="utf-16" ?>
<FaceProject DeviceType="{dt}">
    <Screen Title="probe" Bitmap="preview.png">
        <Widget Shape="34" Name="app_lua%2Fmain.lua" X="0" Y="0" Width="336" Height="480" Alpha="0" />
    </Screen>
</FaceProject>
"""

lo = int(sys.argv[1]) if len(sys.argv) > 1 else 350
hi = int(sys.argv[2]) if len(sys.argv) > 2 else 700
found = {}
for dt in range(lo, hi + 1):
    p = os.path.join(ROOT, "probe.fprj")
    open(p, "w", encoding="utf-16").write(FPRJ.format(dt=dt))
    face = os.path.join(ROOT, "out", "probe.face")
    if os.path.exists(face):
        os.remove(face)
    r = subprocess.run([COMPILER, "-b", p, os.path.join(ROOT, "out"), "probe.face", "1"],
                       capture_output=True, text=True, timeout=30)
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"Watch:\s*(\S+)", out)
    e = re.search(r"expected:\s*(\d+x\d+)", out)
    if m:
        found[dt] = "NAME=" + m.group(1)
        print(f"[{dt}] {m.group(1)}", flush=True)
    elif e:
        found[dt] = "SCR=" + e.group(1)
        print(f"[{dt}] screen {e.group(1)}", flush=True)
    else:
        # 无名无尺寸错误：记录首行错误便于诊断新设备段
        first = out.strip().splitlines()[0] if out.strip() else "(no output)"
        if dt % 50 == 0:
            print(f"...{dt}: {first[:60]}", flush=True)
print(f"---- scanned {lo}-{hi}: {len(found)} valid codes ----")
