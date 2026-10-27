# 项目级规则：证据 manifest 必须声明哈希基座（+ 只读门禁工具）

- 编号：`manifest_hash_basis_rule_20261027_r01`；时间：2026-10-27 20:35（UTC+8）。
- 批准：**Wong 原话「加」**（回应"要不要我加这条规则 + 小工具"的建议）。
- 落地：`AGENTS.md`「产物落点、阶段对接与 ROSS 使用」新增一条；工具 `verification/check_manifest_hash_basis.py`。

## 1. 规则

证据 manifest 的**每个哈希项必须声明 `hash_basis`**：
- `commit_blob`（**推荐、内容权威**）：按 `git cat-file blob <commit>:<path>` 的字节计算；
- `worktree_disk`（**仅作附注**）：按工作区磁盘文件字节计算，受 `autocrlf`/换行转换影响。

基座可写**条目级**（`hash_basis`）或 **manifest 级**默认值；条目级覆盖 manifest 级。
**未声明基座的新证据不得作为交付物**；legacy 不追溯（`declared-only` 模式下跳过并计数）。

## 2. 工具

`verification/check_manifest_hash_basis.py`（只读、fail-closed）

| 参数 | 说明 |
|---|---|
| `--repo` | 仓库/工作树根（默认当前目录） |
| `--commit` | `commit_blob` 基座所用提交（默认 HEAD） |
| `--paths` | manifest glob（可重复；默认 `report/evidence/**/*.json`） |
| `--mode` | `declared-only`（默认，豁免未声明基座的 legacy）/ `strict`（未声明按 `commit_blob` 强校验） |
| `--json` | 机器可读输出 |

**退出码**：`0` 全一致 / `1` 存在不一致 / `2` 输入或环境错误（异常一律 2，不伪装成通过）。

## 3. 工具自证（我方实跑，真实退出码）

| 场景 | 退出码 | 结果 |
|---|---|---|
| `--help` | 0 | 正常 |
| 负例（`hash_basis=commit_blob` + 故意错哈希） | **1** | 捕获 `hash_mismatch` |
| 正例（`hash_basis=worktree_disk` + 正确哈希） | **0** | 通过 |
| 全仓 `declared-only` | 0 | 29 份 manifest / 0 项检查 / **4664 项因未声明基座跳过** / 29 份 manifest 无基座（legacy 豁免） |
| 阶段4 `…/s4_d1a_landing_20261027_r02/*.json`（strict） | **1** | 多项 `hash_mismatch`——证实 `S4-T30` 的 NB-4 基座缺陷 |
| 阶段5 `…/S5-T27/…_r01/*.json`（strict） | **1** | 多项 `hash_mismatch`——与阶段5 N1 同源 |

**结论**：工具的 0/1 两态**真实可区分**（非恒真），且已在两个阶段的现有清单上直接命中真实缺陷。

## 4. 执行方式（我方）

1. **验收门禁**：此后我方接受任何阶段交付前，先跑 `--mode declared-only`（新证据必须带基座）＋ 对被交付包跑 `--mode strict`；
2. **要求写入任务卡**：新证据的 manifest 必须带 `hash_basis`，并在交付说明里附本工具的真实退出码；
3. **Reviewer 要求**：复审时把"基座是否声明、是否与声明一致"列为固定检查项；
4. 本规则**不追溯** legacy（避免为历史清单无收益返工），但**新 RunId 一律适用**。

## 5. 背景（为什么必须加）

同一类缺陷在本项目已出现三次：
1. **阶段3**：`git add --renormalize` 把 110 个证据 blob 由 LF 改回 CRLF，声明却写"未改一字节"；
2. **阶段5**：S5-T27 清单绑定工作树 LF 字节，独立检出（`autocrlf=true`）变 CRLF ⇒ checker exit 2（N1）；
3. **阶段4**：`S4-T30` r01 13 项仅 3 项等于提交 blob、r02 12 项中 9 项为 disk 字节，且两个 manifest 均无 `hash_basis` ⇒ 按"绑定被审提交"验证必 FAIL。

⇒ 一个只读脚本 + 一条 `hash_basis` 声明规则，即可一次性堵住该类复发。

## 6. 边界

本规则不改变任何模型的数值语义、不构成关口通过、不授权板级活动；只约束**证据绑定方式**。