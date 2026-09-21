#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整差异分析：上游原版 vs 国内适配版
分类统计 278 个差异文件，输出结构化对比报告
"""
import os, re, hashlib, json, struct

BASE = "/sdcard/Download/recovery_diff/unpacked"
OUT = "/sdcard/Download/recovery_diff"

PAIRS = {
    "UPSTREAM": "/sdcard/Download/OrangeFox-R12.0-Unofficial-dash.img",
    "CN": "/sdcard/Download/REDMI Turbo 5 Max-OrangeFox R12.0-CN .img",
}


def parse_cpio(path):
    files = {}
    buf = open(path, "rb").read()
    pos, n = 0, len(buf)
    order = []
    while pos + 110 <= n:
        if buf[pos:pos + 6] not in (b"070701", b"070702"):
            break
        fld = [int(buf[pos + 6 + i * 8: pos + 6 + i * 8 + 8], 16) for i in range(13)]
        mode, filesize, namesize = fld[1], fld[6], fld[11]
        ns = pos + 110
        name = buf[ns:ns + namesize - 1].decode("utf8", "replace")
        ds = (ns + namesize + 3) // 4 * 4
        data = buf[ds:ds + filesize]
        pos = (ds + filesize + 3) // 4 * 4
        if name == "TRAILER!!!":
            break
        files[name] = {"size": filesize, "mode": oct(mode),
                       "sha256": hashlib.sha256(data).hexdigest(), "off": ds}
        order.append(name)
    return files, order


up, up_order = parse_cpio(os.path.join(BASE, "UPSTREAM_ramdisk.cpio"))
cn, cn_order = parse_cpio(os.path.join(BASE, "CN_final_ramdisk.cpio"))

print("上游文件数: %d   国内版文件数: %d" % (len(up), len(cn)))
print("目录项顺序完全一致: %s" % (up_order == cn_order))

only_up = sorted(set(up) - set(cn))
only_cn = sorted(set(cn) - set(up))
changed = sorted([x for x in set(up) & set(cn) if up[x]["sha256"] != cn[x]["sha256"]])

print("仅上游: %d   仅国内版: %d   内容不同: %d" % (len(only_up), len(only_cn), len(changed)))

# 分类
cat = {"kernel_module": [], "text_config": [], "sepolicy": [], "binary_other": [],
       "dir_or_link": []}
for x in changed:
    if x.endswith(".ko"):
        cat["kernel_module"].append(x)
    elif x in ("sepolicy",):
        cat["sepolicy"].append(x)
    elif os.path.splitext(x)[1] in ("", ".txt", ".default", ".mt6991") or \
            "contexts" in x or x.endswith("prop.default") or x.endswith("fstab.mt6991"):
        cat["text_config"].append(x)
    else:
        cat["binary_other"].append(x)

print()
print("=== 差异分类 ===")
for k, v in cat.items():
    print("  %-16s %d" % (k, len(v)))
    if k != "kernel_module":
        for x in v:
            print("      %s" % x)

# 检查非 .ko 差异文件的大小变化
print()
print("=== 非内核模块差异文件 大小对比 ===")
for x in sorted(set(changed) - set(cat["kernel_module"])):
    print("  %-42s %8d -> %8d  (%+d)" %
          (x, up[x]["size"], cn[x]["size"], cn[x]["size"] - up[x]["size"]))

# .ko 大小总变化
ku = sum(up[x]["size"] for x in cat["kernel_module"])
kc = sum(cn[x]["size"] for x in cat["kernel_module"])
print()
print("=== 内核模块 ===")
print("  差异 .ko 数量: %d / 全部 272" % len(cat["kernel_module"]))
print("  这些模块总大小: %d -> %d (%+d bytes)" % (ku, kc, kc - ku))

# 全部 .ko 中未变化的数量
allko = [x for x in up if x.endswith(".ko")]
same_ko = [x for x in allko if x not in changed]
print("  未变化的 .ko: %d 个" % len(same_ko))

json.dump({"only_up": only_up, "only_cn": only_cn, "changed": changed, "cat": cat},
          open(os.path.join(OUT, "diff_summary.json"), "w"), ensure_ascii=False, indent=1)
print("DONE")