# -*- coding: utf-8 -*-
# 参考 .bin 表盘解包器（移植自 m0tral/UnpackMiColorFace FaceV2Decompiler）
# 用法: python unpack-ref.py <face.bin> <outdir>
import sys, io, os, struct, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

def u8(b, o): return b[o]
def u16(b, o): return struct.unpack_from("<H", b, o)[0]
def u32(b, o): return struct.unpack_from("<I", b, o)[0]

def rle_v20(data, destLen):
    """1 字节记录 RLE"""
    out = bytearray(destLen)
    off = 0
    ln = 0
    while off < len(data):
        control = data[off]; off += 1
        size = control & 0x7F
        if control & 0x80 == 0:
            if off >= len(data): break
            point = data[off]; off += 1
            for _ in range(size):
                if ln >= destLen: break
                out[ln] = point; ln += 1
        else:
            for _ in range(size):
                if ln >= destLen or off >= len(data): break
                out[ln] = data[off]; ln += 1; off += 1
    return bytes(out)

def rle_v10(data, destLen, rec):
    """4/2 字节记录 RLE（0x00=重复, 0x80=唯一）"""
    out = bytearray(destLen)
    off = 0
    ln = 0
    while off < len(data):
        control = data[off]; off += 1
        size = control & 0x7F
        if control & 0x80 == 0:
            if off >= len(data) - rec: break
            point = data[off:off+rec]; off += rec
            for _ in range(size):
                if ln + rec > destLen: break
                out[ln:ln+rec] = point; ln += rec
        else:
            for _ in range(size):
                if ln + rec > destLen or off + rec > len(data): break
                out[ln:ln+rec] = data[off:off+rec]; ln += rec; off += rec
    return bytes(out)

def rle_v11(data, destLen, rec):
    """4/2 字节记录 RLE（0x80=重复, 0x00=唯一，含 size+1）"""
    out = bytearray(destLen)
    off = 0
    ln = 0
    while off < len(data):
        control = data[off]; off += 1
        size = control & 0x7F
        if control & 0x80 == 0x80:
            if off >= len(data) - rec: break
            point = data[off:off+rec]; off += rec
            for _ in range(size + 1):
                if ln + rec > destLen: break
                out[ln:ln+rec] = point; ln += rec
        else:
            for _ in range(size + 1):
                if ln + rec > destLen or off + rec > len(data): break
                out[ln:ln+rec] = data[off:off+rec]; ln += rec; off += rec
    return bytes(out)

def rgb565_to_rgb(data, w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            v = u16(data, (y * w + x) * 2)
            px[x, y] = ((v >> 11) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31)
    return img

def rgba_bytes_to_img(data, w, h, order="BGRA"):
    try:
        return Image.frombytes("RGBA", (w, h), data, "raw", order)
    except Exception:
        return Image.frombytes("RGBA", (w, h), bytes(data[:w*h*4]))

def rgb565alpha_to_img(data, w, h):
    """RGB565(2B) + A(1B) 每像素 3 字节"""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for i in range(w * h):
        v = u16(data, i * 3)
        a = data[i * 3 + 2]
        px[i % w, i // w] = ((v >> 11) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31, a)
    return img

def indexed_to_img(data, w, h, clut):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for i in range(w * h):
        idx = data[i] if i < len(data) else 0
        c = clut[idx * 4: idx * 4 + 4] if clut and idx * 4 + 4 <= len(clut) else (0, 0, 0, 255)
        px[i % w, i // w] = (c[2], c[1], c[0], c[3])  # BMP 调色板是 BGRA
    return img

def indexed_decode(dec, w, h):
    """rle=0x10 索引色：解压流 = 0x400 调色板(BGRA×256) + w*h 索引"""
    clut = dec[:0x400]
    return indexed_to_img(dec[0x400:], w, h, clut)

def decode_image_block(data, dataOfs, dataLen):
    """解一个图片条目，返回 (PIL.Image, meta)"""
    bin_ = data[dataOfs: dataOfs + dataLen + 4]
    w, h = u16(bin_, 4), u16(bin_, 6)
    rle, typ = bin_[0], bin_[1]
    if u32(bin_, 0) == 0:
        typ = 4
    magic = u32(bin_, 0x0C)
    meta = {"w": w, "h": h, "rle": rle, "type": typ, "magic": hex(magic)}

    if magic == 0x5AA521E0:
        cpr_len = u32(bin_, 0x08)
        cpr = bin_[0x14: 0x14 + cpr_len - 8]
        ctrl = u32(bin_, 0x10)
        typ = ctrl & 0x0F
        dec_len = ctrl >> 4
        meta["type"] = typ
        rec = 2 if typ in (2, 3) else 4
        for name, fn in [("v20", lambda: rle_v20(cpr, dec_len)),
                         ("v10", lambda: rle_v10(cpr, dec_len, rec)),
                         ("v11", lambda: rle_v11(cpr, dec_len, rec))]:
            try:
                dec = fn()
                if len(dec) >= dec_len * 0.98:
                    meta["rle_algo"] = name
                    break
            except Exception:
                dec = b""
        else:
            dec = rle_v20(cpr, dec_len)
        if rle == 0x10:
            return indexed_decode(dec, w, h), meta
        if rle == 0x06:
            return rgb565alpha_to_img(dec, w, h), meta
        # 其它：按类型
        if typ == 4:
            return rgba_bytes_to_img(dec, w, h, "BGRA"), meta
        if typ in (2, 3):
            return rgb565_to_img(dec[:w*h*2], w, h), meta
        return rgba_bytes_to_img(dec, w, h, "BGRA"), meta
    else:
        px = bin_[0x0C:]
        if typ == 1:
            clut = bin_[0x15 + w * h:][:0x400]
            return indexed_to_img(px, w, h, clut), meta
        if typ == 4:
            return rgba_bytes_to_img(px[:w*h*4], w, h, "BGRA"), meta
        if typ in (2, 3):
            return rgb565_to_img(px[:w*h*2], w, h), meta
        return rgb565_to_img(px[:w*h*2], w, h), meta

def main(path, outdir):
    data = open(path, "rb").read()
    os.makedirs(outdir, exist_ok=True)
    name = os.path.splitext(os.path.basename(path))[0]

    shift_unk = data[0x18]
    count = data[0x1C]
    shift_words = data[0x1D]
    sub_version = u16(data, 0x1E)
    print(f"== {name}: {len(data)}B, slots={count}, shift={shift_words}/{shift_unk}, sub={sub_version:#x}")

    inventory = {"name": name, "slots": []}
    offset = 0xA8 + shift_words * 4 + shift_unk * 4

    for slot in range(count):
        slot_dir = os.path.join(outdir, f"slot{slot}")
        os.makedirs(slot_dir, exist_ok=True)
        img_dir = os.path.join(slot_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        slot_info = {"slot": slot, "images": [], "imagelists": [], "elements": [], "widgets": [], "apps": []}

        back_id = u32(data, offset)
        preview_ofs = u32(data, offset + 4)
        offset += 8
        sections = []
        for i in range(10):
            sections.append((u32(data, offset), u32(data, offset + 4)))
            offset += 8

        def section_entries(idx):
            cnt, blk = sections[idx]
            if cnt == 0 or blk == 0 or blk + cnt * 0x10 > len(data):
                return []
            out = []
            for k in range(cnt):
                o = blk + k * 0x10
                out.append({"idx": u16(data, o), "id": u32(data, o), "ofs": u32(data, o + 8), "len": u32(data, o + 12)})
            return out

        # i=0 elements
        for e in section_entries(0):
            o = e["ofs"]
            slot_info["elements"].append({"target": hex(u32(data, o)), "x": u16(data, o + 4), "y": u16(data, o + 6)})

        # i=2 single images
        for e in section_entries(2):
            try:
                img, meta = decode_image_block(data, e["ofs"], e["len"])
                fn = f"img_{e['idx']:04d}.png"
                img.save(os.path.join(img_dir, fn))
                meta.update({"id": hex(e["id"]), "file": fn})
                slot_info["images"].append(meta)
            except Exception as ex:
                slot_info["images"].append({"err": str(ex), "id": hex(e["id"])})

        # i=3 imagelists（动画帧）
        for e in section_entries(3):
            try:
                o, ln = e["ofs"], e["len"]
                bin_ = data[o: o + ln + 4]
                w, h = u16(bin_, 4), u16(bin_, 6)
                rle = bin_[0]
                arr = bin_[1]
                info = {"id": hex(e["id"]), "w": w, "h": h, "rle": rle, "frames": arr, "files": []}
                magic = u32(bin_, 0x0C + 4 * arr)
                if arr > 0 and magic != 0x5AA521E0:
                    # 诊断：非压缩路径头信息 + 前几帧
                    info["diag"] = {
                        "magic": hex(magic), "cprType": bin_[2], "binlen": len(bin_),
                        "maxSize": u32(bin_, 8), "head": bin_[:0x20].hex(),
                        "need_rgba": w * h * 4 * arr, "need_565a": w * h * 3 * arr,
                    }
                if magic == 0x5AA521E0:
                    arr_ofs = 0x0C + 4 * arr
                    cur = arr_ofs
                    for j in range(arr):
                        cpr_len = u32(bin_, 0x0C + j * 4)
                        blk = data[o + cur: o + cur + cpr_len + 8]
                        ctrl = u32(blk, 4)
                        typ2 = ctrl & 0x0F
                        dec_len = ctrl >> 4
                        rec = 2 if typ2 in (2, 3) else 4
                        cpr = blk[8: 8 + cpr_len - 8]
                        dec = None
                        for fn2, f2 in [("v20", lambda: rle_v20(cpr, dec_len)),
                                        ("v10", lambda: rle_v10(cpr, dec_len, rec)),
                                        ("v11", lambda: rle_v11(cpr, dec_len, rec))]:
                            try:
                                d = f2()
                                if len(d) >= dec_len * 0.98:
                                    dec = d; break
                            except Exception:
                                pass
                        if dec is None:
                            dec = rle_v20(cpr, dec_len)
                        if rle == 0x10:
                            img = indexed_decode(dec, w, h)
                        elif rle == 0x06:
                            img = rgb565alpha_to_img(dec, w, h)
                        elif typ2 in (2, 3):
                            img = rgb565_to_img(dec[:w*h*2], w, h)
                        else:
                            img = rgba_bytes_to_img(dec, w, h, "BGRA")
                        fn = f"arr_{e['idx']:04d}_{j:02d}.png"
                        img.save(os.path.join(img_dir, fn))
                        info["files"].append(fn)
                        cur += cpr_len
                else:
                    bpp = 4
                    if (rle & 0x0F) == 0x04:
                        bpp = 3
                    elif rle == 0 and bin_[2] == 0:
                        bpp = 4
                    for j in range(arr):
                        start = 0x0C + j * w * h * bpp
                        px = bin_[start: start + w * h * bpp]
                        if bpp == 4:
                            img = rgba_bytes_to_img(px, w, h, "BGRA")
                        else:
                            img = rgb565alpha_to_img(px, w, h)
                        fn = f"arr_{e['idx']:04d}_{j:02d}.png"
                        img.save(os.path.join(img_dir, fn))
                        info["files"].append(fn)
                slot_info["imagelists"].append(info)
            except Exception as ex:
                o = e["ofs"]
                head = data[o: o + 0x30].hex() if o + 0x30 < len(data) else ""
                slot_info["imagelists"].append({"err": str(ex), "id": hex(e["id"]),
                    "raw": {"len": e["len"], "head": head}})

        # i=5 apps（内嵌文件）
        for e in section_entries(5):
            try:
                o = e["ofs"]
                hdr = data[o: o + 0x20]
                file_size = u32(hdr, 0) & 0xFFFFFF
                fn_len = hdr[3]
                fn = data[o + 0x14: o + 0x14 + fn_len].decode("ascii", "replace")
                content = data[o + 0x14 + fn_len: o + 0x14 + fn_len + file_size]
                app_dir = os.path.join(slot_dir, "app", os.path.dirname(fn))
                os.makedirs(app_dir, exist_ok=True)
                open(os.path.join(slot_dir, "app", fn), "wb").write(content)
                slot_info["apps"].append({"file": fn, "size": file_size})
            except Exception as ex:
                slot_info["apps"].append({"err": str(ex)})

        # i=7 widgets
        for e in section_entries(7):
            try:
                o = e["ofs"]
                b = data[o: o + e["len"]]
                slot_info["widgets"].append({
                    "id": hex(e["id"]), "shape": b[0], "src": b[1], "typeid": b[3] >> 4,
                    "digits": b[2], "target": hex(u32(b, 8)),
                    "anchor": (u16(b, 0x14) if len(b) >= 0x20 else 0, u16(b, 0x16) if len(b) >= 0x20 else 0),
                })
            except Exception as ex:
                slot_info["widgets"].append({"err": str(ex)})

        inventory["slots"].append(slot_info)
        print(f"  slot{slot}: imgs={len(slot_info['images'])} lists={len(slot_info['imagelists'])} "
              f"(总帧={sum(i.get('frames', 0) for i in slot_info['imagelists'])}) "
              f"elems={len(slot_info['elements'])} widgets={len(slot_info['widgets'])} apps={len(slot_info['apps'])}")

    json.dump(inventory, open(os.path.join(outdir, "inventory.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved inventory.json")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
