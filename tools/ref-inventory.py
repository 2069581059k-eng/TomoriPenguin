# -*- coding: utf-8 -*-
# 参考表盘结构清单打印
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

for tag, p in [("哥伦比亚", r"D:\AGI\TraeCode\bin\unpacked-gelunbiya\inventory.json"),
               ("相变临界", r"D:\AGI\TraeCode\bin\unpacked-xiangbian\inventory.json")]:
    inv = json.load(open(p, encoding="utf-8"))
    print(f"===== {tag} =====")
    for s in inv["slots"]:
        if not s["elements"] and not s["widgets"]:
            continue
        print(f"-- slot{s['slot']} --")
        print(" elements:", [(e["target"], e["x"], e["y"]) for e in s["elements"]])
        print(" widgets:")
        for w in s["widgets"]:
            print("   ", w)
        print(" imagelists:")
        for l in s["imagelists"]:
            if "err" in l:
                print("    ERR", l.get("id"), str(l["err"])[:40])
                continue
            print(f"    id={l['id']} {l['w']}x{l['h']} rle={l['rle']} frames={l['frames']}")
        for im in s["images"]:
            if "err" in im:
                print("    single ERR", str(im.get("err", ""))[:40])
                continue
            print(f"    single: {im['w']}x{im['h']} rle={im['rle']} type={im['type']} {im.get('file')}")
