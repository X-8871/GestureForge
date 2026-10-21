# S3-T05-SW6 v10：传感器端去色（黑白）尝试 4 个变体 ELF（task-10）

日期：2026-10-21（UTC+8）｜基线 HEAD：`65f2b6b9625a788e99f2808df69ec01962ec4e68`｜未提交 Git｜**只构建：未上板/未下载/未烧 QSPI**

用途：Wong 决定“试试黑白能不能接受”（手势识别不需要颜色，黑白可直接消除偏黄观感）。
优先走**传感器寄存器**（不动 PL）：4 个编译期变体各刷一次，看画面是否变黑白。

## 1. 四个 ELF（文件名固定）

| 文件名 | 编译期配置 | SHA-256（306,272 B） |
|---|---|---|
| `an5642_j11cmos2_v10_read.elf` | `S3_GRAY_TRY=0` 只回读不写 | `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073` |
| `an5642_j11cmos2_v10_sat0.elf` | `S3_GRAY_TRY=1`：`0x5583=0x5584=0x00` | `8cc925896da0b5847a7560b2135d9f406f45834e53eebf711e9b88eb21bc439c` |
| `an5642_j11cmos2_v10_bw40.elf` | `S3_GRAY_TRY=2`：`0x5580=(rb&~0xC0)|0x40` | `d951d328055dcc6c08a52e59fee37808a728e1f0a12eff1f2894aa4ca69978c4` |
| `an5642_j11cmos2_v10_bw80.elf` | `S3_GRAY_TRY=3`：`0x5580=(rb&~0xC0)|0x80` | `2eb4104a799d733c63ea41e39e796797f8078b249c1a5ece55690f2a932aaf15` |

目录 `tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/`；**5 次 make 全部退出码 0**。

## 2. 编译行（原文；完整见 `elf_build_evidence.txt`）

```
v10_read : arm-none-eabi-gcc -O2 -c -DS3_GRAY_TRY=0 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
v10_sat0 : arm-none-eabi-gcc -O2 -c -DS3_GRAY_TRY=1 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
v10_bw40 : arm-none-eabi-gcc -O2 -c -DS3_GRAY_TRY=2 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
v10_bw80 : arm-none-eabi-gcc -O2 -c -DS3_GRAY_TRY=3 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
对照（非交付）: arm-none-eabi-gcc -O2 -c -mcpu=cortex-a9 … -c display_demo.c …   ← 无 -D
```

* **源码默认值证明**：不带 `-D` 构建的 `…_v10_read_default.elf` 与官方 `v10_read`（显式 `=0`）**逐字节相同**（同为 `1457cda4…`）。
* 分支机器证据（ELF 内字符串计数，read/sat0/bw40/bw80）：`TRY0note 1/0/0/0`、`TRY1note 0/1/0/0`、`TRY2note 0/0/1/0`、`TRY3note 0/0/0/1`；
  `SKIPPED reg=5583` 仅 sat0=1，`SKIPPED reg=5580` 仅 bw40/bw80=1；四个 ELF 都保留 v9 的 `S3_DIAG9_PAD=` 回读行。

## 3. 构建方式（遵守“只跑 make”，与 task-9 重型构建串行）

* **只运行了 make**（`arm-none-eabi-gcc`、`make` 来自 Vitis 2026.1）；**未运行 sdtgen/HSI，未运行任何 Vivado 综合/实现**。
* 应用目录**从厂商源全新铺开**，BSP/`lscript.ld`/`Makefile` 复用 v9 构建目录（那是标准入口用**同一份 SOF 修复 XSA** 生成的）；
  脚本先校验 XSA 副本哈希 `1f5b138e…cb0e3`、pristine `display_demo.c` 哈希 `1e2c74f1…a985`，再 `git apply -p1`（exit 0），
  补丁后源码哈希 `e5fafa2e…aa377`（与生成器 verify 副本一致）。
* **踩到并已修掉的坑**（保留在日志里）：首版把 Vitis 的 `gnuwin` 目录放在 `PATH` 前面，那里的 **Windows `cp.exe` 遮蔽了 MSYS coreutils**，
  使“覆盖式铺开源码”静默失效（`cp` 返回 0 但没覆盖）→ 补丁应用失败。修法：Vitis 路径放到 `PATH` 末尾（`cp=/usr/bin/cp`）+ 全新目录铺开。

## 4. 四档去色策略与判读

| TRY | 动作 | 风险/预期 |
|---|---|---|
| 0 | 只回读（`0x5580/0x5583/0x5584`） | 先看真实值（厂商 init 表：`0x5580=0x06`、`0x5583=0x40`、`0x5584=0x10`） |
| 1 | `0x5583=0x5584=0x00`（U/V 饱和置 0），`0x5580` 不动 | **风险最低**：ISP 结构不变，只把色度信息归零 → 预期画面接近灰阶 |
| 2 | `0x5580[7:6]=10` | 依赖手册语义；若无效/花屏，用 UART 的 before/after/readback 确认写入本身生效 |
| 3 | `0x5580[7:6]=11` | 同上，另一编码 |

统一打印（四档都有）：

```
S3_DIAG10_GRAY=TRY=%d 5580 before=0x%02X after=0x%02X readback=0x%02X | 5583 before=0x%02X after=0x%02X readback=0x%02X | 5584 before=0x%02X after=0x%02X readback=0x%02X write_status=%d
```

外加一行 `S3_DIAG10_GRAY_NOTE=TRY<n>_…` 标明本次编译进的是哪一档（便于确认手里刷的是哪个 ELF）。
读失败则跳过对应写入并打印 `S3_DIAG10_GRAY_SKIPPED reg=…`，`write_status=-2`（沿用 v7~v9 的安全原则）。

**判读**：`after` 与 `readback` 一致 ⇒ 写入生效；画面变黑白 ⇒ 该档可用。
若某档把画面弄坏，复位或重跑应用即可恢复（厂商 init 表会重写 `0x5580=0x06`/`0x5583=0x40`/`0x5584=0x10`）。

## 5. 命令与退出码（全 0）

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 v5 补丁**逐字节相同** |
| `v4`/`v6`/`v7`/`v8`/`v9` 回归 | 0 / 0 / 0 / 0 / 0 | 分别与 v4/v6/v7/v8/v9 补丁**逐字节相同** |
| `v10` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D10_*` 全 True |
| 厂商副本 `git apply --check` | 0 | 只含 `display_demo.c` |
| `make_only_build.sh`（5 次 make） | 0 | `ALL_V10_MAKE_OK` |

## 6. 交付物哈希

* 补丁 `board/stage3/software/sensor/s3_t04_app_diag_v10.patch`（608 行，只改 display_demo.c）：见 `build_report.json`
* 生成器 `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v10`，默认仍 `v5`）：同上
* 证据 `elf_build_evidence.txt` = `77ba67b4e1a0f98d840f4f2d10d8db3850f0f69da141c10794a65ef2556608e9`

## 7. 限制 / 未执行

* **未上板、未下载、未采集 UART** → `S3_DIAG10_*` 实际数值与“黑白是否可接受”的结论尚未产生；本卡交付的是可上板 ELF。
* 未运行 sdtgen/HSI（按“只跑 make”）；未运行 Vivado 综合/实现；未烧 QSPI；未提交 Git；未查 OV5640 手册核对位定义。
* TRY=2/3 只改 `0x5580[7:6]`，其余位保持回读值；若语义与任务卡口径不同，可能“无明显变化”或异常花屏。
* v10 保留 v6 的 5 次指纹采样，UART 时长仍 ≥30 s；G3 未闭合。