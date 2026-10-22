# S5CTRL-20261022-002｜阶段5 离线准备收尾记录

- 时间：2026-10-22 10:52（UTC+8）
- 阶段总控：DSH 阶段5 总控（Lead）
- 工作树/分支：`D:\codex-worktrees\w5` / `stage5-display-prep`（起始提交 `acd2df6`，开工核验干净、无 `index.lock`）
- 性质：**阶段5 的离线准备完成，不是阶段5 正式开工、不是验收（G0/G1/G3/G4/G5 均未通过）**。

## 1. 交付清单（本轮）

| 任务 | 交付 | 权威证据 |
|---|---|---|
| S5-A | `docs/stage5/S5A_stage5_display_g0_spec_v2.md`（G0 定稿）、`docs/stage5/s5a_stage5_display_g0_fields.json`（契约 `S5A-G0-v2`）、`verification/s5_display_geometry_reference.py`（唯一几何/口径来源）、`verification/test_s5_display_geometry_reference.py`（自动内插误改优先：26 用例） | `report/evidence/S5-A/s5a_g0_20261021_r03/`（unittest exit 0，26/26 PASS） |
| S5-B | `scripts/stage5_s5b/render_s5b_overlay.py`、`run_s5b_evidence.py`、`test_s5b_overlay.py` | `report/evidence/S5-B/s5b_20261021_r07_a|_b/`（driver exit 0；21 用例、583/583 断言、26 PNG + 21 JSON、双 pass 逐文件 SHA256 一致） |
| S5-C | `scripts/stage5_s5c/check_s5c_stage4_regression.py`、`test_s5c_regression.py`、`run_s5c_evidence.ps1` | `report/evidence/S5-C/s5c_regression_20261021_r04/`（driver exit 0，13/13 步骤与期望一致；109/109 样本、104 框、最大 score/坐标误差 0、最大像素往返 0.499 px） |
| S5-D | `docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md`（5 条修订建议，不生效） | 本记录 §4；未改 w4 草案 |
| 基线出处 | `docs/stage5/PROVENANCE_s4d_v1_baseline.md`（5 个 v1 文件逐字节复制，SHA 绑定） | — |
| 独立审查 | `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01/`（第 1 轮：CHANGES_REQUIRED，3 项）、`s5r01_20261022_r02/`（第 2 轮聚焦关闭：**PASS**） | 见 §3 |

## 2. 冻结版本上的 Lead 最终验证（真实退出码）

| 检查 | 命令（简） | 退出码 | 预期 |
|---|---|---|---|
| S5-A 契约自检 | `python -B -m unittest verification.test_s5_display_geometry_reference -v` | **0** | 0 |
| S5-C 正对照 | `check_s5c_stage4_regression.py --limit 8 --seed 20261021` | **0** | 0 |
| S5-C 反例 | 同上 `--tamper-probe source_order` | **1** | 1（检出） |
| S5-B 渲染自检 | `render_s5b_overlay.py --selfcheck` | **0** | 0 |
| 写入方停止 | `git rev-parse --git-path index.lock` | **无锁** | 无锁 |
| 交付清单机器核验 | `python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json` | **0**（CHECKS_OK，errors 为空） | 0 |
| 交付清单确定性 | 两次生成逐字节一致（SHA-256 `6b3176cf…`） | **一致** | 一致 |

原始输出：`console/lead_final_*.txt`、`console/lead_final_git_state.txt`、`console/lead_final_hash_binding.txt`。

## 3. 独立审查结论与关闭

- **第 1 轮（`s5r01_20261022_r01`）verdict = CHANGES_REQUIRED**，3 项发现（均为文档/证据标注层面；未发现门槛放宽、伪造通过、几何第二套实现）：
  - F-01（MEDIUM）C1「离散字段全等」覆盖被表述为完整（8 项 vs 实比 6 项）→ 已用 `S5-C/S5C-ADDENDUM-20261022-001-C1-discrete-fields.md` + `c1_discrete_fields_claim_v2.json` 显式登记 `nms_decision`/`output_order` 为 `NOT_COMPARED（上游未承载）`，并收窄措辞；未改 r04 产物。
  - F-02（MEDIUM）加固前 r03 被标为权威 → 已改标权威=r04，r03/r03_limit8 补 `SUPERSEDED_BY_r04.md`（原产物保留）。
  - F-03（LOW）S5-A 取代链不完整 → r02 补 `SUPERSEDED_BY_r03.md`，r01 说明指向 r03。
- **第 2 轮聚焦关闭核验（`s5r01_20261022_r02`）closure verdict = PASS**：F-01/F-02/F-03 全部 CLOSED；被审技术文件与 S5-B/S5-C 权威证据哈希**未被本轮修复改动**（ref `4d9fe369…`、spec `ca5968d4…`、checker `703959a2…`、r04 manifest `61c0d507…`、r07_a manifest `75b68019…`）。
- Reviewer 独立复现（自建探针 + 隔离目录）：13 组尺寸几何三方一致；109 样本全量 checker exit 0；`source_order` 篡改 exit 1；`score_ulp` 篡改 exit 1（仅 Gate D 捕获，Gate A 误差 1.1e-16）；**独立重渲染 S5-B 与 r07_a 逐文件全等**（26 PNG + 21 JSON）⇒ Lead 代跑不降低可复现性。

## 4. 过程事实与缺陷登记（不隐藏）

1. **证据保留违规（S5-C）**：Developer 曾删除 `s5c_regression_20261021_r01`（驱动 bug 中止）与 `r02`（措辞修正前）两个运行目录，违反 `AGENTS.md` 证据保留口径；**不可恢复**。已如实登记于 `report/evidence/S5-C/EVIDENCE_RETENTION_INCIDENT.md` 并交 Reviewer 核查；技术结论不受影响。
2. **子代理失败与 Lead 代跑**：请求 Developer 用新 RunId 重跑时，`dev-s5b`/`dev-s5c` 均在完成前失败退出（无收尾消息）。为不阻塞，S5-B r07 与 S5-C r04 由 Lead 按既有驱动执行（真实退出码 0）；Reviewer 已独立复现确认无碍。归属如实记录。
3. **接口加固**：加固前证据（S5-B r06_a/b、S5-C r03/r03_limit8、S5-A r01/r02）一律标为历史/被取代，保留不删；权威证据均绑定加固后接口 `4d9fe369…` 与契约 `8eac7007…`。
4. **硬件**：开工时观测到阶段3 的 4 个 vivado 进程（22:43–22:45）；本轮期间本机出现他人 `hw_server`（观测 PID 4812，10:19 起）。本阶段**未启动、未重启、未结束**任何硬件服务，未占 JTAG/COM4。

## 5. 未冻结项与未执行项（如实标注）

- **NOT_RUN（需硬件）**：真实 HDMI 显示与摄像头联调、上板、烧录、连续 30 分钟无死锁（T5-09）、真实 FPS/延迟统计（T5-08）、截图/连续视频留证、阶段6 联动实测；G3/G4/G5 均不适用或未通过。
- **未冻结**：成品允许延迟上限、颜色表/字号（待阶段5 正式 G0 与 Wong）；阶段4 `stale_age_limit` 仍 `DRAFT_PROPOSED`（阶段5 已按同源同一常量 200 ms 使用，正式冻结须同步）；选项 A 扩展帧仍待与 2B 协商。
- **G0 后续动作**：把契约 `discrete_fields_must_match` 拆为「本层可比较 / 上游未承载」两段并与阶段4 契约同步（F-01 的根因，属正式 G0 范围）。
- **部分覆盖**：S5-B 的 T5-08/T5-10/T5-11 为 PARTIAL（口径与可复算性已断言，实测属硬件）；S5-C 的 T5-01/02/03/04/07 为 PARTIAL（像素索引级已断言，出图属 S5-B）。

## 6. 跨方事项（须由项目总控转达，本阶段不自行协商）

- **X-01**：阶段4 `stale_age_limit` 与阶段5 过期阈值须**同源同一数值**（本阶段用 200 ms / 严格大于）；阶段4 正式 G0 若取其他值须通知本阶段做适用回归。
- **X-02**：方案 B 下「采集/结果时间与推理耗时」的满足方式需项目总控确认（PS 侧日志证据方案落点，或推进方案 A 扩展帧与 2B 协商）；**不得**据此宣称满足阶段计划第 88 行。
- **X-03**：阶段5 显示实测的前置条件＝阶段3 颜色验收通过（当前受阻、根因=硬件）＋ 阶段4 正式联调跑通 ＋ 2B 明确让出 JTAG/COM4 与 `hw_server`。

## 7. 机器可读交付清单

- 权威清单：`report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json`（`schema_version=1`）：绑定 `source_commit`、上游接口（S5A-G0-v2 契约/规格、S4-A DRAFT、阶段计划）、运行目录全部文件与交付源码（`role=source`）的 SHA-256、检查项与真实退出码、限制；由 `verification/check_stage_delivery.py --mode evidence` 只读核验，**退出码 0 / CHECKS_OK（errors 为空）**，输出确定性（两次生成逐字节一致，SHA-256 `6b3176cf…`）。
- 布局说明：控制记录按提示词要求落在 `report/evidence/S5-CTRL/<task_id>/<run_id>/`（三段式），而检查器要求 `evidence_dir` 精确等于 `report/evidence/<task_id>/<run_id>`（两段式），故机器清单落在规范路径。本目录首次尝试的清单被检查器拒绝（退出码 2、41 条 schema 违规），**保留为失败证据**，说明见 `DELIVERY_MANIFEST_SUPERSEDED.md`。
- `--mode inputs` **不适用**：本任务无冻结的上游接口（按 `report/README.md`：无本地输入的独立任务只对交付证据运行 evidence），未伪造接口或输入。
- 检查器通过**仅**表示清单/文件绑定与目录检查通过，**不代表**接口语义正确、阶段5 开工或任何验收通过。

### 7.1 字节保真与 EOL 修复（提交后发现并修复，如实登记）

- **发现**：首次提交 `0b942ed` 时 Git 提示 `LF will be replaced by CRLF`。核查后确认：Python 文本模式写出的证据文件（`console/*.txt`、`run_manifest.json`、`summary.md`）在**工作树为 CRLF**，而 `core.autocrlf=true` 提交后 **blob 为 LF** → 交付清单绑定的 12 个文件中 **4 个** blob ≠ 工作树字节。
- **影响**：清单绑定的是**工作树字节**；在另一种 checkout 配置（如 `autocrlf=false`）下由 blob 还原的文件哈希会与清单不符，削弱「按清单复现」的能力。**技术结论与断言不受影响**（独立审查在同一工作树完成，当时哈希一致）。
- **修复**：按项目既有惯例（`.gitattributes` 对证据/验证文件使用 `-text`），为阶段5 路径加 `-text` 并重新入库，使 **blob == 工作树字节**；修复后清单绑定的 12/12 文件 blob 与工作树 SHA-256 一致。
- **复现口径**：所有证据/清单哈希以**仓库内字节**为准；复现命令 `git cat-file blob <commit>:<path> | sha256sum` 与工作树 `sha256sum <path>` 应相同。
- 该修复只涉及 EOL 策略与重新入库，**不改**任何实现、规格、阈值或结论；交付清单核验（CHECKS_OK / exit 0）在修复后重新确认。
- **提交链（本阶段）**：`0b942ed`（交付本体，425 文件）→ `ff8d78c`（`.gitattributes` `-text` + 本记录与 STATE 更新）→ `256fc98`（`git add --renormalize`，143 文件按新属性重存）＝ 本阶段 HEAD。修复后复验：清单绑定的 **12/12** 文件 blob 与工作树 SHA-256 一致，`check_stage_delivery.py --mode evidence` 仍 **exit 0 / CHECKS_OK**，工作区干净。
- **清单 `source_commit` 语义**：`delivery_manifest.json` 的 `source_commit = acd2df6` 是**起始基线**（本阶段交付即 `acd2df6`→`256fc98` 的差异）；清单对交付物的绑定以**逐文件 SHA-256**（`role=source` 8 项 + 运行目录文件）为准，不以 `source_commit` 指代最终版本。

## 8. 边界声明与下一步

- 本阶段未改 w4、主树、`dbdf`、`w2b`、`96a3`、厂商原件与两个 mailbox；未提交任何他人工作树。
- 下一步（阶段5 正式开工入口）：① Wong/正式 G0 固定成品指标与契约清单拆分；② 阶段3 颜色验收通过；③ 阶段4 正式跑通；④ 2B 让出硬件；之后方可开启阶段5 正式开工与真实显示验收。
- 本树在本记录同批提交中入库（提交哈希见 Lead 给 Wong 的报告）。

## 交接行（11 字段，2026-10-22 10:52）

任务=`HL-T13 阶段5 离线准备（规格定稿 + 离线渲染自测 + 阶段4 数值链回归勾连 + 独立审查关闭）` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`acd2df6` | 允许修改范围=`docs/stage5|stage4|stage6/**`、`verification/s5_*.py`、`scripts/stage5_*/**`、`report/evidence/S5-*/**`、`tmp/5/**`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，随本记录同批提交（tmp/ 为忽略项）` | 让出声明=`本阶段离线准备完成，写入停止；本树可交回项目总控/下一阶段总控（OFFERED 语义），无遗留未提交改动` | 心跳(UTC+8)=`2026-10-22 11:50` | 证据入口=`report/evidence/S5-A/s5a_g0_20261021_r03/`、`report/evidence/S5-B/s5b_20261021_r07_a/`、`report/evidence/S5-C/s5c_regression_20261021_r04/`、`report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261022_r02/` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`DONE（离线准备）/ 项目总控核对后决定阶段5 正式开工时机；显示实测待阶段3 通过 + 阶段4 跑通 + 2B 让出硬件`