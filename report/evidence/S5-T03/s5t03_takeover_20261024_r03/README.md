# S5-T03 NB 轮（r03）安静窗口与接管核对记录（w5，2026-10-24 02:3x UTC+8）

- 任务：`task-24`（复审 `PASS` 后收掉 NB-1..NB-5；**不动已通过内容之外不必要的部分**）。**全离线**。
- 工作树/分支/HEAD：`D:\codex-worktrees\w5` / `stage5-display-prep` / 本记录时刻 `5fd3336`；被审基线 `b6d11d4`（内容）+ `a60d73b`（证据/STATE）。
- **全局事实**：板卡已由 Wong 于 2026-10-24 **拔下**（`decisions/board_detached_boardfree_plan_20261024_r01.md`）⇒ 一切板级工作**暂停**；本记录与整个 NB 轮**未进行任何板级操作**。
- 检查方式：只读；**未使用 `--claim`**（同阶段接续，无需跨方接管）。按 `task-24` 纪律，核验在**安静窗口**内完成。

## 1. 安静窗口与接管核对

| 检查 | 结果 | 证据 |
|---|---|---|
| 硬件/仿真进程 | `PROC_IDLE`（0 个 vivado/xsdb/hw_server/vitis/xsim） | `console/checks.txt` C1_proc exit 0、`console/quiet_window.txt`（骨架包） |
| 3121 端口 | `PORT_3121_IDLE`（未监听） | `console/checks.txt` C1_port exit 0 |
| 已跟踪修改 | `TRACKED_CLEAN` | `console/checks.txt` C2 exit 0 |
| 工作树/分支/HEAD | `stage5-display-prep` @ `5fd3336`；`index.lock` ABSENT | `console/git_state.txt`、`console/handoff_check.json` 检查项 a/b |
| 阶段3 部署身份（只读重算） | 三产物 `ALL_MATCH`（bit/ELF 全哈希 + XSA 全哈希） | `console/deploy_verify.txt`、C3 exit 0 |
| 板卡拔下记录存在 | `BOARD_DETACHED_RECORD_PRESENT` | C4 exit 0 |
| `handoff_check`（只读，未提供 record） | `HANDOFF_FAILED` PASS3/FAIL1/SKIP5，**exit 1** | `console/handoff_check.json` |

**FAIL 只来自检查项 c**：本记录写盘时 `report/evidence/S5-T03/` 为未跟踪且无 record 声明归属
（复审已观察到同类现象，并建议在安静窗口或无未跟踪改动时核验）；a/b/d 三项 PASS。提交后同一命令复跑为
`HANDOFF_OK PASS4/FAIL0/SKIP5 exit 0`（见 w5 STATE 与本轮汇报）。

## 2. NB 逐项处置（详见绑定文档 §9b）

| 编号 | 处置 |
|---|---|
| **NB-1** | 等价 `frame_id` 改 **fail-closed**：同 session、`frame_id` 已接受、未显式声明重复/重放 ⇒ 判 `duplicate_frame_id`（verdict=FAIL，拒绝：不写已接受集合、不更新 latest、不绘制），新增计数 `duplicate_frame_id_results`；放行只看 `repeat_declared=true` / `repeat_index` 递增；含 3 条定向用例（未声明必拒、声明放行、**判别力对照**）与 `equiv` 流 40 帧；**未削弱 B-2**（回退仍先判 out_of_order）。 |
| **NB-2** | 漂移登记改为**扫描判据**：登记规则 + 旧/新哈希 + 19 个清单文件（10 个包目录）逐条；新增 `scripts/stage5_t03/scan_hash_drift.py`（命中集合 == 登记集合，双向）；扫描实跑 **COVERED / exit 0**（`console/impact_scan.txt`）。**未改写任何旧包**。 |
| **NB-3** | 计数单位改为**逐字相等**：JSON 15 键（14 计数 + `definition`）↔ 流水线 14 键，测试断言逐字一致；清单 limitations 由 JSON **生成完整 14 条**。 |
| **NB-4** | 三处 `revised/generated_utc8` 改为**本文件最后写入的分钟值**（`2026-10-24T02:34:00+08:00`，容差 ≤60 s；实测 mtime 02:34:00/02:34:17/02:34:30 见骨架包 `console/file_mtimes.txt`），并写明重建工作区后 mtime 会变、字节权威为 Git blob。 |
| **NB-5** | T01 补断言（回放 `capture_time_ns` 非零要求、`carry_fields` 10 字段、`implementation_status`、NB-1 规则登记）；文档/STATE 明写**实现层 camera/回放路径未实现**（`replay_source`/`frame_integrity` 未接线）。 |

## 3. 原始输出

- `console/git_state.txt`、`console/handoff_check.json`(+`stderr.txt`)
- `console/checks.txt`（C1 空闲/端口、C2 已跟踪干净、C3 部署身份、C4 板卡拔下记录，均带真实 `*_exit=`）
- `console/deploy_verify.txt`（三产物 `sha256sum` 原始输出）
- `run_meta.json`、`delivery_manifest.json`、`hashes_sha256.txt`

`CHECKS_OK`（如清单检查通过）仅代表包装/绑定检查通过，不代表独立审查、G0/G4/G5 或实物验收。