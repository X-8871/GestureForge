# S5-R 第 2 轮 · 聚焦关闭核验报告

- RunId：`s5r01_20261022_r02`
- Reviewer：`rev-s5`（只读核验；未修改被审文件）
- 完成时刻（UTC+8）：2026-10-22 10:46
- 范围：仅核第 1 轮（`s5r01_20261022_r01`）3 项发现的关闭 + 确认被审技术文件与权威证据未被本轮修复改动（**不做全量重审**）
- **closure verdict：`PASS`** —— F-01 / F-02 / F-03 全部关闭，未发现新的阻断项
- 机器可读版：`closure_review.json`（同目录）

## 1. 逐项关闭结论

### F-01（原 MEDIUM）C1「离散字段全等」覆盖被表述为完整 → **CLOSED**

| 关闭条件（第 1 轮） | 实际交付 | 核验 |
|---|---|---|
| 显式登记 `nms_decision`/`output_order` 为 NOT_COMPARED 并写明理由 | `S5-C/S5C-ADDENDUM-20261022-001-C1-discrete-fields.md`（3432 B）+ `S5-C/c1_discrete_fields_claim_v2.json`（1997 B，`json.load` exit 0） | 8 项契约清单 ↔ 6 项 COMPARED ↔ 2 项 NOT_COMPARED（上游未承载）逐条写明 |
| 不覆盖 r04 产物 | addendum 的 `amend_scope` 明确「仅收窄措辞、不修改 r04 任何原始产物、不改变其 PASS 与退出码」 | **r04 目录内全部文件 mtime = `10:29:38`**（早于修复 `10:43`）；`run_manifest.json` = `61c0d507f022de3ce2e57255b284df2e7f4ed5f3a0115b728fbd8561313120a9`（与 Lead 声明一致） |
| 绑定真实 | addendum 绑定 r04 manifest `61c0d507…`、checker `703959a2…`、契约 `8eac7007…`、ref `4d9fe369…` | 四项**均与磁盘现值一致** |
| 事实正确 | 理由：S4-C golden `detections_expected`/`detections_actual` 与该二字段无交集；S4-A `detection_record.fields` 未承载 | 我独立复核为真（第 1 轮已逐文件确认，本轮复查一致） |

### F-02（原 MEDIUM）加固前 r03 被标为「权威」 → **CLOSED**

| 关闭条件 | 实际交付 | 核验 |
|---|---|---|
| 改标权威 = r04、r03/r03_limit8 = 加固前历史被取代 | `S5-C/EVIDENCE_RETENTION_INCIDENT.md:7-9` 已更正 | 第 9 行明确「保留不删、不作权威引用」，并注明 r03 报告无 `degenerate_source_rule` 段 |
| 历史绑定陈述与磁盘一致 | r03 / r03_limit8 各自 `run_manifest` 绑定 ref `556f78c53bba8a75db5746b2cf94f5cfbb5c0f004400acafb5dfec809a05e4be`、checker `60b5c7c70ca6cde1eed12cb49bcdfbf1f6849a65f4c7e0f5f5c19260c61cd759` | **逐值一致** |
| 附带陈述正确 | 「r03 报告无 `degenerate_source_rule` 段」「r03 与 r04 均为 PASS 且 13/13 退出码一致」 | r03 `degenerate_guard.contract_key_present` 为空字符串；r03 `exit_code_verification.step_count=13`、`all_matched=true` |
| 不删原产物 | r03 与 r03_limit8 各新增 `SUPERSEDED_BY_r04.md`（747 B / 458 B） | r03 目录 52 个文件、r03_limit8 5 个文件；未发现删除或改写迹象 |

### F-03（原 LOW）S5-A 旧 RunId 取代链不完整 → **CLOSED**

| 关闭条件 | 实际交付 | 核验 |
|---|---|---|
| r02 补取代说明 | 新增 `S5-A/s5a_g0_20261021_r02/SUPERSEDED_BY_r03.md`（644 B） | 指认 r02 绑定契约 `abc976a1…`；**复核为真**（r02 manifest 该值 = `abc976a1fe7a953e0d309411e5e8124495efd9a4c9ff9cf2ed490a02076623ab`） |
| r01 绑定指向改为 r03 | `S5-A/s5a_g0_20261021_r01/SUPERSEDED_BY_r02.md` 第 6 行已改 | 明示权威证据为 r03（契约 `8eac7007…`、参考实现 `4d9fe369…`），不再指向 r02；r01/r02 原产物保留（各 5 个文件） |
| r03 仍为 S5-A 权威、manifest 绑定契约 `8eac7007…` | r03 `run_manifest.json`：`status=PASS`、`contract_id=S5A-G0-v2`，8 项 `local_artifact_sha256` 与磁盘逐值一致 | 契约 = `8eac70076c3ba39de0c615bcc08b66bcc45f3fe87f0449a9eb3e32a318709911`、参考实现 = `4d9fe369edadb12394e65a0c5c90fda0fbbd61cdff597ecf5793700c43473553` |
| 附带陈述 | r01/r02/r03「unittest 同为 26/26 PASS」 | 三者 `console/unittest_s5a.txt` 均 `Ran 26 tests ... OK` |

## 2. 第 4 项确认：技术文件与权威证据未被本轮修复改动

| 对象 | 磁盘哈希 | 判定 |
|---|---|---|
| `verification/s5_display_geometry_reference.py` | `4d9fe369edadb12394e65a0c5c90fda0fbbd61cdff597ecf5793700c43473553` | 未变（= 第 1 轮值） |
| `docs/stage5/s5a_stage5_display_g0_fields.json` | `8eac70076c3ba39de0c615bcc08b66bcc45f3fe87f0449a9eb3e32a318709911` | 未变 |
| `docs/stage5/S5A_stage5_display_g0_spec_v2.md` | `ca5968d444db7a017a3c2e4e95d838f385c605837da92e31b4c2aa9d3cf56932` | 未变 |
| `scripts/stage5_s5c/check_s5c_stage4_regression.py` | `703959a2df4d230e596baca52e556b782f609efaf19b27d877ad1511eebfc5ab` | 未变 |
| `scripts/stage5_s5b/render_s5b_overlay.py` | `dbfef7aab3f5190f51f949646b9355cbe43ca326bf3318674ad9553b3f83bb5e` | 未变 |
| S5-C **r04** `run_manifest.json` | `61c0d507f022de3ce2e57255b284df2e7f4ed5f3a0115b728fbd8561313120a9` | 与 Lead 声明一致；**r04 最新 mtime = 10:29:38**（早于修复 10:43） |
| S5-B **r07_a** `run_manifest.json` | `75b6801945fb287015f835faa92aee0e25ee5fdc8f1d705f3dec47521313e5cb` | 与 Lead 声明一致；**r07_a 最新 mtime = 10:29:10** |

行为回归（证明技术文件内容未变 ⇒ 行为不变）：

```bash
python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --run-id rev2_pristine \
  --out tmp/5/S5-R/s5r01_20261022_r02/pristine --limit 8 --seed 20261021   # exit 0（C1 mismatch 0 → PASS）
python -B -m unittest verification.test_s5_display_geometry_reference -v   # exit 0（Ran 26 tests ... OK）
python -B -c "import json; json.load(open('report/evidence/S5-C/c1_discrete_fields_claim_v2.json',encoding='utf-8'))"  # exit 0
```

## 3. 残留观察项（非阻断，不构成关闭条件）

- **OBS-01**：`S5-A/r01/SUPERSEDED_BY_r02.md` 的文件名与标题仍为「已被 r02 取代」，正文第 6 行已更正权威指向为 r03。命名与内容存在历史不一致，但正文显式说明且 r02 目录另有 `SUPERSEDED_BY_r03.md`，实际不误导。
- **OBS-02**：`r04/summary.md` 仍保留原「离散字段全等」措辞（这**符合**「不修改 r04 任何产物」的取舍），收窄说明位于上级目录。若需提升可发现性，可在 r04 目录**新增**一个不改动既有产物的指针文件（如 `r04/SEE_S5C-ADDENDUM-20261022-001.md`）；非必须。
- **OBS-03**：addendum 已登记后续动作——正式阶段5 G0 建议把契约 `discrete_fields_must_match` 拆为「本层可比较 / 上游未承载」两段并与阶段4 契约同步。属阶段5 正式 G0 / Wong 决策范围。

## 4. 限制

- 本轮为聚焦关闭核验，未做全量重审；第 1 轮技术结论在技术文件哈希未变的前提下继续有效。
- 未运行 Vivado/xsim、未接硬件、未触碰他人 `hw_server`；本审查**不构成 G3/G4/G5**。
- 未逐字节比对 r03/r03_limit8 目录内每个历史文件与第 1 轮快照（采用 mtime + 文件清单 + manifest 绑定值复核，未发现删除或改写迹象）。
- 结论仅对本次记录的磁盘哈希有效；被审文件此后变更则本结论失效。

## 5. 交付与合规

- `closure_review.md`（本文件）、`closure_review.json`
- `console/closure_verification.txt`（[C1]–[C7] 逐项核验）、`console/regression_pristine_limit8.txt`、`console/regression_unittest_s5a.txt`
- 写权：仅 `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r02/` 与 `tmp/5/S5-R/**`；未改被审文件、未写 mailbox、未 `git add/commit`。