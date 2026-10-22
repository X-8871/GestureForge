# S6-A 修订记录 v1.7 / r08（第 7 轮复评：BLK-r07-1 + N-r07-1..6 收尾）

- 任务：`S6-A`；被审基线：`bdcf8963300475a61f26cbc3ec85a32275b781d2`（r07，判 CHANGES_REQUIRED）；新 RunId：`s6a_g0_20261022_r08`（r01..r07 均不覆盖）
- 复评来源：report/evidence/CTRL-DSH-HANDOFF/reviews/S6A_r07_20261023_r01/ 与 reviews/S6B_r02_20261023_r01/（其 NB-09 段由本任务取代）
- 复评结论：S6-A r07 = CHANGES_REQUIRED（1 阻断 BLK-r07-1 + 6 非阻断）
- 阈值纪律：**24 项参数值与 PENDING_APPROVAL 未改**；未在测试集调参；未触碰硬件
- 状态：**PENDING_REVIEW（是否再复评由项目总控决定；本记录不构成通过）**

## 阻断

### BLK-r07-1
- 问题：M4 修正在 S6-A 侧漏 8 处仍写「不可达／『不得』计·入覆盖」，其中 `hand_computed_cases.json` 的 HC-23 `expected.m4_reachable_under_draft 为 false` 由 C7 机器断言 → C7 与 C16 同时通过却结论相反。
- 修正：8 处统一为「M4 可达并计入覆盖；不可达仅 B16 S_DEDUP 与 M7」；HC-23 的机器断言改为 true 并保留「若 TARGET_CONTINUES 含分数门」的历史对照字段（仅对照、不参与判定）；C16 新增全包禁语断言防复发。
- 证据：docs/stage6/s6a_stage6_g0_behavior_v1.json（parameter_notes.T6-S04 / reachability.consequence / review_correction）, report/evidence/S6-A/s6a_g0_20261022_r08/hand_computed_cases.json（HC-23）, verification/s6_g0_selfcheck.py（C16 禁语断言）, probe_m4_unreachable_phrase_stdout.txt（注入实测 exit 1）, claim_verification.json（S6A-C1/S6A-C2）
- 状态：FIXED_PENDING_REVIEW

## 非阻断

| 项 | 处置 | 证据 |
|---|---|---|
| N-r07-1 | 调整顺序（先工作区、后清单）；报告内写明 order_note。 | verification/export_selfproof.py, export_selfproof.json |
| N-r07-2 | 报告移至 `_selfproof` 兄弟目录（不进清单绑定域），提交后可原地补入交付提交主体；S6-B 模式跳过 S6-A 旧轮次清单复算的降级口径已显式写明（NB-10）。 | report/evidence/S6-A/s6a_g0_20261022_r08_selfproof/export_selfproof.json |
| F2/F4/F5/F11 | 统一口径并写明语义；keep_reason 归因统一为「样例数不足 32：29」；STATE 按实际更新；令牌统一 v1.7。 | delivery_manifest.json, .codex/STATE.md, coverage_matrix.json |

## 硬规则与边界

- 本记录是修订者自述，不是独立审查结论；是否再复评由项目总控决定。
- 全部 24 项参数值与 PENDING_APPROVAL 状态未改；未在测试集上调整任何参数。
- r01..r07 证据保持原样不改写（RunId 证据不可覆盖）；更正记于本记录与本包。
- 新增硬规则：任何『已关闭/已落盘/已同步』声明必须附 `claim_verification` 附录（命令 + 真实退出码 + 可观察输出）。
- 未触碰硬件；未 push；未改 main/w4/w5/dbdf/w2b 与厂商原件。

## 结论边界

`ALL_PASS` / `CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不代表状态机行为、
G0 复评、独立审查或实物验收通过。任何「已关闭」声明见同包 `claim_verification.json`（命令 + 真实退出码 + 可观察输出）。
