# 阶段6 冻结决定：产品核心冻结、认证工具链单列开放（2026-10-23 09:05 UTC+8）

- 决定方：DSH 项目总控；触发：定向解冻后的增量复核（批次 C）判 `CHANGES_REQUIRED`（3 阻断 + 6 非阻断），**三项阻断全部位于"认证工具链"而非产品语义/证据链**。
- 依据报告：`report/evidence/CTRL-DSH-HANDOFF/reviews/FREEZE_DELTA_C_20261023_r01/REVIEW_FREEZE_DELTA_C_r01.md`

## 1. 冻结内容（产品核心）

- **S6-A v1.8 / r10**：行为表（24 项参数全 `PENDING_APPROVAL`）+ 规格文档 + 自检工具链（C1–C17）。
- **S6-B r05**：纯核心状态机 + 动作层 + 确定性用例（26/26）+ 4 项判别力探针 + 交付检查器。
- 交付提交 **F4 = `6b8e5f2a23ce6f7dec41fc9992141b3423612081`**；自证记录 **G4 = `f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d`**；tag `stage6-freeze-20261023-r3` → G4（旧 tag r1/r2 与两个 per-profile tag 保留未动）。
- **冻结依据（DSH 独立复跑，传输克隆，非采信自述）**：
  - S6-A 自检 **C1–C17 ALL_PASS**；S6-B **26/26 用例 PASS**；探针 **4/4**；两个交付检查器 **exit 0**；
  - `export_selfproof --commit F4` → **`ALL_SELF_PROVEN [0,0,0,0]`，exit 0**；`--commit G4` 同（DSH 亲自在 `clone --no-local` 内跑）；
  - 24 项参数逐字段与上一冻结**零差异**、全 `PENDING_APPROVAL`；行为表仅 `run_id`／`status_label` 两处变化；`src/stage6/**` 无改动。

## 2. 不予认证：开放工具链缺口（3 阻断，本决定不作修复轮）

| 编号 | 事实 | 后果 |
|---|---|---|
| `BLK-C1` | 入库 `s6a_g0_20261023_r10/fresh_selfcheck_pair.json` 的 `verdict = **FAILED**`（两次 exit 1，"清单哈希不符：claim_verification.json"），却被清单以 `fd6fda19…` 绑定 | 与同包 `S6A-C6`「均 ALL_PASS」及检查器全 PASS 矛盾；**该件为陈旧记录**（克隆内实跑为 `BOTH_ALL_PASS`） |
| `BLK-C2` | 套件新增的两条必 FAIL 例以**真实 `--project-root`／`--run-dir`** 调 `claim_verify`，而该工具总把附录写回 run-dir | **跑一次套件即改写冻结附录**（克隆内实证 4 个附录被改写，r10 被留为 `NOT_ALL_VERIFIED/claims=[]`）；与"冻结后禁止写入"结构性冲突，且是 `BLK-C1` 的直接成因 |
| `BLK-C3` | 入库 `tool_self_tests.json` 的 `selfproof_valid_commit` 为 **`skipped / exit_code=null`**（构建时缺 r2 tag），却记 `AS_EXPECTED`；总判定只要求 `ALL_AS_EXPECTED`（**fail-open**），`S6A-C5` 仅读 `verdict` | 硬条件④**未达成**；"套件 10/10"仅在不入库的 `tmp/6/tool_self_tests.json` 成立 |

**明确禁止**：不得把 r10 的 `fresh_selfcheck_pair.json` 与入库 `tool_self_tests.json` 当作"通过凭据"引用；引用套件结论时必须同时说明"该件有一例 skipped 且计数 fail-open"。

## 3. 非阻断（同批登记，留待未来排期）

`transport_clone_check.json` 只在 `tmp/6`（未入库）；r10 清单含 2 条陈旧 `NOT_RUN`（与检查器全 PASS 不符）；`fix_record.json.new_run_id` 仍写 r07、摘要标题仍 r09、`--delivery-commit` 帮助文本仍写 r2/F2；`check_identity` 把 RunId 白名单放宽到 {r09,r10} 未登记；S6-B 自证文件 `task_id` 写 `S6-A`。

## 4. amend 事实更正（依复核 reflog 证据，DSH 一并更正自己的采信）

- 被 `amend` 的是 **amend 前的 F3 `66f45dd47056261720f55abc7d661bafd8714970` → `efb9f191`**；
- **F2 从未失去可达性**：克隆内 `--commit F2` 双侧 `ALL_SELF_PROVEN`、exit 0；
- 真正不可达的是 `66f45dd`（F3 树内 `source_commit=66f45dd` 无法解析 ⇒ `--commit F3` 失败）；
- **F4/G4 树内 `source_commit=efb9f191`（可达）**，故 F4/G4 的可复现性不受影响。
- ⇒ 任务卡前言与 w6 STATE 中「F2 失去可达性」的叙述**作废**；DSH 上一轮直接采信了该叙述而未核，属我的疏漏，一并更正。

## 5. 后续边界

- **不再为认证工具链开启修复轮**；如后续需要"完全自证包"，作为独立改进项排期（三个阻断 + 六项非阻断一并处理，并加"套件必须对副本运行"与"skipped 不得计绿"两条硬约束）。
- 本决定**不含 G3（板上验证）**，也不等于 G5 全阶段验收；**G4/G5 仍需 Wong 批准 24 项参数与 `U6-16`**（清单 `report/evidence/CTRL-DSH-HANDOFF/approval_sheet_20261023_r01/stage6_approval_sheet.md`）。