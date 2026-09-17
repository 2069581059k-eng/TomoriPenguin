# -*- coding: utf-8 -*-
# .face 容器条目格式逆向：hexdump 关键区域
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FILES = {
    "ours":   r"D:\AGI\TraeCode\Watchface-TomoriPenguin\bin\TomoriPenguin.face",
    "xiangbian": r"D:\AGI\TraeCode\bin\动态「相变临界」.bin",
    "gelunbiya": r"D:\AGI\TraeCode\bin\哥伦比娅.bin",
}

def dump(data, base, length, label):
    print(f"--- {label} @{base} ---")
    for i in range(0, length, 16):
        chunk = data[base + i: base + i + 16]
        hexs = " ".join(f"{b:02X}" for b in chunk)
        asc = "".join(chr(b) if 0x20 <= b < 0x7f else "." for b in chunk)
        print(f"  {base+i:>8}  {hexs:<47}  {asc}")

name = sys.argv[1]
data = open(FILES[name], "rb").read()
print(f"== {name} {len(data)} bytes ==")

if len(sys.argv) > 2 and sys.argv[2] == "full":
    dump(data, 0x70, 0x1A0, "头部+首条目")
    # lua 条目前后
    import re
    m = re.search(rb"lua/main\.lua", data)
    if m:
        dump(data, m.start() - 0x40, 0x120, "lua/main.lua 条目")
    dump(data, len(data) - 0x60, 0x60, "文件尾")
else:
    base = int(sys.argv[2], 0)
    length = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x100
    dump(data, base, length, f"区域 @{base:#x}")
