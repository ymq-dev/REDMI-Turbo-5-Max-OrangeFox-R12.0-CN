#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度差异分析：内核模块 vermagic、sepolicy 字符串、dtb、上下文文件"""
import os, re, hashlib, json

BASE = "/sdcard/Download/recovery_diff/unpacked"
OUT = "/sdcard/Download/recovery_diff"
NAMES = ["UPSTREAM", "CN_final"]


def parse_cpio(path):
    files = {}
    buf = open(path, "rb").read()
    pos, n = 0, len(buf)
    while pos + 110 <= n:
        if buf[pos:pos + 6] not in (b"070701", b"070702"):
            break
        fld = [int(buf[pos + 6 + i * 8: pos + 6 + i * 8 + 8], 16) for i in range(13)]
        filesize, namesize = fld[6], fld[11]
        ns = pos + 110
        name = buf[ns:ns + namesize - 1].decode("utf8", "replace")
        ds = (ns + namesize + 3) // 4 * 4
        data = buf[ds:ds + filesize]
        pos = (ds + filesize + 3) // 4 * 4
        if name == "TRAILER!!!":
            break
        files[name] = data
    return files


rp = {k: parse_cpio(os.path.join(BASE, k + "_ramdisk.cpio")) for k in NAMES}

# ---------- 1. 内核模块 vermagic ----------
print("### 内核模块 vermagic 抽样 ###")
for k in NAMES:
    mods = {n: d for n, d in rp[k].items() if n.endswith(".ko")}
    print("%s: 共 %d 个 .ko" % (k, len(mods)))
    for mn in ["lib/modules/mtk-mmc.ko", "lib/modules/zram.ko", "lib/modules/mi_memory.ko"]:
        d = mods.get(mn, b"")
        m = re.search(rb"vermagic=([^\x00]{0,80})", d)
        print("   %-28s %s" % (mn, m.group(1).decode("utf8", "replace") if m else "N/A"))

# ---------- 2. sepolicy strings 差异 ----------
print()
print("### sepolicy 关键字符串 ###")
for k in NAMES:
    d = rp[k].get("sepolicy", b"")
    for kw in [b"by-name", b"bootdevice", b"super", b"vendor_boot", b"recovery"]:
        print("  %-9s %-14s 出现 %d 次" % (k, kw.decode(), d.count(kw)))

# ---------- 3. 上下文文件差异 ----------
print()
print("### 上下文文件行数 ###")
for f in ["vendor_file_contexts", "vendor_property_contexts"]:
    a = rp["UPSTREAM"].get(f, b"").split(b"\n")
    b = rp["CN_final"].get(f, b"").split(b"\n")
    sa, sb = set(a), set(b)
    print("  %s: upstream %d 行 / cn %d 行；仅上游 %d 行 / 仅 CN %d 行"
          % (f, len(a), len(b), len(sa - sb), len(sb - sa)))
    for x in list(sa - sb)[:10]:
        print("     - [UP]  " + x.decode("utf8", "replace"))
    for x in list(sb - sa)[:10]:
        print("     + [CN]  " + x.decode("utf8", "replace"))

# ---------- 4. dtb ----------
print()
print("### dtb 段 ###")
for k in NAMES:
    d = rp[k].get("lib/modules/zram.ko", b"")
    pass
# dtb 在 vendor_boot 尾部，单独读
import struct
for k, p in [("UPSTREAM", "/sdcard/Download/OrangeFox-R12.0-Unofficial-dash.img"),
             ("CN_final", "/sdcard/Download/REDMI Turbo 5 Max-OrangeFox R12.0-CN .img")]:
    f = open(p, "rb")
    hdr = f.read(2128)
    hver, page_size, ka, ra, vrs = struct.unpack("<IIIII", hdr[8:28])
    ds = 8 + 20 + 2048 + 4 + 16
    hs, dtbs = struct.unpack("<II", hdr[ds:ds + 8])
    align = lambda x: (x + 4095) // 4096 * 4096
    dtb_off = align(hs) + align(vrs)
    f.seek(dtb_off)
    dtb = f.read(dtbs)
    print("  %-9s dtb_size=%d  sha256=%s" % (k, dtbs, hashlib.sha256(dtb).hexdigest()[:20]))
    open(os.path.join(OUT, k + "_dtb.bin"), "wb").write(dtb)

print("DONE")