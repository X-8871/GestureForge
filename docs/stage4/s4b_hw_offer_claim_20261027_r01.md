# 硬件 OFFER / CLAIM 的正确做法与模板（2026-10-27 r01）

- 场景：候选 `hardware_run_id=s4b_ps_tensor_hw_20261027_r01` 已定，但 main STATE 没有
  `S4-B-REAL-02B::s4b_hardware_session_handoff` 行。
- 问题：「新建正式 OFFER 行」还是「仅把 RunId 给 DSH 填写」？
- 结论：**必须新建正式 OFFER 行并由 main 提交**。「仅提供 RunId」不构成任何可用凭证。

## 1. 为什么"只给 RunId"无效

`validate_hardware_gates` → `_verified_hardware_handoff` 校验的不是消息，而是 Git 对象：

| 校验点 | 要求 |
|---|---|
| 行存在性 | main 当前分支历史可达提交中，`S4-B-REAL-02B::s4b_hardware_session_handoff` **恰好 1 行** |
| 三方一致 | 该行在「offer 提交」「main 当前 HEAD」「main 工作树」三处必须完全相同（撤销即失效） |
| 不可变绑定 | handoff 的 `authority_source` 必须绑定该提交的 `commit` / `path` / `blob_oid` / 字节 `sha256` |
| 发送者 | 负责人必须精确为 `DSH` |
| 接收者 | 状态字段必须精确为 `OFFERED Workbuddy 阶段4总控` |
| 范围 | `允许修改范围` 必须精确为 `S4B_PS_TENSOR_DIAGNOSTIC` |
| 证据入口 | 只能且仅能为 `hardware_run_id=<完整RunId>` |
| 有效期 | `心跳(UTC+8)` 距校验时刻 **≤ 1 小时** |

口头/消息形式的 RunId 无法满足"三方一致 + blob 绑定"，因此**不产生任何授权效果**。

## 2. 但现在不要发 OFFER（重要）

心跳有效期只有 **1 小时**（`_recent_time(..., maximum_age_seconds=3600)`）。当前其余门禁
远未就绪（地址图仍 `DRAFT_PENDING_REVIEW`、adapter 复审未绑定、六类记录全缺），
现在发 OFFER 只会在真正开跑前过期作废，还留下一条"已撤销/过期"的历史行。

**正确顺序**：先把六类记录做到"只差 OFFER"，再在开跑同一小时内提交 OFFER → 立即提交
CLAIM → 执行。

## 3. 前置就绪清单（OFFER 之前必须完成）

| 序号 | 事项 | 归属 | 现状 |
|---|---|---|---|
| P1 | 地址图 `S4B_stage4_address_map.json` 由 `DRAFT_PENDING_REVIEW` → `APPROVED`（或经复审的**范围化批准**） | Wong 裁决 + 阶段4 | **未完成** |
| P2 | RAW owner 方案（`DECISION_REQUESTED`）裁决并落盘 | Wong | **未完成** |
| P3 | 对当前 adapter 字节 `9c74f520…` 的独立复审 → `command_delivery_review` | 阶段4 + 独立 Reviewer | **未完成** |
| P4 | `operator_authorization`（`authorized_by` ∈ {Wong, 阶段4负责人}，含精确诊断操作集） | Wong / 阶段4 | **未完成** |
| P5 | `timing_freeze`（时基 + 阈值 APPROVED） | 阶段4 | **未完成** |
| P6 | `range_reservation`（非零 seed + session 闭区间，与旧预留不重叠） | 阶段4 | **未完成** |
| P7 | `cold_basis`（物理断电重建或等价独立证明） | Wong 现场 + 阶段4 | **未完成** |
| P8 | **main OFFER**（本文件 §4） | main / DSH | 待 P1–P7 |
| P9 | **w4 CLAIM**（本文件 §5） | 阶段4 | 待 P8 |
| P10 | `exclusive_session`（执行时现场取证，30 分钟窗口） | 阶段4 | 执行时 |

## 4. main OFFER 行模板（11 字段，逐字段有校验）

一行到底，字段顺序固定，值必须用反引号包裹：

```text
任务=`S4-B-REAL-02B::s4b_hardware_session_handoff` | 负责人=`DSH` | 工作树/分支=`D:\FPGA_Competition / main` | 起始提交=`<本行提交的父提交 40 位 SHA>` | 允许修改范围=`S4B_PS_TENSOR_DIAGNOSTIC` | 未提交改动归属=`main 侧既有未提交项保持原位，本行不改动任何未提交文件` | 让出声明=`OFFERED` | 心跳(UTC+8)=`<提交时刻 YYYY-MM-DD HH:MM>` | 证据入口=`hardware_run_id=s4b_ps_tensor_hw_20261027_r01` | 恢复命令=`git --no-optional-locks -C D:/FPGA_Competition rev-parse HEAD` | 状态/下一接手方=`OFFERED Workbuddy 阶段4总控`
```

字段级校验要求：

| 字段 | 校验 |
|---|---|
| 任务 | 必须含 `S4-B-REAL-02B::s4b_hardware_session_handoff`；全 STATE 唯一 |
| 负责人 | 必须精确 `DSH` |
| 工作树/分支 | 必须精确 `D:\FPGA_Competition / main`（`git rev-parse --show-toplevel` 的实际结果 + `" / "` + 分支名） |
| 起始提交 | 必须是**本行提交的祖先**，40 位小写 SHA（通常取父提交） |
| 允许修改范围 | 必须精确 `S4B_PS_TENSOR_DIAGNOSTIC` |
| 未提交改动归属 | 非空即可，但须与实际一致 |
| 让出声明 | 必须精确 `OFFERED` |
| 心跳(UTC+8) | `YYYY-MM-DD HH:MM`，校验时须在 1 小时内 |
| 证据入口 | **只能**是 `hardware_run_id=<完整RunId>`，不得带其他键 |
| 恢复命令 | 非空 |
| 状态/下一接手方 | 必须精确 `OFFERED Workbuddy 阶段4总控`（= w4 已提交 STATE 的写权负责人） |

## 5. w4 CLAIM 行（本侧生成，不手写）

OFFER 提交后执行：

```powershell
& 'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4_s4b/make_claim_line.py --offer-commit <OFFER提交SHA> --run-id s4b_ps_tensor_hw_20261027_r01
```

工具从 main 只读取出 `offer_blob_oid` / `offer_sha256` / `offer_source_commit`，拼出六键证据入口：

```text
offer_commit=<OFFER提交>;offer_blob_oid=<main STATE blob>;offer_sha256=<该blob字节SHA>;offer_source_commit=<OFFER起始提交>;hardware_run_id=s4b_ps_tensor_hw_20261027_r01;scope=S4B_PS_TENSOR_DIAGNOSTIC
```

CLAIM 侧另有约束：`负责人` 必须等于 w4 写权负责人（`Workbuddy 阶段4总控`）、
`工作树/分支` 必须精确 `D:\codex-worktrees\w4 / stage4-infer-prep`、`让出声明=CLAIMED`、
`状态/下一接手方=CLAIMED Workbuddy 阶段4总控`、心跳同样 1 小时内、
`起始提交` 必须是本行写入前的 w4 HEAD 且为该提交的祖先。

## 6. 谁写什么（不得越界）

| 动作 | 唯一合法执行方 |
|---|---|
| main STATE 写 OFFER | main / DSH（阶段4 不写主 STATE，也不写项目总控信箱） |
| w4 STATE 写 CLAIM | 阶段4 总控 |
| 硬件窗口授权 | **Wong**（本次超出"只交接 w4 写权"范围，需单独授权） |
| 板上执行 | 阶段4，且需八类记录齐全 |

## 7. 本轮明确不做

- 不在 main STATE 新建任何行（本文件只是模板，不是执行）。
- 不发过期 OFFER；不预热提交。
- 不改地址图状态（P1 未裁决）。
