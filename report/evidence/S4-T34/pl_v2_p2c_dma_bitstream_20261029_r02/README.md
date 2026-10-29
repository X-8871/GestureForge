# P2c r02 候选位流（RunId `pl_v2_p2c_dma_bitstream_20261029_r02`）

- 构建：2026-10-29 16:15:21 -> 16:29:56（UTC+8，约 14.6 min），Vivado v2026.1（BASIC）
- **状态：BUILD_ONLY（构建完成，未上板）**；`ENABLE=0`；未烧 QSPI；不改线；不主张 G3/G4/G5。
- 取代 `pl_v2_p2c_dma_bitstream_20261029_r01`（r01 的 AXI DMA LENGTH 位宽 14 bit，功能不可用；见 r01 的 ERRATUM）。

## 1. 复审闭环（rev-s5）

| 轮次 | 结论 | 记录 |
|---|---|---|
| 初复审（r01 设计） | `CHANGES_REQUIRED`（B1 功能阻断 / B2 证据阻断 + 8 非阻断） | `D:\tmp\reviews\p2c_design_20261029_r01\REVIEW.md` |
| 增量复审（r02） | **`PASS`**：B1、B2 均关闭（复审者独立复跑 3 个 TB 并独立重算 golden FNV） | 同目录 `REVIEW_DELTA.md` |

两项关闭证据：
- **B1**：`bd_p2c.tcl` 加 `CONFIG.c_sg_length_width {23}` ⇒ 生成 netlist `wire [22:0] s2mm_length`（见 `logs/dma_length_width_check.txt`），
  519,168 B 只需 19 bit，不再被截断。
- **B2**：`SRC_BASE` 改为可参数化（engine/wrapper 默认 `0` = 冻结基线；BD 覆盖 `0x12000000`），
  3 个冻结 TB **原样**复跑 ⇒ `regression/results.tsv` 三行 `EQUIV`，engine `cycles=2655174`、
  `FNV1a64 dut=gold=0x39a2a8950a11322e`。判据已按复审建议强制 FNV。

## 2. 产物身份

| 产物 | 字节 | sha256 |
|---|---|---|
| `s4d_p2c.bit` | 4,045,770 | `022f48fbf78722424a7c10a3b2fca6c26d2ce7cbc89e0f8dd1dbd02a99d52ca4` |
| `s4d_p2c.xsa` | 353,213 | `8051dd485d9c76fdbc00dff99dbf1716d1f613cebdee40975ec85469de61bf4c` |

## 3. 实现结果（50 MHz）

- 时序：**WNS +0.039 ns / WHS +0.042 ns**（TNS/THS = 0）。
  ⚠ **余量仅 39 ps**（r01 为 226 ps）：后续任何加逻辑（VDMA/HDMI/叠加/应用改动）都必须重跑时序，不得沿用本结果。
- 资源：| Slice LUTs | 24838 | 0 | 0 | 53200 | 46.69 | / | Slice Registers | 11574 | 0 | 0 | 106400 | 10.88 | / | Block RAM Tile | 33.5 | 0 | 0 | 140 | 23.93 | / | DSPs | 158 | 0 | 0 | 220 | 71.82 |。
  DSP 余量仅 62；E 项合并部署的资源结论必须用本实测值重算。
- DRC：0 error；`write_bitstream completed successfully`。
- 说明：impl_1 启动时曾出现 `runme.log Permission denied`（与另一个残留 Vivado 实例争用同一工程目录所致）；
  终止残留实例后该 run 正常完成，最终 log 完整（82 KB+）、位流与 XSA 均产出、时序/DRC 均通过。**不是实现异常**。

## 4. 设计要点（全部差异见 `inputs/P2C_R02_vs_frozen.patch`）

1. `s4d_preproc_engine_v2.sv`：加参数 `SRC_BASE`（默认 0），3 处 `rd_addr` 加基址。
2. `s4d_preproc_v2_wrap.sv`：加同名参数并透传给 engine（BD 覆盖 `0x12000000`）。
3. 新增打包器 `s4d_axis8_to_axis64`：8b→64b，小端、TKEEP=0xFF、TLAST 透传。
   - 单元 TB：`PACKER_TB_RESULT=PASS beats=3`（`logs/packer_tb_output.txt`）
   - 反压/多帧 TB（本目录自建，替代复审者未被保留的对抗用例）：`PACKER_BP_TB_RESULT=PASS frames=8 bytes=104`
     （8 帧×13 B、随机反压最长连续低 37 拍、重建流逐字节相等、TLAST 计数与帧边界正确）
4. BD：`AXI DMA S2MM`（非 SG，MM/STREAM 64b，LENGTH 23 bit）→ `smc_data` 第 3 从口 → HP0；寄存器 `0x43C20000`。

## 5. 上板前必须遵守的应用契约（由 stage4-lead 的应用变体实现）

- 应用 ELF：`D:\tmp\lead\s4t35_pl_preproc_20261029_r01\build\s4d_ps_app_pl_dma.elf`
  sha256 `56c6967b0114347b0fce37966ddaabffde324257ee27c31b12507c764ac93100`（267,904 B，6 项编译退出码全 0）。
- 顺序：**halt 态**写 `DA(0x48) → DMACR.RS=1 → LENGTH(0x58)=519168`，回读 LENGTH 自检后，**再**写 preproc `CTRL.START`。
- 完成判据：`DMASR.IOC_Irq(bit12)` 或 `Idle(bit1)`；**不要**用 preproc `done_sticky`（尾部最多 16 B 可能未落 DDR）。
- 每帧：`DMACR=0` → 等 `Halted=1` → 重写 `DA/LENGTH` → `RS=1`（不跨帧保持 RS）。
- `done_sticky` 是 sticky：每轮先写 `IRQ_CLR(0x1C)=1`。
- B1 兜底：应用写 LENGTH 后立即回读，`!=519168` 即 `PCB_DMA_LENGTH_WIDTH_BAD` 并撤销 arm、不算 CRC。

## 6. 未做 / 限制（引用本产物时必须一起引用）

1. **未上板**：无板级判据；`tensor_crc32=0x5B183B50` 仍是目标而非结果。
2. 无整链仿真（引擎→打包→DMA→DDR）；依据是单元 TB + 反压 TB + 冻结 TB 回归 + 64/64 位宽 + 519168=64,896×8 整除。
3. `SRC_BASE` 是参数不是寄存器；换帧缓冲地址需重建位流。
4. 未冻结、未进入冻结集；本证据的复审为 rev-s5 的 delta PASS，**不代表 G2/G3/G4/G5**。
5. DMA 寄存器语义来源为 IP `component.xml` + Vitis 驱动（工具口径），**不是板上实测**；`DMASR` 复位值等仍 UNKNOWN。
