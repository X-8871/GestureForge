# P2d 合并位流证据清单（方向 A）

## 产物

- bit `s4d_p2d_r01.bit` sha256 `58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3`
- XSA `s4d_p2d_r01.xsa` sha256 `4ebc631ed56c204f40d585acffa9a9aa0488938e99711c0cf8b5bad38426a3ab`
- 时序 WNS +0.128 / WHS +0.036；DRC 0 error
- 资源 LUT 44.08% / FF 9.79% / BRAM 23.93% / DSP 158 (71.82%)

## 与 P2c r02 的差异

1. `infer_0/M_AXI` 直连 `ps7_0/S_AXI_HP0`（不经 smc_data）
2. `smc_data` 2S/1M：`s4d_0/M_AXI_RD` + `axi_dma_0/M_AXI_S2MM` → `ps7_0/S_AXI_HP1`
3. PS7 使能 `S_AXI_HP1`（64-bit）

## 文件

| 文件 | 字节 | sha256 |
|---|---|---|
| `report/evidence/S4-T34/s4d_p2d_merged_bitstream_20261029_r01/bd_p2d.tcl` | 10166 | `415e97929f28fe9fd01c897ad3fc3c74ef28666d6a56e69dd2ee8aa7db374ffa` |
| `report/evidence/S4-T34/s4d_p2d_merged_bitstream_20261029_r01/build_key_lines.txt` | 1576 | `3067f2c8c1a501826a69ecf65e132651b6d12c1041b5666cd3ea1218e6df57d3` |
