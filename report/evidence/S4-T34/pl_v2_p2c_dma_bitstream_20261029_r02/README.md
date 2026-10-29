# P2c r02 候选位流（RunId `pl_v2_p2c_dma_bitstream_20261029_r02`）

- 构建：2026-10-29 16:15:21 -> 16:29:56（UTC+8，约 14.6 min），Vivado v2026.1（BASIC）
- **状态：BUILD_ONLY（构建完成，未上板）**；`ENABLE=0`；未烧 QSPI；不改线；不主张 G3/G4/G5。
- 取代 `pl_v2_p2c_dma_bitstream_20261029_r01`（r01 的 AXI DMA LENGTH 位宽 14 bit，功能不可用；见 r01 的 ERRATUM）。

## 1. 本轮修复（rev-s5 复审 CHANGES_REQUIRED 的两项）

| 编号 | 问题 | 修复 | 关闭证据 |
|---|---|---|---|
| B1（功能阻断） | `c_sg_length_width=14` ⇒ S2MM 只收 16,383 B，519,168 B 被截断成 11,264 B | `bd_p2c.tcl` 加 `CONFIG.c_sg_length_width {23}` | 生成 netlist：`wire [22:0] s2mm_length`（`logs/dma_length_width_check.txt`） |
| B2（证据阻断） | `SRC_BASE` 改动无仿真回归 | 改为可参数化：engine/wrapper 默认 `0`（与冻结基线一致），BD 覆盖 `0x12000000` | 3 个冻结 TB 原样复跑：`regression/results.tsv` → `P2C_TB_REGRESSION=PASS cases=3 fails=0`；engine `cycles=2655174`、`FNV dut=gold=0x39a2a8950a11322e` |

## 2. 产物身份

| 产物 | 字节 | sha256 |
|---|---|---|
| `s4d_p2c.bit` | 4,045,770 | `022f48fbf78722424a7c10a3b2fca6c26d2ce7cbc89e0f8dd1dbd02a99d52ca4` |
| `s4d_p2c.xsa` | 353,213 | `8051dd485d9c76fdbc00dff99dbf1716d1f613cebdee40975ec85469de61bf4c` |

## 3. 实现结果（50 MHz）

- 时序：**WNS +0.039 ns / WHS +0.042 ns**（TNS/THS = 0）。
- 资源：| Slice LUTs | 24838 | 0 | 0 | 53200 | 46.69 | / | Slice Registers | 11574 | 0 | 0 | 106400 | 10.88 | / | Block RAM Tile | 33.5 | 0 | 0 | 140 | 23.93 | / | DSPs | 158 | 0 | 0 | 220 | 71.82 |。
  （DSP 余量很小；E 项合并部署的资源结论必须用本实测值重算，而不是"看起来装得下"。）
- DRC：0 error（route 后 `report_drc` 通过）。

## 4. 设计要点（与冻结输入的全部差异见 `inputs/P2C_R02_vs_frozen.patch`）

1. `s4d_preproc_engine_v2.sv`：加参数 `SRC_BASE`（默认 0），3 处 `rd_addr` 加基址。
2. `s4d_preproc_v2_wrap.sv`：加同名参数并透传给 engine（BD 覆盖 `0x12000000`）。
3. 新增打包器 `s4d_axis8_to_axis64`（8b→64b，小端、TKEEP=0xFF、TLAST 透传；xsim 自检 PASS）。
4. BD：`AXI DMA S2MM`（非 SG，MM/STREAM 64b，LENGTH 23 bit）→ `smc_data` 第 3 从口 → HP0；寄存器 `0x43C20000`。

## 5. 未做 / 限制（引用本产物时必须一起引用）

1. **未上板**：无板级判据；`tensor_crc32=0x5B183B50` 仍是目标。
2. 应用侧 DMA 编程未在本证据内验证（另包：`D:\tmp\lead\s4t35_pl_preproc_20261029_r01\`）；上板必须遵守：
   halt 态写 `DA(0x48)→RS=1→LENGTH(0x58)=519168` → 回读 LENGTH 自检 → 再触发 preproc START；
   完成判据用 `DMASR.IOC(bit12)`/`Idle(bit1)`（**不要**用 preproc `done_sticky`，尾部最多 16 B 可能未落 DDR）。
3. 无整链仿真（引擎→打包→DMA→DDR）。
4. `SRC_BASE` 是参数不是寄存器；换帧缓冲地址需重建位流。
5. 未冻结、未进入冻结集；独立复审的 delta 结论见 `D:\tmp\reviews\p2c_design_20261029_r01\REVIEW_DELTA.md`。
