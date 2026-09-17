# -*- coding: utf-8 -*-
# .face/.bin 容器考古：字符串提取（路径/lua/结构线索）
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FILES = {
    "ours":   r"D:\AGI\TraeCode\Watchface-TomoriPenguin\bin\TomoriPenguin.face",
    "xiangbian": r"D:\AGI\TraeCode\bin\动态「相变临界」.bin",
    "gelunbiya": r"D:\AGI\TraeCode\bin\哥伦比娅.bin",
}

def ascii_strings(data, minlen=6):
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % minlen, data):
        yield m.start(), m.group().decode("ascii")

name = sys.argv[1] if len(sys.argv) > 1 else "ours"
data = open(FILES[name], "rb").read()
print(f"== {name} {len(data)} bytes ==")

# 1) 路径/扩展名线索
print("--- 路径类字符串 ---")
seen = set()
for off, s in ascii_strings(data, 5):
    if re.search(r"\.(lua|png|bin|json|fprj|ttf|xml)|(^|/)images|app/|preview|watchface", s, re.I):
        if s not in seen:
            seen.add(s)
            print(f"  @{off:>8}  {s[:120]}")

# 2) lua 源码片段（local/function/lvgl 关键词，长串）
print("--- Lua 源码线索 ---")
hits = []
for m in re.finditer(rb"[\x20-\x7e]{40,}", data):
    s = m.group().decode("ascii")
    if re.search(r"local |function |lvgl|require|end\)", s):
        hits.append((m.start(), s))
print(f"  共 {len(hits)} 段 >=40 字符的代码样串；前 8 段：")
for off, s in hits[:8]:
    print(f"  @{off:>8}  {s[:150]}")
if hits:
    lo = min(h[0] for h in hits); hi = max(h[1] for h in hits)
    print(f"  代码区大致范围: {lo} - {data.find(b'}', hi)+1 if b'}' in data[hi:hi+100] else hi}")

# 3) UTF-16LE 字符串（fprj XML 等）
print("--- UTF-16LE 字符串 ---")
for m in re.finditer(rb"(?:[\x20-\x7e]\x00){6,}", data):
    s = m.group().decode("utf-16-le")
    print(f"  @{m.start():>8}  {s[:120]}")
