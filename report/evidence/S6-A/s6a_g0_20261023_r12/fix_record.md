# S6-A 修订记录 v1.8 / r09（终审 A/B 阻断与工具修正）

- 任务：`S6-A`；新 RunId：`s6a_g0_20261023_r12`（r01..r08 均不覆盖）
- 被审基线：`f3c537d` / `1839766`（终审 A 判 CHANGES_REQUIRED：2 阻断 + 8 非阻断）、`e3aeb09`（终审 B：2 阻断 + 12 非阻断）
- 阈值纪律：24 项参数值未改；批准状态已按批准记录更新；未在测试集调参；未触碰硬件
- 状态：**PENDING_REVIEW（增量专项复核）**

## 本轮关闭（r09）

| 项 | 处置 | 证据 |
|---|---|---|
| BLK-r08-1 | 余 3 处清零（limitations not_run[7] / coverage item4 / STATE）+ C16 扩到全部交付文件并改语义判定 + 回归脚本用真实残留行验证必须 FAIL | `m4_residual_regression.json`、`selfcheck_result.json` |
| BLK-r08-2 | `claim_verify` 真实 subprocess 退出码、run_dir 相对路径跳过判定、首版即中止、清单引用 verdict | `claim_verification.json` |
| N-r08-1 | `source_commit` 改可达提交 + 传输克隆可解析性检查 + 本地附注 tag | `transport_clone_check.json` |
| NB-r03-10 | M4 第 9 处（两个表示法）统一 + C16 交叉一致性断言 | 行为表 + `selfcheck_result.json` |

（本记录为修订者自述；旧口径措辞按规则标注：历史语境除外。）
