# S3-T05 上板诊断记录（v5 软件诊断 + 只读 DDR 复核 + fsync A/B）

时间：2026-10-20 12:2x–12:3x（UTC+8）｜执行：阶段3总控（唯一写入方 `D:\codex-worktrees\dbdf`）
基线：分支 `codex/stage3-video`，起始 HEAD `41ee5ba`

## 1. 输入（易失性 JTAG 下载，未烧 QSPI）

| 项 | 路径 | SHA-256 |
|---|---|---|
| bitstream | `tmp/s3r06/t04_camera_j11cmos2_20261020_r01/.../impl_1/design_1_wrapper.bit` | `7c6d2522df7596e63339624cbeae2112fcb4ca8ab39c94fc33899c1e23bade98` |
| XSA | `tmp/s3r06/t04_camera_j11cmos2_20261020_r01/design_1_wrapper.xsa` | `c598375429f88f17f9e80c680555ece943837257aee13ce25ce34a477566dd27` |
| ELF（v5 诊断） | `tmp/s3r06/t04_j11cmos2_elf_v5/elf_build/app/an5642_j11cmos2_v5.elf` | `a54d038530fc1a63ea84c897600195f68b7f14d7094f89951d6218e8fb1b0c3e` |

命令：`bash scripts/stage3_t05/run_t05_board_capture.sh <run_dir> <elf> diag5 120`（内部：后台抓 COM4@115200 → `run_jtag_download_t03.sh`（PS_RESET/FPGA_PROGRAM/PS7_INIT/DOW/RUN）→ 只读 `jtag_read_safe.tcl`）
退出码：`T05_DOWNLOAD_EXIT=0`、`T05_READ_EXIT=0`、`XSDB_EXIT=0`。下载九步全 `T03_DL_OK`。

## 2. 关键结果（UART 原文见 `uart_diag5.log`）

- **传感器在流**：`S3_DIAG5_SENS=4202=0x00`（stream on）、`3008=0x02`、`4740=0x20`（默认极性）、`503D=0x00`（未开测试图）、`3808/380A=1280/720`、`VTS=0x2E4`、`3035=0x21`（PCLK≈84 MHz）。
- **帧缓冲有真实且随时间变化的图像数据**（v5 已修 cache 语义：memset 后 flush、读前 invalidate）：
  `S3_DIAG5_NZ site=0 off=0x000000 nz=4095/4096`、`site=2 off=0x080000 nz=4096/4096`，
  三次采样（t≈5/15/25 s）数值均不同（例：site0 fb0 `08100008…` → `00100C00…` → `00080C00…`）。
  `site=1 off=0x400000`（超出 720 行实际写入范围）为 0，符合预期。
- **JTAG 直读物理 DDR 复核**（`jtag_read_safe.tcl`，halt→mrd→con）：
  `110C00: 00080C00 00001000 100C0010 00100C00 …`、`111C00: 0C28180C 180C2818 20202420 …`（非零真实像素）；
  与 CPU 视角一致 → **不是 cache 假象**。
- **S2MM 状态**：`CR=0x00018003`、`SR=0x00014810/0x00015810`、`VSIZE=0x2D0 HSIZE=STRIDE=0xF00 ADDR=0x00110C00`、`MM2S_SR=0x00011000`（显示通道运行、无错误）。
  位解码（依据 `xaxivdma_hw.h` + IP 元数据/HDL，见 `t05_sw_20261020_r01/s2mm_sr_decode_conclusion.md`）：
  `INT(bit4)=1`、`FSZ_MORE/ **SOFLate**(bit11)=1`、`ErrIrq=1`、其余错误位 0；Halted=0、Idle=0。
  → **数据与 TLAST 在流，但帧起始 TUSER 从未被 S2MM 认出**。
- **在线 A/B（`scripts/stage3_t05/jtag_s2mm_fsync_ab.tcl`）**：把 S2MM CR 的 FSYNC_SRC 由 `00`（同通道）改成 `10`（显式 tuser）→ 两例 SR 完全相同（`0x00014810`），DDR 首字相同。
  → **软件侧改 fsync 源无效**；SOF 确实未到达。

## 3. 结论与影响

1. **旧的“S2MM 没写数据 / 帧缓冲全 0 / 显示因此全黑”结论不成立**：零值是 v4 应用“第二次 memset 后未做 cache 维护”的 CPU 视角假象（脏零行还会回写覆盖 DMA 数据）。
2. **采集链路本体是通的**：传感器→DVP→厂商 IP→subset converter→S2MM→DDR 有活图像；显示 MM2S 从同一缓冲读取且运行无错、dynclk/v_tc 正常。
3. **唯一确定缺陷是帧同步**：TUSER(SOF) 未产生（厂商 IP 的 SOF 只在 `cmos_vsync` 下降沿产生；HREF/PCLK/数据都通，只有该路 VSYNC 疑似未到达 IP）。
   后果预期：S2MM 帧边界不成立 → 图像撕裂/滚动，而非黑屏。
4. **HDMI 物理画面仍未验证**（Wong 明确“没接显示器”）；本记录不构成 G3 通过。

## 4. 限制与未执行

- 未接显示器、未做电气测量；未烧 QSPI/非易失；未改厂商原件与主工作树。
- ILA 波形未取得：BASIC 许可拒绝网表插入 ILA（`ERROR [Vivado 12-29205] 'create_debug_core' … BASIC`），BD 路线尝试中有 Tcl 报错（见 `t05_ila_20261020_r01/`），已改派为“SOF 修复变体”构建。
- VSYNC 是否真的没有翻转，**未用 ILA 直接观测**；当前依据是“数据在流但 TUSER 不出现”的行为推断 + 引脚映射已独立核验正确。
- 帧同步修复变体（HREF 长间隔推导 SOF）在构建中，尚未上板。