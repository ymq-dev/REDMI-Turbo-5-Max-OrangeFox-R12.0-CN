<div align="center">

# 🦊 OrangeFox Recovery · R12.0

### Redmi Turbo 5 Max (dash) · CN Adaptation

<br>

[![Device](https://img.shields.io/badge/Device-Redmi_Turbo_5_Max-dc2626?style=for-the-badge&logo=xiaomi&logoColor=white)](#)
[![SoC](https://img.shields.io/badge/SoC-Dimensity_9500s-f97316?style=for-the-badge)](#)
[![Platform](https://img.shields.io/badge/Platform-mt6991-0891b2?style=for-the-badge)](#)
[![Version](https://img.shields.io/badge/OrangeFox-R12.0-ea580c?style=for-the-badge)](#)

[![Firmware](https://img.shields.io/badge/Firmware-OS3.0.305.0.WPLCNXM-2563eb?style=flat-square)](#)
[![Android](https://img.shields.io/badge/Android-16-3ddc84?style=flat-square&logo=android&logoColor=white)](#)
[![VendorBoot](https://img.shields.io/badge/vendor__boot-v4-7c3aed?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Stable-16a34a?style=flat-square)](#)

<br>

[**中文**](README.md) ｜ **English**

</div>

---

> **📌 About this project**
>
> An OrangeFox R12.0 recovery built on top of the upstream [**rakarizaldy-id/android_device_xiaomi_dash-recovery**](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery), recompiled and adapted for the **Chinese Redmi Turbo 5 Max** running `OS3.0.305.0.WPLCNXM`.

---

<div align="center">

### 📱 Device Specifications

</div>

| | |
|:---|:---|
| **Codename** | `dash` / `2602BRT18C` |
| **SoC** | MediaTek Dimensity 9500s |
| **Platform** | `mt6991` |
| **Architecture** | ARM64 |
| **Partition scheme** | Virtual A/B |
| **Recovery location** | `vendor_boot` (header v4) |
| **Data filesystem** | F2FS |
| **Stock OS** | Xiaomi HyperOS |

---

## ⚠️ Disclaimer

```
╔══════════════════════════════════════════════════════════════╗
║  This is an UNOFFICIAL build.                                ║
║  Not affiliated with OrangeFox / TeamWin / Xiaomi.           ║
║  No responsibility for flashing risks or data loss.          ║
╚══════════════════════════════════════════════════════════════╝
```

- 🔒 Verified for the **Chinese Redmi Turbo 5 Max** with **HyperOS `OS3.0.305.0.WPLCNXM`**. It **must not** be cross-flashed with the international upstream baseline.
- ✅ Before flashing, verify: device model, current slot, firmware baseline, file checksums
- 💾 Back up your data first, and make sure the bootloader is unlocked

---

## 📊 Differences from Upstream

<div align="center">

**`278` files differ in content · zero additions / zero removals**

</div>

This is not a simple repack. All changes come from a **kernel baseline switch plus CN firmware policy adaptation**.

| Item | 🔵 Upstream | 🟢 This build (CN) |
|:---|:---|:---|
| Target device | POCO X8 Pro Max (dash) | **Redmi Turbo 5 Max (dash)** |
| Firmware baseline | HyperOS `OS3.0.303.0.WPLIDXM` (global) | **HyperOS `OS3.0.305.0.WPLCNXM` (cn)** |
| Firmware build date | 2026-08-06 | 2026-07-02 |
| Adaptation build date | — | **2026-09-22** |
| Security patch | 2026-08-01 | **2026-06-01** |
| Radio region | `build_region=global` | **`build_region=cn`** |
| CPU ABI | 64-bit only `arm64-v8a` | **includes 32-bit `armeabi-v7a,armeabi`** |

<details>
<summary><b>🔍 Measured on target device (click to expand)</b></summary>

<br>

> **Redmi Turbo 5 Max** / `2602BRT18C` / `dash`

```ini
ro.build.version.security_patch = 2026-06-01
ro.vendor.build.security_patch  = 2026-02-01
ro.build.version.incremental    = OS3.0.305.0.WPLCNXM
ro.build.date                   = Thu Jul 2 22:40:54 CST 2026
```

> ⚠️ The "security patch `2026-06-01`" in the table above is the on-device value; the `prop.default` inside the image carries a base value of `2026-02-01`, overridden by an upper layer after boot.

</details>

<br>

### 🧩 1. Kernel modules · 272 `.ko`

All 272 kernel modules were **recompiled** against the new firmware. The module vermagic changed:

```diff
- Upstream:   6.6.118-android15-8-g26238aa48eab-4k SMP preempt mod_unload modversions aarch64
+ This build: 6.6.118-android15-8-gdc1ec8d87f1c-4k SMP preempt mod_unload modversions aarch64
```

> ⚠️ The kernel major version is identical (`6.6.118-android15`). **Kernel modules must match their ROM kernel** and must not be mixed across baselines.

<br>

### 💾 2. Partition table · `first_stage_ramdisk/fstab.mt6991`

The CN firmware requires AVB verification, so this build adds the `avb` flags to the dynamic partitions:

```diff
- # Upstream (no AVB)
- system /system erofs ro wait,slotselect,logical,first_stage_mount

+ # This build (AVB + GSI public keys)
+ system /system erofs ro wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

**Affected partitions**

`system` · `system_ext` · `vendor` · `product` · `mi_ext` · `odm` · `vendor_dlkm` · `odm_dlkm` · `system_dlkm` · `vbmeta_system`

<br>

### ⚙️ 3. System properties · `prop.default`

| | Change |
|:---|:---|
| 🏷️ Build fingerprint | → `OS3.0.305.0.WPLCNXM` (system / vendor / odm / product / system_ext) |
| 🛡️ Security patch | `ro.build.version.security_patch` = **`2026-06-01`** (matches on-device value)<br>`ro.vendor.build.security_patch` = `2026-02-01` |
| 🧬 32-bit ABI | `ro.*.product.cpu.abilist` now includes `armeabi-v7a,armeabi`<br>new `ro.bionic.2nd_arch=arm`, `dalvik.vm.isa.arm.variant=cortex-a55` |
| 📡 Radio region | `global` → **`cn`** |

<br>

### 🔐 4. SELinux policy · `sepolicy`

<div align="center">

**`+6317` bytes · adds Xiaomi mslg (MSLG rootfs keeper) security rules**

</div>

```ini
New types:  mslg_app  mslg_init  mslg_init_exec  mslgd_exec  mslg_rootfs_file  vendor_mslg_prop
New paths:  /dev/msl  /data/rootfs  /data/vendor/mslg  /(odm|vendor/odm)/etc/assets/mslgusrimg
New props:  vendor.mslgrootfs.isready  vendor.mslg.rootfs.version  persist.vendor.unzip.mslgrootfs
```

<br>

### 📁 5. Security context files

| File | Change |
|:---|:---|
| `vendor_file_contexts` | `+14` lines (mslg file contexts) |
| `vendor_property_contexts` | `+7` lines (mslg property contexts) |
| `system/etc/copylib.txt` | library list reordered (semantically equivalent) |

<br>

### ✅ 6. Unchanged

| Item | Status |
|:---|:---|
| **DTB segment** | 535963 bytes, `sha256` **identical** in both builds — hardware description untouched |
| **File listing** | both have `1250` cpio entries in the exact same order |
| **Container** | both are `VNDRBOOT` header v4, 64 MB, page size 4096, ramdisk zstd-compressed |

> 📄 Full per-file diff data: **[`docs/DIFF_EN.md`](docs/DIFF_EN.md)**

---

## 📥 Download

| Source | Link | Note |
|:---|:---|:---|
| 🐙 **GitHub Releases** | [R12.0-dash-v1.1-cn](https://github.com/ymq-dev/REDMI-Turbo-5-Max-OrangeFox-R12.0-CN/releases/tag/R12.0-dash-v1.1-cn) | Official release (recommended) |

> Both sources host the same image. Verify the SHA256 below after downloading.

---

## 📦 Package Contents

| File | Description |
|:---|:---|
| 📀 `OrangeFox-R12.0-Unofficial-dash-CN.img` | This build's recovery image (flash to vendor_boot) |
| 📄 [`README.md`](README.md) | Chinese documentation |
| 📄 [`README_EN.md`](README_EN.md) | English documentation (this file) |
| 📊 [`docs/DIFF.md`](docs/DIFF.md) | Full diff report (Chinese) |
| 📊 [`docs/DIFF_EN.md`](docs/DIFF_EN.md) | Full diff report (English) |
| 🐍 [`scripts/`](scripts/) | Python scripts to reproduce the diff analysis |
| 🔑 [`checksums/`](checksums/) | Checksums for upstream and this build |

---

## 🔑 Checksums

> ⚠️ **Always verify before flashing**

```yaml
# Upstream
SHA256  e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f
FILE    OrangeFox-R12.0-Unofficial-dash.img

# This build (CN adaptation)
SHA256  ab6a722c0bae5682c9f4cfa8425b60ab5181e68529bcf3a0a3807ca44d90fd08
MD5     f536c8419df2addcdf7e210fae654e78
FILE    OrangeFox-R12.0-Unofficial-dash-CN.img
```

Verify with:

```bash
sha256sum OrangeFox-R12.0-Unofficial-dash-CN.img
# Windows: certutil -hashfile <file> SHA256
```

---

## 🚀 Installation

### 📋 Requirements

- [x] Unlocked bootloader
- [x] `fastboot` installed (Android SDK Platform Tools)
- [x] **Firmware baseline confirmed as `OS3.0.305.0.WPLCNXM`**

<br>

### ① Check the current slot

```bash
adb devices
adb reboot bootloader
fastboot getvar current-slot
```

<br>

### ② Flash the matching slot

```bash
# If the current slot is a
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img

# If the current slot is b
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img

# Alternatively, flash both slots
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img
```

<br>

### ③ Boot into recovery

```bash
fastboot reboot recovery
```

<br>

### ↩️ Rollback

Flash back the stock `vendor_boot` images for your firmware.

> 🔴 **Back up the original partitions first**

```bash
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_a of=/sdcard/vendor_boot_a.img"
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_b of=/sdcard/vendor_boot_b.img"
adb pull /sdcard/vendor_boot_a.img
adb pull /sdcard/vendor_boot_b.img
```

---

## ✨ Feature Status

| Feature | Status | | Feature | Status |
|:---|:---:|:---:|:---|:---:|
| Recovery boot | ✅ | | Reboot modes | ✅ |
| Display & touchscreen | ✅ | | FastbootD | ✅ |
| FBE metadata decryption | ✅ | | USB OTG host storage | ✅ |
| Internal storage | ✅ | | Haptics | ✅ |
| MTP / ADB / sideload | ✅ | | Flashlight | ✅ |
| Backup / Restore | ✅ | | Screenshots | ✅ |
| ZIP & image flashing | ✅ | | | |

> 📎 Upstream note: the AOSP / LineageOS installer is experimental; destructive operations (Format Data, Repair / Resize / Change FS) are not part of the validated runtime certification. This repository carries the same note.

---

## 🙏 Upstream & Credits

**All original work belongs to the upstream author.** This repository only performs the CN device adaptation and documents the differences.

| | |
|:---|:---|
| **Upstream repo** | [rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery) |
| **Upstream release** | `R12.0-dash-v1.1` |
| **Upstream author** | [rakarizaldy-id](https://github.com/rakarizaldy-id) |

<br>

**Credits**

<table>
<tr>
<td align="center" width="25%">
<b>OrangeFox</b><br>
<a href="https://gitlab.com/OrangeFox">Recovery Project</a>
</td>
<td align="center" width="25%">
<b>TeamWin</b><br>
<a href="https://twrp.me/">Recovery Project</a>
</td>
<td align="center" width="25%">
<b>AOSP</b><br>
<a href="https://source.android.com/">Android Open Source</a>
</td>
<td align="center" width="25%">
<b>rakarizaldy-id</b><br>
<a href="https://github.com/rakarizaldy-id">upstream device tree</a>
</td>
</tr>
</table>

---

## 📜 License & Liability

Derivative portions follow the same license as upstream.

<div align="center">

**⚠️ This is a personal adaptation project**

No guarantee of usability or safety · Flash at your own risk

</div>

---

<div align="center">

**If this project helps you, consider giving it a ⭐ Star**

<sub>Built with 🦊 for Redmi Turbo 5 Max (dash)</sub>

</div>