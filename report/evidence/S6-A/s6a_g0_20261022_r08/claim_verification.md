# 验证附录 claim_verification

任何『已关闭/已落盘/已同步』的声明必须附：命令 + 真实退出码 + 可观察输出（或命中位置）。本附录由 verification/claim_verify.py 生成，逐条可复跑。

- 生成：2026-10-23 04:48:31；判定：**ALL_CLAIMS_VERIFIED**

## S6A-C1-no-m4-unreachable — VERIFIED

- 声明：全包不再出现「M4 不可达」类表述（含 JSON/文档/手算样例/清单文本/STATE/自检与构建器）
- 命令：`python -B verification/claim_verify.py --package s6a --run-dir report/evidence/S6-A/s6a_g0_20261022_r08 --project-root D:\codex-worktrees\w6`
- 真实退出码：0
- 期望：禁语命中 = 0
- 可观察输出：
  - 禁语命中："无"

## S6A-C2-hc23-agrees-with-c16 — VERIFIED

- 声明：HC-23 的 expected.m4_reachable_under_draft = true，与 C16（要求 REACHABLE/计入覆盖）一致；C7 与 C16 不再结论相反
- 命令：`python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261022_r08/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261022_r08/upstream_bindings.json --out <tmp> --project-root D:\codex-worktrees\w6`
- 真实退出码：0
- 期望：HC-23 断言 true 且 C16 PASS
- 可观察输出：
  - HC-23.expected.m4_reachable_under_draft = True
  - C16 = PASS

验证附录只证明这些声明有可观察依据；不代表独立审查或验收通过。
