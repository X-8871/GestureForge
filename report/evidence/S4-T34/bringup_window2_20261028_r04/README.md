# 阶段4 4-D bring-up 窗口 #2 证据说明（S4-T34，2026-10-28）

- 执行方：`stage6-lead4`（DSH 直接指令**临时接管**；原阶段4 执行体在收尾失败，非 OFFERED 交接）
- 硬件占用：**12:23:50–12:40:01（UTC+8）**，约 16 min（预算 ≤60 min）
- 驱动：`scripts/stage4_s4b/run_bringup_driver.py` **v3.1**，SHA-256 `467506d1…`（本窗口未改驱动）
- 结论一句话：**S1 单窗口三段同 SHA（`NEITHER_STAGE`）；R1 与两处收尾恢复 `diff=0`（恢复路径已验证）；
  M4-b FAIL（根因：PS-PL level shifters 未使能）；M4-a / M3 full-region recheck / chain-lite 未执行。**

> 边界：**不主张 G3/G4/G5**；`ENABLE=0` 未碰；未写 QSPI；未改线；未发独立 `stop`；未 push。

## 1. M3 口径更新（重要，按总控 2026-10-28 指令）

窗口 #2 在**同一窗口内**依次得到 D0（恢复后、停核）/ D1（装 PL 后）/ D2（`dow init.elf`+`con` 后）三段
候选区整区 dump，长度均为 **12,615,680 B**，SHA-256 全为 `41907f53…0a0abf`，两两差异字节数 **0/0/0**：

| 段 | 字节 | SHA-256 |
|---|---:|---|
| D0 | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| D1 | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| D2 | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |

**判读（严格按指令措辞）**：

1. **单窗口内 `NEITHER_STAGE`**：本窗口内"装 PL"与"执行 init"这两个动作**都不改变候选区**内容。
   因此此前 `REGION_CHANGED`（6 字节）**不是这两个动作造成的**。
2. **`REGION_CHANGED` 仍未解释**，但**已被排除两个主要嫌疑**（装 PL、执行 init）；剩余可能方向为
   **跨窗口因素**（前窗口未完全恢复的写、复位/掉电保持问题等）。**该项仍未闭合。**
3. **恢复路径已验证**：R1（本窗口开窗即按 M3 快照整区恢复）`diff=0`；收尾 R2 首次写后复读 `diff=28,126`
   即**未通过**，补写后 `diff=0`；诊断与顺序实验的收尾恢复亦各 `diff=0`。
   ⇒ "`mwr -bin -file … 3153920 words` 整区写回"这条路本身有效，**但必须在停核状态下复读校验**。

**⚠ 状态声明：M3 项保持 `FAIL / 未闭合`，本文件不写"M3 PASS"。**
本窗口新增证据**挂在该项之下**作为"缩小嫌疑 + 恢复路径可用"的证据，不改变该项结论。

## 2. 逐步结果与真实退出码

| 步 | 结果 | 退出码 | 说明 |
|---|---|---|---|
| IDENT | PASS | 0 | bit `555a70c2…` / init.elf `237dd959…` / m4b r2 `ada4b30d…` / M3 快照 `41907f53…` / 驱动 `467506d1…` 全一致 |
| P0_gate | PASS | 0 | 无重型进程、3121 无 LISTENING、无 `index.lock`、COM4 可开 |
| P1_hw_server | PASS | 0 | 自起 `hw_server` |
| R0_dump | PASS | 0 | 当前态 SHA `580e9bb6…`，**与 M3 快照 diff = 25,168 B**（上一窗口 M4-b 预置残留，已知偏差，只记录不判定） |
| R1_restore | **PASS** | 0 | 整区恢复后复读 **diff = 0**，SHA `41907f53…` |
| S1_bisect | PASS | 0 | `NEITHER_STAGE`；含驱动自带恢复（diff=0） |
| **M4-b** | **FAIL** | 1 | 见 §3 |
| M4-a | NOT_RUN | — | M4-b FAIL 即停（符合纪律） |
| R2_final_restore | **FAIL** | 1 | `write_exit=0`，但 `dump_exit=1`：`Cannot read memory if not stopped`（核仍在运行）⇒ 该步**不通过**，未据此声称恢复完成 |
| S3_chain_lite | NOT_RUN | — | 前序失败 + 时限 |
| P4_teardown | PASS | 0 | 3121 LISTENING=0、无残留、串口已关 |

收尾恢复的补做与核验在独立 RunId：`bringup_window2_restore_20261028_r01`（`RESTORE_VERIFIED`）：
`RC_verify` 复读 `diff=28,126` → `RC_rewrite` 写回后 **`diff=0`**（SHA `41907f53…`）。

## 3. M4-b 失败证据与根因（本轮关键产出）

UART 原始行（`m4b_uart.log`）：

```
S4D PS APP: PREPROC_SRC=0 ABI=1
S4D MODE=M4B_SELFCHECK geom=letterbox_640x480_to_416x416
M4B STEP=0 enter
M4B STEP=1 read CSR_ID addr=0x43C00000      ← 此后挂住，无 M4B CSR / RESULT / HEADS
```

- preload 四项退出码全 0（head13→RAW、head26→RAW+0x2000、input/weights→arena）；`load_exit=0`；采集 58.6 s。
- **应用本身已运行到 STEP=1**（r2 的 STEP 标记有效），卡在**读 AXI-Lite CSR `0x43C00000`**。

根因两条独立证据（`bringup_window2_diag_20261028_r01`）：

1. 停核后 `mrd 0x43C00000` → `Cannot access FPGA: **Bitstream is not programmed**`
   ⇒ `rst -system -stop` 会清空 PL 配置（而 v3.1 的三个 ELF 装载点都用它）。
2. 重新 `program_hw_devices` 后 → `Cannot access FPGA: **Level shifters are not enabled**`；
   且"先装 PL 再 init"与"先 init 再装 PL"两种顺序（`bringup_window2_order_20261028_r01`）
   **均**报同一错误 ⇒ 缺 `ps7_post_config`/FSBL 流程中的 **SLCR `LVL_SHFTR_EN` 使能**。

依据与修法见 `docs/stage4/S4D_ps_pl_level_shifter_enable_20261028_r01.md`（UG585 v1.2 §2.4.8/§2.5/§6/
Appendix B.28 原文核对；含"加锁写 `0x767B`→`0xF8000004`"的纠错）。

## 4. 目录内容与哈希基座

**哈希基座声明**：本目录所有哈希均为 **`hash_basis = worktree_disk`（仅附注）**；
`commit_blob` 基座应由 DSH 项目总控在提交时按 `git cat-file blob <commit>:<path>` 重算后写入交付清单。

| 文件 | 字节 | SHA-256（worktree_disk） |
|---|---:|---|
| `R0_current.bin` | 12,615,680 | `580e9bb670a8a72c5ad56d1a0e86203cb8d3db84da628e5582feb39921ac5934` |
| `R1_restored_baseline.bin` | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| `s1_D0.bin` | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| `s1_D1.bin` | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| `s1_D2.bin` | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| `s1_post_restore.bin` | 12,615,680 | `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf` |
| `m4b_uart.log` | — | 见文件；含 `M4B STEP=0/1` 与 MODE 行 |

其余：`window_open.txt` / `window_close.txt` / `results_window2.json` / `IDENT.json` / `P0_gate.json` /
`R0_dump.json` / `R1_restore.json` / `S1_bisect.json` / `M4b_dma_visibility.json` / `R2_final_restore.json`，
以及每步 `<step>.log` 与 `<step>.exit_code.txt`。

关联 RunId（均**不覆盖、不改写**）：
`bringup_window2_restore_20261028_r01`（收尾恢复核验）、`bringup_window2_diag_20261028_r01`（两条 mrd 错误原文）、
`bringup_window2_order_20261028_r01`（顺序实验）；
失败尝试 `bringup_window2_20261028_r01`（IDENT 失败，未碰板）、`r02`（NameError，已收尾）、`r03`（import 期失败，无产物）。

## 5. 未做项

S2 DDR 位测试、`P2_load_app` 之外的驱动段、M4-a、M3 全量 `step_m3_recheck`、chain-lite —— 均因
M4-b FAIL 即停或不在本窗口指令顺序内，**如实登记为未执行/不适用，不补写结论**。