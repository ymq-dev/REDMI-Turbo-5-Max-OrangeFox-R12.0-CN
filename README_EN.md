# Redmi Turbo 5 Max · OrangeFox R12.0 (CN Adaptation)

> An OrangeFox R12.0 recovery adapted for the **Chinese Redmi Turbo 5 Max** (`OS3.0.305.0.WPLCNXM`), built on top of the upstream project [rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery).

<p>
  <b>Device</b>: Redmi Turbo 5 Max (dash) · <b>SoC</b>: MediaTek Dimensity 9500s · <b>Platform</b>: mt6991<br>
  <b>Partition scheme</b>: Virtual A/B · <b>Recovery location</b>: vendor_boot (header v4) · <b>Data FS</b>: F2FS
</p>

---

## ⚠️ Disclaimer

- This is an **unofficial** build. The author is not affiliated with OrangeFox, TeamWin, or Xiaomi, and takes no responsibility for any damage.
- This build targets the **Chinese Redmi Turbo 5 Max** with **HyperOS OS3.0.305.0.WPLCNXM**. It **must not** be cross-flashed with the international upstream baseline.
- Verify your device model, active slot, firmware baseline, and checksums before flashing.
- Back up your data and make sure the bootloader is unlocked.

---

## 1. Differences from Upstream

This is not a simple repack. All changes come from a **kernel baseline switch plus CN firmware policy adaptation** — **278** files differ in content, with no added or removed files.

| Item | Upstream | This build (CN) |
|---|---|---|
| Target device | POCO X8 Pro Max (dash) | **Redmi Turbo 5 Max (dash)** |
| Firmware baseline | HyperOS `OS3.0.303.0.WPLIDXM` (global) | **HyperOS `OS3.0.305.0.WPLCNXM` (cn)** |
| Build date | 2026-08-06 | **2026-07-02** |
| Security patch | 2026-08-01 | 2026-02-01 |
| Radio region | `ro.vendor.radio.build_region=global` | **`=cn`** |
| CPU ABI | 64-bit only `arm64-v8a` | **includes 32-bit `armeabi-v7a,armeabi`** |

### 1.1 Kernel modules (272 `.ko`, the bulk of the diff)

All 272 kernel modules were **recompiled** against the new firmware baseline. The module vermagic changed:

```
Upstream:   6.6.118-android15-8-g26238aa48eab-4k SMP preempt mod_unload modversions aarch64
This build: 6.6.118-android15-8-gdc1ec8d87f1c-4k SMP preempt mod_unload modversions aarch64
```

The kernel major version is identical (`6.6.118-android15`); the difference comes from a different build source baseline. **Kernel modules must match their ROM kernel** and must not be mixed across baselines.

### 1.2 Partition table `first_stage_ramdisk/fstab.mt6991`

The CN firmware requires AVB verification. This build adds the `avb` flags to the dynamic partitions:

```
# Upstream (no AVB)
system /system erofs ro wait,slotselect,logical,first_stage_mount

# This build (AVB + GSI public keys)
system /system erofs ro wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

Affected partitions: `system`, `system_ext`, `vendor`, `product`, `mi_ext`, `odm`, `vendor_dlkm`, `odm_dlkm`, `system_dlkm`, `vbmeta_system`.

### 1.3 System properties `prop.default`

- Build fingerprint → `OS3.0.305.0.WPLCNXM` (system / vendor / odm / product / system_ext)
- Security patch → `2026-02-01`
- **32-bit ABI added**: `ro.*.product.cpu.abilist` now includes `armeabi-v7a,armeabi`, plus new `ro.bionic.2nd_arch=arm` and `dalvik.vm.isa.arm.variant=cortex-a55`
- Radio region → `cn`

### 1.4 SELinux policy `sepolicy` (+6317 bytes)

Adds Xiaomi **mslg (MSLG rootfs keeper)** rules, exclusive to CN firmware:

```
New types:  mslg_app  mslg_init  mslg_init_exec  mslgd_exec  mslg_rootfs_file  vendor_mslg_prop
New paths:  /dev/msl  /data/rootfs  /data/vendor/mslg  /(odm|vendor/odm)/etc/assets/mslgusrimg
New props:  vendor.mslgrootfs.isready  vendor.mslg.rootfs.version  persist.vendor.unzip.mslgrootfs
```

### 1.5 Context files

| File | Change |
|---|---|
| `vendor_file_contexts` | +14 lines (mslg file contexts) |
| `vendor_property_contexts` | +7 lines (mslg property contexts) |
| `system/etc/copylib.txt` | library list reordered (semantically equivalent) |

### 1.6 Unchanged

- **DTB segment**: 535963 bytes, `sha256` **identical** in both builds — hardware description untouched
- **File listing**: both contain 1250 cpio entries in the exact same order
- Container: both are `VNDRBOOT` header v4, 64 MB, page size 4096, ramdisk zstd-compressed

> Full per-file diff data: [`docs/DIFF_EN.md`](docs/DIFF_EN.md)

---

## 2. Package Contents

| File | Description |
|---|---|
| `OrangeFox-R12.0-Unofficial-dash-CN.img` | This build's recovery image (flash to vendor_boot) |
| `docs/DIFF.md` | Full diff report (Chinese) |
| `docs/DIFF_EN.md` | Full diff report (English) |
| `scripts/` | Python scripts to reproduce the diff analysis |
| `checksums/` | Checksums for upstream and this build |

---

## 3. Checksums

Verify before flashing:

```
# Upstream
e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f  OrangeFox-R12.0-Unofficial-dash.img

# This build (CN adaptation)
see checksums/ or the repository Releases assets
```

---

## 4. Installation

### Requirements

- Unlocked bootloader
- `fastboot` (Android SDK Platform Tools)
- Firmware baseline confirmed as `OS3.0.305.0.WPLCNXM`

### Step 1 — Check the current slot

```bash
adb devices
adb reboot bootloader
fastboot getvar current-slot
```

### Step 2 — Flash the matching slot

```bash
# If the current slot is a
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img

# If the current slot is b
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img

# Alternatively, flash both slots
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img
```

### Step 3 — Boot into recovery

```bash
fastboot reboot recovery
```

### Rollback

Flash back the stock `vendor_boot` images for your firmware. **Back up the original partitions first:**

```bash
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_a of=/sdcard/vendor_boot_a.img"
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_b of=/sdcard/vendor_boot_b.img"
adb pull /sdcard/vendor_boot_a.img
adb pull /sdcard/vendor_boot_b.img
```

---

## 5. Feature Status

| Feature | Status |
|---|---|
| Recovery boot | ✅ |
| Display and touchscreen | ✅ |
| FBE metadata decryption (PIN / password) | ✅ |
| Internal storage | ✅ |
| MTP / ADB / sideload | ✅ |
| Backup / Restore | ✅ |
| ZIP and image flashing | ✅ |
| Reboot modes | ✅ |
| FastbootD | ✅ |
| USB OTG host storage | ✅ |
| Haptics | ✅ |
| Flashlight | ✅ |
| Screenshots | ✅ |

> Upstream note: the AOSP / LineageOS installer is experimental; destructive operations (Format Data, Repair/Resize/Change FS) are not part of the validated runtime certification. This repository carries the same note.

---

## 6. Upstream & Credits

All original work belongs to the upstream author. This repository only performs the CN device adaptation and documents the differences.

**Upstream repository**: [https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery)
**Upstream release**: `R12.0-dash-v1.1`
**Upstream author**: [rakarizaldy-id](https://github.com/rakarizaldy-id)

Credits:

- [OrangeFox Recovery Project](https://gitlab.com/OrangeFox)
- [TeamWin Recovery Project](https://twrp.me/)
- [Android Open Source Project](https://source.android.com/)
- [rakarizaldy-id](https://github.com/rakarizaldy-id) — upstream dash device tree and recovery

---

## 7. License & Liability

Derivative portions follow the same license as upstream. **This is a personal adaptation project, provided with no guarantee of usability or safety. Flash at your own risk.**