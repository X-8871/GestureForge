# S6-A 运行摘要：阶段6 G0 包与行为表 v1

- 任务：`S6-A`（阶段6 = 交互控制）
- RunId：`s6a_g0_20261022_r01`
- 工作树/分支：`D:\codex-worktrees\w6` / `stage6-interact-prep`
- 起始提交：`d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（开工只读核验：工作区干净、`index.lock` 不存在）
- 本轮提交身份：见 `git -C D:/codex-worktrees/w6 log -1 -- .codex/STATE.md`（同批提交，不在本文内自指哈希）
- 时间：2026-10-22（UTC+8），阶段6 总控 `stage6-lead`

## 1. 本轮做了什么

1. 只读核验开工（工作树/分支/HEAD/index.lock），并只读核对上游：主 `AGENTS.md`、主 STATE、`CDX-20261022-012`（阶段6 操作文档）、`CDX-20261022-015`（总入口 r02）、w5 的三份阶段6 草案、w4 的 S4-A 草案、w5 的 S5A v2 显示契约、阶段计划 L102–L108。
2. 把 `w6/.codex/STATE.md` 由主 STATE 副本重写为**阶段6 专用状态**（≤80 行、覆盖更新、含 11 字段交接行）。
3. 产出**阶段6 G0 包 + 行为表 v1**：`docs/stage6/S6A_stage6_g0_behavior_spec_v1.md`（人读）+ `docs/stage6/s6a_stage6_g0_behavior_v1.json`（机器可读，28 行行为、24 个参数/指标、15 条迁移、9 条硬不变量）。
4. 新增自检 `verification/s6_g0_selfcheck.py`（10 项检查，含 20 例人工手算边界复算与 11 项上游哈希复算），真实退出码 0、状态 `ALL_PASS`。
5. 本运行目录为证据包；缓存目录 `tmp/6/S6-A/s6a_g0_20261022_r01/`（不入库）。

## 2. 关键结论（不含任何验收声明）

- **行为语义 v1 已声明**：五类动作映射（提案）、多框迟滞与同分排序、稳定窗口与抖动、丢失/重获、冷却与再触发、`NO_HAND`/过期/未知/超时错误的处理与恢复、重复/倒序/缺帧/重启帧号、时间边界、低 FPS 交互延迟口径。
- **“持续保持只触发一次”只有一种解释**：一次**获取**只触发一次；冷却结束后即使目标仍保持且窗口再次满足也**不再触发**（M15 路径不是新获取）；二次触发只允许来自新获取（丢失确认后重获，或切换到另一目标）。草案备选 B（周期性重触发）被显式否决并登记为语义变更项。
- **提交成功与实际生效分开**：`ACTION_SUBMITTED` ≠ `ACTION_EFFECTIVE`；只有生效计入成功率分子，`unobserved` 单列按 `NOT_RUN` 且不得从分母剔除；误接受/误动作按**已提交**动作计数。
- **全部阈值与指标待批准**：分数门、窗口、帧数、冷却、去重窗口、样本数与三项目标值一律 `PENDING_APPROVAL`，责任人=项目总控转呈 Wong；本轮未在正式测试集上调参。
- **上游并发写入（本轮新事实）**：阶段4 工作树 `w4` 虽 HEAD 仍为 `73c3dad`，但其 `s4a_stage4_g0_fields.json` 与 S4A 草案已被**未提交修改**（工作副本哈希由 `3524d02a…` 漂移到 `657ea2fb…`），并新增 S4B 共享输入契约 / S4-C02 证据 / `s4_inject_frame.c`；阶段5 `w5` HEAD 由 `e4533e1` 推进到 `875e487`（引用的三份文件内容未变）。本 G0 绑定的是 w4 提交 `73c3dad` 版本，漂移已记录，阶段6 集成验收依赖继续 `BLOCKED`。

## 3. 实际执行的命令与真实退出码

| # | 命令（工作目录 `D:\codex-worktrees\w6`） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `git status --short` / `git rev-parse --short HEAD` / `git rev-parse --git-path index.lock` | 0 | 干净、HEAD `d8bc70e`、锁文件不存在 |
| 2 | `python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261022_r01/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261022_r01/upstream_bindings.json --out report/evidence/S6-A/s6a_g0_20261022_r01/selfcheck_result.json --project-root .` | **0** | `ALL_PASS`（10/10 检查；28 行行为 + 24 参数双向一致；20 例手算复算一致；11 项上游哈希一致） |
| 3 | 同上自检的首次运行（修复前） | 1 | 真实失败被保留并修复：HC-03 手算 `lower_bound_W` 记错、w4 上游工作副本漂移、C10 否定语境误报；修复后重跑为 0 |
| 4 | `python -B verification/check_stage_delivery.py --mode inputs --project-root . --manifest report/evidence/S6-A/s6a_g0_20261022_r01/inputs_manifest.json` | 见本目录 `delivery_manifest.json` 的 `checks` | 输入清单绑定核验 |
| 5 | `python -B verification/check_stage_delivery.py --mode evidence --project-root . --manifest report/evidence/S6-A/s6a_g0_20261022_r01/delivery_manifest.json` | 见本目录 `delivery_manifest.json` 的 `checks` | 证据目录枚举与哈希核验 |

- 首次自检失败属**真实失败证据**，其错误文本记录在 `selfcheck_result.json` 修复前的运行中（本轮未覆盖 RunId，失败原因逐条写入本文与修复记录；最终态以 `ALL_PASS` 的 `selfcheck_result.json` 为准）。

## 4. 证据文件

| 文件 | 说明 |
|---|---|
| `delivery_manifest.json` | 机器可读产物清单（源码基线、逐文件 SHA-256、接口、检查项与退出码、限制、工具版本） |
| `inputs_manifest.json` | `inputs` 模式输入清单（仅登记已冻结的 4 项上游 + 本轮源码绑定） |
| `upstream_bindings.json` | 11 项上游只读绑定（w4/w5 按**提交版本**复算，工作副本漂移另记） |
| `hand_computed_cases.json` | 20 例人工手算边界样例（含推导过程与复算字段） |
| `coverage_matrix.json` | 操作文档 6-A 十条 + 计划 L102–L108 + 阶段5 五条建议的覆盖矩阵 |
| `selfcheck_result.json` | 自检 10 项结果（`ALL_PASS`）与输入哈希 |
| `limitations_not_executed.json` | `NOT_RUN`/`BLOCKED`/`NOT_APPLICABLE` 逐项与理由 |
| `hashes_sha256.txt` | 关键文件 SHA-256 清单（含本轮源码、规格与证据文件） |

## 5. 恢复入口

```bash
git -C D:/codex-worktrees/w6 log --oneline -3
git -C D:/codex-worktrees/w6 status --short
python -B D:/codex-worktrees/w6/verification/s6_g0_selfcheck.py \
  --json D:/codex-worktrees/w6/docs/stage6/s6a_stage6_g0_behavior_v1.json \
  --doc D:/codex-worktrees/w6/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md \
  --cases D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r01/hand_computed_cases.json \
  --upstream D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r01/upstream_bindings.json \
  --out D:/codex-worktrees/w6/tmp/6/S6-A/s6a_g0_20261022_r01/selfcheck_rerun.json \
  --project-root D:/codex-worktrees/w6
```

- 恢复时须写新 RunId 到 `tmp/`，**不得**覆盖本 RunId 的证据；不得在正式测试集上调参。

## 6. 限制与不宣称

- 本轮**未实现状态机、未执行任何测试、未上板、未接摄像头、未操作 HDMI、未烧录**；`6-B/6-C/6-D/6-E` 全部 `NOT_RUN`，真摄像头项 `BLOCKED`（摄像头不可用）。
- 阶段4 结果记录与阶段5 显示契约均未冻结 → 集成验收依赖 `BLOCKED`；阶段4 文件本轮仍在变动。
- 显示侧新增 HUD 字段与五类动作映射为**提案**；全部阈值与指标**待批准**。
- 本轮**未完成独立审查**（本阶段总控在本次会话无法创建子代理，委派深度已用尽）；该限制已登记，须由项目总控安排后续轮次。
- 回放/注入结论适用范围仅限回放/注入输入。
- `CHECKS_OK`（检查器）与 `ALL_PASS`（自检）都**不**代表接口语义正确、独立审查通过或 G0/G2/G4/G5 与实物验收通过。