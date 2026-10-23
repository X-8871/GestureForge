# 窗口证据修复轮 r2 记录（复审 CHANGES_REQUIRED：3 阻断 + 4 非阻断）

- 被审锚点：`6fa77a64`（G）；**本轮不改任何被引用提交**（不 amend/rebase），修复落在**新提交 H**（自证产物另在 I）。
- 复审已独立复现的部分（不再重复自证）：B-2 数据层（69/69 MATCH、`check-attr=-text`）、B-2 工具层（未覆盖 ⇒ exit 4；改 `_scope_covers` 恒真后自测变红）、B-3（UR-2 diff 精确）、B-4（transcript 标注）、`38-249`/C2/I-O 结论可采信。

## BL-1（最重要）：`-text` 广域生效 + `--renormalize` 导致历史 blob 重存，且我先前的陈述失实
- **事实**：`report/evidence/S3-T05/** -text` 是**全树**规则，F 的 `git add --renormalize` 因此把
  **126 个历史证据文件（42 个父目录）**的 blob 由 LF 归一重存为**原始 CRLF**，OID 变化，当时未登记；
  而我写下了「历史 S3-T05 目录沿用原 LF 归一 blob、未改动一字节」——**该陈述失实，已撤回**。
- **登记**：`t05_renormalize_migration_20261024_r01/`（`README.md` + `renormalize_migration.json` 逐文件旧/新 OID
  + `41to5_recompute.txt` 复算）。
- **判定**：**保留**广域 `-text`（客观上是修好：提交字节 == 原始字节）；**静默改写才是缺陷，改写本身不是**。
- **计数口径差异如实列出**：复审的数字为 28 个历史 run 目录 / 110 个文件；本登记按**父目录**（含嵌套
  `_patchwork/...`、`patch_scratch/...`）计得 42 个父目录 / 126 个文件——同一批变更，以**逐文件 OID 清单**为准。

## BL-2：`selfproof_artifacts` 引用不存在文件；G 段无机器可读产物
- 4 个 manifest 的 `selfproof_artifacts` 列了不存在的 `selfproof_G.json`，且 3 个目录列出只存在于 window 目录的裸文件名。
- **修复**：① 生成并入库 **`selfproof_G.json`**（在改动前以 `--commit 6fa77a6` 实跑得到：90 文件 / 0 不一致 / `BLOB_BYTE_IDENTITY_OK` / exit 0），
  使 G 段**可机器复算**；② manifest 的该字段改为结构化 `packaging`（`excluded_from_outputs` 用**模式**表达、
  `selfproof_artifacts_present_in_this_dir` 只列**本目录真实存在**的件、并写明相对基准与"自证件只在 window 目录"）。

## BL-3：README 声称 log 例外已在 manifest 登记，实际无字段
- **修复**：window manifest 增 `packaging_exceptions`（路径、`.gitignore:20 *.log` 规则、`git add -f`、理由）；
  其余目录补空数组。

## 非阻断
- **NB-1**：`.gitattributes` 补 `scripts/stage3_t17/** -text`（否则默认 `core.autocrlf=true` 克隆下同命令 8 MISMATCH / exit 1）。
- **NB-2**：`38-249` 口径统一为「**已由部署 DCP 只读重跑确认**」——改 §1 结论、§3/C3 行、§5 第 2 项、§7 状态、
  §8 关系句、`offline/README.md` 表、`.codex/STATE.md`。
- **NB-3**：适用报告改为 **§7 在前、§8 在后**；§8 强调符成对（重写该段）。
- **NB-4**：`vdma_fsz_more_analysis.md` 的引用改为**入库路径**并新增 §6 指向落盘证明；
  新增 `t05_stage3_window_20261024_r01/uart_dedup_byte_identity.txt`（三份同哈希 + 字节数 + 可复跑命令）。

## 本轮再次自我披露：一处**静默未命中**的替换
- G 提交中，适用报告 §5 第 2 项（`38-249` 归因）的替换**未命中**（当时脚本对该处 `t.replace` 未加断言），
  旧文本残留在文件中，正是 NB-2 指出的矛盾来源之一。本轮改以**原文精确锚点 + 复核**方式修正，
  并在 §5 同时更正 `report_methodology -checks timing` 为**非法参数**（本版须全量）。
- 教训：**任何 `replace` 必须有命中断言**；已在后续脚本中沿用该纪律。

## 边界
本记录不代表阶段3 通过/冻结；不改任何判据数值；不改历史证据内容（只登记 OID 迁移）。
