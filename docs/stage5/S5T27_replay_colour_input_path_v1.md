# S5-T27 回放/彩色输入路径实现 + 离线动态显示回归（v1，2026-10-27）

> 口径：**回放/离线**。本文件与配套证据**不主张**任何板级、实时、实物或 G0/G1/G3/G4/G5 结论。
> 上游输入（只读）：阶段3 回放绑定 `replay_input_binding.json`（`939fce22…` 固定帧、`source_kind=camera`、
> `mode=offline_replay`、`timing_claim_scope=replay_only`、`capture_time_ns` 非零）；阶段4 **已冻结**回放结果包
> `s4t27_replay_positive_20261027_r01`（`freeze_index.json`：`package_sha256=988f2cae…`、`replay_only`、1 框）。
> 证据：`report/evidence/S5-T27/s5t27_replay_colour_20261027_r01/`（`results.json` 权威）。

## 1. 实现层交付（NB-5 遗留关闭）

模块：`scripts/stage5_t03/s5t03_replay_colour_input.py`（**新文件**，不改动 S5-T04 冻结成员）。

| 要求（task-27 §1） | 实现方式 | 判据/用例 |
|---|---|---|
| 逐帧 `frame_integrity` 校验 | `load_replay_source` 装载时**现场重算**源帧 sha256 与字节数并与声明比对；`frame_integrity_of` 逐帧重算；`validate_frame_integrity` 要求 algorithm/value/length_bytes **三者全等**，否则 `ReplayInputError`（fail-closed） | 篡改源帧 1 字节 ⇒ 拒收；`frame_integrity` 值/长度不符 ⇒ 拒收 |
| `replay_source_*` 绑定 | 每条结果记录携带 `replay_source_path/file_sha256/width/height/stride_bytes/byte_order/pixel_format`、`stage3_capture_evidence_entry`、`source_frame_id`、`source_capture_time_ns`（`REPLAY_SOURCE_FIELDS` 10 项） | 缺任一字段 ⇒ 守卫拒收；正常记录逐项断言在位 |
| **非零** `capture_time_ns` 传递 | 证据模式取阶段3 **文档化真实抓取时刻**（`1792776253000000000`，非零）；绑定 `capture_time_ns=0`、`capture_time_available=false` ⇒ 装载即拒收 | `capture_time_ns=0` 注入 ⇒ 拒收；`capture_time_available=false` ⇒ 拒收；`source_kind=synthetic` ⇒ 拒收 |
| `replay_not_live=true` 标记 | `ReplaySource.replay_not_live=True` 且每条记录携带；`assert_replay_record` 强制为 `True` | 置 `False` ⇒ 拒收 |
| 实现层而非绑定层 | 上述均在**运行期**执行（`assert_replay_record` 对每条记录跑阶段4 输入契约校验 `R.validate_result_record`），不依赖文档声明 | 自检 4 类注入全部被拒收（`replay_input_selftest.json`） |

时间语义（**不得混同**）：证据模式 `result_time_ns/inference_time_ns/end_to_end_latency_ns` 一律 `null`
（回放无单调发布时钟，不伪造延迟/年龄）；离线回归模式另设 `replay_timebase.basis="replay_local_logical"`，
把 `capture` 映射为"文档化抓取时刻 + 帧序号×周期"，**仅验证规则**。

用例：`scripts/stage5_t03/test_s5t03_replay_colour.py`（14 项，含 5 类拒收负例与 1 项回归判别力负例）。

## 2. 离线动态显示回归（回放/离线）

驱动：`scripts/stage5_t03/s5t03_replay_colour_regression.py`。冻结包**只含 1 帧结果内容**，
回归将其**逐帧重复回放**（`replay_content_origin` 记录来源键），明确标注"不是新推理"。

| 覆盖项 | 结论（回放/离线） |
|---|---|
| 坐标映射（原图坐标口径） | 冻结框 → 1280×720 像素逐值计算；正面积、画布内、`clip_unit_box` 幂等（未裁剪） |
| 帧关联 | 240 帧五元组成对（`displayed_frame_id == result_frame_id`）、语义唯一 `B_latest_result_overlay`、每帧恰一次提交事件 |
| 过期边界 | `age == 200 ms` **不过期**、`+1 ns` 过期、显式 `stale_flag` 过期（严格大于，replay-local 逻辑时基） |
| 顺序规则 | 重复结果键拒绝、`frame_id` 回退拒绝、等价 `frame_id` 未声明拒绝（NB-1）、显式声明放行、跳帧致过期 |
| 异常分支 | `TIMEOUT/ERROR/DROPPED/NO_HAND/裁剪后零面积` 分列；均不绘制、不冒充零框或过期 |
| 长跑 | **106 573 帧**（区间 106 572 × 16.89 ms = 1 800 001 080 000 ns）；每帧恰一次提交、时间戳单调、计数可复算、无重复/乱序叠加 |

判定：`results.json.verdict = REPLAY_OFFLINE_REGRESSION_PASS`（断言全过；任一失败则驱动 exit 1）。
**判别力**：篡改冻结包字节 ⇒ 驱动 exit 2（`test_regression_detects_injected_failure` 证明回归非恒真）。

## 3. 板级待验清单 B1–B10 对齐（离线前置 vs 必须上板）

> R1 清单原文（`docs/stage5/S5T03_board_verification_pending_v1.md`）是 S5-T04 **冻结成员**，按纪律**不改写**；
> 本节是**增量对齐**。逐项结论仍以该冻结文档为准，本节只标"离线已获前置证据 / 必须上板"。

| 项 | 离线是否已有前置证据 | 必须上板 | 说明 |
|---|---|---|---|
| B1 部署身份一致性 | 部分（阶段3 哈希只读重算 + 本卡复核引用） | **是**（重连后第 0 步） | 换板/换端口/部署变更后必须重算 |
| B2 真彩目视 | **否** | **是**（需 Wong 在场） | 离线只有固定帧字节，无颜色结论 |
| B3 ≥100 帧五元组 + 顺序规则 | **是（回放/离线）** | **是**（真实结果注入） | 本卡 240 帧成对 + 四类拒绝已验；板上需真实阶段4 结果流 |
| B4 坐标映射（板上绘制） | 部分（像素值逐值一致） | **是** | 板上反向映射与绘制时序未验 |
| B5 过期边界（实时 stale） | 部分（规则已验证） | **是** | 实时 stale 需真实时钟与发布节奏；`capture_clock` 仍 `PENDING_MEASUREMENT` |
| B6 30 分钟长跑 | 部分（虚拟 1 800 001 080 000 ns） | **是** | 板上耐久与内存/热行为未验 |
| B7 HUD 屏上视觉 | **否**（仅有离线栅格化遮挡量化） | **是** | 屏上字号/颜色/遮挡需人眼确认 |
| B8 异常注入（断流/超时） | 部分（离线异常分支） | **是** | 板上需真实断流/复位 |
| B9 重连/恢复 | **否** | **是** | 需真实热插拔/复位序列 |
| B10 采集 FPS / 端到端延迟 | **否** | **是** | 均未实测；不得用回放时基替代 |

**窗口申请材料更新**：阶段5 板级项（W-E）在 `end2end_real_chain_window_plan_20261027_r01`
（主仓 `report/evidence/CTRL-DSH-HANDOFF/decisions/`）下单次窗口内合并执行；**需 Wong 开工信号**，
第 0 步（占用/部署身份/运行期回读地址/**真彩目视需 Wong 在场**）未过不得进入 B1–B10。

## 4. 未做项（NOT_RUN，如实）

1. 板上回放/实时回放接入（PL 实跑、UART 实收）、八类门禁（当前 0/8）。
2. 摄像头真实采集、颜色/质量结论、端到端延迟（`capture_clock=PENDING_MEASUREMENT`）。
3. 真实集成 30 分钟、T5-10 板上回归、HUD 屏上视觉确认、真彩目视。
4. B1–B10 全项（需重连 + Wong 信号 + 第 0 步）。
5. `G0/G1/G3/G4/G5` 与实物验收（均未通过、未主张）。

## 5. 与 S5-T04 冻结基线的关系

- 本卡**只新增**文件（`scripts/stage5_t03/s5t03_replay_colour_input.py`、
  `s5t03_replay_colour_regression.py`、`test_s5t03_replay_colour.py`、`scripts/stage5_t27/`、本文件、新证据 RunId），
  **未修改** S5-T04 冻结集的任何成员；冻结集校验器仍应 `FROZEN_SET_VERIFIED`。
- 若后续要求把本卡实现纳入冻结，按 S5-T04 复审 F1–F5 一并修正后**重冻结**（新 RunId、新 tag）。