# 验证附录 claim_verification

任何『已关闭/已落盘/已同步』的声明必须附：命令 + 真实退出码 + 可观察输出（或命中位置）。本附录由 verification/claim_verify.py 生成，逐条可复跑。

- 生成：2026-10-23 04:48:22；判定：**ALL_CLAIMS_VERIFIED**

## S6B-C1-acquisition-id — VERIFIED

- 声明：acquisition_id 在 M11/M4 与目标切换时真的递增，并落进 run_report.json 与 JSONL；C3 两次获取得到 0,1
- 命令：`python -B verification/s6b_run_cases.py --project-root D:\codex-worktrees\w6 --run-dir report/evidence/S6-B/s6b_core_20261023_r03`
- 真实退出码：0
- 期望：命中 ≥1 且 C3 序列严格递增（0 → 1）
- 可观察输出：
  - run_report.json 中 'acquisition_id' 命中 18 次
  - logs/*.jsonl 中 'acquisition_id' 命中 222 次
  - C3 动作记录的 acquisition_id 序列 = [0, 1]（去重 [0, 1]）
  - 行为表 B11/B15 的 must_log 需要该字段，可由 action_records 逐获取核对

## S6B-C2-action-records — VERIFIED

- 声明：action_records 写进 run_report.json（含 action_type/target_id/acquisition_id/t_trigger_ns），且四个 ACTION_* 事件名在证据中出现
- 命令：`python -B verification/claim_verify.py --package s6b --run-dir report/evidence/S6-B/s6b_core_20261023_r03 --project-root D:\codex-worktrees\w6`
- 真实退出码：0
- 期望：四字段齐全且四个 ACTION_* 事件各 ≥1 次
- 可观察输出：
  - 样本记录的四个必需字段存在性：{'action_type': True, 'target_id': True, 'acquisition_id': True, 't_trigger_ns': True}
  - 证据内四个 ACTION_* 事件计数：{"ACTION_SUBMITTED": 17, "ACTION_EFFECTIVE": 16, "ACTION_FAILED": 1, "ACTION_UNOBSERVED": 2}
  - run_report.json 中 'action_records' 命中 23 次

## S6B-C3-no-dead-constants — VERIFIED

- 声明：未使用的 OUT_*/SUP_* 死常量已删除（每个常量都在文件内被引用）
- 命令：`python -B verification/claim_verify.py --package s6b --run-dir report/evidence/S6-B/s6b_core_20261023_r03 --project-root D:\codex-worktrees\w6`
- 真实退出码：0
- 期望：未使用常量 = 0
- 可观察输出：
  - 未使用常量：无

## S6B-C4-registrations — VERIFIED

- 声明：NB-03/NB-04 登记真实落盘（open_behavior_deviations / not_implemented），且 M4 计入覆盖
- 命令：`python -B verification/claim_verify.py --package s6b --run-dir report/evidence/S6-B/s6b_core_20261023_r03 --project-root D:\codex-worktrees\w6`
- 真实退出码：0
- 期望：两类登记均非空且 M4 在计数覆盖内
- 可观察输出：
  - not_implemented 条数 = 1
  - open_behavior_deviations 条数 = 1
  - reachability_counted = ['M4（TARGET_CONTINUES 不含 score ≥ T6-P02 → M10 不先命中；用例 C4-jitter-reset）']

验证附录只证明这些声明有可观察依据；不代表独立审查或验收通过。
