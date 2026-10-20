# S3-T05-SW v6：帧缓冲 64 KB 指纹 + S2MM SR + 传感器回读 + 彩条测试图 ELF（task-3）

日期：2026-10-20（UTC+8）｜基线 commit：`41ee5ba003147d77349e8908c38b2efc97752ca8`｜未提交 Git｜**未上板**

## 1. 交付物与哈希（哈希全部见 `build_report.json`）

| 产物 | SHA-256 |
|---|---|
| 补丁 `board/stage3/software/sensor/s3_t04_app_diag_v6.patch`（只改 `display_demo.c`，302 行） | `4c7becc145c845d14b457e7917273f9c50120d9d513a0dc2612ecd057c08b960` |
| ELF `tmp/s3r06/t04_j11cmos2_elf_v6/elf_build/app/an5642_j11cmos2_v6.elf`（普通，`S3_TESTPATTERN=0`） | `1053673a35d3140d448528887f80bae3d79f5e239c67c7e54e193dbc694fccf7`（306,208 B） |
| ELF `…/an5642_j11cmos2_v6_tp.elf`（测试图，`-DS3_TESTPATTERN=1`） | `1594d67612d78cf8b1c0834973d6bb666a422d9260f2b6bcb3353fe265e7c5c5`（306,208 B） |
| 生成器 `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v6`；默认变体改为 `v5`） | `b7c91fbdfe7c27eae0ac509775bd3f74a0d36ef0826b49f946bac4b902fdf5f0` |

## 2. 命令与真实退出码

| 步骤 | 命令（原文见 `build_report.json`） | 退出码 |
|---|---|---|
| 默认变体回归 | `python make_app_diag_patch.py <vendor an5642_single> <…>/default_regen.patch <…>/scratch_default` | 0；输出与 `s3_t04_app_diag_v5.patch` **逐字节相同** |
| v4 回归 | 同脚本 + 末尾 `v4` | 0；输出与 `s3_t04_app_diag_v4.patch` **逐字节相同** |
| v6 生成 | 同脚本 + 末尾 `v6` → `s3_t04_app_diag_v6.patch` | 0；`GIT_APPLY_EXIT=0` |
| 干净应用校验 | 厂商副本上 `git apply --check -p1 <v6 patch>` | 0 |
| v6 ELF | `bash tmp/s3r06/t04_j11cmos2_elf_v6/run_v6_elf_build.sh`（内部 `run_stage3_vitis_elf.cmd <SOF_FIX_XSA> …`） | 0 |
| 测试图 ELF | `bash …/run_v6_tp_elf_build.sh` → `del display_demo.o && make -f Makefile.app EXEC=an5642_j11cmos2_v6_tp.elf "OPT_FLAGS=-O2 -c -DS3_TESTPATTERN=1"` | 0（日志里逐字可见 `-DS3_TESTPATTERN=1`） |

输入 XSA = `tmp/s3r06/t04_sof_fix_20261020_r01/design_1_wrapper.xsa`，SHA-256 `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3`（与任务卡一致）。

**开关生效的机器证据**：普通 ELF 只含字符串 `S3_DIAG6_TESTPATTERN=OFF`（ON 计数 0）；测试图 ELF 只含 `S3_DIAG6_TESTPATTERN=ON`（OFF 计数 0）。不是同一条运行时判断。

## 3. 指纹算法（五次采样完全相同）

* 范围：帧缓冲 +`0x000000`、+`0x080000`、+`0x100000` 三处，每处 **64 KB = 16384 个字**（三处都在 S2MM 实写区内：720 行 × stride 3840 B = 2,764,800 B = 0x2A3000）。
* `sum` = 32 位循环进位加和；`hash` = **反射式 CRC-32**（多项式 `0xEDB88320`、初值 `0xFFFFFFFF`、末取反，按小端 32 位字依次喂入）。
* **每次读取前** `Xil_DCacheInvalidateRange(p, 65536)`。
* `S3_DIAG6_FP t=<真实秒> site=<n> sum=0x%08X hash=0x%08X nz=%u`；`t` 由 `XTime_GetTime()/COUNTS_PER_SECOND` 测得（启动 S2MM 之后）。

## 4. 上板判读规则（v6 UART 输出）

1. `S3_DIAG6_FP` 三处 × 五次：**同一 site 的 sum/hash/nz 在 5 次之间是否变化**。
   * 全部相同 → 该 5 秒窗口内 64 KB 区内容未变（可能是静态画面，也可能是 DMA 停止）；
   * 有变化 → DMA 确实在这段时间往 DDR 写入了新内容（**活视频的必要证据**）。
2. `S3_DIAG6_SR` 每次采样的 `S2MM_SR`：`HALTED=0` 且 `FSZ_MORE/INT` 是否保持；`SOF 修复位流 + 应用启动路径` 之前实测为 `0x14810→0x15810`（sticky），清零后 20 s 无新错误。
3. `S3_DIAG6_SENS=4202=… 3008=… 503D=… 3035=… t=…`（t≈30 s）：`0x4202=0x00` ⇒ 传感器仍在 stream on；`0x503D=0x00` ⇒ 普通 ELF 没开测试图；`0x3035` 应与启动时一致。格式沿用任务卡的 `S3_DIAG6_SENS=…` 与 v5 的 `S3_DIAG5_SENS=4202=…` 风格。
4. **测试图 ELF 是决定性对照**：彩条是传感器产生的**静态**图案，其指纹应基本不变；
   若测试图 ELF 下指纹**有变化**（或画面出现彩条），即证明“传感器→PL→DDR→显示”整条通路在搬运真实数据；
   此时普通 ELF 指纹随挥手而变化，就同时排除了“静态场景偶发写入”。

## 5. 与 v5 的关系

* v5 补丁/ELF **未被改动**（默认变体回归逐字节相同即为证据）。v6 = v5 的辅助函数与一次性打印（`S3_DIAG5_REG/SR_DECODE/CFG/SENS`）+ **新增 S3_DIAG6 五次 64 KB 指纹采样**（取代 v5 的三次 16 KB 采样）+ 30 s 传感器回读 + 测试图开关。
* 需要 v5 的 `S3_DIAG5_NZ` 明细时仍用 v5 ELF `a54d0385…1b0c3e`。

## 6. 限制 / 未执行

* **未上板**：`S3_DIAG6_*` 的实际数值尚未产生；未下载、未运行、未做 UART 采集（上板由阶段总控执行）。
* 未跑 Vivado 综合/实现；未烧 QSPI；未提交 Git。
* 指纹扫描不是对 DMA 的原子快照（64 KB 扫描期间 DMA 可能仍在写），单次指纹是“复合值”；判读基于**五次之间的差异**，不是绝对值。
* 静态画面下指纹也会相同 → 指纹不变不能单独证明 DMA 停止；最终判据仍是挥手 + 测试图对照。
* 测试图 ELF 内的 `0x503D=0x80` 是**对传感器的写**（v6 其它诊断均为只读），`i2c_reg16_write` 失败会打印 `write_status` 供核对。
* 时间戳来自全局定时器，与 `sleep(1)` 名义值可能差几十毫秒。