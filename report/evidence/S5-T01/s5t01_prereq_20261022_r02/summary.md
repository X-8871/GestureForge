# S5-T01 硬性前置核验 RunId `s5t01_prereq_20261022_r02`

- 时间（UTC+8）：2026-10-22 13:10
- 任务：S5-T01 阶段5 上板 bring-up（HDMI 出图 + 叠框）
- 结论：**`BLOCKED_NOT_RELEASED`（门禁退出码 1）** —— 硬性前置未满足，**未连接板卡、未启动 `hw_server`、未写任何寄存器**
- 唯一阻断原因：`codex_mailbox` **未发现新的书面让出/释放通知**（最近占用通知 `CDX-20261022-006-2b-final-acceptance-resume.md`，10:29，明确写明“不将本通知当作完成或硬件释放”）

## 1. 门禁事实（机器可读：`hardware_gate.json`）

| 检查 | 结果 |
|---|---|
| 信箱让出通知 | **未发现**（最近占用通知 `CDX-20261022-006`）；DSH 项目总控已于 `DSH-20261022-009`（13:05）向 2B 请求书面让出 |
| 提供 `--release-id` | 未提供（无可匹配的让出编号） |
| 进程枚举 | **成功**（`hardware_process_enumeration_ok=true`，`cmd.exe /c tasklist` 路径，原始输出见 `console/process_enumeration.txt`） |
| 硬件/重型进程 | **0 个**（无 `hw_server`/`vivado`/`xsdb`/`vitis`/`xsim`）—— 但**不作为让出依据**（任务卡与 `DSH-20261022-009` 均明确） |
| 六棵树 `index.lock` | 均无（`console/worktrees.json`） |
| 主 STATE 出现让出/空档字样 | 见 `hardware_gate.json` 字段 `main_state_release_wording_present`（仅作参考，不放行） |
| **决策** | **BLOCKED**（fail-closed） |

## 2. 本轮发现并修复的自身缺陷（如实登记）

- **缺陷**：门禁首版（RunId `s5t01_prereq_20261022_r01`）用 `tasklist /FO CSV /NH` 枚举进程；在 Git Bash(MSYS) 下 `/FO` 会被改写成路径导致命令失败，而代码把“枚举失败”当作“无进程”返回 `[]` —— 违反 fail-closed，可能误判放行。
- **修复**：改为 `cmd.exe /c tasklist` 优先 + 直接调用 + PowerShell 兜底，并新增 `hardware_process_enumeration_ok`：**枚举失败即判 BLOCKED**；原始枚举输出落盘留证。
- **影响**：r01 的 `decision=BLOCKED` 结论不变（当时阻断原因同为“缺书面让出”），但其进程检查不可信；**r01 已标为被 r02 取代**（保留不删）：`s5t01_prereq_20261022_r01/SUPERSEDED_BY_r02.md`。

## 3. 本轮交付的离线准备件（硬件一到即可一次执行）

| 交付 | 路径 | 离线验证 |
|---|---|---|
| 上板运行书（前置/输入/叠框路径/注入格式/测量定义/验收表/证据布局/停止条件/收尾） | `docs/stage5/S5T01_stage5_board_bringup_runbook.md` | 文档，自检一致 |
| 硬性前置门禁（fail-closed，只读） | `scripts/stage5_t01/check_hardware_gate.py` | 本轮实际运行：**exit 1 / BLOCKED** |
| 注入计划离线校验器 | `scripts/stage5_t01/validate_injection_plan.py` | **exit 0**，8 记录 / 25 框 / 0 失败（`console/injection_plan_validation.txt`） |
| 注入计划示例（覆盖边缘/多框15/零框/零面积/过期/奇数补边） | `docs/stage5/s5t01_injection_plan_example.json` | 同上（`injection_plan_preview.json`） |

## 4. 未执行项（NOT_RUN，明确标注）

- 一切上板动作：位流下载、`0x503D` 写 `0x80`（v12 彩条）与**写回 `0x00`**、送显叠框、截图/照片、FPS 与延迟实测、T5-08/T5-09/T5-11 真实统计、G3。
- 未占用/未启动/未结束任何硬件服务；未烧录 QSPI；未改 `w4`/`dbdf`/`w2b`/主树；未写两个 mailbox 目录。

## 5. 下一步（硬件释放后）

1. 收到 `codex_mailbox` 新编号的书面让出 + DSH 宣布空档后，运行门禁并附 `--release-id <让出编号>`，要求 **exit 0**。
2. 按运行书 §3 先**只读**核对送显缓冲布局/所有权与板上位流指纹（不复用旧状态），再选 `overlay_path`（默认 P1 PS 软件叠框，冻结位流零改动）。
3. 每个 run 新 RunId、独立录屏/照片与数值表；收尾把 `0x503D` 写回 `0x00`、退出 `hw_server`、记录实际释放时间。