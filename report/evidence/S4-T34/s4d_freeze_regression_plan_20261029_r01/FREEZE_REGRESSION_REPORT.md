# 冻结回归报告（2026-10-30 r01）

- 执行器：`run_freeze_regression.py`（fail-closed；前置 19 项冻结输入校验 OK）
- 平台：2B 基线位流 `555a70c2…` + P2d 合并位流 `58c66cdb…`（50 MHz）
- 结论：**7/7 PASS**

| # | 项 | RunId | 结论 | 关键数字 |
|---|---|---|---|---|
| R1 | 2B 基线：M3 只读复检 + M4-a | `s4d_freeze_r1_m3_m4a_2b_20261029_r01` | `P2B_4D_STOPPED_ON_FAILURE`（该 runner 的总体结论；本项只判 M3/M4-a） | **m3=PASS m4a=PASS**；同窗口的 M4-b 段不计入本项判据（由 R2 覆盖） |
| R2 | 2B 基线：M4-b 收口（padded 参考 + 投毒） | `s4d_freeze_r2_m4b_2b_20261029_r01` | `M4B_PASS_TAIL13_CLOSED` | done=1 error=0 elapsed_ms=47287; diff13=0 diff26=0 stale=1 pass=1 |
| R3 | 2B 基线：chain-lite A | `s4d_freeze_r3_chaina_2b_20261029_r01` | `CHAINLITE_A_PASS` | done=1 error=0 elapsed_ms=47287 |
| R4 | 2B 基线：chain-lite B | `s4d_freeze_r4_chainb_2b_20261029_r02` | `PASS` | done=1 error=0 elapsed_ms=47287; crc=0x5B183B50; W3a=True W3b=PASS |
| R5 | P2d：M4-b 收口 + 2B 单帧性能 | `s4d_freeze_r5_m4b_p2d_20261029_r02` | `M4B_PASS_TAIL13_CLOSED` | done=1 error=0 elapsed_ms=47287; diff13=0 diff26=0 stale=1 pass=1 |
| R6 | P2d：chain-lite A | `s4d_freeze_r6_chaina_p2d_20261029_r01` | `CHAINLITE_A_PASS` | done=1 error=0 elapsed_ms=47287 |
| R7 | P2d：preproc→DMA(HP1) 张量 CRC | `s4d_freeze_r7_crc_p2d_20261029_r01` | `P2C_TENSOR_CRC_MATCH` | - |

## 未采用的运行记录（保留，不覆盖）

| 记录 | RunId | 原因 |
|---|---|---|
| R4-r01 | `s4d_freeze_r4_chainb_2b_20261029_r01` | 缺 fixture/离线参考，IDENT 即停、未碰板 |
| R5-r01 | `s4d_freeze_r5_m4b_p2d_20261029_r01` | 旧 runner 采集截断（末尾半行），板面 done=1；未被采用 |

## 覆盖判定

- 2B 基线上：M3 逐字节一致、M4-a 对拍通过、M4-b `pass=1`、chain-lite A/B 均 `pass=1`（含 CRC `0x5B183B50` 与离线参考框 8 字段一致）。
- P2d 上：M4-b `pass=1` 且 `elapsed_ms=47287`（约 47.3 s，未见慢 2x 复发）、chain-lite A `pass=1`、preproc→DMA(HP1) 张量 CRC 与离线一致。
- 未覆盖（明确排除）：A 项 30 min 长跑（已由 `bringup_longrun_probe_20261029_r05` 完成）、M2 重跑（以勘误为准）、M3 成对取样（Codex 外部依赖）、视频链（阶段6）。

## 冻结结论

冻结输入 19 项 sha 全程未变、7 项回归全 PASS ⇒ **阶段4/5 具备进入 G4（任务验收）的条件**；M3 成对取样仍为遗留外部依赖，不阻塞其余项。
