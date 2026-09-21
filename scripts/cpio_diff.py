#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 newc(cpio) 归档，输出文件清单与内容哈希，用于差异对比"""
import os, hashlib, json, sys

BASE = "/sdcard/Download/recovery_diff/unpacked"
OUT = "/sdcard/Download/recovery_diff"
NAMES = ["UPSTREAM", "CN_v8", "CN_final", "ATTACH"]


def parse_cpio(path):
    """解析 newc 格式 cpio，返回 {name: {mode,size,sha256,data}}"""
    files = {}
    with open(path, "rb") as f:
        buf = f.read()
    pos = 0
    n = len(buf)
    while pos + 110 <= n:
        magic = buf[pos:pos + 6]
        if magic not in (b"070701", b"070702"):
            break
        fld = []
        for i in range(13):
            s = pos + 6 + i * 8
            fld.append(int(buf[s:s + 8], 16))
        ino, mode, uid, gid, nlink, mtime, filesize, devmaj, devmin, rdevmaj, rdevmin, namesize, chksum = fld
        name_start = pos + 110
        name = buf[name_start:name_start + namesize - 1].decode("utf8", "replace")
        # header + name 按 4 字节对齐
        data_start = (name_start + namesize + 3) // 4 * 4
        data = buf[data_start:data_start + filesize]
        pos = (data_start + filesize + 3) // 4 * 4
        if name == "TRAILER!!!":
            break
        files[name] = {
            "mode": oct(mode),
            "size": filesize,
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return files


report = {}
for k in NAMES:
    p = os.path.join(BASE, k + "_ramdisk.cpio")
    if not os.path.exists(p):
        print("MISS", k); continue
    files = parse_cpio(p)
    report[k] = files
    print("=" * 50)
    print(k, "文件数:", len(files))

# 保存清单
with open(os.path.join(OUT, "cpio_manifest.json"), "w") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)

# 对比 UPSTREAM vs ATTACH
def diff(a, b, an, bn):
    fa, fb = report.get(a, {}), report.get(b, {})
    only_a = sorted(set(fa) - set(fb))
    only_b = sorted(set(fb) - set(fa))
    changed = sorted([x for x in set(fa) & set(fb) if fa[x]["sha256"] != fb[x]["sha256"]])
    print()
    print("#" * 60)
    print("对比 %s  vs  %s" % (an, bn))
    print("  仅在 %s: %d 个" % (an, len(only_a)))
    print("  仅在 %s: %d 个" % (bn, len(only_b)))
    print("  内容不同: %d 个" % len(changed))
    return only_a, only_b, changed

for a, b in [("UPSTREAM", "ATTACH"), ("UPSTREAM", "CN_final"), ("CN_v8", "CN_final")]:
    oa, ob, ch = diff(a, b, a, b)
    print("  --- 内容不同清单 ---")
    for x in ch:
        print("     %s" % x)
print("DONE")