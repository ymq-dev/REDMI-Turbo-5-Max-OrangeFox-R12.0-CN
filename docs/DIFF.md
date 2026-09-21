# 差异对比报告 · 上游原版 vs 国内适配版

本文档记录上游 `R12.0-dash-v1.1` 原版镜像与国内版 Redmi Turbo 5 Max 适配镜像之间的**完整差异分析结果**。

---

## 一、对比对象

| 项 | 上游原版 | 国内适配版 |
|---|---|---|
| 文件名 | `OrangeFox-R12.0-Unofficial-dash.img` | `REDMI Turbo 5 Max-OrangeFox R12.0-CN .img` |
| MD5 | `79961ca695cc8aba26dd69d87aad8756` | `f536c8419df2addcdf7e210fae654e78` |
| SHA256 | `e8c37606d30f41bc25384c5a948901f974f6d480b286e71227e7c76194b7a56f` | `ab6a722c0bae5682c9f4cfa8425b60ab5181e68529bcf3a0a3807ca44d90fd08` |
| 文件大小 | 67,108,864 字节（64 MiB） | 67,108,864 字节（64 MiB） |
| 目标机型 | POCO X8 Pro Max (dash) | Redmi Turbo 5 Max (dash) |
| 固件基线 | HyperOS `OS3.0.303.0.WPLIDXM` | HyperOS `OS3.0.305.0.WPLCNXM` |

> 说明：上游 img 与本仓库收到的 `attachment_7251546109930737606.img` 逐字节一致（MD5 相同），确认后者为上游原始包。

---

## 二、容器层结构对比

两版均为 **Android vendor_boot 镜像（header version 4）**，结构完全对齐：

| 字段 | 上游 | 国内版 | 是否一致 |
|---|---|---|---|
| 魔数 | `VNDRBOOT` | `VNDRBOOT` | ✅ |
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
| ramdisk 压缩方式 | zstd | zstd | ✅ |
| ramdisk 解压后大小 | 93,686,908 | 93,690,608 | ❌ (+3,700) |

### DTB 段

两版 DTB 段 **sha256 完全一致**（`2636d5a861e909f5bf32...`），硬件描述表未做任何改动。差异全部集中在 ramdisk 内部。

---

## 三、ramdisk 内容对比（cpio newc 归档）

| 指标 | 上游 | 国内版 | 结果 |
|---|---|---|---|
| cpio 条目总数 | 1250 | 1250 | 一致 |
| 目录项顺序 | — | — | **完全一致** |
| 仅上游存在 | — | — | **0 个** |
| 仅国内版存在 | — | — | **0 个** |
| 内容不同（sha256 不同） | — | — | **278 个** |

**结论：文件清单零增删，仅 278 个文件内容被替换。**

---

## 四、278 处差异分类

| 类别 | 数量 | 说明 |
|---|---|---|
| 内核模块 `.ko` | 272 | 全部重编译 |
| 文本配置 | 5 | fstab / prop.default / copylib.txt / 两个 contexts |
| SELinux 策略 | 1 | sepolicy |
| 其他二进制 | 0 | — |
| 目录/链接 | 0 | — |

### 4.1 内核模块（272 个，全部）

- 上游共 272 个 `.ko`，国内版 272 个，**100% 全部不同**
- 模块总体积：45,272,330 → 45,267,994 字节（**-4,336**，几乎无变化）
- vermagic 对比（抽样）：

| 模块 | 上游 vermagic | 国内版 vermagic |
|---|---|---|
| `mtk-mmc.ko` | `6.6.118-android15-8-g26238aa48eab-4k` | `6.6.118-android15-8-gdc1ec8d87f1c-4k` |
| `zram.ko` | 同上 | 同上 |
| `mi_memory.ko` | 同上 | 同上 |

> 内核版本号（6.6.118-android15）不变，仅**构建源码提交号变化**（`g26238aa48eab` → `gdc1ec8d87f1c`），说明内核模块跟随新固件内核基线整体重编译。

### 4.2 五个文本配置文件的体积变化

| 文件 | 上游 | 国内版 | 变化 |
|---|---|---|---|
| `first_stage_ramdisk/fstab.mt6991` | 9,537 | 9,978 | +441 |
| `prop.default` | 15,287 | 15,485 | +198 |
| `system/etc/copylib.txt` | 1,900 | 1,793 | -107 |
| `vendor_file_contexts` | 143,360 | 144,211 | +851 |
| `vendor_property_contexts` | 81,432 | 82,013 | +581 |
| `sepolicy` | 1,514,725 | 1,521,042 | +6,317 |

### 4.3 `fstab.mt6991` 详细差异

动态分区的挂载参数增加了 AVB 校验：

| 分区 | 上游参数 | 国内版参数 |
|---|---|---|
| `system` | `wait,slotselect,logical,first_stage_mount` | `wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey` |
| `system_ext` | 同上（无 avb） | 同上（补 avb_keys） |
| `vendor` | 同上（无 avb） | `wait,slotselect,avb,logical,first_stage_mount` |
| `product` | 同上（无 avb） | `wait,slotselect,avb,logical,first_stage_mount` |
| `mi_ext` | `...first_stage_mount,nofail` | `wait,slotselect,avb=vbmeta,logical,first_stage_mount,nofail` |
| `odm` | 无 avb | `+avb` |
| `vendor_dlkm` | 无 avb | `+avb` |
| `odm_dlkm` | 无 avb | `+avb` |
| `system_dlkm` | 无 avb | `+avb` |
| `vbmeta_system`（emmc 项） | `first_stage_mount,nofail,slotselect` | `first_stage_mount,nofail,slotselect,avb=vbmeta` |

其余 `/dev/block/by-name/*` 与 overlay 挂载项完全一致。

### 4.4 `prop.default` 详细差异

| 属性 | 上游 | 国内版 |
|---|---|---|
| `ro.system.build.date` | `Thu Aug 6 14:06:15 CST 2026` | `Thu Jul 2 22:40:44 CST 2026` |
| `ro.system.build.date.utc` | `1785996375` | `1783003244` |
| `ro.*.build.fingerprint` | `...:OS3.0.303.0.WPLIDXM:user/release-keys` | `...:OS3.0.305.0.WPLCNXM:user/release-keys` |
| `ro.*.build.version.incremental` | `OS3.0.303.0.WPLIDXM` | `OS3.0.305.0.WPLCNXM` |
| `ro.build.version.security_patch` | `2026-08-01` | `2026-02-01` |
| `ro.vendor.build.security_patch` | `2026-08-01` | `2026-02-01` |
| `ro.build.host` | `pangu-build-component-vendor-1043906-41w58-rdk84-qvw23` | `pangu-build-component-vendor-1002712-2pqgt-txkqg-kx6bn` |
| `ro.system.product.cpu.abilist` | `arm64-v8a` | `arm64-v8a,armeabi-v7a,armeabi` |
| `ro.system.product.cpu.abilist32` | （空） | `armeabi-v7a,armeabi` |
| `ro.bionic.2nd_arch` | （空） | `arm` |
| `ro.bionic.2nd_cpu_variant` | （空） | `cortex-a55` |
| `dalvik.vm.isa.arm.variant` | （无） | `cortex-a55` |
| `dalvik.vm.isa.arm.features` | （无） | `default` |
| `ro.vendor.radio.build_region` | `global` | `cn` |
| `vendor.mbrain.build.version` | `OS3.0.303.0.WPLIDXM` | `OS3.0.305.0.WPLCNXM` |

上述版本号类改动同时出现在 `system` / `vendor` / `odm` / `product` / `system_ext` **五个命名空间**。

### 4.5 `sepolicy` 详细差异（+6317 字节）

国内固件新增小米 **mslg（MSLG rootfs keeper）** 安全策略，新增字符串如下：

```
# SELinux 类型
mslg_app
mslg_app_devpts
mslg_app_userfaultfd
mslg_init
mslg_init_exec
mslg_rootfs_file
mslgd_exec
vendor_mslg_prop

# 文件上下文
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

# 属性上下文
vendor.mslgrootfs.isready       u:object_r:vendor_mslg_prop:s0
vendor.mslgrootfs.version       u:object_r:vendor_mslg_prop:s0
vendor.mslg.                    u:object_r:vendor_mslg_prop:s0
persist.vendor.unzip.mslgrootfs u:object_r:vendor_mslg_prop:s0
ro.vendor.mslg.rootfs.version   u:object_r:vendor_mslg_prop:s0
vendor.setup.mslgrootfs         u:object_r:vendor_mslg_prop:s0
```

### 4.6 上下文文件差异

**`vendor_file_contexts`（+14 行）**

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
（共 14 行，均为 mslg 相关）
```

**`vendor_property_contexts`（+7 行）**

```
vendor.mslgrootfs.isready       u:object_r:vendor_mslg_prop:s0
vendor.mslgrootfs.version       u:object_r:vendor_mslg_prop:s0
vendor.mslg.                    u:object_r:vendor_mslg_prop:s0
persist.vendor.unzip.mslgrootfs u:object_r:vendor_mslg_prop:s0
ro.vendor.mslg.rootfs.version   u:object_r:vendor_mslg_prop:s0
vendor.setup.mslgrootfs         u:object_r:vendor_mslg_prop:s0
#line 1 "vendor/xiaomi/proprietary/mslg/keeper/1.0/default/sepolicy/property_contexts"
```

**`system/etc/copylib.txt`**：库名清单顺序重排，同时 `libcap.so` / `libsysutils.so` 的路径行顺序调整；无库增删，内容等价。

---

## 五、差异总结

| 维度 | 结论 |
|---|---|
| 容器结构 | 完全一致（vendor_boot v4） |
| 硬件描述（DTB） | 完全一致，未改动 |
| 文件清单 | 完全一致（1250 项，无增删） |
| 内核模块 | 272 个全部按新基线重编译 |
| 分区挂载 | 补全 AVB 校验参数 |
| 系统属性 | 版本切换到 CN 基线、补 32 位 ABI、切 cn 区域 |
| SELinux | 新增小米 mslg 安全策略 |

**改动性质**：内核基线切换 + 国内固件策略适配，属于**同一设备（dash）跟随国内固件基线的重新编译**，而非简单的文件替换或重签名。

---

## 六、复现方法

仓库 `scripts/` 目录提供完整分析脚本，按顺序执行即可复现本报告：

```bash
# 1. 解析 vendor_boot 头部
python3 scripts/vb_parse.py

# 2. 提取 ramdisk 段
python3 scripts/extract_ramdisk.py

# 3. zstd 解压 → 得到 cpio
python3 scripts/unpack_ramdisk.py

# 4. 解析 cpio 并对比文件清单
python3 scripts/cpio_diff.py

# 5. 分类统计全部差异
python3 scripts/full_diff.py

# 6. 内核 vermagic / 上下文文件 / DTB 深度对比
python3 scripts/deep_diff.py

# 7. sepolicy 字符串差异
python3 scripts/sepolicy_diff.py

# 8. 提取关键文本文件做逐行 diff
python3 scripts/extract_targets.py
```

依赖：Python 3 + `zstandard` 模块（`pip install zstandard`）。