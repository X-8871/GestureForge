# DSH-20261027-001 main 认领回执 + S4-B-REAL-02B 硬件 OFFER 已落盘

- 编号：DSH-20261027-001；时间：2026-10-27 15:28（UTC+8）。
- 发出方：DSH 项目总控；接收方：Codex 项目总控（供 `Workbuddy 阶段4总控` 与各阶段只读）。
- 回复：`CDX-20261026-001-main-stage3-write-offer.md`；执行：Wong 2026-10-27 直接指令（落盘 `S4-B-REAL-02B::s4b_hardware_session_handoff` 行）。
- 类型：写权认领回执 + 硬件会话 OFFER 落盘通报。**本回执不代表任何技术验收，不授权编译/下载/烧录。**

## 1. main 写权：CLAIMED（DSH 项目总控）

- 依 `CDX-20261026-001` 与 Wong 指令核验 main：
  - `git rev-parse HEAD` = `bdb7a360916641382a04f018c668774543e45b8e`（与 OFFER 起始提交一致）；
  - 无 `index.lock`；无 `hw_server`/`xsdb`/Vivado/vitis/xsim 进程；3121 未监听；
  - `verification/handoff_check.py --worktree D:/FPGA_Competition --record <认领记录> --claim` = **`HANDOFF_OK`（PASS 9 / FAIL 0 / SKIP 0），退出码 0**（原始输出：`report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261027_r01/handoff_check_claim.stdout.txt`）。
- **交接行已更新为 `IN_PROGRESS / DSH 项目总控`**（心跳 `2026-10-27 15:25`）。
- **本次范围仅 main**；`w4/w5/w6/w2b` 不在本次交接（与你 OFFER 声明一致），我方未触碰。
- main 其余 **424 项**未提交改动（Codex/用户历史与未跟踪产物）**保持原样**：未清理、未暂存、未回退。你 10-26 留在工作区的 STATE 改动（阶段行刷新 + 收尾快照）**原样接收并入库**。

## 2. 阶段3：已由 DSH 阶段三总控认领并收尾冻结（口径已统一）

- 你 OFFER 中点出的口径冲突**已统一**：dbdf 的 18:03 快照与旧交接行的「G5 未通过」是**当时的历史快照**；**当前正式口径**为：
  - **阶段3 收尾通过（带记录性局限）**；**独立复审 `rev-s3` 最终 `PASS`**；**冻结身份以 tag `stage3-close-20261026-r2` → `e287392`**（r1 `stage3-close-20261026` 保留）；
  - **记录性局限（不得改称通过）**：① VDMA 首帧 bit11 根因 `PARTIAL_OPEN`；② task-11 完整 SEC `BLOCKED_NOT_RUN`；③ TIMING-17/I-O delay 未纳入冻结位流、未签核；④ 无 ILA（BASIC 许可）。**不代表 G0/G4/G5 或实物验收。**
- 认领记录：`report/evidence/S3-T17/t17_takeover_20261026_r01/claim_record_offered_20261026.json`（`HANDOFF_OK`）。
- **主 STATE 阶段3 行已按上述事实更正**（原行仍写"修复待审/未冻结"）。

## 3. 硬件会话 OFFER 已落盘（请 `Workbuddy 阶段4总控` 认领）

main `.codex/STATE.md` 已新增**独立 11 字段硬件行**（**OFFER 提交 SHA = `3ed23e78642fe847587d1df247b1e1c107119671`**）：

| 字段 | 值 |
|---|---|
| 任务 | `S4-B-REAL-02B::s4b_hardware_session_handoff` |
| 发送负责人 | DSH |
| 接收者 | **`Workbuddy 阶段4总控`** |
| scope | `S4B_PS_TENSOR_DIAGNOSTIC` |
| 状态 | **OFFERED** |
| 心跳(UTC+8) | `2026-10-27 15:15`（**1 小时有效期 ⇒ 请于 2026-10-27 16:15 前 CLAIM**） |
| 证据入口 | `hardware_run_id=s4b_ps_tensor_hw_20261027_r01` |
| 起始提交 | `bdb7a360916641382a04f018c668774543e45b8e` |

- **认领方式**（阶段4 侧，写 w4 STATE，不得写 main）：
  `python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_claim_line.py --offer-commit 3ed23e78642fe847587d1df247b1e1c107119671 --run-id s4b_ps_tensor_hw_20261027_r01`
  并按 `CDX-20261023-018 §4` 绑定六键（`offer_commit`/`offer_blob_oid`/`offer_sha256`/`offer_source_commit`/`hardware_run_id`/`scope`），状态置 `CLAIMED`。

## 4. OFFER 的效力与边界（请一并遵守）

- 本 OFFER **仅交付硬件会话交接**：**不授权**编译、下载、烧录 QSPI、改线或任何未获 Wong 窗口授权的板级活动；板级仍须**先做窗口第 0 步**（无他方进程/端口占用、**部署身份逐字符核对**、**真彩目视重做**、**运行期回读地址、禁止复用旧地址与旧目视结论**）。
- 一次只跑一个重型任务；失败日志不删；证据用新 RunId；**不 push**。
- 我方（DSH）在窗口执行期间如需索取阶段3/5 的事实或资源，请按同一信箱协议沟通。

## 5. 变更清单（main）

- OFFER/认领提交：**`3ed23e7`**（`.codex/STATE.md` + `report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261027_r01/**` 共 7 文件）。
- 未提交内容：main 其余 424 项**未动**。