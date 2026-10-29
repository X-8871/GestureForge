# P2d 合并计算体位流 —— 阶段5 收口说明（2026-10-29 r01）

- 位流 RunId：`s4d_p2d_merged_bitstream_20261029_r01`（构建证据在该目录）
- bit：`s4d_p2d_r01.bit`，4,045,770 B，sha256 **`58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3`**
- XSA：`s4d_p2d_r01.xsa`，326,940 B，sha256 **`4ebc631ed56c204f40d585acffa9a9aa0488938e99711c0cf8b5bad38426a3ab`**
- 状态：**候选位流（未冻结）**；未主张 G3/G4/G5

## 1. 设计构成

| 块 | 说明 |
|---|---|
| PS7 | FCLK0 = 50 MHz；M_AXI_GP0；**S_AXI_HP0（64-bit）供 2B 推理核**；**S_AXI_HP1（64-bit）供 preproc 读 + AXI DMA 写** |
| 控制面 | `smc_ctrl`（1S/3M）：preproc CSR `0x43C10000`（0x80）、2B CSR `0x43C00000`（64K）、AXI DMA `0x43C20000`（64K） |
| 2B 推理核 | `s2b_inference_top`（w2b 冻结源，只读引用）→ **M_AXI 直连 HP0**（不经 SmartConnect） |
| 预处理 | `s4d_preproc_v2_wrap`（`SRC_BASE=0x12000000`，即 ABI `raw_frame`）+ `s4d_axis8_to_axis64` 打包器 |
| DMA | AXI DMA（仅 S2MM、非 SG、MM 64-bit/STREAM 64-bit、**`c_sg_length_width=23`**）→ `smc_data`(2S/1M) → HP1 |

**与 P2c r02 的唯一差异（方向 A，2026-10-29 深夜定）**：2B 的 `M_AXI` 由"经 smc_data"改为"直连 HP0"，同时把 preproc 读 + DMA 写迁到 HP1。

理由（实测）：同一 M4-b ELF 在 P2b（2B 经 SmartConnect）上 85,899 ms 仍未完成；在 P2d 上 **47,287 ms** 完成。归因见 `s4d_p2b_infer_slowdown_20261029_r01/ANALYSIS.md`（2B 核是单 outstanding/单 beat 的延迟暴露型主端，SMC 会整条串行化）。

## 2. 实现结果

- 时序：**WNS +0.128 ns / WHS +0.036 ns**（50 MHz，`report_timing_summary` 已落盘）
- DRC：**0 error**（routed）
- 资源：LUT 23,451（44.08%）、FF 10,414（9.79%）、BRAM 33.5（23.93%）、**DSP 158（71.82%）**
  - ⚠ DSP 余量仅 62；阶段6 加视频链前必须重算资源与时序

## 3. 板上验证（四个窗口，全部 PASS）

| 项 | RunId | 关键结果 |
|---|---|---|
| 2B 性能恢复 | `s4d_m4b_p2d_20261029_r01` | `done=1/error=0/elapsed_ms=47287`（P2b 同 ELF：85,899 ms 超时） |
| 4-D 链路 | `s4d_chainlite_a_p2d_20261029_r01` | `pass=1/done=1/error=0/decode_rc=0/count=1/ack_idle=1/47,287 ms`；检测框与 r13 参考逐字段一致 |
| 预处理数据面 | `s4d_p2c_crc_on_p2d_20261029_r03` | `tensor_crc32=0x5B183B50 pass=1`、`length_reg=519168`（HP1 通路正确） |
| M4-b 收口 | `s4d_m4b_close_p2d_20261029_r02` | `pass=1/diff13=0/diff26=0/stale=1/gate=1/error=0/47,287 ms`；`TAIL13 after=0x5A5A0506`、`lane01_ok=1 lane23_ok=1` |

## 4. 使用约定（上板前必读）

1. 位流 sha 前缀核对：**`58C66CDB`**；XSA sha 前缀 `4ebc631e`。
2. 编程 PL 后**禁止 `rst -system`**（会清 PL → 应用首读 CSR 挂死 → DAP 粘连，只能整机断电）。
3. DMA 契约：halt 态 `DA(0x48)→DMACR.RS=1→LENGTH(0x58)=519168` → 回读 LENGTH 自检 → 再启动 preproc `CTRL.START`；完成判据 `DMASR.IOC(bit12)`/`Idle(bit1)`；每帧重武装。
4. 应用侧硬前提：**`core_timeout` 必须 ≥ 0xFFFFFFFF 级（85.9 s @50 MHz）**，旧冻结值 `0x40000000`（21.5 s）会必然超时；时间基座必须用 `S4D_MS_DIV`（带括号，333,333,343）。
5. `ENABLE=0`；不写 QSPI；不改线。

## 5. 边界与未做

- **未做**：视频链（VTC/axi_dynclk/VDMA/HDMI/叠加）→ 阶段6；摄像头实拍链；`ENABLE=1` 的 4-D 全链路实时流。
- 资源/时序结论只对 `58c66cdb…` 这一版有效，任何 RTL/BD 改动都必须重跑时序。
- 不主张 G3/G4/G5；本文件只是阶段5 收口说明，不替代冻结回归。