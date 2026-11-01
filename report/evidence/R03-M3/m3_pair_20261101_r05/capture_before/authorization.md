Wong当前授权：现在起至2026-11-01T01:00:00+08:00独占板卡；已明确确认12V+USB断电至少10秒再上电。

# DSH-20261031-030 — R-09 闭环回执 + 板卡 OFFER（Codex，1 小时）

- 时间：2026-10-31 23:5x（UTC+8）→ 建议窗口 00:00–01:00（UTC+8，60 分钟）
- 发出方：DSH 项目总控
- 接收方：Codex 项目总控

## 1. R-09 闭环（已完成，无需你回执）

- 你侧残留交付已由我方**串行提交**至 w6：
  - `97e07a4`（27 文件）：`c2_integration/`、`c3_collect/`、`c4_r02/C4_r05_incremental_20261031.md`、`c4_r02/C4_rev4_incremental_20261031.md`、`m3_w02/`、`r03/review_new/` 8 篇
  - `f0fab84`（3 文件）：`report/evidence/CTRL-LEGACY/{c3_collector,closeout,final_followup}_20261031_r01/submission_inventory.json`
- 主目录归档：`report/evidence/CTRL-DSH-HANDOFF/r09_c3c4_20261031/`
  - `manifest.json`（30 项，`hash_basis: commit_blob`，绑定上述两个提交）
  - `R09_CLOSEOUT.md`、`verify_r09_manifest.py`（实测 **checked=30 mismatch=0**）
- 主目录提交：`b10a9e2`；遗留清单补 §2.8：**R-09 关闭**。
- 与 Codex 相关开放项只剩：**R-02②④（待 Wong 裁决）**、**R-03（BLOCKED，恢复需新 OFFER + 新 RunId）**、**R-05（待板上验收）**。

## 2. 板卡 OFFER（60 分钟，接受即 CLAIM）

| 字段 | 内容 |
|---|---|
| 任务 | Codex 板窗（R-03 M3 恢复 或 R-05 C2 板上验收，二选一或都做，按你优先级） |
| 负责人 | Codex 项目总控（CLAIM 后独占） |
| 工作树/分支 | `D:\codex-worktrees\w6` / `stage6-interact-prep`（只读归档 + `legacy_codex_20261031/` 独立写入；提交仍由 DSH 串行） |
| 起始提交 | w6 `97e07a4`（清单提交后为 `f0fab84`） |
| 允许修改范围 | `w6` 内 `legacy_codex_20261031/` 与 `report/evidence/<你的 task_id>/<run_id>/`；**不得**改主目录、其他工作树、我方信箱 |
| 未提交改动归属 | Codex（窗口结束前请落盘并给我清单，我串行提交） |
| 让出声明 | DSH 本轮板窗已全部收窗，**主动让出** |
| 心跳(UTC+8) | 窗口内每 15 分钟更新一次（信箱落一行即可） |
| 证据入口 | `w6/report/evidence/<task_id>/<run_id>/`（新 RunId，不得复用） |
| 恢复命令 | 见下 §3 |
| 状态/下一接手方 | **OFFERED → IDLE（待你 CLAIM）**；窗口结束回 DSH |

## 3. 前置与规则（必须遵守）

1. **当前 `board_state` = abnormal=true**（`s3_camera_repro_20261031_r02`，阶段3 对照实验残留）⇒ **使用前必须物理 POR**：请 Wong 断电重启一次，然后跑
   `python D:\tmp\lead\p3b_smoke_20261030_r01\run_e1_enum_readonly.py --run-id s6e_e1_recover_20261031_r38 --por`
   清标记后方可开正式窗。
2. 板卡纪律照旧：**禁止 `rst -system`**；单次 `ps7_init`；XSDB 用 `.bat` 入口；异常拆除后必须 POR；**窗口结束零残留**（无 hw_server/xsdb、3121/3122 空闲、核已停、`board_state` clean）。
3. 若你的任务需要**重新综合/实现位流**，请先告知——我方 `video-bd` 正在构建 build11g（CPU 占用中），本机 16 GB **同一时刻只允许一个重型 Vivado**。
4. 窗口 60 分钟；超时请回信说明并归还板卡，不自动延长。

## 4. 回执要求（窗口结束时）

请回一封 `CDX-...` 到 `codex_mailbox/`，含：RunId、命令、证据路径、`board_state` 最终值、是否 POR、残留检查结果、未提交文件清单（供我串行提交）。

— DSH 项目总控


# DSH-20261031-031 — 板卡执行确认：已物理空闲、可 CLAIM（POR 前置未满足）

- 时间：2026-10-31T23:51:00+08:00（UTC+8）
- 发出方：DSH 项目总控（board-runner 执行）
- 接收方：Codex 项目总控
- 关联：DSH-20261031-030（板卡 OFFER 1h）
- 状态补充：**OFFERED → 可 CLAIM**（DSH 侧已停止一切板窗操作）

## 1. 零残留核验（只读，23:50:3x UTC+8）

| 检查项 | 结果 |
|---|---|
| `hw_server` 进程 | **0 个** |
| `xsdb` 进程 | **0 个** |
| TCP 3121（listen/any） | **0 / 0** |
| TCP 3122（listen/any） | **0 / 0** |
| 板卡相关脚本进程（`run_ecam_diag` / `run_e1_enum_readonly` / `run_sccb_pin_test` / `hwimpl` / `xsdb`） | **0 个** |
| `vivado` / `vivado_lab` 进程 | **0 个**（build11g 当前未在跑；若后续重跑属 CPU 侧，与板卡无关） |
| 双核状态 | 无 `hw_server` 连接 ⇒ 无活动 JTAG 会话；最后收窗（`ecam_diag_20261031_r51`，23:38:39）为 clean teardown，核已停 |
| 残留进程列表 | `[]`（空） |

结论：**板卡物理空闲，JTAG/UART 均无占用，可移交 CLAIM。**

## 2. 必读前置：`board_state` = abnormal（未物理 POR）

```json
{
  "abnormal": true,
  "run_id": "DSH-20261031-031_board_handoff_to_codex",
  "reason": "阶段3 对照实验(s3_camera_repro_20261031_r02)残留 + 记录过 process_exit_without_clean_teardown(ecam_diag_20261031_r43)；板卡物理空闲但 PS/PL 配置残留，需 Wong 物理断电后 E1 --por 清除方可开正式窗",
  "por_confirmed_by": "s6e_e1_recover_20261031_r18",
  "last_clean_run": "ecam_diag_20261031_r51",
  "last_clean_ts": "2026-10-31T23:38:39+08:00"
}
```

- `por_precondition()` = **`not_satisfied`**；`preflight_ok()` = **False**
- ⇒ **Codex 若需开正式板窗，必须先请 Wong 物理断电重启一次**，再执行：
  ```
  python D:\tmp\lead\p3b_smoke_20261030_r01\run_e1_enum_readonly.py --run-id s6e_e1_recover_20261031_r38 --por
  ```
  清除 abnormal 后方可开窗。
- 只读枚举（不做 PS/PL 重配置）可在 POR 前进行，但**不得写 CR/不得改 PS7 配置**。

## 3. 板卡纪律（沿用 DSH-20261031-030 §3）

1. 禁止 `rst -system`；`rst -processor` 仅限明确批准且每窗最多一次。
2. 单次 `ps7_init`；XSDB 走 `.bat` 入口；DAP/halt 异常立即停手并报 POR。
3. 窗口结束零残留：无 `hw_server`/`xsdb`、3121/3122 空闲、核已停；`board_state` 按实际状态落盘。
4. 若需重新综合/实现：本机 16 GB 同一时刻只允许一个重型 Vivado，先与 DSH 侧沟通（当前 build11g 待重跑）。
5. 窗口 60 分钟，超时请回信并归还板卡，不自动延长。

## 4. DSH 侧状态

- **已停止一切板窗操作**：原定 `ecam_diag_20261031_r52`（build11g + v29d）顺延到 Codex 归还之后执行，窗口内不会开任何板窗。
- 我方 CPU 侧（Vivado build11g 重跑）与板卡不冲突；若 Codex 需要整机资源请提前告知。
- 归还后恢复顺序：① 核 `board_state` 与零残留 ② 跑 `ecam_diag_20261031_r52`（build11g 到位时）③ 否则只做只读核验并回报。

## 5. 回执要求

窗口结束时请在 `codex_mailbox/` 回一封 `CDX-...`，含：RunId、命令、证据路径、`board_state` 最终值、是否物理 POR、残留检查结果、未提交文件清单。

— DSH 项目总控（board-runner 代执行）


Wong在r04软件映射拒绝、正常收尾后，已明确回复“已再次断电重启”。E1 s6e_e1_recover_20261101_r01实际PASS并清标记；本新POR仅在r05执行一次init。
