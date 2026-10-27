# DSH-20261027-002 S4-B-REAL-02B 硬件 OFFER 重发（新提交 SHA，取代 001 中的 `3ed23e7`）

- 编号：DSH-20261027-002；时间：2026-10-27 15:34（UTC+8）。
- 发出方：DSH 项目总控；接收方：Codex 项目总控（**供 `Workbuddy 阶段4总控` 认领**，各阶段只读）。
- 回复/取代：`DSH-20261027-001`（其中记载的 OFFER 提交 `3ed23e7` **已被本轮取代**，请勿再按其认领）。
- 依据：Wong 2026-10-27 15:32 给出的完整 11 字段硬件 OFFER 行。

## 1. 权威 OFFER 提交（请以此为准）

| 字段 | 值 |
|---|---|
| **OFFER 提交 SHA** | **`8b57876d922050b10c060378797c425ed6b92c5f`**（main HEAD） |
| 任务 | `S4-B-REAL-02B::s4b_hardware_session_handoff` |
| 发送负责人 | DSH |
| 接收者 | **`Workbuddy 阶段4总控`** |
| 起始提交 | `05eac1bfa708832f7a4582069ab3ec4d0c8677a3` |
| scope | `S4B_PS_TENSOR_DIAGNOSTIC` |
| 状态 | **OFFERED** |
| 心跳(UTC+8) | `2026-10-27 15:32`（**1 小时有效期 ⇒ 请于 2026-10-27 16:32 前 CLAIM**） |
| 证据入口 | `hardware_run_id=s4b_ps_tensor_hw_20261027_r01` |

- main `.codex/STATE.md` 中该任务的硬件行**只有一行**：旧的 15:15 心跳行已在 `8b57876` 中**就地替换**（不是并列两行）。
- 生效方式：Wong 提供完整行 → DSH 按行落盘 → 提交 `8b57876`。

## 2. 认领方式（阶段4 侧，写 w4，不得写 main）

```text
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_claim_line.py \
  --offer-commit 8b57876d922050b10c060378797c425ed6b92c5f \
  --run-id s4b_ps_tensor_hw_20261027_r01
```
按 `CDX-20261023-018 §4` 绑定六键：`offer_commit` / `offer_blob_oid` / `offer_sha256` / `offer_source_commit` / `hardware_run_id` / `scope=S4B_PS_TENSOR_DIAGNOSTIC`，并在 w4 STATE 置 `CLAIMED`。

## 3. 边界（不变）

- 本 OFFER **仅交付硬件会话交接**：**不授权**编译、下载、烧录 QSPI、改线或任何未获 Wong 窗口授权的板级活动。
- 开板前必须先做**窗口第 0 步**：无他方进程/端口占用 → **部署身份逐字符核对**（无补偿 SOF `7cb33068…`、XSA `1f5b138e…`、`an5642_j11cmos2_v10_read.elf` `1457cda4…`）→ **真彩目视重做（需 Wong 在场）** → **运行期回读 `ADDR_S2MM`/`ADDR_MM2S`（禁止复用旧地址与旧目视结论）**。
- 一次只跑一个重型任务；失败日志不删；证据用新 RunId；**不 push**。
- `w4/w5/w6/w2b` 写权不在 DSH 本次范围；main 其余 424 项未提交改动未动。