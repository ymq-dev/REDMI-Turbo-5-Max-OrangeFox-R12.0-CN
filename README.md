# Redmi Turbo 5 Max · OrangeFox R12.0（国内适配版）

> 基于上游 [rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery) 的 OrangeFox R12.0 recovery，针对**国内版 Redmi Turbo 5 Max** 固件 `OS3.0.305.0.WPLCNXM` 重新编译适配。

**English version: [README_EN.md](README_EN.md)**

<p>
  <b>设备</b>: Redmi Turbo 5 Max (dash) · <b>SoC</b>: 联发科 Dimensity 9500s · <b>平台</b>: mt6991<br>
  <b>分区方案</b>: Virtual A/B · <b>Recovery 位置</b>: vendor_boot (header v4) · <b>文件系统</b>: F2FS
</p>

---

## ⚠️ 重要声明

- 本仓库为**非官方**（Unofficial）编译产物，作者与 OrangeFox / TeamWin / 小米无关，不承担刷机风险。
- 本版针对**国内版 Redmi Turbo 5 Max** 与 **HyperOS OS3.0.305.0.WPLCNXM** 验证，与上游的国际版基线**不能混刷**。
- 刷机前请自行核对机型、当前分区槽位、固件基线版本与文件校验值。
- 动手前请确保已备份数据，并确认已解锁 Bootloader。

---

## 一、与上游的差异（核心）

本版并非简单的重打包，全部改动来自**内核基线切换 + 国内固件策略适配**，共 **278 处**文件内容差异，无新增/删除文件。

| 对比项 | 上游原版 | 本版（国内适配） |
|---|---|---|
| 目标机型 | POCO X8 Pro Max (dash) | **Redmi Turbo 5 Max (dash)** |
| 固件基线 | HyperOS `OS3.0.303.0.WPLIDXM`（global） | **HyperOS `OS3.0.305.0.WPLCNXM`（cn）** |
| 固件编译日 | 2026-08-06 | 2026-07-02 |
| **适配构建日** | — | **2026-09-22** |
| 安全补丁 | 2026-08-01 | **2026-06-01** |
| 无线区域 | `ro.vendor.radio.build_region=global` | **`=cn`** |
| CPU ABI | 仅 64 位 `arm64-v8a` | **含 32 位 `armeabi-v7a,armeabi`** |

> **目标机实测值**（Redmi Turbo 5 Max / `2602BRT18C` / dash，用于校准上表）：
> `ro.build.version.security_patch` = `2026-06-01`　`ro.vendor.build.security_patch` = `2026-02-01`
> `ro.build.version.incremental` = `OS3.0.305.0.WPLCNXM`　`ro.build.date` = `Thu Jul 2 22:40:54 CST 2026`
> 注：上表中的「安全补丁 2026-06-01」取自设备实测；镜像内 `prop.default` 写入的基值为 `2026-02-01`，设备启动后由更上层覆盖。

### 1. 内核模块（272 个 `.ko`，占差异主体）

全部 272 个内核模块跟随新固件**重新编译**，模块版本签名（vermagic）发生变化：

```
上游:   6.6.118-android15-8-g26238aa48eab-4k SMP preempt mod_unload modversions aarch64
本版:   6.6.118-android15-8-gdc1ec8d87f1c-4k SMP preempt mod_unload modversions aarch64
```

内核主版本相同（6.6.118-android15），差异源于构建源码基线不同。**这意味着内核模块与 ROM 内核必须配套使用**，不可跨基线混用。

### 2. 分区挂载表 `first_stage_ramdisk/fstab.mt6991`

国内固件要求开启 AVB 校验，本版为动态分区挂载项补全了 `avb` 参数：

```
# 上游（无 avb 校验）
system /system erofs ro wait,slotselect,logical,first_stage_mount

# 本版（开启 avb + GSI 公钥）
system /system erofs ro wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey
```

涉及分区：`system`、`system_ext`、`vendor`、`product`、`mi_ext`、`odm`、`vendor_dlkm`、`odm_dlkm`、`system_dlkm`、`vbmeta_system`。

### 3. 系统属性 `prop.default`

- 构建指纹 → `OS3.0.305.0.WPLCNXM`（system / vendor / odm / product / system_ext 五处）
- 安全补丁 → `ro.build.version.security_patch` = **`2026-06-01`**（与目标机 Redmi Turbo 5 Max 实测一致），`ro.vendor.build.security_patch` = `2026-02-01`
- **新增 32 位 ABI 支持**：`ro.*.product.cpu.abilist` 补上 `armeabi-v7a,armeabi`，并新增 `ro.bionic.2nd_arch=arm`、`dalvik.vm.isa.arm.variant=cortex-a55`
- 无线区域 → `cn`

### 4. SELinux 策略 `sepolicy`（+6317 字节）

新增小米 **mslg（MSLG rootfs keeper）** 相关内容，属国内固件独有的安全机制：

```
新增类型: mslg_app  mslg_init  mslg_init_exec  mslgd_exec  mslg_rootfs_file  vendor_mslg_prop
新增路径: /dev/msl  /data/rootfs  /data/vendor/mslg  /(odm|vendor/odm)/etc/assets/mslgusrimg
新增属性: vendor.mslgrootfs.isready  vendor.mslg.rootfs.version  persist.vendor.unzip.mslgrootfs
```

### 5. 安全上下文文件

| 文件 | 变化 |
|---|---|
| `vendor_file_contexts` | +14 行（mslg 相关文件上下文） |
| `vendor_property_contexts` | +7 行（mslg 相关属性上下文） |
| `system/etc/copylib.txt` | 库清单顺序重排（内容等价） |

### 6. 未变动的部分

- **DTB 段**：535963 字节，两版 `sha256` **完全一致**，硬件描述未改动
- **文件清单**：两版均 1250 个 cpio 条目，目录项顺序完全一致
- 容器结构：均为 `VNDRBOOT` header v4，64 MB，page size 4096，ramdisk 使用 zstd 压缩

> 完整的逐文件差异数据见 [`docs/DIFF.md`](docs/DIFF.md)。

---

## 二、文件清单

| 文件 | 说明 |
|---|---|
| `OrangeFox-R12.0-Unofficial-dash-CN.img` | 本版 Recovery 镜像（刷入 vendor_boot） |
| `docs/DIFF.md` | 与上游的完整差异对比报告 |
| `docs/DIFF_EN.md` | 差异对比报告（英文） |
| `scripts/` | 用于复现差异分析的 Python 脚本 |
| `checksums/` | 上下游镜像校验值 |

---

## 三、校验值

刷入前请务必核对：

```
# 上游原版
e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f  OrangeFox-R12.0-Unofficial-dash.img

# 本版（国内适配）
（见 checksums/ 目录，或仓库 Releases 附件）
```

---

## 四、安装方法

### 前置条件

- Bootloader 已解锁
- 已安装 fastboot（Android SDK Platform Tools）
- **已确认当前固件基线为 `OS3.0.305.0.WPLCNXM`**

### 步骤 1：确认当前分区槽位

```bash
adb devices
adb reboot bootloader
fastboot getvar current-slot
```

### 步骤 2：刷入对应槽位

```bash
# 若当前槽位为 a
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img

# 若当前槽位为 b
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img

# 保险起见，两个槽位都刷也可以
fastboot flash vendor_boot_a OrangeFox-R12.0-Unofficial-dash-CN.img
fastboot flash vendor_boot_b OrangeFox-R12.0-Unofficial-dash-CN.img
```

### 步骤 3：进入 Recovery

```bash
fastboot reboot recovery
```

### 回滚方法

刷回官方固件对应的 vendor_boot 分区镜像即可恢复原状。**操作前请务必备份原始 `vendor_boot_a` / `vendor_boot_b` 分区**：

```bash
# 刷机前先备份（强烈建议）
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_a of=/sdcard/vendor_boot_a.img"
adb shell su -c "dd if=/dev/block/by-name/vendor_boot_b of=/sdcard/vendor_boot_b.img"
adb pull /sdcard/vendor_boot_a.img
adb pull /sdcard/vendor_boot_b.img
```

---

## 五、功能支持

| 功能 | 状态 |
|---|---|
| Recovery 启动 | ✅ |
| 显示与触控 | ✅ |
| FBE 元数据解密（PIN / 密码） | ✅ |
| 内部存储访问 | ✅ |
| MTP / ADB / sideload | ✅ |
| 备份 / 恢复 | ✅ |
| ZIP 与镜像刷入 | ✅ |
| 重启模式切换 | ✅ |
| FastbootD | ✅ |
| USB OTG 外接存储 | ✅ |
| 振动反馈 | ✅ |
| 手电筒 | ✅ |
| 截图 | ✅ |

> 上游声明：AOSP / LineageOS 安装包为实验性功能，破坏性操作（Format Data、Repair/Resize/Change FS）未经完整运行时验证认证。本仓库同样沿用该声明。

---

## 六、上游仓库与致谢

本项目的所有原始工作均来自上游作者，本仓库仅做国内机型适配与差异记录：

**上游仓库**：[https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery](https://github.com/rakarizaldy-id/android_device_xiaomi_dash-recovery)
**上游版本**：`R12.0-dash-v1.1`
**上游作者**：[rakarizaldy-id](https://github.com/rakarizaldy-id)

致谢：

- [OrangeFox Recovery Project](https://gitlab.com/OrangeFox)
- [TeamWin Recovery Project](https://twrp.me/)
- [Android Open Source Project](https://source.android.com/)
- [rakarizaldy-id](https://github.com/rakarizaldy-id) — 上游 dash 设备树与 Recovery

---

## 七、许可与免责

本项目对上游衍生部分沿用相同许可。**本仓库为个人适配折腾产物，不保证任何可用性与安全性，刷机风险自负。**