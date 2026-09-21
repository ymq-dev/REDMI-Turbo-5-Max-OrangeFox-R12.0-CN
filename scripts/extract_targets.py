#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 cpio 中提取指定文件的原始内容，用于逐字节差异分析"""
import os, hashlib, json

BASE = "/sdcard/Download/recovery_diff/unpacked"
OUT = "/sdcard/Download/recovery_diff/files"
os.makedirs(OUT, exist_ok=True)

TARGETS = [
    "first_stage_ramdisk/fstab.mt6991",
    "prop.default",
    "system/etc/copylib.txt",
    "vendor_file_contexts",
    "vendor_property_contexts",
    "sepolicy",
    "first_stage_ramdisk/fstab.mt6991",
]


def parse_cpio(path, wanted):
    """只提取 wanted 里的文件"""
    got = {}
    with open(path, "rb") as f:
        buf = f.read()
    pos, n = 0, len(buf)
    want = set(wanted)
    while pos + 110 <= n:
        if buf[pos:pos + 6] not in (b"070701", b"070702"):
            break
        fld = [int(buf[pos + 6 + i * 8: pos + 6 + i * 8 + 8], 16) for i in range(13)]
        filesize = fld[6]
        namesize = fld[11]
        name_start = pos + 110
        name = buf[name_start:name_start + namesize - 1].decode("utf8", "replace")
        data_start = (name_start + namesize + 3) // 4 * 4
        data = buf[data_start:data_start + filesize]
        pos = (data_start + filesize + 3) // 4 * 4
        if name == "TRAILER!!!":
            break
        if name in want:
            got[name] = data
    return got


for tag in ["UPSTREAM", "CN_final"]:
    src = os.path.join(BASE, tag + "_ramdisk.cpio")
    got = parse_cpio(src, TARGETS)
    for name, data in got.items():
        safe = name.replace("/", "__")
        dst = os.path.join(OUT, "%s__%s" % (tag, safe))
        with open(dst, "wb") as f:
            f.write(data)
        print("%-10s %-40s %8d bytes  sha=%s" %
              (tag, name, len(data), hashlib.sha256(data).hexdigest()[:16]))
print("DONE")