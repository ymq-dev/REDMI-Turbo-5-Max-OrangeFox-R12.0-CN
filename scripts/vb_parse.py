#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 vendor_boot (VNDRBOOT) 头部差异对比脚本 —— v4 结构修正版"""
import struct, os, json

FILES = {
    "UPSTREAM": "/sdcard/Download/OrangeFox-R12.0-Unofficial-dash.img",
    "CN_v8": "/sdcard/Download/OF-CN-v8.img",
    "CN_final": "/sdcard/Download/REDMI Turbo 5 Max-OrangeFox R12.0-CN .img",
    "ATTACH": "/sdcard/Download/Operit/cleanOnExit/attachment_7251546109930737606.img",
}


def parse(path):
    with open(path, "rb") as f:
        head = f.read(16384)
    out = {"path": path, "size": os.path.getsize(path)}
    if head[:8] != b"VNDRBOOT":
        out["magic"] = repr(head[:8])
        return out
    p = 8
    hver, page_size, kernel_addr, ramdisk_addr, vendor_ramdisk_size = \
        struct.unpack("<IIIII", head[p:p + 20]); p += 20
    cmdline = head[p:p + 2048].rstrip(b"\x00").decode("utf8", "replace"); p += 2048
    tags_addr, = struct.unpack("<I", head[p:p + 4]); p += 4
    name = head[p:p + 16].rstrip(b"\x00").decode("utf8", "replace"); p += 16
    header_size, dtb_size = struct.unpack("<II", head[p:p + 8]); p += 8
    dtb_addr, = struct.unpack("<Q", head[p:p + 8]); p += 8

    out.update({
        "header_version": hver,
        "page_size": page_size,
        "kernel_addr": hex(kernel_addr),
        "ramdisk_addr": hex(ramdisk_addr),
        "vendor_ramdisk_size": vendor_ramdisk_size,
        "cmdline": cmdline,
        "tags_addr": hex(tags_addr),
        "name": name,
        "header_size": header_size,
        "dtb_size": dtb_size,
        "dtb_addr": hex(dtb_addr),
    })

    off = header_size
    if hver >= 4 and off + 16 <= len(head):
        tbl_size, entry_num, entry_size, bootcfg_size = struct.unpack(
            "<IIII", head[off:off + 16])
        out.update({
            "v4_table_size": tbl_size,
            "v4_entry_num": entry_num,
            "v4_entry_size": entry_size,
            "bootconfig_size": bootcfg_size,
        })
        segs = []
        base = off + 16
        for i in range(entry_num):
            e = head[base + i * entry_size: base + (i + 1) * entry_size]
            if len(e) < 44:
                break
            rsize, roff, rtype, rname = struct.unpack("<II32sI", e[:44])
            segs.append({"name": rname.rstrip(b"\x00").decode("utf8", "replace"),
                         "type": rtype, "size": rsize, "offset": roff})
        out["segments"] = segs
    return out


result = {}
for k, p in FILES.items():
    if os.path.exists(p):
        try:
            result[k] = parse(p)
        except Exception as ex:
            result[k] = {"error": repr(ex)}
    else:
        result[k] = {"error": "not found"}

with open("/sdcard/Download/vb_report.json", "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

for k in FILES:
    r = result.get(k, {})
    print("=" * 46)
    print(k, "|", os.path.basename(FILES[k]))
    for kk, vv in r.items():
        if kk == "segments":
            print("  segments:")
            for s in vv:
                print("    - %-22s type=%-3d size=%-9d off=%d" %
                      (s["name"], s["type"], s["size"], s["offset"]))
        elif kk == "path":
            continue
        else:
            print("  %-22s %s" % (kk, vv))
print("DONE")