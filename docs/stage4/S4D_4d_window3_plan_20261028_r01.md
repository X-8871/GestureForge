# S4D 4-D bring-up 窗口 #3 计划（2026-10-28 r01，离线编写；待总控签发执行）

- 任务：S4-T34。前置：窗口 #2 已收窗，候选区已回到 M3 登记基线 `41907f53…`（diff=0）。
- 目标：验证"补 `LVL_SHFTR_EN` 使能"后 **M4-b 能否越过 `M4B STEP=1`**。
- 预算：**≤35 min**；超时即收窗留证。
- 驱动：`scripts/stage4_s4b/run_bringup_driver.py` **v3.2**，SHA-256 `260332580164d0c9795a0f54e49312abcea4926e7c7212a7b9c9ace829d9fa79`；
  离线自检 **36/36 PASS，真实 exit 0**（`report/evidence/S4-T34/bringup_driver_v32_20261028_r01/offline_selftest.json`）。
- 依据：`docs/stage4/S4D_ps_pl_level_shifter_enable_20261028_r01.md`（UG585 v1.2 §2.4.8/§2.5/§6/Appendix B.28 原文核对）。

## 顺序（固定）

| # | 步 | 判据 | 预算 |
|---|---|---|---:|
| 0 | P0 门禁 + 身份核对（bit `555a70c2…`、init.elf `237dd959…`、m4b r2 `ada4b30d…`、M3 快照 `41907f53…`、驱动 `26033258…`） | 全一致；无重型进程、3121 无 LISTENING、无 `index.lock`、COM4 可开 | 1 min |
| 1 | `rst -system -stop` → `LVL_SHFTR_EN=0xA` → `program_pl` → `LVL_SHFTR_EN=0xF` | **读回 `mrd -value 0xF8000900` = `0x0F`**（不符即 FAIL，不继续） | 2 min |
| 2 | **CSR 直探** `mrd -value 0x43C00000` | 无 `Cannot access FPGA` / `Memory read error`；失败即停（省时间、留原始错误） | 0.5 min |
| 3 | M4-b（r2 STEP 标记 ELF；preload head13/26→RAW、input/weights→arena；装载期内联重断言 0xF） | 收 `M4B STEP=0..8` / `M4B CSR` / `M4B RESULT` / `M4B HEADS`，60 s；判定 PASS/FAIL/INCONCLUSIVE（判据不变） | 8 min |
| 4 | 若 M4-b PASS → M4-a | 判据不变（R/I/F/W 对拍 + 恢复校验） | 5 min |
| 5 | 收尾恢复：停核 + ps7_init → 按 M3 快照整区写回 → 复读 | **diff = 0**；≠0 立即停并保留现场 | 3 min |
| 6 | 清理：停自起 `hw_server`、关串口、核验 3121 无 LISTENING / 无残留 / 无 `index.lock` | 全清 | 1 min |

## 停止规则（硬）

1. `LVL_SHFTR_EN` 读回 ≠ 0x0F ⇒ **停**，保留原始 xsdb 日志与错误串。
2. CSR 直探仍报 `Cannot access FPGA` ⇒ **停**，报总控（PL/时钟/复位/地址映射的另一层问题）。
3. 使能后 M4-b **仍卡 `M4B STEP=1`** ⇒ **立即停**，保留现场与 UART 原始行，**不连续试错**。
4. 收尾恢复 diff ≠ 0 ⇒ 立即停、保留现场。
5. 全程：不改判据、不升级通过、`ENABLE=0`、不写 QSPI、不改线、不 push、不删失败证据。

## 预期文件

- 新 RunId：`report/evidence/S4-T34/bringup_window3_20261028_r01/`
  （`window_close.txt`、`results_window3.json`、`IDENT.json`、`P0_gate.json`、`PL_lvl_shifter.json`、
  `CSR_probe.log`、`M4b_dma_visibility.json`、`m4b_uart.log`、`FINAL_restore.json`、逐步 `<step>.log`/`.exit_code.txt`）
- 执行器（tmp，不提交）：`tmp/4/S4-T34/run_window3.py`（`python -B tmp/4/S4-T34/run_window3.py <run_id>`）
- 判定口径：`M4B STEP` 行用于**定位**；M4-b 的 PASS/FAIL/INCONCLUSIVE 判据与窗口 #2 完全相同，不放宽。