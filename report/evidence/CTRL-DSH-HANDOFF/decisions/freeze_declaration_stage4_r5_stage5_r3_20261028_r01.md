# 冻结声明：阶段4（r5）与阶段5（r3）（2026-10-28）

- 编号：`freeze_declaration_stage4_r5_stage5_r3_20261028_r01`；时间：2026-10-28 10:50（UTC+8）。
- 依据：Wong 2026-10-28 指令「继续往下走，冻结阶段45」。
- 声明人：DSH 项目总控。

## 1. 阶段5 离线冻结（已完成，独立复审确认）

| 项 | 值 |
|---|---|
| tag | `stage5-offline-freeze-20261027-r3` → `679b8a19b3a42b946d473c85acc9260d6e43f8a1` |
| 冻结集 | `frozen_set.json` = `4461bbbcd22cf993c4e7bc2985c73f578f16f9996b51e262c6350995c5a8cb4c`（tag 提交与 HEAD 同字节） |
| 成员 | 93 成员 / 93 唯一 id；repo 221 登记 = 221 唯一 + host 9 |
| 校验 | 93/93 exit 0，三路（w5 / `git archive` 导出 / attrs-first 钉定检出） |
| 自测 | 4/4（clean=0/改一字节=1/删一件=2/路径逃逸=2） |
| 回归 | 冻结套件 159 通过 / 0 失败 / 2 skip |
| 历史 | r1→`26b7439`、r2→`6f95743` 均未改未删；r05/r06 包 0 字节改动 |

## 2. 阶段4 离线冻结（r5，DSH 独立复核通过）

| 项 | 值 |
|---|---|
| tag | `stage4-offline-freeze-20261028-r5` → `a0ecc710ff95fa427b816c57473ca161945c8642`（tree `5b6fc279cbab24659a143eb8c0f9e5ecccb64d95`） |
| 冻结包 | `report/evidence/S4-FREEZE/stage4_freeze_20261028_r05/` **6 个输入类文件**（`frozen_set.json`/`README.md`/`results_freeze.json`/`frozen_set_report.json`/`landing_manifest.json`/`delivery_manifest.json`） |
| 成员 | 115（规格 17 / 校验器 5 / 实现 8 / 证据 RunId 85）+ 11 项真实产物身份（均按文件重算） |
| 验证包 | post-freeze 提交 `3ddb0af9…`（**不在 tag r5 树内**；`git merge-base --is-ancestor` = NO） |
| 五项退出码 | selftest 5/5=0；仓库 115/115=0；**真 `git archive(tag r5)` 导出 4,359 文件 → `--disk` 115/115=0**；冻结包门禁 0；验证包门禁 0；`check_stage_delivery` 0；`check_manifest_hash_basis --strict` 两包 0 |
| 确定性 | 同输入连跑两次 → 清单逐字节相同 |
| 结构防线 | 生成器 4 条 fail-closed 断言：①路径必须在绑定提交内 ②输入类不得含绑定提交/树哈希 ③`.log`/gitignore 命中即拒 ④包内 `*_verification/` 子目录即拒 |
| 历史 | r1→`4bb27b6`、r2→`a5f5485`、r3→`5bed04f5` 保留；r4 已删 tag 并作废（tag 树内旧验证包描述别的提交） |
| DSH 独立复核 | 我亲自核：tag 身份、tag 树内 `_verification/` 计数=0、冻结包 6 文件、输入无自指哈希、验证提交非 tag 祖先、真导出 4,359 文件 → `FROZEN_SET_VERIFIED (115/115)` exit 0 |

## 3. 迭代过程中被拦下的真缺陷（记录，不掩盖）

| 轮 | 缺陷 | 处置 |
|---|---|---|
| r1 | 产物身份写成 `ea52da1b0000…` 假哈希 | 打回；r2 修正为真值并升级验证器（拒绝占位） |
| r2 | "干净导出 115/115"不可复现（disk 模式仍解析 commit；文件数不符；沿用旧证据） | 打回；r3 修 |
| r3 | 交付清单含 6 个 gitignore `.log`（tag 内不可复现） | 打回；r4 移除并加断言 |
| r4 | tag 树内仍含验证目录，且其退出码描述 `commit=9243d487…` 而非 tag 提交 | 打回；r5 彻底分离（tag 树内 0 条） |
| r5 | 五项全 0 + 结构正确 | 接受 |

## 4. 明确未主张（冻结 ≠ 验收）

- **未主张 G3/G4/G5、未主张阶段4 或阶段5 验收通过**；
- 阶段4：`M3=FAIL/未闭合（REGION_CHANGED 6 字节，根因未定）`、`M4-a/M4-b/M4-b 长跑=NOT_RUN`、`PL 预处理 v2=未完成`、`4-D 位流=未产出`、`PS 应用接线未完成`、`候选区 owner=BLOCKED`、`ENABLE=1 未解锁`；
- 阶段5：板级 `B1–B10` 全部未做；真彩目视/HUD 屏上需 Wong 在场；真实回放接入/真实 30 分钟/T5-10 未做。
- 冻结只表示：**上述交付物身份可复现、可校验、旧冻结未被破坏**。

## 5. 入口

- 阶段5 验证：`w5` 内 `verification/verify_stage5_frozen_set.py`（93/93）；
- 阶段4 验证：`w4` 内 `scripts/stage4_s4ctrl/verify_stage4_freeze_package.py`（115/115）；
- 两份冻结的复审报告：`report/evidence/CTRL-DSH-HANDOFF/reviews/`（S5 系列）+ `reviews/S4_FREEZE_r*`（按需归档）。