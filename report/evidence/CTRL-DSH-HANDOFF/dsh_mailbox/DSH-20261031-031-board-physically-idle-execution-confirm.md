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