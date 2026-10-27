# 主仓检查器支持内联 `hash_basis`（2026-10-27 r01）

- 编号：`checker_inline_hash_basis_support_20261027_r01`；时间：2026-10-27 20:40（UTC+8）。
- 决策：DSH 项目总控（主目录写权方）。
- 起因：阶段5 报 `check_stage_delivery.py` **拒绝**清单内联 `hash_basis`（"含未知字段"、exit 2），只能用"双文件"（`delivery_manifest.json` + `hash_basis_manifest.json`）绕过。
- **裁定：采用内联形式**，把白名单加进主仓检查器；**不采用双文件**（双文件会引入"基座文件与清单不同步/漏项"的新漂移面）。

## 1. 改动（`verification/check_stage_delivery.py`，向后兼容）

1. `TOP_LEVEL_FIELDS` 增加 `hash_basis`、`hash_basis_note`、`hash_basis_commit`
2. `FILE_FIELDS` 增加 `hash_basis`、`hash_basis_note`
3. 新增校验 `_valid_hash_basis()`：
   - `hash_basis` ∈ {`commit_blob`, `worktree_disk`}，否则报错；
   - `hash_basis_note` 若存在须为非空字符串；
   - `hash_basis_commit`（**仅清单级**）必须是 **40 位小写十六进制**，**禁止 `HEAD` 等符号引用**；
4. 清单级与 `files[]` 级各调用一次。

**未声明基座的旧清单仍合法**（legacy 兼容）；非法取值 ⇒ `errors` ⇒ 检查器 exit 2。

## 2. 自测（`verification/selftest_check_stage_delivery_hash_basis.py`，可复跑）

9/9 PASS，exit 0：内联字段不再被判未知（清单级/文件级）、`commit_blob`/`worktree_disk` 合法、`disk` 被拒、`HEAD` 符号引用被拒、大写 SHA 被拒、40 位小写 SHA 通过、未声明基座兼容。

## 3. 回归

| 对象 | 命令要点 | 结果 |
|---|---|---|
| 阶段5 `S5-T27/…_r02/delivery_manifest.json` | `--mode evidence --project-root w5 --manifest <相对路径>` | **CHECKS_OK / exit 0** ✓（补丁未破坏既有清单） |
| 阶段4 `S4-CTRL/s4_d1a_landing_20261027_r02/landing_manifest.json` | 同上（root=w4） | **exit 2，但原因与本补丁无关**：该文件是**阶段4 自定义格式**清单，缺 `evidence_dir`/`interfaces`/`limitations` 等必填字段、含 `boundary`/`card`/`nb_fixes` 等自定义字段 ⇒ **本就不适配 `check_stage_delivery` schema**。 |

**要求阶段4**：要么补一份 checker schema 的 `delivery_manifest.json`，要么在证据中**明确声明"本包不使用 checker schema，改用专用校验器 + 新基座门禁"**，**不得**笼统声称"CHECKS_OK"。

## 4. 对阶段5 的要求

1. 把基座**内联**进 `delivery_manifest.json`（清单级 `hash_basis`/`hash_basis_commit` + `files[]` 逐项），`hash_basis_commit` 写**真实 40 位 SHA**（不得写 `HEAD`）；
2. 保留 `hash_basis_manifest.json` 仅作**派生交叉核对**（须断言覆盖 `delivery_manifest.files` 全集），或直接删除；
3. 复跑并报真实退出码：`check_stage_delivery --mode evidence`、`check_manifest_hash_basis.py --mode strict/declared-only`，均须 exit 0。

## 5. 背景与边界

- 规则出处：`decisions/manifest_hash_basis_rule_20261027_r01.md`（Wong 批准「加」）；
- 本改动只放行**字段与取值**，不改变 checker 的任何验收语义（`CHECKS_OK` 仍不代表 G0/G4/G5）；
- 与 Codex 共享规则：本补丁为**向后兼容**的白名单扩展，Codex 侧旧清单不受影响。