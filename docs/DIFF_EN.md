# Diff Report · Upstream vs CN Adaptation

This document records the **complete diff analysis** between the upstream `R12.0-dash-v1.1` image and the adapted image for the Chinese Redmi Turbo 5 Max.

---

## 1. Compared Artifacts

| | Upstream | CN adaptation |
|---|---|---|
| File | `OrangeFox-R12.0-Unofficial-dash.img` | `REDMI Turbo 5 Max-OrangeFox R12.0-CN .img` |
| MD5 | `79961ca695cc8aba26dd69d87aad8756` | `f536c8419df2addcdf7e210fae654e78` |
| SHA256 | `e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f` | `ab6a722c0bae5682c9f4cfa8425b60ab5181e68529bcf3a0a3807ca44d90fd08` |
| Size | 67,108,864 bytes (64 MiB) | 67,108,864 bytes (64 MiB) |
| Target device | POCO X8 Pro Max (dash) | Redmi Turbo 5 Max (dash) |
| Firmware baseline | HyperOS `OS3.0.303.0.WPLIDXM` | HyperOS `OS3.0.305.0.WPLCNXM` |

> Note: the upstream image is byte-identical to this repo's received `attachment_7251546109930737606.img` (same MD5), confirming the latter is the original upstream package.

---

## 2. Container Structure

Both are **Android vendor_boot images (header version 4)** with a fully aligned structure:

| Field | Upstream | CN | Match |
|---|---|---|---|
| Magic | `VNDRBOOT` | `VNDRBOOT` | ✅ |
| header_version | 4 | 4 | ✅ |
| page_size | 4096 | 4096 | ✅ |
| kernel_addr | `0x80000000` | `0x80000000` | ✅ |
| ramdisk_addr | `0xa6f00000` | `0xa6f00000` | ✅ |
| tags_addr | `0x87c80000` | `0x87c80000` | ✅ |
| dtb_addr | `0x87c80000` | `0x87c80000` | ✅ |
| cmdline | `bootopt=64S3,32N2,64N2` | `bootopt=64S3,32N2,64N2` | ✅ |
| header_size | 2128 | 2128 | ✅ |
| dtb_size | 535963 | 535963 | ✅ |
| **vendor_ramdisk_size** | **53,075,540** | **53,797,938** | ❌ (+722,398) |
| ramdisk compression | zstd | zstd | ✅ |
| ramdisk decompressed | 93,686,908 | 93,690,608 | ❌ (+3,700) |

### DTB Segment

The DTB segment `sha256` is **identical** in both builds (`2636d5a861e909f5bf32...`). The hardware description table is untouched; all differences reside inside the ramdisk.

---

## 3. Ramdisk Contents (cpio newc archive)

| Metric | Upstream | CN | Result |
|---|---|---|---|
| Total cpio entries | 1250 | 1250 | identical |
| Entry order | — | — | **identical** |
| Upstream-only entries | — | — | **0** |
| CN-only entries | — | — | **0** |
| Content differs (sha256) | — | — | **278** |

**Conclusion: zero additions/removals; only 278 files have replaced content.**

---

## 4. The 278 Differences, Classified

| Category | Count | Note |
|---|---|---|
| Kernel modules `.ko` | 272 | all recompiled |
| Text configs | 5 | fstab / prop.default / copylib.txt / two contexts |
| SELinux policy | 1 | sepolicy |
| Other binaries | 0 | — |
| Dirs / links | 0 | — |

### 4.1 Kernel modules (all 272)

- Both builds contain 272 `.ko` files, and **100% differ**
- Total module size: 45,272,330 → 45,267,994 bytes (**-4,336**, negligible)
- vermagic (sampled):

| Module | Upstream vermagic | CN vermagic |
|---|---|---|
| `mtk-mmc.ko` | `6.6.118-android15-8-g26238aa48eab-4k` | `6.6.118-android15-8-gdc1ec8d87f1c-4k` |
| `zram.ko` | same | same |
| `mi_memory.ko` | same | same |

> The kernel version string (`6.6.118-android15`) is unchanged; only the **build source revision** changed (`g26238aa48eab` → `gdc1ec8d87f1c`), indicating a full recompile against the new firmware kernel baseline.

### 4.2 Size changes of the five text config files

| File | Upstream | CN | Change |
|---|---|---|---|
| `first_stage_ramdisk/fstab.mt6991` | 9,537 | 9,978 | +441 |
| `prop.default` | 15,287 | 15,485 | +198 |
| `system/etc/copylib.txt` | 1,900 | 1,793 | -107 |
| `vendor_file_contexts` | 143,360 | 144,211 | +851 |
| `vendor_property_contexts` | 81,432 | 82,013 | +581 |
| `sepolicy` | 1,514,725 | 1,521,042 | +6,317 |

### 4.3 `fstab.mt6991` details

AVB verification flags were added to the dynamic partitions:

| Partition | Upstream flags | CN flags |
|---|---|---|
| `system` | `wait,slotselect,logical,first_stage_mount` | `wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` |
| `system_ext` | same (no avb) | same (avb_keys added) |
| `vendor` | same (no avb) | `wait,slotselect,avb,logical,first_stage_mount` |
| `product` | same (no avb) | `wait,slotselect,avb,logical,first_stage_mount` |
| `mi_ext` | `...first_stage_mount,nofail` | `wait,slotselect,avb=vbmeta,logical,first_stage_mount,nofail` |
| `odm` | no avb | `+avb` |
| `vendor_dlkm` | no avb | `+avb` |
| `odm_dlkm` | no avb | `+avb` |
| `system_dlkm` | no avb | `+avb` |
| `vbmeta_system` (emmc) | `first_stage_mount,nofail,slotselect` | `first_stage_mount,nofail,slotselect,avb=vbmeta` |

All other `/dev/block/by-name/*` and overlay entries are identical.

### 4.4 `prop.default` details

| Property | Upstream | CN |
|---|---|---|
| `ro.system.build.date` | `Thu Aug 6 14:06:15 CST 2026` | `Thu Jul 2 22:40:44 CST 2026` |
| `ro.system.build.date.utc` | `1785996375` | `1783003244` |
| `ro.*.build.fingerprint` | `...:OS3.0.303.0.WPLIDXM:user/release-keys` | `...:OS3.0.305.0.WPLCNXM:user/release-keys` |
| `ro.*.build.version.incremental` | `OS3.0.303.0.WPLIDXM` | `OS3.0.305.0.WPLCNXM` |
| `ro.build.version.security_patch` | `2026-08-01` | `2026-02-01` (value inside the image)<br>measured on target device: `2026-06-01` |
| `ro.vendor.build.security_patch` | `2026-08-01` | `2026-02-01` |
| `ro.build.host` | `pangu-build-component-vendor-1043906-41w58-rdk84-qvw23` | `pangu-build-component-vendor-1002712-2pqgt-txkqg-kx6bn` |
| `ro.system.product.cpu.abilist` | `arm64-v8a` | `arm64-v8a,armeabi-v7a,armeabi` |
| `ro.system.product.cpu.abilist32` | (empty) | `armeabi-v7a,armeabi` |
| `ro.bionic.2nd_arch` | (empty) | `arm` |
| `ro.bionic.2nd_cpu_variant` | (empty) | `cortex-a55` |
| `dalvik.vm.isa.arm.variant` | (absent) | `cortex-a55` |
| `dalvik.vm.isa.arm.features` | (absent) | `default` |
| `ro.vendor.radio.build_region` | `global` | `cn` |
| `vendor.mbrain.build.version` | `OS3.0.303.0.WPLIDXM` | `OS3.0.305.0.WPLCNXM` |

Version-related changes appear across all five namespaces: `system` / `vendor` / `odm` / `product` / `system_ext`.

### 4.5 `sepolicy` details (+6317 bytes)

The CN firmware adds Xiaomi **mslg (MSLG rootfs keeper)** security rules:

```
# SELinux types
mslg_app
mslg_app_devpts
mslg_app_userfaultfd
mslg_init
mslg_init_exec
mslg_rootfs_file
mslgd_exec
vendor_mslg_prop

# File contexts
/(odm|vendor/odm)/bin/clear-caddata.sh     u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/clear-cajdata.sh     u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/clear-wpsdata.sh     u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/losetup.sh           u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/set_dns.sh           u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/start-rootfs.sh      u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/tar-rootfs.sh        u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/hw/mslgservice       u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/etc/assets/mslgusrimg    u:object_r:vendor_file:s0
/dev/msl(/.*)?                             u:object_r:mslg_rootfs_file:s0
/data/rootfs(/.*)?                         u:object_r:mslg_rootfs_file:s0
/data/vendor/mslg(/.*)?                    u:object_r:mslg_rootfs_file:s0

# Property contexts
vendor.mslgrootfs.isready       u:object_r:vendor_mslg_prop:s0
vendor.mslgrootfs.version       u:object_r:vendor_mslg_prop:s0
vendor.mslg.                    u:object_r:vendor_mslg_prop:s0
persist.vendor.unzip.mslgrootfs u:object_r:vendor_mslg_prop:s0
ro.vendor.mslg.rootfs.version   u:object_r:vendor_mslg_prop:s0
vendor.setup.mslgrootfs         u:object_r:vendor_mslg_prop:s0
```

### 4.6 Context files

**`vendor_file_contexts` (+14 lines)** — all mslg-related entries:

```
/(odm|vendor/odm)/bin/clear-caddata.sh          u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/clear-cajdata.sh          u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/clear-wpsdata.sh          u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/losetup.sh                u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/bin/hw/mslgservice            u:object_r:mslgd_exec:s0
/(odm|vendor/odm)/etc/assets/mslgusrimg         u:object_r:vendor_file:s0
/(odm|vendor/odm)/etc/assets(/.*)?              u:object_r:vendor_file:s0
/dev/msl(/.*)?                                  u:object_r:mslg_rootfs_file:s0
/data/rootfs(/.*)?                              u:object_r:mslg_rootfs_file:s0
/data/vendor/mslg(/.*)?                         u:object_r:mslg_rootfs_file:s0
```

**`vendor_property_contexts` (+7 lines)**

```
vendor.mslgrootfs.isready       u:object_r:vendor_mslg_prop:s0
vendor.mslgrootfs.version       u:object_r:vendor_mslg_prop:s0
vendor.mslg.                    u:object_r:vendor_mslg_prop:s0
persist.vendor.unzip.mslgrootfs u:object_r:vendor_mslg_prop:s0
ro.vendor.mslg.rootfs.version   u:object_r:vendor_mslg_prop:s0
vendor.setup.mslgrootfs         u:object_r:vendor_mslg_prop:s0
#line 1 "vendor/xiaomi/proprietary/mslg/keeper/1.0/default/sepolicy/property_contexts"
```

**`system/etc/copylib.txt`**: library list reordered, with `libcap.so` / `libsysutils.so` path lines swapped; no libraries added or removed — semantically equivalent.

---

## 5. Summary

| Dimension | Conclusion |
|---|---|
| Container structure | Identical (vendor_boot v4) |
| Hardware description (DTB) | Identical, untouched |
| File listing | Identical (1250 entries, zero add/remove) |
| Kernel modules | All 272 recompiled against the new baseline |
| Partition mounting | AVB verification flags added |
| System properties | Switched to CN baseline, added 32-bit ABI, region → cn |
| SELinux | Xiaomi mslg policy added |

**Nature of the changes**: a kernel baseline switch plus CN firmware policy adaptation — a **recompile of the same device (dash) following the CN firmware baseline**, not a simple file swap or re-sign.

---

## 6. Reproducing This Analysis

The `scripts/` directory contains all analysis scripts. Run them in order:

```bash
# 1. Parse the vendor_boot header
python3 scripts/vb_parse.py

# 2. Extract the ramdisk segment
python3 scripts/extract_ramdisk.py

# 3. Decompress zstd → get the cpio
python3 scripts/unpack_ramdisk.py

# 4. Parse cpio and compare file listings
python3 scripts/cpio_diff.py

# 5. Classify and count all differences
python3 scripts/full_diff.py

# 6. Deep compare: vermagic / context files / DTB
python3 scripts/deep_diff.py

# 7. sepolicy string diff
python3 scripts/sepolicy_diff.py

# 8. Extract key text files for line-by-line diff
python3 scripts/extract_targets.py
```

Requirements: Python 3 + the `zstandard` module (`pip install zstandard`).