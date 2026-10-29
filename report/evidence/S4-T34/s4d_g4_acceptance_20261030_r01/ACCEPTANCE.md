# 阶段4/5 任务验收记录（G4，2026-10-30 r01）

- 判定角色：DSH 项目总控汇总 + 独立证据核查；**最终判定待 Wong 签署**
- 冻结基线：见 `FROZEN_INPUTS.json`（19 项 sha256，2026-10-30 00:06 与 00:46 两次校验均为 OK）
- 板级回归：`s4d_freeze_regression_plan_20261029_r01/FREEZE_REGRESSION_REPORT.md`（**7/7 PASS**，00:06–00:46）
- 结果口径：通过 / 失败 / 未执行 / 不适用（不适用须写技术理由；未执行不得记为通过）

## A. 阶段4（摄像头推理 / 4-D 数值链路）逐项验收

| 编号 | 要求 | 阈值与口径 | 实际值 | 证据 RunId | 结果 |
|---|---|---|---|---|---|
| S4-01 | 冻结参考与接口身份 | 2B CSR ID `0x53324250`、VER `0x0100` 可读；参考张量/权重身份固定 | ID/VER 读回一致 | `s4d_freeze_r1_m3_m4a_2b_20261029_r01`、`s4d_p2c_crc_on_p2d_20261029_r03` | 通过 |
| S4-02 | M2 CSR 语义勘误 | `INT_STS[2]` 为唯一 PCFG_DONE 判据；W1C 写 1 清零；两处 hex 口径更正 | 勘误文档 + 自检脚本 exit 0 | `s4d_m2_erratum_20261029_r01` | 通过 |
| S4-03 | M3 候选区完整性（只读） | 12,615,680 B dump 与登记快照逐字节相同 | diff=0，sha256 `41907f53…` | `s4d_freeze_r1_m3_m4a_2b_20261029_r01` | 通过 |
| S4-04 | M3 成对取样（同窗口读写） | 同窗口内候选区读→写→读一致 | — | — | **未执行**（外部依赖：Codex 的 DDR 读工具，已发 `DSH-20261029-007`） |
| S4-05 | M4-a CSR 应答回读 | 0x100 B R/F 应答与期望 CRC 全对，且恢复逐字节相等 | `R=0xCFB6FB9B`、`F=0xFE55DA7C`，恢复 byte-equal | `s4d_freeze_r1_m3_m4a_2b_20261029_r01` | 通过 |
| S4-06 | M4-b 头部一致性 | `pass=1`：`diff13=0 / diff26=0 / stale=1 / gate=1 / ack_idle=1 / error=0` | 47,287 ms，`pass=1`；尾字 `after=0x5A5A0506`、`lane01_ok=1 lane23_ok=1` | `s4d_freeze_r2_m4b_2b_20261029_r01` | 通过 |
| S4-07 | 4-D 链路端到端（chain-lite A） | `pass=1`、解码 `ok`、检测框与 r13 冻结参考逐字段一致（abs≤1e-9） | `pass=1`、`count=1`、参考一致 | `s4d_freeze_r3_chaina_2b_20261029_r01` | 通过 |
| S4-08 | 4-D 链路端到端（chain-lite B，SW 预处理） | 张量 CRC `0x5B183B50`；检测框 8 字段与离线参考 abs≤1e-9 | `pass=1`、CRC 一致、8 字段 match | `s4d_freeze_r4_chainb_2b_20261029_r02` | 通过 |
| S4-09 | 长跑稳定性 | 真实 ≥30 min、逐轮结果一致、无失败、无死锁 | 40 轮 / 1,844,812 ms / 0 失败 / 每轮 47,287 ms / CRC 恒定 | `bringup_longrun_probe_20261029_r05` | 通过 |
| S4-10 | 时间基座正确性 | 应用 ms 与宿主一致（比值≈1.000） | `ratio_x1000=999~1000`、`elapsed_ms=47,287` vs 宿主 47.3 s | `s4d_time_basis_20261029_r01`、`s4d_freeze_r7_crc_p2d_20261029_r01` | 通过 |
| S4-11 | PL 预处理数据面 | preproc→打包→DMA→张量 CRC 与离线 golden 一致 | `tensor_crc32=0x5B183B50`、`len=519168` | `s4d_freeze_r7_crc_p2d_20261029_r01` | 通过 |

## B. 阶段5（合并部署，当前范围）逐项验收

> 范围依据：`s4d_stage5_scope_decision_20261029_r01/DECISION.md`。**显示链（VTC/axi_dynclk/VDMA/HDMI/叠加）按 Wong 指示移出阶段5、归阶段6**，故本阶段不判显示相关项。

| 编号 | 要求 | 阈值与口径 | 实际值 | 证据 RunId | 结果 |
|---|---|---|---|---|---|
| S5-01 | 合并计算体可构建 | 一版 BD 同时含 2B + preproc + 打包器 + DMA，构建 exit 0 | bit `58c66cdb…`、XSA `4ebc631e…` | `s4d_p2d_merged_bitstream_20261029_r01` | 通过 |
| S5-02 | 时序收敛 | 50 MHz 下 WNS/WHS ≥ 0，DRC 0 error | **WNS +0.128 / WHS +0.036**，DRC 0 error | `s4d_p2d_merged_bitstream_20261029_r01` | 通过 |
| S5-03 | 资源可接受 | 记录实测占用并留余量说明 | LUT 44.08%、FF 9.79%、BRAM 23.93%、DSP **158/220（71.82%）** | `s4d_p2d_merged_bitstream_20261029_r01` | 通过（DSP 余量 62，阶段6 前须重算） |
| S5-04 | 2B 在合并体上不劣化 | 单帧 ≈47.3 s（不得出现 >85.9 s 超时） | 47,287 ms（P2b 同 ELF 为 85,899 ms 超时 ⇒ 方向 A 修复） | `s4d_freeze_r5_m4b_p2d_20261029_r02` | 通过 |
| S5-05 | 合并体上链路正确 | chain-lite A `pass=1`、参考一致 | `pass=1` | `s4d_freeze_r6_chaina_p2d_20261029_r01` | 通过 |
| S5-06 | 合并体上预处理数据面 | preproc→DMA(HP1) 张量 CRC 与离线一致 | CRC 一致、`len=519168` | `s4d_freeze_r7_crc_p2d_20261029_r01` | 通过 |
| S5-07 | 合并体上 M4-b | `pass=1`、尾字 lane 正确 | `pass=1`、47,287 ms、`lane01_ok=1 lane23_ok=1` | `s4d_freeze_r5_m4b_p2d_20261029_r02` | 通过 |
| S5-08 | 地址表/文档收口 | 地址、时钟、数据通路、约束、恢复入口齐全 | README/ADDRESS_MAP/EVIDENCE_INDEX | `s4d_p2d_stage5_close_20261029_r01` | 通过 |
| S5-09 | 显示链（HDMI 结果输出） | 阶段5 原始计划含显示 | — | — | **不适用**（Wong 决定归阶段6；技术理由：视频链需新 BD + DSP/时序重算） |
| S5-10 | 吞吐/帧率门槛 | 原"5 fps"目标 | 实测 47.3 s/帧 @50 MHz | — | **不适用**（Wong 明确不追 5 fps、任务移交 Codex；不作为本阶段判据） |

## C. 版本一致性

| 项 | 值 |
|---|---|
| 部署候选位流 | P2d `58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3` |
| 参考平台位流 | 2B 基线 `555a70c2…` |
| 应用 ELF | M4-b 收口 `553fbf7e…`、M4-b 重建 `aaedaf3c…`、chainA `87e049b4…`、chainB `06bb0209…`、P2c-DMA `bff4b80f…` |
| 驱动 | `run_bringup_driver.py` v3.2.7 `6c41ff4c…` |
| 重型工具 | Vivado / Vitis 2026.1；器件 `xc7z020clg400-2` |
| 冻结输入校验 | 19/19 OK（回归前与回归后各一次） |

## D. G4 判定

- **阶段4：G4 通过（含 1 项跟踪遗留）**（Wong 2026-10-30 认可）。11 项中 10 项通过、1 项（S4-04 M3 成对取样）**未执行**（外部工具依赖，非本侧缺陷），按验收手册不计为通过，作为跟踪遗留 R-01 保留。
- **阶段5：当前范围 G4 通过**（Wong 2026-10-30 认可）。8 项适用项全通过；2 项不适用已给技术理由（显示链归阶段6、吞吐移交 Codex）。
- **不主张 G5**（阶段验收）：阶段5 显示链未做、阶段6/7 未启动，G5 由 Wong 在阶段边界判定。

## E. 未执行 / 不适用（汇总）

| 项 | 状态 | 理由 | 关闭条件 |
|---|---|---|---|
| S4-04 M3 成对取样 | 未执行 | 需 Codex DDR 读工具（已发信箱 007） | 工具入口确认后单窗口补测（约 3 min） |
| S5-09 显示链 | 不适用（本阶段） | Wong 决定归阶段6 | 阶段6 BD 合入后按显示项验收 |
| S5-10 吞吐门槛 | 不适用 | Wong 明确不追 5 fps，任务移交 Codex | 若 Codex 产出指标，另行评审 |
| `ENABLE=1` 实时 4-D 流 | 未执行 | 跟随显示链阶段 | 阶段6 联调时补 |
| 摄像头实拍（非生成 fixture） | 未执行 | fixture 为生成数据，非实拍 | 实拍链在阶段6/7 补 |