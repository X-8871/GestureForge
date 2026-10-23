# 阶段4：回放输入绑定与离线真实彩色链设计（task-26，无板卡轮）

- 状态：**方案就绪（PLAN_READY）**；**契约/地址图落盘待 lead 放行**——被审基线 `81d7e86` 的复审仍在进行，按「审查期间不得改被审范围」的规则，本文件先只做设计，不改契约/地址图/缺口登记表。
- 日期：2026-10-24（UTC+8）；所有者：DSH 阶段4 总控（本树 `D:\codex-worktrees\w4`）。
- 依据：`report/evidence/CTRL-DSH-HANDOFF/decisions/board_detached_boardfree_plan_20261024_r01.md`（板卡已拔下、先做无板卡工作）、`task-26` 卡、`CDX-20261023-019`。
- 边界：**不动硬件**、`status` 保持 `DRAFT_PENDING_REVIEW`、**`ENABLE=0`**、未 FROZEN；**回放/离线结论不得升级为实物集成结论**；`P` 与全部硬件项保持 `NOT_RUN`。

## 1. 回放输入包事实（阶段3 `task-25` 产出，只读引用）

目录：`D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_stage3_window_20261024_r01\`（dbdf 有 `report/evidence/S3-T05/** -text`，按 **git blob 内容**口径绑定）

| 文件 | 字节 | blob 口径 SHA-256 | 说明 |
|---|---|---|---|
| `frame_full.bin` | 2,764,800 | `939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0` | **单帧冻结**整帧（1280×720×3） |
| `reference_frame_set.md` | 3,422 | `995395f8b6bc61cf772fe0c60dbd13d25dda85b3594a5ad28966d1eb77ddcad1` | 参考帧集说明（方法/字节序/几何/自检/未决） |
| `hashes_sha256.txt` | 2,886 | `46d17a0cb6db9ad329323a00b4d6db3be148b42ced46f672bcffed2af57fd60a` | 目录级哈希清单 |
| `manifest.json` | 7,764 | `33c2c04bd6de3adbe79e2c84fc17d736b357af6ffc81efdc009ff6ae1727e914` | 窗口清单 |
| `row_y100.bin` / `row_y400.bin` / `row_y600.bin` | 各 3,840 | `35f1193c…` / `39de672c…` / `8df7620d…` | 行样本（与整帧切片逐字节一致） |

交叉核对：该目录自带 `hashes_sha256.txt` 内 `address_facts.md` = `d5ba4b6b…`，与本树 B-2 重绑值**一致**；`frame_full.bin` 与索取值 `939fce22…` 一致（本地复算）。

**已记录的部署事实**（摘自 `reference_frame_set.md`，不重解释）：v11 冻结应用、帧基址 `0x00114C00`（运行期分配，**禁止硬编码**）、`stride=0x0F00`、`720×3840=0x2A3000`；**内存字节序 B,G,R**；采集时刻（UTC+8）2026-10-24 01:24:13（单次窗口独占）；内容自检 0 个全零行、B/G/R 三通道均可达满量程、画面为真实场景（非彩条/非灰度）。

## 2. 按 `camera_capture_replay_colour` 的绑定设计

| 字段 | 取值/来源 | 说明 |
|---|---|---|
| `contract_version` | `s4-shared-io/1.1.0`（r05） | 消费当前草案版本 |
| `source_kind` | `camera`（→ S4-A `CAMERA`） | 回放仍是 camera 来源类别 |
| `range_label`（描述性） | `camera_capture_replay_colour` | `timing_claim_scope = replay_only`；**不得**标实时 |
| `session_id` | 本次离线运行的固定 u32（新 RunId 派生） | 与结果包 `(session_id, frame_id, result_seq)` 一致 |
| `frame_id` | `1`（本集仅 1 帧） | 递增语义保留，单帧无回绕 |
| `width`/`height`/`stride_bytes` | 1280 / 720 / 3840 | 原图坐标基准 |
| `pixel_format`/`byte_order` | `RGB888` / `little`；**输入源字节序为 B,G,R** | 展开时显式重排为 R,G,B，并记录映射方向 |
| `frame_integrity` | `sha256` = `939fce22…`、`length_bytes` = 2,764,800 | 逐帧记录（本集 1 帧）；行样本另作切片一致性核验 |
| `capture_time_available` | `true`（camera 必须真值） | 但**时基来源不同**：见下 |
| `capture_time_ns` | 由 `reference_frame_set.md` 记录的**墙钟 UTC+8 采集时刻**换算的非零值 | 在 `timestamp_source.epoch_note` 显式声明：**文档记录的墙钟纪元，非 PS 单调计数器**；因此**仅可作回放内一致性/元数据**，不得据此声明实时端到端延迟 |
| `clock_domain` | `replay_documented_wallclock` | 与实时部署的 PS 单调时基**不同域**、不得相减 |
| `measurement_scope` | 沿用 S4-A 键集合；`pl_timing`/`uart_transport`/`board_pl` 取值为**离线/不适用** | 不含板上实测 |
| `buffer` | 离线：`scope=offline_host`（主机内存）；`region_name` 仅在板上路径才映射 `raw_frame` | **`ENABLE=0`、不访问候选区** |

**漂移断言（B-3 口径）**：本绑定同时登记 **被绑树 = `dbdf`、记录时 HEAD = `6fa77a64…`**（提交时以实测为准）与**证据时间窗**；用 `scripts/stage4_s4ctrl/check_bound_tree_heads.py` 断言实际 HEAD == 记录值，不等即 FAIL。

## 3. 离线真实彩色链（确定性、可复跑）

```
frame_full.bin (BGR,1280x720)
  → [S1] 字节序重排 BGR→RGB + 长度/对齐/哈希校验
  → [S2] 冻结 D2 预处理（离线等价）：缩放/补边/归一化/量化 → CHW INT8 [1,3,416,416]
  → [S3] 冻结网络（离线等价）：CPU INT8 前向（与 PL 冻结核同源参考）
  → [S4] 头输出 head13/head26 → PS 解码/NMS 参考 → 结果记录
  → [S5] 回放结果包（离线/回放标记）
```

- S2 用冻结参考 `verification/s1_t02_d2_numeric_reference.py`（其 SHA 已在既有 G0 绑定内）。
- S3 用既有 CPU INT8 前向实现（`verification/s1_t02_d2_int8_forward.py`）作为**离线等价**；**不代表 PL 实测**。
- S4 用既有 PS 解码/NMS 参考（`verification/s2a_ps_decode_nms_reference.c` / `s4_ps_decode` 链）。
- 一致性对照：与既有离线数值核（单通道 G2、半边界反例 202×329→416、`s4c_replay` 109/109 的历史范围）比对，**只声明离线一致，不声明板上一致**。
- 停止条件：任一阶段哈希/长度不符、NaN/Inf、或与参考不一致且无法解释 ⇒ 停止并保留失败证据（新 RunId）。

## 4. 回放结果包（给阶段5，离线可用子集）

- `contract_result_key = (session_id, frame_id, result_seq)`；另给出 `stage4a_join_key` / `ps_log_primary_key` / `uart_observable_key` 的**离线可用子集**（缺的字段显式列 `unavailable_fields`，不得留空冒充）。
- 逐帧源帧哈希：`frame_integrity`（sha256 + 字节数）+ 行样本切片核验结论。
- **标记**：`evidence_kind = offline_replay`、`range_label = camera_capture_replay_colour`、`timing_claim_scope = replay_only`；**禁止**出现 `real_live` 或任何实时/板级字样。
- 交付形态：`report/evidence/S4-CTRL/<new_run_id>/` 下的机器可读 JSON + 逐帧记录 + 清单（含命令、退出码、脚本 SHA、被绑树 HEAD）。

## 5. 需 lead 裁决的一点

被审基线 `81d7e86`（地址图/契约/缺口登记表 + 四脚本）的复审仍在进行。task-26 目标 1 需要在这三份文件里**新增回放绑定**（契约 `upstream_bindings`/`input_source_profiles`、缺口登记表依据、地址图 factsources）——属**同范围改动**。按流程规则，请裁决其一：
- **(a) 先落盘**：授权我在当前复审进行中修改这三份文件，并对新提交另行复审（我按此执行，并在提交信息与 STATE 写明）；或
- **(b) 等复审**：复审结论到位后我再一次性落盘（本文件与只读/新文件工作先行）。

在裁决前我**只做不改被审范围的工作**：回放包事实核实（已完成）、离线链脚本与运行（写入新文件/新 RunId）、G0 缺口离线项设计、窗口申请包草稿。

## 6. 边界复述

未装位流、未开 COM4/JTAG、未起 hw_server；`status=DRAFT_PENDING_REVIEW`、`ENABLE=0`、未 FROZEN；`P` 与硬件项 `NOT_RUN`；不 push；不改他树。