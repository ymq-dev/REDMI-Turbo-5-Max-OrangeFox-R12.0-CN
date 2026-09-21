#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 vendor_boot 中的 vendor_ramdisk 段并检测压缩格式"""
import struct, os, gzip, lzma, io, hashlib

FILES = {
    "UPSTREAM": "/sdcard/Download/OrangeFox-R12.0-Unofficial-dash.img",
    "CN_v8": "/sdcard/Download/OF-CN-v8.img",
    "CN_final": "/sdcard/Download/REDMI Turbo 5 Max-OrangeFox R12.0-CN .img",
    "ATTACH": "/sdcard/Download/Operit/cleanOnExit/attachment_7251546109930737606.img",
}
OUTDIR = "/sdcard/Download/recovery_diff/raw"
os.makedirs(OUTDIR, exist_ok=True)


def parse(path):
    with open(path, "rb") as f:
        f.seek(0)
        hdr = f.read(2128)
        hver, page_size, kernel_addr, ramdisk_addr, vr_size = struct.unpack("<IIIII", hdr[8:28])
        header_size, dtb_size = struct.unpack("<II", hdr[8 + 20 + 2048 + 4 + 16:8 + 20 + 2048 + 4 + 16 + 8])
        page = 4096
        def align(x):
            return (x + page - 1) // page * page
        # v4: header(align to page) + ramdisk(align) + dtb(align) + bootconfig
        vr_off = align(header_size)
        dtb_off = vr_off + align(vr_size)
        f.seek(vr_off)
        ramdisk = f.read(vr_size)
    return {"hver": hver, "page_size": page_size, "vr_size": vr_size,
            "vr_off": vr_off, "dtb_off": dtb_off, "dtb_size": dtb_size,
            "ramdisk": ramdisk}


def detect(data):
    if data[:2] == b"\x1f\x8b":
        return "gzip"
    if data[:4] == b"\x02\x21\x4c\x18" or data[:4] == b"\x04\x22\x4d\x18":
        return "lz4"
    if data[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if data[:4] == b"0707" or data[:6] == b"070701" or data[:6] == b"070702":
        return "cpio"
    return "unknown:" + repr(data[:8])


for k, p in FILES.items():
    info = parse(p)
    rd = info.pop("ramdisk")
    fmt = detect(rd)
    outp = os.path.join(OUTDIR, k + "_ramdisk.bin")
    with open(outp, "wb") as f:
        f.write(rd)
    print("=" * 50)
    print(k, os.path.basename(p))
    print("  vr_size    :", info["vr_size"])
    print("  vr_offset  :", info["vr_off"])
    print("  dtb_offset :", info["dtb_off"])
    print("  compress   :", fmt)
    print("  sha256     :", hashlib.sha256(rd).hexdigest()[:24])
    print("  -> saved   :", outp)
print("DONE")