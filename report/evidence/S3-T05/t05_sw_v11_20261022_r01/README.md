# S3-T05-SW7 v11：取帧应用（停 S2MM 保持静止 240 s，供整帧导出）（task-12）

日期：2026-10-22（UTC+8）｜基线 HEAD：`eb4599690249a26a311c82222643a64f26c2b74e`｜未提交 Git｜**只构建：不上板/未下载/未烧 QSPI**

背景：整帧经 JTAG 慢读时 VDMA 仍在写新帧 ⇒ 导出的是**撕裂帧**（Wong 看到的显示器画面正常，说明通路没问题，是读取方法问题）。
本变体在 **t≈20 s 停住 S2MM**，让帧缓冲**静止 240 s**，阶段总控在这段时间里读到的就是干净整帧。

## 1. 唯一交付 ELF

| 文件名 | 配置 | SHA-256（310,368 B） |
|---|---|---|
| `an5642_j11cmos2_v11_freeze.elf` | 不带任何 `-D`（所有写开关默认 0） | `c01133b1bb0204f07a5be215dbeb58ca0dcc627115cd3a06f1c56f9b21ca26c4` |

目录 `tmp/s3r06/t04_j11cmos2_elf_v11/elf_build/app/`；make 退出码 0（`V11_MAKE_OK`）。

编译行（原文见 `elf_build_evidence.txt`）：

```
arm-none-eabi-gcc -O2 -c -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -c display_demo.c -o display_demo.o …   ← 无 -D
```

## 2. 时间线（UART 上照这个用）

| 时刻 | 事件 |
|---|---|
| t≈5 / 10 / 15 s | 3 次指纹（`S3_DIAG6_SAMPLE`、`S3_DIAG6_SR`、`S3_DIAG6_FP`×3 区）——确认帧在动 |
| t≈15 s | `S3_DIAG6_SENS`（只读传感器回读，保留 v6 行） |
| **t≈20 s** | **停 S2MM**：`S3_DIAG11_HALT=1 CR_before=… CR_after=… SR=… HALTED_bit=… FRAME0=… STRIDE=… FB=… FB_BYTES=0x2A3000 t=…` ⇒ **帧缓冲从此静止** |
| t≈50…260 s | 每 30 s 一次 `S3_DIAG11_HOLD t=<秒> SR=… HALTED_bit=…`（共 8 次 = 240 s） |
| t≈260 s | `S3_DIAG11_HOLD_DONE holds=8 seconds=240 frozen=1` |

* **JTAG 整帧转储窗口**：看到 `S3_DIAG11_HALT=1` 起约 240 s。帧缓冲起点看该行 `FB=`（预期 `0x00110C00`），
  长度 `FB_BYTES=0x2A3000`（720 行 × 3840 字节 = 2,764,800）。
* 停 S2MM 后**显示器画面定格**（预期）；恢复办法：重写 CR 的 RS 位，或断电/重跑正常应用。

## 3. 实现要点

* `S2MM_CR` = `XPAR_AXIVDMA_1_BASEADDR + XAXIVDMA_RX_OFFSET(0x30) + XAXIVDMA_CR_OFFSET(0x00)` = **0x43010030**；
  读 CR → 写 `CR & ~XAXIVDMA_CR_RUNSTOP_MASK`（只清 RUN/STOP 位，保留其他位）→ 回读 CR（`CR_after`）与 SR（`HALTED_bit`）。
* 停**前**、停**后**各一次 `Xil_DCacheInvalidateRange(FB, 720*3840)`（`VERIFY_D11_INV_COUNT=2`），
  起点取 `dispCtrl.framePtr[dispCtrl.curFrame]`，避免把 CPU cache 里的陈旧行当成 DDR 内容。
* 保持阶段只**读** `S2MM_SR`，不再写任何寄存器；8×30 s = 240 s。

## 4. 无写测试证据（卡面要求）

ELF 内字符串矩阵：保留的只读/OFF 行各 =1（`S3_DIAG6_TESTPATTERN=OFF`、`S3_DIAG7_AWB_OFF=OFF`、`S3_DIAG8_WB=OFF`、
`S3_DIAG9_ORDER=OFF`、`S3_DIAG10_GRAY_NOTE=TRY0_read_only_no_write`、`S3_DIAG9_PAD=3017=`、`S3_DIAG11_HALT=1`、`S3_DIAG11_HOLD t=`）；
所有写测试路径 =**0**（`TESTPATTERN=ON`、`AWB_OFF=ON`、`WB=MANUAL`、`FIX=301D`、`ORDER=NOT_RESTORED`、`GRAY_SKIPPED`）
⇒ v6/v7/v8/v9/v10 的写开关全部保持默认 0，**本变体不做任何寄存器写测试**。

## 5. 命令与退出码（全 0）

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 v5 补丁**逐字节相同** |
| `v4`/`v6`/`v7`/`v8`/`v9`/`v10` 回归 | 0×6 | 分别与 v4/v6/v7/v8/v9/v10 补丁**逐字节相同** |
| `v11` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D11_*` 全 True，`VERIFY_D11_INV_COUNT=2`，`VERIFY_NO_D11_5SAMPLES=True` |
| 厂商副本 `git apply --check` | 0 | 只含 `display_demo.c` |
| `make_only_build.sh`（make run） | 0 | XSA/pristine 双哈希校验 + `git apply`=0 + make=0 → `V11_MAKE_OK` |

> 构建脚本首次调用时 harness 未回显输出且退出码 1（无日志残留）；改为分号串接后重跑成功并留下完整日志，本卡以该次日志为准。

## 6. 交付物哈希

* 补丁 `board/stage3/software/sensor/s3_t04_app_diag_v11.patch`（661 行，只改 display_demo.c）= `2e6428acffbc1ec9c905abf7f6838ab3d40e91665ae3bf7171317185f6f48537`
* 生成器 `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v11`，默认仍 `v5`）= `ff97c0a2a2a6940d906c62edb2f270c34d6136e724e15d6ead39a072afff94c2`
* 证据 `elf_build_evidence.txt` = `0e5b21d8c94c7f193a103c34a230f93b4240ebddcc6f74982cc3aa97f03b0712`
* 证据 pack 的现场哈希与命令原文见 `build_report.json`

## 7. 限制 / 未执行

* **未上板、未下载、未采集 UART** → `S3_DIAG11_*` 实际数值与整帧导出尚未产生；撕裂是否消除需上板实测确认。
* 未运行 sdtgen/HSI（按“只跑 make”）；未运行 Vivado 综合/实现；未烧 QSPI；未提交 Git；未做整帧 JTAG 导出。
* 停 S2MM 会让画面定格（预期）；`t≈20 s` 是软件计时，实际时刻以 `S3_DIAG11_HALT t=` 为准。
* 指纹从 v6 的 5 次减为 3 次（t≈5/10/15 s），之后停止采样（卡面要求）。
* BSP 为复用既有构建树产物（同一 XSA，已哈希校验）；若需完全走标准入口重建，建议另开一轮（预期字节一致）。
* 若 JTAG 转储超过 240 s，会读到静止窗口之外的内容；用心跳行判断窗口。