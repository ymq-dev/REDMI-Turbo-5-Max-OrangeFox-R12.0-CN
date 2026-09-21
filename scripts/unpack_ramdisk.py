#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解压 zstd 压缩的 ramdisk 并列出 cpio 内容"""
import zstandard as zstd, os, io, struct

RAW = "/sdcard/Download/recovery_diff/raw"
OUT = "/sdcard/Download/recovery_diff/unpacked"
os.makedirs(OUT, exist_ok=True)

NAMES = ["UPSTREAM", "CN_v8", "CN_final", "ATTACH"]

for k in NAMES:
    src = os.path.join(RAW, k + "_ramdisk.bin")
    if not os.path.exists(src):
        print("MISS", k)
        continue
    data = open(src, "rb").read()
    try:
        dec = zstd.ZstdDecompressor().decompress(data, max_output_size=400 * 1024 * 1024)
    except Exception as e:
        print(k, "zstd error:", e)
        continue
    dst = os.path.join(OUT, k + "_ramdisk.cpio")
    open(dst, "wb").write(dec)
    print("=" * 50)
    print(k, "decompressed:", len(dec), "->", dst)
    print("  first bytes:", dec[:8])

print("DONE")