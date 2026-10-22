# S6-A r05 独立复评记录（PASS）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`1632761`**（契约 v1.4 / r05）
- 评审方：DSH 项目总控派出的**第 5 位独立 Reviewer 子代理**（只读；全部写入隔离目录 `tmp/review/S6A_r05_20261023_r01/`）
- 时间（UTC+8）：2026-10-23 02:10–02:24
- **结论：`PASS`（阻断 0；新增非阻断 4 项）**
- 边界：只覆盖 r05，不代表 G0/G2/G4/G5；未复核 S6-B/6-C/6-D/6-E。

## 1. 上一轮 5 项非阻断：5/5 实质关闭（评审自注入验证）

| 项 | 评审验证 |
|---|---|
| `N-r04-01` | JSON `M5.condition`、文档 §4 M5 行、`stable_latching.suppressed_trigger_release` 三处均带窗口推进帧限定；**4 种删改注入全部 FAIL 由 C12 捕获**；自推角落场景与 HC-30 七键全等（门在 `TIMEOUT` 帧开启→不动作；下一 OK 帧触发；恰好 1 次） |
| `N-r04-02` | statement 三要素与实测字段一致（M5 有 `global_cooldown_gate`、B13 无、两者均无 `predicates_used`）；旧措辞注入→FAIL |
| `N-r04-03` | C12 普适非空列表断言；`[]`／字符串三种注入**全 FAIL** |
| `N-r04-04` | `window_span_ms` 改为按第 `T6-S02` 个匹配帧计算（HC-29=200ms）；两口径分歧注入→C7 FAIL |
| `N-r04-05` | WIP 悬空引用已消失（该 WIP 未提交，不在被审提交内） |

## 2. 自检工具改动：只增强，无削弱

diff = +105/−8；8 个删除行全部被更强或同强形式替换；唯一被删逻辑是样例数下限 `29→30`；无删检查、无降级、无 try 包裹。
探针：入库 7 条注入 + 1 基线，评审**逐条复刻** → 各 `exit 1` 且由预期项（C12/C7）捕获，基线 `exit 0`，与 `probe_summary.json` **8/8 逐字段一致**；另自造 10 例注入 10/10 按预期 FAIL。

## 3. 复跑一致性（真实退出码）

- r05 全量自检（绝对 `--project-root` + `--evidence-dir/--manifest/--state`）→ **exit 0 / ALL_PASS 17/17**，与入库结果 **17 项 id+status+detail 逐字一致（差异 0）**。
- `check_stage_delivery --mode inputs/--mode evidence` → 均 **exit 0 / CHECKS_OK**，与入库 `*_mode_output.txt` **逐字节相同**。
- r04 原始字节（`git cat-file blob`）重跑 → **exit 1**，`FAILED=[C7,C12]` 与入库证据逐字相同，5/5 哈希一致。

## 4. 无回归 / 无夸大

24 项参数逐字段差异 0；ID 集合新增=删除=[]；`artifact_version` v1.4 四处一致；manifest 声明缺失 0；r01..r04 证据零改动；无虚假完成声明。

## 5. 本轮新增非阻断（供 r06）

| # | 问题 | 关闭条件 |
|---|---|---|
| `N-r05-01` | "8 个注入用例"实为 **7 条注入 + 1 基线**（脚本 docstring、builder 3 处、fix_record、run summary、manifest、提交信息） | 统一改为「基线 1 例 + 注入 7 例（共 8 例）」 |
| `N-r05-02` | r04 重跑失败被归因「C7 捕获 N-r04-04」，实测 C7 唯一失败是「样例数 29<30」；N-r04-04 的判别力实际由探针 `case_span_wrong` 证明 | 改归因，N-r04-04 只引探针证据 |
| `N-r05-03` | HC-30 三个布尔恒 True、`total_actions` 封顶 1 → "恰好 1 次"实为"至少 1 次"（真实判别力在 `gate_open_frame`/`first_action_frame`） | 注明覆盖边界或去掉封顶 |
| **`N-r05-04`（最要紧）** | C7 只按"第 `T6-S02` 个 `WINDOW_MATCH` 帧"取跨度，**未实现 M3/§9/§14 `T6-S03` 的"取较晚满足者"**；当 `P < T6-S01/(T6-S02−1)`（草案 40ms，**30fps=33.3ms 即命中**）计数先满足，模型报 `m3_fires=false` 而规格要求 `true`——**文档 §15 自己的「30fps → 第 8 帧 233.1ms」示例被该模型否掉**（评审构造 P=33.3ms 用例 → 自检 FAIL） | 完成帧改为"第一个计数≥`T6-S02` 且 (帧序−首帧)·P ≥ `T6-S01` 的帧"，或在 limitations 声明近似与适用区间（`P≥40ms`）。**因真实相机为 30fps，这条必须先修再谈 S6-B 验收** |

## 6. 其他观察（不列为问题）

- 证据哈希绑定**工作区 CRLF 字节**，`git cat-file blob` 为 LF（`core.autocrlf=true`）；被审 42 个改动文件逐一比较**内容真正不同者 0**（git 归一化相等）→ 非回归；建议后续对 `docs/stage6`、`report/evidence/S6-A` 加 `-text`。
- 文档无完整令牌 `S6A-G0-v1.4`（用"v1.4 / r05"）；`coverage_matrix.json` 残留"（v1.3）"标签。
- **并发提示**：评审期间 w6 新增未跟踪 `report/evidence/S6-B/`、`verification/s6b_*.py` → **S6-B 开发与评审/提交流程须串行**。
- `allowed_versions` 是历史白名单（v1…v1.4），旧包重跑需先过 C1 才能考 C7/C12/C17，属既有设计；版本真实性由 C11 绑定保证。

## 7. 处置

- 已派 `task-7`（r06）：`N-r05-04` **优先**（影响 30fps），`N-r05-01..03` 同批；要求 S6-B 的窗口完成判定与修正后的 C7 口径一致。
- 本记录只搬结论与边界；r05 规格与证据仍在 w6。