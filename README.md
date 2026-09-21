<div align="center">

# 🦊 OrangeFox Recovery · R12.0

### Redmi Turbo 5 Max (dash) · 国内适配版

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

**中文** ｜ [**English**](README_EN.md)

</div>

---

> **📌 项目定位**
>
> 基于上游 [**rakarizaldy-id/android_device_xiaomi_dash-recovery**](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery) 的 OrangeFox R12.0，针对**国内版 Redmi Turbo 5 Max** 固件 `OS3.0.305.0.WPLCNXM` 重新编译适配。

---

<div align="center">

### 📱 设备规格

</div>

| | |
|:---|:---|
| **设备代号** | `dash` / `2602BRT18C` |
| **处理器** | 联发科 Dimensity 9500s |
| **平台** | `mt6991` |
| **架构** | ARM64 |
| **分区方案** | Virtual A/B |
| **Recovery 位置** | `vendor_boot`（header v4） |
| **数据分区** | F2FS |
| **原厂系统** | Xiaomi HyperOS |

---

## ⚠️ 重要声明

```
╔══════════════════════════════════════════════════════════════╗
║  本仓库为非官方（Unofficial）编译产物                          ║
║  作者与 OrangeFox / TeamWin / 小米官方均无关联                 ║
║  不承担任何刷机风险与数据损失责任                              ║
╚══════════════════════════════════════════════════════════════╝
```

- 🔒 本版针对**国内版 Redmi Turbo 5 Max** 与 **HyperOS `OS3.0.305.0.WPLCNXM`** 验证，与上游国际版基线**不能混刷**
- ✅ 刷机前请核对：机型、当前分区槽位、固件基线、文件校验值
- 💾 动手前请**务必备份数据**，并确认已解锁 Bootloader

---

## 📊 与上游的差异

<div align="center">

**共 `278` 处文件内容差异 · 无新增 / 无删除**

</div>

本版并非简单重打包，全部改动来自 **内核基线切换 + 国内固件策略适配**。

| 对比项 | 🔵 上游原版 | 🟢 本版（国内适配） |
|:---|:---|:---|
| 目标机型 | POCO X8 Pro Max (dash) | **Redmi Turbo 5 Max (dash)** |
| 固件基线 | HyperOS `OS3.0.303.0.WPLIDXM`（global） | **HyperOS `OS3.0.305.0.WPLCNXM`（cn）** |
| 固件编译日 | 2026-08-06 | 2026-07-02 |
| 适配构建日 | — | **2026-09-22** |
| 安全补丁 | 2026-08-01 | **2026-06-01** |
| 无线区域 | `build_region=global` | **`build_region=cn`** |
| CPU ABI | 仅 64 位 `arm64-v8a` | **含 32 位 `armeabi-v7a,armeabi`** |

<details>
<summary><b>🔍 目标机实测值（点击展开）</b></summary>

<br>

> **Redmi Turbo 5 Max** / `2602BRT18C` / `dash`

```ini
ro.build.version.security_patch = 2026-06-01
ro.vendor.build.security_patch  = 2026-02-01
ro.build.version.incremental    = OS3.0.305.0.WPLCNXM
ro.build.date                   = Thu Jul 2 22:40:54 CST 2026
```

> ⚠️ 上表中的「安全补丁 `2026-06-01`」取自设备实测；镜像内 `prop.default` 写入的基值为 `2026-02-01`，设备启动后由更上层覆盖。

</details>

<br>

### 🧩 1. 内核模块 · 272 个 `.ko`

全部 272 个内核模块跟随新固件**重新编译**，模块版本签名（vermagic）发生变化：

```diff
- 上游：6.6.118-android15-8-g26238aa48eab-4k SMP preempt mod_unload modversions aarch64
+ 本版：6.6.118-android15-8-gdc1ec8d87f1c-4k SMP preempt mod_unload modversions aarch64
```

> ⚠️ 内核主版本一致（`6.6.118-android15`），差异源于构建源码基线不同。**内核模块必须与 ROM 内核配套使用**，不可跨基线混用。

<br>

### 💾 2. 分区挂载表 · `first_stage_ramdisk/fstab.mt6991`

国内固件要求开启 AVB 校验，本版为动态分区挂载项补全了 `avb` 参数：

```diff
- # 上游（无 avb 校验）
- system /system erofs ro wait,slotselect,logical,first_stage_mount

+ # 本版（开启 avb + GSI 公钥）
+ system /system erofs ro wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

**涉及分区**

`system` · `system_ext` · `vendor` · `product` · `mi_ext` · `odm` · `vendor_dlkm` · `odm_dlkm` · `system_dlkm` · `vbmeta_system`

<br>

### ⚙️ 3. 系统属性 · `prop.default`

| | 变更 |
|:---|:---|
| 🏷️ 构建指纹 | → `OS3.0.305.0.WPLCNXM`（system / vendor / odm / product / system_ext 五处） |
| 🛡️ 安全补丁 | `ro.build.version.security_patch` = **`2026-06-01`**（目标机实测一致）<br>`ro.vendor.build.security_patch` = `2026-02-01` |
| 🧬 32 位 ABI | `ro.*.product.cpu.abilist` 补上 `armeabi-v7a,armeabi`<br>新增 `ro.bionic.2nd_arch=arm`、`dalvik.vm.isa.arm.variant=cortex-a55` |
| 📡 无线区域 | `global` → **`cn`** |

<br>

### 🔐 4. SELinux 策略 · `sepolicy`

<div align="center">

**`+6317` 字节 · 新增小米 mslg（MSLG rootfs keeper）安全机制**

</div>

```ini
新增类型: mslg_app  mslg_init  mslg_init_exec  mslgd_exec  mslg_rootfs_file  vendor_mslg_prop
新增路径: /dev/msl  /data/rootfs  /data/vendor/mslg  /(odm|vendor/odm)/etc/assets/mslgusrimg
新增属性: vendor.mslgrootfs.isready  vendor.mslg.rootfs.version  persist.vendor.unzip.mslgrootfs
```

<br>

### 📁 5. 安全上下文文件

| 文件 | 变化 |
|:---|:---|
| `vendor_file_contexts` | `+14` 行（mslg 相关文件上下文） |
| `vendor_property_contexts` | `+7` 行（mslg 相关属性上下文） |
| `system/etc/copylib.txt` | 库清单顺序重排（内容等价） |

<br>

### ✅ 6. 未变动的部分

| 项 | 状态 |
|:---|:---|
| **DTB 段** | 535963 字节，两版 `sha256` **完全一致**，硬件描述未改动 |
| **文件清单** | 两版均 `1250` 个 cpio 条目，目录项顺序完全一致 |
| **容器结构** | 均为 `VNDRBOOT` header v4，64 MB，page size 4096，ramdisk zstd 压缩 |

> 📄 完整的逐文件差异数据见 **[`docs/DIFF.md`](docs/DIFF.md)**

---

## 📥 下载

| 渠道 | 链接 | 备注 |
|:---|:---|:---|
| 🐙 **GitHub Releases** | [R12.0-dash-v1.1-cn](https://github.com/ymq-dev/REDMI-Turbo-5-Max-OrangeFox-R12.0-CN/releases/tag/R12.0-dash-v1.1-cn) | 本仓库正式发布（推荐） |
| ☁️ **123 云盘** | [点击下载](https://1828915014.share.123pan.cn/123pan/pI67jv-CM6Rv?pwd=1hLY) | 提取码：`1hLY` |

> 两个渠道为同一镜像文件，下载后请核对下方 SHA256。

---

## 📦 文件清单

| 文件 | 说明 |
|:---|:---|
| 📀 `OrangeFox-R12.0-Unofficial-dash-CN.img` | 本版 Recovery 镜像（刷入 vendor_boot） |
| 📄 [`README.md`](README.md) | 中文说明（本文件） |
| 📄 [`README_EN.md`](README_EN.md) | English documentation |
| 📊 [`docs/DIFF.md`](docs/DIFF.md) | 与上游的完整差异对比报告（中文） |
| 📊 [`docs/DIFF_EN.md`](docs/DIFF_EN.md) | Full diff report (English) |
| 🐍 [`scripts/`](scripts/) | 用于复现差异分析的 Python 脚本 |
| 🔑 [`checksums/`](checksums/) | 上下游镜像校验值 |

---

## 🔑 校验值

> ⚠️ **刷入前请务必核对**

```yaml
# 上游原版
SHA256  e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f
FILE    OrangeFox-R12.0-Unofficial-dash.img

# 本版（国内适配）
SHA256  ab6a722c0bae5682c9f4cfa8425b60ab5181e68529bcf3a0a3807ca44d90fd08
MD5     f536c8419df2addcdf7e210fae654e78
FILE    OrangeFox-R12.0-Unofficial-dash-CN.img
```

验证命令：

```bash
sha256sum OrangeFox-R12.0-Unofficial-dash-CN.img
# Windows: certutil -hashfile <文件> SHA256
```

---

## 🚀 安装方法

### 📋 前置条件

- [x] Bootloader 已解锁
- [x] 已安装 `fastboot`（Android SDK Platform Tools）
- [x] **已确认当前固件基线为 `OS3.0.305.0.WPLCNXM`**

<br>

### ① 确认当前分区槽位

```bash
adb devices
adb reboot bootloader
fastboot getvar current-slot
```

<br>

### ② 刷入对应槽位

```bash
# 若当前槽位为 a
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img

# 若当前槽位为 b
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img

# 保险起见，两个槽位都刷也可以
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img
```

<br>

### ③ 进入 Recovery

```bash
fastboot reboot recovery
```

<br>

### ↩️ 回滚方法

刷回官方固件对应的 `vendor_boot` 分区镜像即可恢复原状。

> 🔴 **操作前请务必备份原始分区**

```bash
# 刷机前先备份（强烈建议）
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_a of=/sdcard/vendor_boot_a.img"
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_b of=/sdcard/vendor_boot_b.img"
adb pull /sdcard/vendor_boot_a.img
adb pull /sdcard/vendor_boot_b.img
```

---

## ✨ 功能支持

| 功能 | 状态 | | 功能 | 状态 |
|:---|:---:|:---:|:---|:---:|
| Recovery 启动 | ✅ | | 重启模式切换 | ✅ |
| 显示与触控 | ✅ | | FastbootD | ✅ |
| FBE 元数据解密 | ✅ | | USB OTG 外接存储 | ✅ |
| 内部存储访问 | ✅ | | 振动反馈 | ✅ |
| MTP / ADB / sideload | ✅ | | 手电筒 | ✅ |
| 备份 / 恢复 | ✅ | | 截图 | ✅ |
| ZIP 与镜像刷入 | ✅ | | | |

> 📎 上游声明：AOSP / LineageOS 安装包为实验性功能，破坏性操作（Format Data、Repair / Resize / Change FS）未经完整运行时验证认证。本仓库沿用该声明。

---

## 🙏 上游仓库与致谢

本项目**所有原始工作均来自上游作者**，本仓库仅做国内机型适配与差异记录。

| | |
|:---|:---|
| **上游仓库** | [rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery) |
| **上游版本** | `R12.0-dash-v1.1` |
| **上游作者** | [rakarizaldy-id](https://github.com/rakarizaldy-id) |

<br>

**致谢**

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
<a href="https://github.com/rakarizaldy-id">上游设备树</a>
</td>
</tr>
</table>

---

## 📜 许可与免责

本项目对上游衍生部分沿用相同许可。

<div align="center">

**⚠️ 本仓库为个人适配折腾产物**

不保证任何可用性与安全性 · 刷机风险自负

</div>

---

<div align="center">

**如果这个项目对你有帮助，欢迎点个 ⭐ Star**

<sub>Built with 🦊 for Redmi Turbo 5 Max (dash)</sub>

</div>
