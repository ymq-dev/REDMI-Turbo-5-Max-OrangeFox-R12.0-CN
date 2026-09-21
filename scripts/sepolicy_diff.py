#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比两版 sepolicy 的字符串差异，定位新增的 SELinux 规则"""
import re

def strings(data, minlen=6):
    return set(m.group().decode("utf8", "replace")
               for m in re.finditer(rb"[\x20-\x7e]{%d,}" % minlen, data))

up = open("/sdcard/Download/recovery_diff/unpacked/UPSTREAM_ramdisk.cpio", "rb").read()
cn = open("/sdcard/Download/recovery_diff/unpacked/CN_final_ramdisk.cpio", "rb").read()

# 直接对整包字符串做差（sepolicy 内容占大头，但内核模块也含字符串）
su, sc = strings(up), strings(cn)
new = sc - su
gone = su - sc

print("整包新增字符串: %d   消失字符串: %d" % (len(new), len(gone)))
print()
print("=== 新增字符串中含 mslg / msl 关键字 ===")
for s in sorted(x for x in new if "msl" in x.lower()):
    print("  +", s)

print()
print("=== 新增字符串中含 by-name / bootdevice / super 关键字 ===")
for s in sorted(x for x in new if any(k in x for k in ("by-name", "bootdevice", "super"))):
    print("  +", s)

print()
print("=== 消失字符串中含 by-name / bootdevice 关键字 ===")
for s in sorted(x for x in gone if any(k in x for k in ("by-name", "bootdevice", "super"))):
    print("  -", s)

print()
print("=== 新增字符串样例（前 40 条，长度<60） ===")
for s in sorted(x for x in new if len(x) < 60)[:40]:
    print("  +", s)