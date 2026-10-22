# 验证附录 claim_verification（v2：真实退出码）

每条声明的 exit_code 均为**真实 subprocess 退出码**；命令可独立复算（无占位符）；内置 self_test_false_claim 证明本工具对假声明会 FAIL。

- 生成：2026-10-23 07:22:50；判定：**ALL_CLAIMS_VERIFIED**
- 复算命令：`python -B verification/claim_verify.py --package s6a --run-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r09 --project-root D:\codex-worktrees\w6`

## self_test_false_claim — VERIFIED

- 声明：故意为假的声明（assert 1==2）必须得到非 0 退出码——证明本工具会 FAIL
- 命令：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -c "assert 1==2"`
- 真实退出码：1（期望 非 0）
- 可观察输出：['AssertionError']

本附录只证明这些声明在**本次真实执行**下成立；不代表独立审查或验收通过。
