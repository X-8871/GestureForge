# S3-T05-SW8 v12：传感器彩条测试图案 + v11 取帧保持（task-14）

日期：2026-10-22（UTC+8）｜基线 HEAD：`a9cd300fc7eef50a4b51e2e117be0fd895edb50e`｜未提交 Git｜**只构建：不上板/未下载/未烧 QSPI**

用途：第三方建议用**已知颜色**的测试图案经**同一条链路**转储，判断“真缺色相/缺位”还是“仅 R/B 顺序或位拼接错”。
本变体 = **传感器内置彩条 ON（`0x503D=0x80`）** + **v11 的停帧保持**（t≈20 s 停 S2MM、240 s 静止窗口）。

## 1. 唯一交付 ELF

| 文件名 | 配置 | SHA-256（310,368 B） |
|---|---|---|
| `an5642_j11cmos2_v12_bars_freeze.elf` | 不带任何 `-D` | `527a74fca6ea0774c34625015720a5163fc58557d44c64e29428700fd09845c5` |

目录 `tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/`；make 退出码 0（`V12_MAKE_OK`）。

编译行（原文见 `elf_build_evidence.txt`）：

```
arm-none-eabi-gcc -O2 -c -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -c display_demo.c -o display_demo.o …   ← 无 -D
```

## 2. 时间线（UART 上照这个用）

| 时刻 | 事件 |
|---|---|
| 上电后（`sensor_init()` 之后） | `S3_DIAG12_BARS=503D before=0x.. after=0x80 readback=0x.. write_status=0` ⇒ 彩条已开 |
| t≈5 / 10 / 15 s | 3 次指纹 `S3_DIAG6_SAMPLE/SR/FP`（此时采到的**就是彩条画面**） |
| t≈15 s | `S3_DIAG6_SENS`（只读传感器回读） |
| **t≈20 s** | **停 S2MM**：`S3_DIAG11_HALT=1 … FB=0x… FB_BYTES=0x2A3000 t=…` ⇒ 帧缓冲静止 |
| t≈50…260 s | 每 30 s 一次 `S3_DIAG11_HOLD t=<秒> SR=…`（8 次 = 240 s）→ `S3_DIAG11_HOLD_DONE … frozen=1` |

**JTAG 整帧窗口 ≈240 s**（看到 `S3_DIAG11_HALT=1` 起）；起点看 `FB=`（预期 `0x00110C00`），长度 `0x2A3000`。
停住后画面定格（预期）；彩条可用复位/重跑应用恢复（厂商 init 表会重写 `0x503D`）。

## 3. 彩条写入协议（卡面要求）

* 先 `s3_diag5_i2c_read16(0x3C, 0x503D, &before)` **回读原值** → `i2c_reg16_write(…, 0x503D, 0x80)` → **再回读**；
* 打印：`S3_DIAG12_BARS=503D before=0x%02X after=0x%02X readback=0x%02X write_status=%d`；
* **读失败即跳过写入**并打印 `S3_DIAG12_BARS_SKIPPED reg=503D reason=read_failed`（`write_status=-2`），不写不可信值（v7~v11 安全原则）。
* 说明：v6 的编译期开关 `S3_TESTPATTERN` 在本 ELF 中为 0，因此 UART 里还会看到 `S3_DIAG6_TESTPATTERN=OFF`；
  **`0x503D` 的实际写入以 `S3_DIAG12_BARS` 行为准**（两处都写同一个值，语义一致）。

## 4. 第三方实验怎么判读

1. 刷本 ELF → 确认 `S3_DIAG12_BARS` 的 `readback=0x80`（写入生效）；
2. 等 `S3_DIAG11_HALT=1` → 在 240 s 窗口内用既有 JTAG 脚本导出整帧；
3. 按彩条的**已知颜色**逐条比对 R/G/B：
   * 色相顺序正确、但某通道幅度系统性偏低 / 最高位恒 0 ⇒ **真缺色相/缺位**；
   * 某两条通道整体互换、或 5/6 位字段错位拼接 ⇒ **顺序 / 位拼接错**。

彩条是纯色块，比人像/实景更容易看出这两类差异；且它与正式链路完全同路（DVP→IP→VDMA→DDR），
所以“图案已知、链路未知”的部分才可判读。早前 v6 彩条上板分析（`t05_color_analysis_20261020_r01`）记录过
“色相与顺序正确、蓝约 42%”，本卡不重复该结论，只提供同一链路下可复核的彩条取帧。

## 5. 命令与退出码（全 0）

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 v5 补丁**逐字节相同** |
| `v4`/`v6`/`v7`/`v8`/`v9`/`v10`/`v11` 回归 | 0×7 | 分别与各自补丁**逐字节相同** |
| `v12` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D12_*` 全 True，`VERIFY_D12_INV_COUNT=2` |
| 厂商副本 `git apply --check` | 0 | 只含 `display_demo.c` |
| `make_only_build.sh` | 0 | XSA/pristine 双哈希校验 + `git apply`=0 + make=0 → `V12_MAKE_OK` |

## 6. 无多余写测试（ELF 字符串层面）

应存在（各=1）：`S3_DIAG12_BARS=503D before=`、`S3_DIAG12_BARS_SKIPPED reg=503D`、`S3_DIAG11_HALT=1`、
`S3_DIAG11_HOLD t=`、`S3_DIAG11_HOLD_DONE`、`S3_DIAG9_PAD=3017=`、`S3_DIAG10_GRAY_NOTE=TRY0_read_only_no_write`、
`S3_DIAG6_FP`、`S3_DIAG6_SENS=4202=`、`S3_DIAG6_TESTPATTERN=OFF`。

应为 0（本卡只新增彩条写）：`S3_DIAG6_TESTPATTERN=ON`、`S3_DIAG7_AWB_OFF=ON`、`S3_DIAG8_WB=MANUAL`、
`S3_DIAG9_FIX=301D`、`S3_DIAG9_ORDER=NOT_RESTORED`、`S3_DIAG10_GRAY_SKIPPED` —— 证据文件里逐条列出。

## 7. 交付物哈希

* 补丁 `board/stage3/software/sensor/s3_t04_app_diag_v12.patch`（682 行，只改 display_demo.c）= `2517c98a3b9b328c51b194c8ff4bd3ac54fefa384700a55c44487314666556d8`
* 生成器 `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v12`，默认仍 `v5`）= `f7aa1dff7fcdfaaf1df34e28fdf92f2c1ca0c8f787a04579bd46f1b49aeddbe8`
* 证据 `elf_build_evidence.txt` = `b4784adb555d9b7b5c7d6d03966d1d3899d04c9c79dd1f2576ebffe90d702b0e`
* 更完整的现场哈希与命令原文见 `build_report.json`

## 8. 限制 / 未执行

* **未上板、未下载、未采集 UART、未做整帧导出** ⇒ `S3_DIAG12_*` 实际数值与判读结论尚未产生。
* 未运行 sdtgen/HSI（按“只跑 make”）；未跑 Vivado 综合/实现；未烧 QSPI；未提交 Git。
* 未查 OV5640 手册核对 `0x503D` 位定义与彩条颜色顺序（沿用任务卡与早前上板记录）。
* 停 S2MM 后画面定格（预期）；`t≈20 s` 为软件计时，实际时刻以 `S3_DIAG11_HALT t=` 为准。
* BSP 为复用既有同 XSA 构建树产物（已哈希校验）；若需完全走标准入口重建，建议另开一轮（预期字节一致）。