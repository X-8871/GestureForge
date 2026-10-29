# P2c 候选位流（RunId `pl_v2_p2c_dma_bitstream_20261029_r01`）

- 开窗/构建：2026-10-29 15:46:09 → 16:00:28（UTC+8，约 14 min）；工具 Vivado v2026.1（BASIC 许可自动生效）
- **状态：BUILD_ONLY（构建完成，未上板）**；`ENABLE=0`；未烧 QSPI；未改线；不主张 G3/G4/G5。
- 目的：给 preproc 的 `M_AXIS` 补上消费者（AXI DMA S2MM → HP0），并把源图基址改成 ABI 的 `0x12000000`，
  使"板上 `tensor_crc32=0x5B183B50` 对拍"在结构上可行（P2a/P2b 因无消费者而不可达）。

## 1. 产物身份（sha256）

| 产物 | 字节 | sha256 |
|---|---|---|
| `s4d_p2c.bit` | 4,045,770 | `0c8ec47660057da8d89a3a0b22ced2b04ba23a4f7a2ba3e51157fe97e2e8352f` |
| `s4d_p2c.xsa` | 353,184 | `3f0ed9eab27cc84790b884d14174b668024ba3e9fc0d05925908a4d19207e38e` |
| `inputs/bd_p2c.tcl` | 8,824 | `bad5cb10a102d9c9…`（全量见 `manifest.json`） |
| `inputs/SRC_BASE.patch` | 1,901 | `2255e06eabc764d7…` |

## 2. 实现结果

| 项 | 值 |
|---|---|
| 时序（50 MHz，place & route 后） | **WNS +0.226 ns**，**WHS +0.036 ns**（TNS/THS = 0） |
| Slice LUTs | 24,761 / 53,200 = **46.54%** |
| Slice Registers | 11,594 / 106,400 = 10.90% |
| Block RAM Tile | 33.5 / 140 = 23.93% |
| DSP | 158 / 220 = **71.82%** |
| DRC / 综合 | 0 errors、0 critical warnings（`logs/build_p2c_output.txt`） |
| 位流头 | `s4d_p2c_wrapper`（design id 与 XSA 一致） |

> DSP 余量仅 62 个。合并部署（阶段5 总闸）还要加视频通路（VDMA/HDMI/叠加），阶段5 侧"相加看起来装得下"的估算
> 未包含本候选的实测值——**E 项的资源结论需要用本实测数字重算**。

## 3. 设计变更（唯一两处）

1. `s4d_preproc_engine_v2.sv`：加参数 `SRC_BASE=32'h1200_0000`，3 处 `rd_addr` 改为 `SRC_BASE + sy*ROW_BYTES`
   （见 `inputs/SRC_BASE.patch`；其余 RTL 与冻结构建输入逐字节相同）。
2. 新增 `s4d_axis8_to_axis64`（8b AXIS → 64b AXIS，小端、TKEEP=0xFF、TLAST 透传），
   BD 内接 `s4d_0/M_AXIS → pack_0 → axi_dma_0/S_AXIS_S2MM`，`axi_dma_0/M_AXI_S2MM → smc_data/S02_AXI → HP0`。

地址（BD validate 实测）：preproc CSR `0x43C10000`（0x80）、2B CSR `0x43C00000`（64 KiB）、**DMA 寄存器 `0x43C20000`**（64 KiB）。

## 4. 自检证据

- 打包器单元 TB（xsim）：`logs/packer_tb_output.txt` → **`PACKER_TB_RESULT=PASS beats=3`**
  （2 个完整 beat 的字节序/keep/last + 1 个 3 字节尾 beat 的 keep=0x07）。
- BD：`bd_p2c.tcl` 内 `validate_bd_design` 通过（完整回显在构建日志里）。

## 5. 未做 / 限制（引用本产物时必须一起引用）

1. **未上板**：无任何板级判据；`tensor_crc32=0x5B183B50` 仍是目标而非结果。
2. **应用侧 DMA 编程未验证**：DMACR/S2MM_DA/S2MM_LENGTH/DMASR 的寄存器序列由应用变体实现（另包），本证据不含其验证。
3. **无整链仿真**：引擎→打包器→DMA→DDR 未做整链仿真；依据是单元 TB + 64/64 位宽无填充歧义 + 519,168=64,896×8 整除。
4. 源图基址是**常量参数**，不是可编程寄存器（换地址需重建）。
5. 打包器反压为"整 beat 未取走即不收字节"，未见死锁，但吞吐上限未测。
6. 位流为**候选**：未冻结、未进入冻结集、未经独立 Reviewer 关闭。

## 6. 复现

```bat
cd /d D:\tmp\lead\p2c_20261029_r01
vivado -mode batch -nojournal -source bd_p2c.tcl -tclargs build
```
`manifest.json` 的 `hash_basis=commit_blob`（本目录随 w4 提交进入 git，可按 commit blob 校验）。