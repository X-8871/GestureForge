# S6-A 修订记录 v1.2 / r03（复评 BLK-1..3 + NBL-1..5）

- 任务：`S6-A`；被审基线：`3b59674`（r02）；新 RunId：`s6a_g0_20261022_r03`（r01/r02 均不覆盖）
- 复评来源：`report/evidence/CTRL-DSH-HANDOFF/reviews/S6A_r02_20261022_r01/S6A_20261022_r02_review.md`
- 阈值纪律：**24 项参数值与 `PENDING_APPROVAL` 状态未改**；未在测试集调参；未触碰硬件
- 状态：**PENDING_REVIEW**；复评由项目总控另派，本记录不构成“已审查/已通过”

## 阻断项

| 项 | 处置 | 证据 |
|---|---|---|
| BLK-1 谓词未落到迁移/行为行 | M3 改 `WINDOW_MATCH` 计数；M10/B10 绑 `TARGET_CONTINUES`；M1/M4/M5/M8/M9/M15 与 B04/B08/B12/B13/B14 显式绑定并写 `predicates_used`；`used_by` 补 M3/M10；C12 增加迁移/行为行断言与裸“匹配”扫描 | JSON + 文档 §4/§5/§12；r02 失败证据 `selfcheck_r02_blk1_failure.json`（C12 FAIL） |
| BLK-2 旧包哈希绑定错误 | 改用 `git cat-file blob <commit>:<path>` 二进制输出直接落盘、按 git 字节算 SHA-256；用同一字节重跑 r01 失败证据。原因：r02 用 PowerShell 文本管道提取改写了行尾/编码 | `old_package_under_test.json`、`selfcheck_old_package_failure.json/.txt`（exit 1，13 项） |
| BLK-3 C11 未入库/声明文件缺失 | 入库 `selfcheck_result.json` 改由 `--manifest` + `--state` 完整命令生成；落盘 `selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`；不动点迭代保证清单/哈希一致 | `selfcheck_result.json` 的 C11 detail、三份 stdout |

## 非阻断项

NBL-1 inputs 清单 checks 两阶段实测回写；NBL-2 统一 `t_last_submit` 并删除“尝试提交”歧义；NBL-3 边界样例引入 `t_now`/几何输入真算（HC-07/08/10/11/17/24/25）并新增 HC-28/HC-29 验证 BLK-1；NBL-4 §15 六列表头；NBL-5 按实际改动重述 B-05，不再使用“全表引用”。

## 结论边界

- `ALL_PASS` / `CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不验证状态机行为，不代表 G0 复评、独立审查或实物验收通过。
- 回放/注入类结论仅限回放/注入输入；本包未运行任何状态机。
