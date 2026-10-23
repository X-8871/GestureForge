# Q-3 处理：被机械改写的已提交证据（task-20）

- 背景：`task-19` 中为消除 `U+21D2`（GBK 不可编码）做过一次**整范围机械替换**，波及受管范围内 22 个文件。
- 复审核实（`S3_T17_QFIX_20261023_r01`）：`f77f363` 时含 `⇒` 的**已提交证据 58 份中 54 份逐字节未变 ✓**，
  但 **4 份 + `.codex/STATE.md` 的 `⇒` 全被替换**，其中**纯机械替换行**为
  takeover README **2**、prep README **9**、`t17_judgement_table.json` **9**、`t17_judgement_table.md` **2**、
  `.codex/STATE.md` **8**。因此本人在 `quickfix_record.md` 中「已提交证据逐字节还原、`CONTENT_DIFF_COUNT=0`」
  的说法**整体不成立**（我实际只还原了 17 个文件，另 5 个未还原），已在 `quickfix_record.md` 内**就地更正**。

## 处理方式：选 (a) —— 纯机械行还原回提交字节

判定规则（脚本 `tmp/3/S3-T17/_q3_restore.py`，不入库）：
> 当前行含 `=>`，且把该行 `=>` 换回 `⇒` 后与 `f77f363` 的某一行**逐字符相同** ⇒ 判为**纯机械替换行**，还原为提交字节。

实际还原（`q3_mechanical_restore.json`）：

| 文件 | 还原行数 | 行号 |
|---|---|---|
| `report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/README.md` | 2 | 30, 52 |
| `report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/README.md` | 9 | 5, 26, 50, 51, 69, 87, 88, 95, 96 |
| `report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.json` | 9 | 14, 15, 16, 22, 57, 72, 73, 74, 85 |
| `report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.md` | 2 | 15, 32 |
| `.codex/STATE.md` | 8 | 5, 6, 8, 25, 33, 42, 43, 44 |
| **合计** | **30** | （与复审计数 2/9/9/2/8 完全一致） |

- 还原后 `t17_judgement_table.json` 仍为**合法 JSON**（`json.load` 通过）。
- 上述 5 个文件中**其余差异**均为本轮**有意修改**（Q-A/Q-1/Q-2/Q-3/Q-4 的文本更正），
  逐行 diff 见 `q3_intentional_diff_f77f363_to_worktree.diff`（`git diff f77f363 -- <5 文件>`，6 个 hunk）。

## 影响与刷新

- 这 5 个文件均在受哈希绑定的目录内 ⇒ 其 `hashes_sha256.txt` 必须刷新（见 `closeout_record.md` §六）：
  prep 目录的 `hashes_sha256.txt` **自 F2 起就已过期**（非本轮引入），本轮一并重算。
- **口径说明**：`U+21D2` 只对**代码**有害（GBK stdout 崩溃，见 R-1/R-2）。因此本轮起：
  **工具源码与工具 README 保持 0 处 `⇒`**；**证据/文档正文**按原样保留中文箭头，不追求「全部替换」。