# S6-B 确定性状态机与用例矩阵运行摘要（契约 S6A-G0-v1.8；RunId s6b_session_clock_20261027_r03）

- RunId：`s6b_session_clock_20261027_r03`；工作树：`D:\codex-worktrees\w6`
- 契约：`S6A-G0-v1.8`（S6-A 侧行为表；批准状态 APPROVED_20261023）
- 用例：26 条，覆盖 CDX-20261022-012 §4 全部 11 类；结果 **PASS**
- 预期：运行前冻结，`expected_freeze.json` SHA-256 = `af7a55bba515554ddd1f1dc5c74edbd09a6d06c4b751ede3abe5dc2336ea3071`
- 参数：全部 `APPROVED_20261023`（2026-10-23 批准，值仍为草案值；见 `params_snapshot.json`）；未写死、未在测试集调参

## 真实命令与退出码

| 步骤 | 命令（绝对 project-root） | 实测退出码 |
|---|---|---|
| 冻结预期 | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\s6b_run_cases.py --project-root D:\codex-worktrees\w6 --run-dir D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03 --cases D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\cases\case_matrix.json --freeze-only` | 0 |
| 运行用例 | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\s6b_run_cases.py --project-root D:\codex-worktrees\w6 --run-dir D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03 --cases D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\cases\case_matrix.json` | 0 |
| 判别力探针 | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\s6b_probe.py --project-root D:\codex-worktrees\w6 --run-dir D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03` | 0 |
| 交付检查 inputs | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode inputs --manifest D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\inputs_manifest.json --project-root D:\codex-worktrees\w6` | 实测 0 (PASS) |
| 交付检查 evidence 首次预检（fixpoint iteration 0） | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 实测 2 (FAIL) |
| 交付检查 evidence 最终收敛检查 | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 实测 0 (PASS) |
| 交付检查 evidence closing | `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-B\s6b_session_clock_20261027_r03\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 实测 0 (PASS) |

## 覆盖（11 类）

- 每类稳定输入：5 条
- 持续保持与冷却后保持：1 条
- 手离开再出现：1 条
- 短暂抖动：1 条
- 两类快速切换：1 条
- 多目标/同分：1 条
- 多目标/维持优先：1 条
- 多目标/目标跳变：1 条
- NO_HAND / 未知类 / 低分：2 条
- TIMEOUT / ERROR / DROPPED / stale：1 条
- 重复 / 倒序 / 缺帧 / 重启帧号：1 条
- 低 FPS / 窗口完成取较晚：1 条
- 时间等于阈值：1 条
- 时间阈值 −1 个计时单位：1 条
- 无新结果但时间前进：1 条
- 动作失败 / 未观察：1 条
- 动作未观察：1 条
- 冷却后保持 / 全局冷却门：1 条
- id 生命周期：3 条

## 结论边界

- 本包只覆盖离线确定性回放（注入输入 + 虚拟单调时钟）；不代表摄像头/HDMI/板上验收。
- `PASS` 只表示 26 条用例的独立预期全部满足；不代表 6-C 验收通过或独立审查通过。
- 计入覆盖：**M4**（BLK-1 修正，见 `reachability_notes.json`）；不计入覆盖：B16 S_DEDUP、M7。
