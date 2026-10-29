# 阶段5 证据索引（截至 2026-10-29 深夜）

本索引只列**阶段5 合并部署**相关证据；阶段4 的 4-D 链路证据见 `S4-T34` 其它目录。

## 1. 合并位流

| 版本 | RunId | 结论 | 备注 |
|---|---|---|---|
| P2c r02 | `pl_v2_p2c_dma_bitstream_20261029_r02` | 候选（preproc+打包+DMA+2B，2B 经 smc_data） | 数据面 CRC 已验；被 P2d 取代 |
| **P2d r01** | `s4d_p2d_merged_bitstream_20261029_r01` | **当前合并体**（方向 A：2B 直连 HP0、preproc+DMA→HP1） | bit `58c66cdb…`、XSA `4ebc631e…`；WNS +0.128 |

## 2. P2d 板上验证（四窗）

| 项 | RunId | 结论 |
|---|---|---|
| 2B 性能恢复 | `s4d_m4b_p2d_20261029_r01` | 47,287 ms（对比 P2b 85,899 ms 超时） |
| 4-D 链路 | `s4d_chainlite_a_p2d_20261029_r01` | **CHAINLITE_A_PASS** |
| 预处理数据面（HP1） | `s4d_p2c_crc_on_p2d_20261029_r03` | **P2C_TENSOR_CRC_MATCH**（`0x5B183B50`） |
| M4-b 收口 | `s4d_m4b_close_p2d_20261029_r02` | **M4B_PASS_TAIL13_CLOSED**（`pass=1`，尾字 lane 正确） |

## 3. 归因与决策（支撑上面结论）

| 主题 | RunId / 文件 | 结论 |
|---|---|---|
| P2b 慢 2× 归因 | `s4d_p2b_infer_slowdown_20261029_r01/ANALYSIS.md` + `LEAD_NOTE.md` | H1：2B 主端单 outstanding/单 beat，经 SmartConnect 串行化；方向 A 只改 BD |
| 阶段5 范围/裁决 | `s4d_stage5_scope_decision_20261029_r01/DECISION.md` | 视频链→阶段6；吞吐→Codex；地址/时钟/应用区/DMA 四项定稿 |
| 超时常量缺陷 | `s4d_elf_rebuild_timeout_20261029_r01` + `bringup_longrun_probe_*` | 旧 ELF `0x40000000`=21.47 s < 单帧 47.3 s ⇒ 必然 `error=5` |
| head13 尾字 | `s4d_m4b_tailword_20261029_r01` + `s4d_m4b_close_*` | 参考预置漏写尾 2 字节（1267 字 vs 5070 B），非 PL 缺陷 |

## 4. 未做（明确边界）

- 视频链（VTC/axi_dynclk/VDMA/HDMI/叠加）→ **阶段6**
- 摄像头实拍链、`ENABLE=1` 实时 4-D 流 → 未做
- 吞吐/帧率优化 → 按 Wong 指示移交 **Codex**
- G3/G4/G5 验收 → 未主张；冻结前需完整回归

## 5. 恢复入口（下一位接手者）

1. 读本目录 `README.md` 与 `ADDRESS_MAP.md`；
2. 位流身份只认 `58C66CDB…`（bit）/ `4ebc631e…`（XSA），不要用 `pl_v2_p2c_*`/`pl_v2_p2b_*` 作最终部署；
3. 上板顺序与契约见本目录 README §4；`rst -system` 禁令见 §4.2；
4. 构建脚本：`s4d_p2d_merged_bitstream_20261029_r01/bd_p2d.tcl`（可重跑，产物目录 `D:\tmp\lead\p2d_merged_20261029_r01\out`）。