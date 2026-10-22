# 更正记录：`s5t01_board_20261022_r01` 中「JTAG 链为空」的结论**作废（WRONG）**

- 更正时间（UTC+8）：2026-10-22 13:47
- 更正人：DSH 阶段5 总控（Lead）
- 被更正的结论：本 run `summary.md` §2 与 `run_manifest.json` 中 `goal_reached=..._JTAG_CHAIN_EMPTY`、`jtag_diagnosis.xsdb_target_tree="EMPTY (0 devices)"`、以及“疑板卡未上电/排线未接”的判读。
- **正确事实**：板卡**一直已连接并已上电**，JTAG 链完整可见；我请求的物理排查是**不必要的**。

## 1. 我自己的原始输出即可证伪

本 run 的 `console/jtag_chain_query2.txt`（13:36 保存，一字未改）第 42–44 行：

```
JTAG_targets=  1  Digilent JTAG-HS1 210512180081
     2  arm_dap (idcode 4ba00477 irlen 4)
     3  xc7z020 (idcode 23727093 irlen 6 fpga)
```

即：**当时链已可见**，我却把它判成“链为空”。

## 2. 误判根因（两条，均为我的方法错误）

1. **判据选错**：我用**裸 `targets`** 的输出作为“是否接上”的证据。裸 `targets` 在**输出重定向**（`> file`）下不打印表格，看起来空 ⇒ 误判“未接上”。正确做法是程序化取值：`set tg [targets]; llength $tg`（>0 即有目标）并配 `jtag targets` 打印链。该陷阱由 Wong 在 `report/evidence/CTRL-HW-SCAN/hw_scan_20261022_r01/README.md` 中以第一版 `scan.tcl`（裸 targets，空白输出）作反例明确指出。
2. **自行过滤证据**：我在查看输出时用 `grep -E "JTAG_servers|JTAG_targets|..."` 只看标记行，把紧随其后的链打印行（`2 arm_dap`、`3 xc7z020`）**过滤掉了**，进一步强化了错误判读。

## 3. 复核（修正后的程序化验据）

- 本树 `report/evidence/S5-T01/s5t01_scan_recheck_20261022_r01/console/scan_recheck.txt`：`jtag targets` 打印 3 项链（JTAG-HS1 / arm_dap idcode `4ba00477` / xc7z020 idcode `23727093`），`SET_XC7Z020_OK=1`。
- 程序化计数版见同 run 的 `console/scan_fixed.txt`（`S5T01_TARGET_COUNT` 与 `S5T01_TREE_COUNT`）。
- 交叉证据（他人、权威）：`D:\FPGA_Competition\report\evidence\CTRL-HW-SCAN\hw_scan_20261022_r01\scan2_stdout.txt`：`SCAN2_TARGET_COUNT=16`、两 A9 核 `(Running)`、`xc7z020`。

## 4. 影响与纠正措施

- **无技术副作用**：本 run 未下载位流/ELF、未写任何寄存器；误判仅导致一次不必要的物理排查请求，已向 Wong 更正。
- **纠正措施**：① 本 run 的 `summary.md` 与 `run_manifest.json` 增加指向本文件的更正字段，原结论保留可追溯但不作判定依据；② 后续所有链探测一律用 `jtag_scan_fixed.tcl`（程序化计数 + 全量打印），**禁止**用裸 `targets` 且**禁止**对链输出做 grep 过滤；③ 该陷阱已写入本树运行书待补充条目。
- **教训（供后续窗口）**：重定向环境下的“空输出”不等于“无目标”；判定连接性必须用可计数/可解析的取值，并保存未过滤的原始输出。