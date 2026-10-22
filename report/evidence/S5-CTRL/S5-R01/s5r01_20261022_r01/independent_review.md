# S5-R 阶段5 离线准备独立审查报告（1 轮，关键风险）

- RunId：`s5r01_20261022_r01`
- Reviewer：`rev-s5`（独立 Reviewer，不属 S5-A/S5-B/S5-C 开发方；仅只读被审文件）
- 完成时刻（UTC+8）：2026-10-22 10:41
- **verdict：`CHANGES_REQUIRED`**（仅限文档/证据包标注与覆盖披露；未发现门槛放宽、伪造通过或几何第二套实现）
- 机器可读版：`independent_review.json`（同目录）

## 1. 核查范围与版本

| 项 | 值 |
|---|---|
| 工作树 | `D:\codex-worktrees\w5`，分支 `stage5-display-prep`，HEAD `acd2df6774ead5c8085fa2417882c8315c18eecd` |
| 未提交状态 | 被审新增文件均为未跟踪；本审查未 `git add`/`commit` |
| 上游只读基线 | `D:\codex-worktrees\w4`，HEAD `73c3dadbf16f58f3ce85f34620855f7bdc408f5a`，`git status --short` **0 行（干净）** |
| 主树 | `D:\FPGA_Competition`，**无任何 stage4/stage5 相关改动** |
| 被审文件哈希（磁盘实际值） | `s5_display_geometry_reference.py` = `4d9fe369edadb12394e65a0c5c90fda0fbbd61cdff597ecf5793700c43473553`（与任务卡声明一致）<br>`s5a_stage5_display_g0_fields.json` = `8eac70076c3ba39de0c615bcc08b66bcc45f3fe87f0449a9eb3e32a318709911`<br>`S5A_stage5_display_g0_spec_v2.md` = `ca5968d444db7a017a3c2e4e95d838f385c605837da92e31b4c2aa9d3cf56932`<br>`PROVENANCE_s4d_v1_baseline.md` = `ed94999e7cc935ac05c371aa63350ab370d1fb3e551e2669574230d787ce190a`<br>`test_s5_display_geometry_reference.py` = `0ef2a969319e34e95155a151da38bef737565789985dbde709041f6d87dae92d`<br>`check_s5c_stage4_regression.py` = `703959a2df4d230e596baca52e556b782f609efaf19b27d877ad1511eebfc5ab`<br>`render_s5b_overlay.py` = `dbfef7aab3f5190f51f949646b9355cbe43ca326bf3318674ad9553b3f83bb5e`<br>`run_s5b_evidence.py` = `de33db93d13931402e7357709f2c34751575a12b15eb3c8063a690daa44061fb`<br>`test_s5b_overlay.py` = `8d4e2e5faaf19e0336e8a55e11c4b0cc7737130d369b8eb20dccb667cb285c9f` |
| 权威证据 | S5-A `s5a_g0_20261021_r03`；S5-B `s5b_20261021_r07_a|_b`；S5-C `s5c_regression_20261021_r04`(+`_limit8`) |
| 历史（加固前） | S5-C `r03`/`r03_limit8`（ref `556f78c5…`、checker `60b5c7c7…`）；S5-B `r06_a|_b`；S5-A `r01`/`r02` |

写权遵守：只写 `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01/` 与 `tmp/5/S5-R/`；未写被审目录、未写 mailbox、未 git 提交、未运行 Vivado/xsim、未触碰 `hw_server`（PID 4812，他人所有）。

## 2. 逐项关键风险结论

| 风险 | 结论 | 关键独立证据 |
|---|---|---|
| 1 几何唯一来源 | **PASS** | 渲染路径全部 `reference.*`；两处本地复算（S5-B `hand_geometry`、S5-C `independent_letterbox`）均在断言侧且已注明。Reviewer 自建探针对 **13 组尺寸**做纯整数正算 + Fraction 精确逆算：S5 参考 == D2 冻结 == 独立值，全部一致 |
| 2 坐标门槛未放宽 | **PASS（附 F-01）** | `GATE_A_SCORE_TOL=1e-6`、`GATE_A_XYXY_TOL=1e-6`、`GATE_B_PIXEL_TOL=1.0` 与契约逐项一致；SKIP/NOT_RUN 均如实分列。缺口：契约 8 个离散字段中 `nms_decision`/`output_order` 未被比较且未披露 |
| 3 过期阈值同源同值 | **PASS** | ref `200_000_000` == 契约 `200000000` == S4-A `stale_age_limit_ms=200`×1e6（S5-C C2 三方 match）；`is_stale(limit)==False`、`is_stale(limit+1)==True`（严格大于）；S5-B `age==limit` 用例 1 框绘制、`limit+1` 用例 0 绘制 |
| 4 画面语义 | **PASS** | 固定语义 B；两个年龄分别记录（5000000 / 15000000 等）；对 S5-B/S5-C 全部文本产物扫「同帧」命中 **0**；docs 中 14 处均为禁止性/定义性语句 |
| 5 零面积/零框/边缘/多框 | **PASS** | 零面积一律不绘制（C4 探针 4/4，原始展开像素 >0 而展示像素 =0）；NO_HAND 恒零框且未被判过期；15 框用例 15/15 且 `source_order` 1000..1014 原样保留；渲染路径无排序 |
| 6 阶段4 数值链追溯 | **PASS** | 指定复现 `--limit 8 --seed 20261021` → **exit 0**；全量 109 样本自跑 → **exit 0**；`--tamper-probe source_order` → **exit 1**（gate=discrete，1035→1036）；`--tamper-probe score_ulp` → **exit 1**（gate=**D**，Gate A 误差 1.110e-16）⇒ 1 ULP 只能由 Gate D 捕获，Gate D 为附加接口证据而非替代门槛 |
| 7 证据诚实性 | **PASS（附 F-01/F-02/F-03）** | 全部声明哈希与磁盘一致；S5-C r04 退出码 13/13 match；**独立重渲染 S5-B 与 r07_a 逐文件全等（26 PNG + 21 JSON）**；S5-A 26 tests、S5-B 56 tests 均 exit 0；r01/r02 删除已如实披露 |
| 8 越权/过度声明 | **PASS** | 状态 `STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED`，正文明确未开工；未声称满足计划 L88；w4 与主树无改动 |

## 3. 复现命令与真实退出码

```bash
# 1) 任务卡指定复现（限 8 样本）
python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --run-id rev_pristine \
  --out tmp/5/S5-R/s5r01_20261022_r01/pristine2 --limit 8 --seed 20261021      # exit 0
# 2) 全量 109 样本
python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --run-id rev_full \
  --out tmp/5/S5-R/s5r01_20261022_r01/pristine_full                            # exit 0
# 3) 反例：离散字段篡改（必须失败）
python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --run-id rev_tamper_so \
  --out tmp/5/S5-R/s5r01_20261022_r01/tamper_source_order --limit 8 --seed 20261021 \
  --tamper-probe source_order                                                  # exit 1
# 4) 反例：1 ULP（Gate A 内，仅 Gate D 可捕获）
python -B scripts/stage5_s5c/check_s5c_stage4_regression.py --run-id rev_tamper_ulp \
  --out tmp/5/S5-R/s5r01_20261022_r01/tamper_score_ulp --limit 8 --seed 20261021 \
  --tamper-probe score_ulp                                                     # exit 1
# 5) S5-A 自检
python -B -m unittest verification.test_s5_display_geometry_reference -v       # exit 0 (26 tests)
# 6) Reviewer 独立几何复算
python -B tmp/5/S5-R/s5r01_20261022_r01/independent_geometry_probe.py          # exit 0 (13 尺寸全一致)
# 7) Reviewer 独立重渲染 + 与 r07_a 逐文件比对
python -B scripts/stage5_s5b/render_s5b_overlay.py \
  --out tmp/5/S5-R/s5r01_20261022_r01/s5b --run-id rev_s5b --seed 20261021     # exit 0；26 PNG + 21 JSON 全等
# 8) S5-B 自带 unittest（包装器把 TMP_ROOT 隔离到 tmp/5/S5-R，避免写被审目录）
python -B tmp/5/S5-R/s5r01_20261022_r01/run_s5b_ut_isolated.py                 # exit 0 (56 tests)
```

原始输出与退出码见 `console/`：`00_repro_commands_and_exit_codes.txt`、`repro_*.txt`、`independent_geometry_probe.txt`、`hash_binding_verification.txt`。

## 4. 发现清单（按严重度，全部可低成本关闭）

### F-01（MEDIUM）离散字段覆盖被表述为完整，`nms_decision`/`output_order` 未比较且未披露

- **位置**：契约 `docs/stage5/s5a_stage5_display_g0_fields.json:110`（8 项清单）；`scripts/stage5_s5c/check_s5c_stage4_regression.py:591`（C1 仅比 `class_id`/`class_name`/`source_order`）与 `:1601-1607`（limitations 未列）；`report/evidence/S5-C/s5c_regression_20261021_r04/summary.md:13`（C1 PASS）。
- **依据**：S4-C golden 的 `detections_expected` **与** `detections_actual` 的框字段均只有 `class_id/class_name/score/xyxy/source_order`；S4-A `detection_record.fields`（required）同样只有这 5 项。契约与 checker 全文除契约第 110 行外**从不出现** `nms_decision`/`output_order`。契约该 8 项清单可追溯到 2A 规格第 75 行（`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md:75`：frame_id、检测数、类别、source_order、NMS 决策、输出顺序）。
- **影响**：读者会以为 8/8 离散字段已逐值核对，实际 6/8，且无 NOT_COMPARED/SKIP 说明，属覆盖与表述不一致，削弱 T5-10 结论强度。
- **缓解（已核实）**：C2 的 `accepted_set_equals_stage4_boxes` + C1 别名/Gate D 位型一致，从「显示层原样消费、不重排、不重判」角度间接约束了这两项，实质风险低。
- **关闭条件**：在新 RunId（或增补说明文件，不覆盖 r04）显式登记 `nms_decision`/`output_order` 为 NOT_COMPARED 并写明理由（上游记录不承载该二字段），同步进 summary.md、C1 段与 run_manifest；或把契约清单拆为「本层可比较」与「上游未承载」两段并注明依据。

### F-02（MEDIUM）证据保留披露文件把加固前的 r03 标为「权威」

- **位置**：`report/evidence/S5-C/EVIDENCE_RETENTION_INCIDENT.md:7`。
- **依据**：r03 绑定 ref `556f78c5…`、checker `60b5c7c7…`（磁盘现值为 `4d9fe369…` / `703959a2…`），其报告**没有** `geometry.degenerate_source_rule` 证据段；r03/r03_limit8 目录内无「历史/加固前」标注。任务卡明确 r04 为权威。
- **影响**：下游可能把加固前证据当作当前被审版本引用，违反「被审版本以磁盘实际文件与哈希为准」「明确被审版本」。
- **关闭条件**：把 r04 标为权威、r03/r03_limit8 标为「加固前历史、已被 r04 取代」；在 r03 与 r03_limit8 各放一条 `SUPERSEDED_BY_r04` 说明（不删除、不改写原产物）。

### F-03（LOW）S5-A 旧 RunId 取代链不完整

- **位置**：`report/evidence/S5-A/s5a_g0_20261021_r01/SUPERSEDED_BY_r02.md:5`；`.../r02/run_manifest.json`（契约哈希 `abc976a1…` ≠ 磁盘现值 `8eac7007…`），r02 目录无 SUPERSEDED 说明。
- **影响**：按 r01 指引使用 r02 会得到与磁盘不一致的绑定；需自行发现 r02 也已过期才能找到 r03。
- **关闭条件**：r02 目录补 `SUPERSEDED_BY_r03` 说明（列出差异），并把 r01 说明的绑定指向改为 r03。

## 5. 过程事实评估（不得忽略的既定事项）

1. **S5-C r01/r02 被删除**：`EVIDENCE_RETENTION_INCIDENT.md` 主动披露、认定为口径违规且不可恢复，纠正措施为「后续一律保留」。本审查确认 r03/r03_limit8/r04/r04_limit8 与 S5-B r06_*/r07_* 均在位、未被覆盖。**判定：削弱失败路径可追溯性，不影响技术结论；已列为阶段收尾过程缺陷**（并附带 F-02 的标注修正要求）。
2. **本轮 S5-B/S5-C 由 Lead 代跑**：证据效力经独立复现确认——我以同参数重跑 S5-B 渲染，与 r07_a **逐文件全等（26 PNG + 21 日志 JSON）**；S5-C pristine 与两个篡改探针退出码与证据一致。**判定：代跑不降低可复现性**。
3. **接口加固（10-21 22:55 / 23:40）**：由哈希链证实（加固前 ref `556f78c5…`/checker `60b5c7c7…` → 加固后 `4d9fe369…`/`703959a2…`，均等于磁盘现值），且加固后证据含 `geometry.degenerate_source_rule` 段、退化守卫正反两向共用同一守卫（我另以 `src_w<=1`/`src_h<=1`/`new_w<=1`/`new_h<=1` 探针复算，全部抛 `DegenerateGeometryError`，无 `ZeroDivisionError`）。

## 6. 限制与未核查项

- 未运行 Vivado/xsim、未接硬件、未触碰 `hw_server` ⇒ T5-08/T5-09/T5-11 真实统计、30 分钟无死锁、上板显示一律 NOT_RUN；本审查**不构成 G3/G4/G5**。
- 未整体运行 S5-B/S5-C 的 `.ps1` 驱动脚本：等价核心步骤已分别独立复现；其余 6 类篡改探针仅核对证据包内真实退出码与 Gate 命中记录。
- 未逐像素目视 26 张 PNG（采用逐哈希 + 断言日志 + 关键字段实读复核）。
- `D:\codex-worktrees\w2b` 不存在（现存 `96a3/dbdf/w4/w5`），无法核对该工作树；w4 与主树已核对且干净。
- 阶段4 `stale_age_limit` 仍为 DRAFT_PROPOSED：只能确认「同源同值 + 严格大于」，不能替代阶段4 G0。
- 结论仅覆盖上述磁盘哈希所示版本；被审文件此后变更则本结论失效。