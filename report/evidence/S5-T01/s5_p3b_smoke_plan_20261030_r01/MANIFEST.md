# S5-T01 P3b 上屏冒烟计划证据清单

- RunId `s5_p3b_smoke_plan_20261030_r01`；状态 **PLAN_ONLY**（未上板；位流未产出；显示 ELF 待重建）
- 生成：2026-10-30T01:46:44+08:00；`hash_basis=commit_blob`，当前 **PENDING_COMMIT**（本会话禁止 git）
- `path` 为仓库相对路径；逐项 sha256 为磁盘字节，提交后须用统一门禁复核

| 文件 | 字节 | sha256 |
|---|---|---|
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/.gitattributes` | 112 | `88e50d81e3ca362827a3ddf429c41dbbd8f3551c70fcf876b9c101e4fcb59fa0` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/ast_check.log` | 18 | `455c95f4ce2193f8463b846baeabf45d9d3e430f13d3742d18f5f6e039c77f88` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/dry_run.log` | 3765 | `bef19aef8225e17a4339bae2453c46571cb4a9fb4bd65a651a15e756e5818b8a` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/make_evidence_manifest.py` | 6343 | `69b4092d63537ae6b6d32dc17f2ad8e4248b9310b3c7d2712380ec7d83465c48` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/P3B_SMOKE_PLAN.md` | 11480 | `13ac6662b2fb441eca78cf8d5160bad7eafb42057ba92495028f511c8b82a5b8` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/run_p3b_smoke.py` | 29452 | `c6cac07bfdfb8acf1cb3cb40690ee86724aeafbd88710c08127da9a0dc40d8c5` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/selftest.log` | 865 | `abe1995c2f00cbcb0f49e1fdb929af3d0a3a676242b1a01407918679cbe40bc3` |
| `report/evidence/S5-T01/s5_p3b_smoke_plan_20261030_r01/verify_manifest.py` | 1652 | `5dddbcb28ba29eb6fd9733b98397bba9bc9947083b9f44f678fb4a87d692b3e8` |

## 外部 tmp 原件（worktree_disk）

| 文件 | 字节 | sha256 | 与证据副本一致 |
|---|---|---|---|
| `D:\tmp\lead\p3b_smoke_20261030_r01\run_p3b_smoke.py` | 29452 | `c6cac07bfdfb8acf1cb3cb40690ee86724aeafbd88710c08127da9a0dc40d8c5` | True |
| `D:\tmp\lead\p3b_smoke_20261030_r01\P3B_SMOKE_PLAN.md` | 11480 | `13ac6662b2fb441eca78cf8d5160bad7eafb42057ba92495028f511c8b82a5b8` | True |
| `D:\tmp\lead\p3b_smoke_20261030_r01\make_evidence_manifest.py` | 6343 | `69b4092d63537ae6b6d32dc17f2ad8e4248b9310b3c7d2712380ec7d83465c48` | True |
| `D:\tmp\lead\p3b_smoke_20261030_r01\verify_manifest.py` | 1652 | `5dddbcb28ba29eb6fd9733b98397bba9bc9947083b9f44f678fb4a87d692b3e8` | True |

## 依赖缺失

- **P3b 位流**：NOT_YET_BUILT —— 真实窗口在 IDENT/X1 停止；dry-run 已报告缺失
- **显示 ELF 的 S5DISP RESULT 打印**：NOT_IMPLEMENTED（当前主循环 for(;;)，只打 frame 行） —— 重建前真实窗口会在 X6 停止（无结果行）

## 边界

离线产物；`ENABLE=0`；未碰板卡/JTAG/COM4/hw_server；未跑 Vivado；未 git；
不主张 G3/G4/G5。PENDING_COMMIT 期间不得声称已通过 `check_manifest_hash_basis.py`。
