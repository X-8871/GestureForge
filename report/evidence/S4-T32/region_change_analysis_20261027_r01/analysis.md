# 候选区 6 字节差异：地址归属分析（region_change_analysis_20261027_r01）

- 结论：**NEITHER_ACCOUNTED**（三选一结果）
- 依据：`address_attribution.json`（逐地址归属 + readelf/nm 段表 + 2B PL 登记窗 + 阶段4 分配表）

## 6 个差异地址
| 地址 | 参考 | 当前 | 清零位 | 归属 |
|---|---|---|---|---|
| `0x12b09e1b` | `0xd3` | `0xc3` | [4] | STAGE4_CANDIDATE_OR_META |
| `0x12b4805b` | `0x4b` | `0x43` | [3] | STAGE4_CANDIDATE_OR_META |
| `0x12b4906a` | `0x34` | `0x30` | [2] | STAGE4_CANDIDATE_OR_META |
| `0x12b4930e` | `0xdc` | `0xd8` | [2] | STAGE4_CANDIDATE_OR_META |
| `0x12bc8f82` | `0x9f` | `0x9d` | [1] | STAGE4_CANDIDATE_OR_META |
| `0x12bc9f5b` | `0xdc` | `0xcc` | [4] | STAGE4_CANDIDATE_OR_META |

## 三方核对
1. **init.elf**：`.text 0x0–0x1dd8`、`.data 0x1e40–0x39c4`、`.mmu_tbl 0x4000–0x7fff`、`.bss 0x9040–0x9203`、`.heap 0x9208–0xb20f`、`.stack 0xffff0000+`；**6 个地址均不在其中**（相距 >280 MB）。
2. **2B PL 已登记写窗**：arena `0x10000000–0x12000000`（ARENA_BYTES `0x02000000`，CSR 0x030/0x034）、weights `0x00100000+5,903,100`、feature `0x01000000–0x01ADADB8`、head13 `0x11A46100`、head26 `0x11AD5E80`；**均不含 6 个地址**（arena 恰好止于候选区起点 `0x12000000`）。
3. **阶段4 区域**：`raw_frame 0x12000000–0x12C00000`、`raw_meta 0x12C00000–0x12C08000`；6 个地址**正落在 raw_frame 内**。

## 解释与限制
- 三选一 ⇒ **NEITHER_ACCOUNTED**：已有登记写入方（init.elf、2B PL 窗）都无法解释，且我方本窗口对该区**只读**。
- 6 处均为**单 bit 清零**，形态上与"数据保持/读写位"类问题一致；但**未证明**，需 bring-up 窗口的只读 bisect 与读写位测试。
- 离线不可观测 PL 内部未文档化写行为；不得据此断言是 DDR 硬件问题。

## 对结论的影响
- `M3 = FAIL/未闭合`（保持不变，不得写 PASS）；
- `M2` 的"候选区空闲/不相交"论证**待重审**；
- 该异常并入 4-D bring-up 窗口处理。
