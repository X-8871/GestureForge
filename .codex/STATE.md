# 阶段5 状态（HDMI 结果显示与结果关联）——**离线范围冻结**

## 收尾快照（2026-10-27 19:55 UTC+8；本节优先于下方任何历史陈述）

- **冻结口径 `OFFLINE_SCOPE_FROZEN`（离线范围冻结）**：只冻结离线契约/实现/证据字节集；**不主张** G0/G1/G3/G4/G5 或任何板级/实物/实时结论。本卡（`task-29`/`S5-T04`）**不需要板卡**，本轮未连接、未加载位流、未烧录。
- **冻结前基线**（构建冻结集时 HEAD）：`2a2d2cc01cd31444a1a854115d99a31cbe8499bf`；**冻结提交（被审）**：`26b743901b4ec76107ca2cd6a010337a5ae40bf2`（tag `stage5-offline-freeze-20261027`；本文件所在的收尾提交为其后置补记）。
- **冻结集**：`report/evidence/S5-T04/s5_freeze_20261027_r05/frozen_set.json`，**77 个成员 / 覆盖 196 个已跟踪文件**（契约与字节保真规则含 `.gitattributes` 共 14 / 离线实现 3 / 离线 replay-display 证据 44 / S5-T02 离线 7 / 宿主只读引用 9；目录成员为 `file_set`，逐件列 path+sha256+bytes），sha256 `109254238e2aede8ab9005ed153e768e611c3ba325a5b1b75b312b415408b1bf`。
- **校验器**：`verification/verify_stage5_frozen_set.py`（只读、fail-closed：0 一致 / 1 不一致 / 2 输入或环境错误；`--frozen-set` **必须显式给出**，禁止内置 RunId 默认路径）→ 实测 **exit 0 / `FROZEN_SET_VERIFIED`（77/77）**；**注入自测**（必须失败）→ **exit 0 / `SELFTEST_PASS`**：clean=0、改一字节=**1**、删一件=**2**。
- **离线回归主套件**：10 个模块 **142 项 / 0 失败 / 2 skip / exit 0**（168 s，虚拟长跑 106 573 帧在内）。
- **包装检查器**：`check_stage_delivery --mode evidence` M1/M2 均 **exit 0 / CHECKS_OK**；运行器 `final_exit=0`。
- **安静窗口**：0 个 `vivado.exe/xsdb/hw_server/vitis/xsim`；2 个 `vivado-mcp-server-windows` 桥接进程按 `DSH-20261027-017` 只作信息记录（非板级占用）。工作树无已跟踪改动、无 `index.lock`。
- **F6 自证（PASS）**：冻结提交 `26b743901b4ec76107ca2cd6a010337a5ae40bf2` 单独导出/检出后复跑——A `git archive` 导出（无 Git 元数据）内校验器 **exit 0 / `FROZEN_SET_VERIFIED`**；B 独立 `--shared --no-checkout` 检出内校验器 **exit 0** 且 `check_stage_delivery` **exit 0 / CHECKS_OK**；C2 提交后 `handoff_check` **HANDOFF_OK / exit 0**。记录：`report/evidence/S5-T04/s5_freeze_f6export_20261027_r01/`。
- **tag**：`stage5-offline-freeze-20261027` → 冻结提交 `26b7439`（本地附注 tag，**不 push**）。
- **冻结后文字纠正**：r05 冻结文书 §1 第 2 项原稿误列 `scripts/stage5_s5a|s5b|s5c/**`（实际不在冻结集内）⇒ **只改 README 文字**并留痕（`console/doc_correction_after_freeze.txt`、README §9）；冻结集成员/哈希、校验器/自检/套件退出码均未变，清单按纠正字节重建后复检 **exit 0**。生成器文案缺陷（属冻结集成员，冻结后不改）登记为下一轮待修。

## 独立复审（2026-10-27）：**PASS，0 阻断**

- 复审记录（主仓，只读）：`report/evidence/CTRL-DSH-HANDOFF/reviews/S5_T04_20261027_r01/`（`review_summary.json` sha256 `317848735171eb79…`、`S5_T04_REVIEW_REPORT.md` sha256 `eb517a52631a2305…`）；主仓接收提交 `d4e835c`。
- 复审核心事实：字节身份 `26b7439`（tag 指向、干净、未 push）｜文书身份 `2797cc3`｜`26b7439..2797cc3` 仅 STATE/文书/清单/F6 包，**`frozen_set.json` 两侧同一 blob `11e1aeb`**｜校验器三路（隔离归档/独立检出/live HEAD）均 `FROZEN_SET_VERIFIED`｜**19 组注入** 0/1/2 真实可区分（非恒真）｜全量重算 **196 文件 0 不符、范围洞 0**（77 成员＝58 file＋19 file_set，分组 14/3/44/7/9）｜F6 两路 exit 0｜回归 **142/0/2**、106 573 帧长跑复现｜构建器可复现 members。
- **5 项非阻断（留到下一次重冻结时修，本冻结基线不受影响）**：
  - **F1**：校验器 docstring 称"路径越界 ⇒ exit 2"，实现无 containment 检查（`../x`/绝对路径越出 `--root` 实测 exit 0）；r05 冻结集内**无**越界路径，风险受限 ⇒ 建议 **G5 前**补检查或改措辞。
  - **F2**：README §6 措辞易误读为"归档导出副本内也跑了 checker"；实际 checker 只在独立检出跑（归档无 `.git` ⇒ checker exit 2），包内 console 已分列、**不构成假 PASS** ⇒ 改措辞。
  - **F3**：`frozen_set.json.superseded_runs` 只登记 r00/r01，r02/r03/r04 的取代原因仅在 STATE/tag/提交消息 ⇒ 下轮补齐。
  - **F4**：两个 F6 失败目录内部 `run_id` 仍为 `…_r01`（修复前硬编码残留）；**不重写失败证据**，下轮加指认说明。
  - **F5**：构建器 docstring 写 `dir_digest`，实为 `file_set`（该分支本次未用）⇒ 下轮修注释。

## task-27（回放/彩色输入路径 + 离线动态回归）：复审 PASS；N1–N5 已修（2026-10-27 20:2x）

- **复审**：`PASS`（0 阻断；实现层为真、30/0 回归可复现、`106 572×16 890 000=1 800 001 080 000 ns` 精确、240 次重复已标注）。
- **N1（阻断，已修）**：`r01` 清单以工作树 LF 字节绑定 `scripts/stage5_t27/run_s5t27_evidence.py`（`eeee8529…`、15 578 B），
  目录无 `-text` ⇒ 干净检出 CRLF（15 847 B）使 checker exit 2。已加子目录 `.gitattributes`（`scripts/stage5_t27/`、`report/evidence/S5-T27/`，`* -text`，
  **未动冻结的根 `.gitattributes`**）并**新 RunId `s5t27_replay_colour_20261027_r02`** 重生成；干净检出自证：`report/evidence/S5-T27/s5t27_clean_checkout_20261027_r01/`
  （gate `--mode strict` **exit 0**、`check_stage_delivery --mode evidence` **exit 0**）。
- **哈希基座新规（2026-10-27 Wong 批准；主仓检查器 HL-T79 已支持内联）**：`delivery_manifest.json` **内联**基座 ——
  清单级 `hash_basis="commit_blob"` + `hash_basis_commit=<40 位真实 SHA>`、`files[]` 逐项 `hash_basis="commit_blob"`；
  伴生基座表 `hash_basis_manifest.json` 与索引 `hashes_sha256.txt` 已**删除**（避免两文件漂移与自引用循环）。
  `hash_basis_commit` 语义＝**承载 `files[]` 全部字节的提交**（清单自身不入 `files[]`，其字节不上卷）：r02＝`f9755f6`、自证包 r02＝`feb34c9`。
  实测（HEAD `643684c`）：r02 与自证包 `check_stage_delivery --mode evidence` **0/0**、`check_manifest_hash_basis --mode strict` **0/0**、`--mode declared-only` **0/0**。
- **干净检出自证**：`report/evidence/S5-T27/s5t27_clean_checkout_20261027_r02/`（针对 C8 `76c74fe`；`CLEAN_CHECKOUT_PASS`，5 项门禁全 0）；r01 保留为历史（双文件形式）。
- **N2（已修）**：`assert_replay_record` 补齐 `algorithm`/`value`/`length_bytes==stride×height` 三要素；自检 6 类注入、用例 17 项全 OK。
- **N3（已修）**：本文件第 62 行旧句改为"离线部分已交付；板级/实时未做"。
- **N4（仅登记）**：冻结 `file_set` 目录 `scripts/stage5_t03/` 新增 3 个跟踪文件（25→28）；冻结成员未变、校验器仍 77/77；**下次重冻结纳入**。
- **N5（已注明）**：相关套件 2 项 skip 属**上游**（阶段4 契约冻结后被改：登记 `7228f513…` ≠ 现状 `25bc30d5…`，消费链按设计 fail-closed），非本卡缺陷。

## task-27 交付明细（r01，2026-10-27 19:55）

- **实现层**（新文件，**未改 S5-T04 冻结成员**）：`scripts/stage5_t03/s5t03_replay_colour_input.py` —— 装载即**现场重算**源帧 sha256/字节数；
  逐帧 `frame_integrity`（algorithm/value/length_bytes 三者全等）；每条记录携带 10 项 `replay_source_*`；
  **非零** `capture_time_ns`（证据模式＝阶段3 文档化真实抓取时刻 `1792776253000000000`）；`replay_not_live=true`；
  对每条记录跑阶段4 输入契约 `validate_result_record`。自检 `REPLAY_INPUT_SELFTEST_PASS`，**4 类必失败注入全部被拒收**
  （`replay_not_live=false` / `capture=0` / 缺 `replay_source_*` / `frame_integrity` 不符）。
- **离线动态回归**（`s5t03_replay_colour_regression.py`；输入＝阶段4 **已冻结**带框回放包 `988f2cae…` + 阶段3 固定帧）：
  `results.json` 判定 **`REPLAY_OFFLINE_REGRESSION_PASS`（30 项断言 / 0 失败）**，结论标注 **回放/离线**；
  覆盖坐标（冻结框→像素逐值、正面积、画布内、裁剪幂等）、帧关联（240 帧成对、语义唯一 B、每帧恰一次提交）、
  过期边界（`==200 ms` 不过期 / `+1 ns` 过期 / 显式 flag 过期）、顺序规则（重复键/回退/等价未声明拒绝、声明放行、跳帧致过期）、
  异常分支（TIMEOUT/ERROR/DROPPED/NO_HAND/裁剪零面积分列且不绘制）、长跑（**106 573 帧 / 1 800 001 080 000 ns**、时间戳单调、计数可复算）；
  判别力：篡改冻结包字节 ⇒ 驱动 **exit 2**（用例固化）。
- 用例：`scripts/stage5_t03/test_s5t03_replay_colour.py` **14 项 OK**（含 5 类拒收负例 + 1 项回归判别力负例）。
- 证据：`report/evidence/S5-T27/s5t27_replay_colour_20261027_r01/`（`results.json`、`frame_assertions.jsonl` 240 行、
  `replay_input_selftest.json`、`summary.md`、`console/**`、清单+哈希）；运行器 `final_exit=0`（自检/回归/套件/安静窗口/检查器 M1/M2 全 0）。
- 板级对齐：`docs/stage5/S5T27_replay_colour_input_path_v1.md` §3 —— B1–B10 逐项标"离线已获前置证据 / 必须上板"
  （B3/B5/B6/B8 部分前置已获；B2/B7/B9/B10 必须上板）；R1 冻结原文不改写，本节为增量对齐。
- **未做**：板上/实时回放、摄像头真实采集、真彩目视、HUD 屏上视觉、真实 30 分钟、T5-10、B1–B10 全项、G0–G5（均未主张）。

## 写权与交接（更正过期陈述）

- 旧 STATEMENT「Codex 仍持本树写权」**已过期**：本树写权自 **2026-10-26 21:21** 起由 **DSH 阶段5 总控**持有（`handoff_check --claim` = `HANDOFF_OK` PASS 9 / 0）。
- 本卡执行方＝DSH 阶段5 总控；复审由 DSH 项目总控另派 Reviewer；**复审期间停写被审对象**。

## 冻结范围（只此四类）

1. **离线契约/规格**（`docs/stage5/**`）：显示契约 JSON、输入绑定 JSON、离线参数/用例骨架、JSON 契约、`stale=200 ms` 的 UR-3 决策（引用 Wong 批准回执）。
2. **离线实现**：`scripts/stage5_t03/**`（渲染/回放/长跑/多几何/HUD 遮挡/JSON 契约/阶段4 冻结包消费）＋ `verification/s5_display_geometry_reference.py`。
3. **离线证据包**：`s5t03_offline_replay_display_…_r06`、`…offline_long_run_replay…_r04`、`…multi_geometry_render…_r02`、`…json_contract…_r04`、`…hud_occlusion…_r02`、`…stage4_frozen_replay…_r04`、`…stage4_positive_replay…_r01`、`S5-T01/s5t02_offline_dynamic_map_20261027_r02`。
4. **宿主只读引用**（`scope=host`）：阶段3 参考帧 `939fce22…` 与回放绑定、阶段4 回放结果包冻结记录/索引/带框包、Wong `stale=200 ms` 回执、阶段3/阶段4 局限引用。

## 明确不主张（逐条）

真实回放接入（板上/实时）｜板上动态映射/绘制｜摄像头真实采集｜真实集成 30 分钟｜T5-10 板上回归｜HUD 屏上视觉确认｜真彩目视｜任何 G0/G1/G3/G4/G5 通过｜真实采集质量/颜色｜端到端延迟实测（时钟 `PENDING_MEASUREMENT`）。
`task-27`（回放/彩色输入路径实现 + 用阶段4 冻结回放包做离线动态回归）**离线部分已交付**（见下文 task-27 节，证据 r01/r02）；**板级/实时部分未做**（NOT_RUN）。本冻结只覆盖既有离线骨架与离线消费。

## 继承的上游局限（引用不改写）

- 阶段3：VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核（`dbdf/…/S3-T17/stage3_closeout_20261026_r01/manifest.json`）。
- 阶段4：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（`w4/docs/stage4/s4_stage4_freeze_supplement_hardware_20261027_r01.md`）。

## 未闭合项

1. **历史模块已知缺口**：`scripts/stage5_s5a|s5b|s5c` 探测 83 项 / **18 失败**（根因：其测试依赖 w4 侧黄金数据 `s4c_replay_20261021_r05`、`S4-B/20261021_r13` 上游漂移）；不在冻结集、不计入本冻结回归主张，原始输出见冻结包 `console/legacy_suite_known_gap.txt`。
2. `task-27` NOT_RUN（阶段4 回放包已冻结、本树有离线消费，但该卡未交付）。
3. 板级 B1–B10 全项暂停：Wong 拔板后未重连复验；重连后需先过第 0 步（占用/部署身份/运行期回读地址/**真彩目视需 Wong 在场**），再按 `CDX-20261023-018` §3 发单次窗口。
4. 端到端真实链窗口（`end2end_real_chain_window_plan_20261027_r01`）：P1=task-27、W-E=B1–B10 均待开工信号。
5. 阶段5 G0/G1/G3/G4/G5 与实物验收仍未通过；`UR-1`（阶段4 回放扩展字段命名并入共享契约）仍待阶段4 确认。

## 证据与恢复入口

- 冻结文书/冻结集/清单：`report/evidence/S5-T04/s5_freeze_20261027_r05/`（README、`frozen_set.json`、`frozen_set_report.json`、`selftest_injection.json`、`results_freeze.json`、`delivery_manifest.json`、`console/**`）
- F6 自证：`report/evidence/S5-T04/s5_freeze_f6export_20261027_r01/`
- **被取代/失败证据（保留不改写）**：`…_r00_runner_crash`（套件摘要解析崩溃）、`…_r01`（导出未带 `.gitattributes` ⇒ 44 项换行所致哈希不符）、`…_r02_incomplete_builder_path`（构建器默认 `--out` 覆盖风险）、`…_r03`（校验器/F6 驱动器硬编码 r01 RunId ⇒ 会验错包）、`…_r04`（目录摘要被未跟踪的 `__pycache__`/构建产物污染 ⇒ 3 项不符）、`s5_freeze_f6export_20261027_r00_crlf_fail` 与 `…_r00b_tracked_dirs_fail`（F6 前两轮失败原始输出）
- 复跑：`python -B verification/verify_stage5_frozen_set.py --root . --frozen-set report/evidence/S5-T04/s5_freeze_20261027_r05/frozen_set.json` → 期望 `FROZEN_SET_VERIFIED` / exit 0；加 `--selftest tmp/5/S5-T04/selftest` → 期望 0/1/2。
- 恢复命令：`git -C D:/codex-worktrees/w5 rev-parse HEAD; git -C D:/codex-worktrees/w5 status --short; git -C D:/codex-worktrees/w5 tag --list "stage5-offline-freeze*"`

## 交接行（11 字段，2026-10-27 19:55 UTC+8）

任务=`task-27 阶段5 回放/彩色输入路径实现 + 离线动态显示回归（已交付 r01；S5-T04 离线冻结复审 PASS 保持）` | 负责人=`DSH 阶段5 总控（2026-10-26 21:21 起正式认领）` | 工作树/分支=`D:\codex-worktrees\w5` / `stage5-display-prep` | 起始提交=`2a2d2cc01cd31444a1a854115d99a31cbe8499bf` | 允许修改范围=`scripts/stage5_t03/s5t03_replay_colour_input.py、s5t03_replay_colour_regression.py、test_s5t03_replay_colour.py、scripts/stage5_t27/**、docs/stage5/S5T27_*、report/evidence/S5-T27/**、.codex/STATE.md` | 未提交改动归属=`本轮全部为本卡产物，随后续提交同批入库；S5-T04 冻结成员未改` | 让出声明=`本卡为**离线回放**：未连接/未加载位流/未烧录/未占用 JTAG 串口；板级 B1–B10 仍暂停（需 Wong 开工信号 + 第 0 步，真彩目视需 Wong 在场）` | 心跳(UTC+8)=`2026-10-27 19:55` | 证据入口=`report/evidence/S5-T27/s5t27_replay_colour_20261027_r01/`、`docs/stage5/S5T27_replay_colour_input_path_v1.md`、`report/evidence/S5-T04/s5_freeze_20261027_r05/` | 恢复命令=`python -B D:/codex-worktrees/w5/scripts/stage5_t03/s5t03_replay_colour_input.py --binding D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json` | 状态/下一接手方=`TASK27_DELIVERED（实现层＋离线回归 PASS：30 断言/0 失败、长跑 106 573 帧、B1–B10 对齐已交；待 DSH 项目总控核收/派审）→ 下一步：W-E 板级窗口待 Wong 信号；重冻结时一并修 S5-T04 复审 F1–F5 / 本阶段总控`
