# ERRATA：本目录两次"迭代计时校核"窗口均无效（执行顺序缺陷，重复了 r02 的已知坑）

- 目录：`report/evidence/S4-T34/s4d_iter_timing_20261029_r01/`（r01）与 `.../s4d_iter_timing_20261029_r02/`（r02）
- 时间：2026-10-29 18:10–18:17（UTC+8）
- 性质：**两次窗口都不产生任何计时/功能结论**；且 r01 把板卡再次推入 DAP 粘连。

## 1. r01 无效原因（自伤，与 2026-10-29 15:01 的 r02 完全同类）

`run_iter_timing.py` 在 `program_pl`（编程 2B 位流）之后，装载段仍用
`rst -system -stop; dow init.elf; ...` —— **系统复位清掉刚编程的 PL 配置**。
应用随后第一次读 `0x43C00000` 时事务永不完成，CPU 挂死：
UART 只到 `LONGRUN PROBE slcr ...` 一行，之后 170 s 无输出（`uart_stamped.log` 5 行）。

随后（18:18）对挂死核做 `rst -system -stop` 的恢复尝试使 DAP 进入
`APB AP transaction error, DAP status 0x30000021` ⇒ 板卡需再次整机断电。
**未用 `-force`**；未写 QSPI；未改线。

## 2. r02 无效原因

修脚本的补丁因引号匹配失败**没有生效**（仍含 `rst -system -stop`），且板卡此时已被 r01 留在
"核挂在 AXI 读"的状态，`W2_four_actions` 直接 FAIL（exit 1），未进入装载与采集。

## 3. 结论与教训（已写入执行器修正清单）

1. **编程 PL 之后，任何装载路径都不得出现 `rst -system`**；只用 `rst -processor -stop`。
2. 装载脚本应在执行前做**静态自检**：若 `PROGRAM_OK` 已发生而命令串包含 `rst -system`，直接拒绝执行。
3. 核挂在 AXI 读上时**不要**用 `rst -system`/反复 `mrd` 救场——实测会把 DAP 推入粘连（第二次复现）。
   正确做法：整机断电，或（若板卡仍可枚举 A9）仅在确知 PL 已配置时做最小操作。
4. 任何"管道/补丁"式修改运行参数后，**必须回读文件确认生效**再执行（本次 r02 的失败就是补丁未生效）。

## 4. 影响的判据

- 本目录两次窗口**不**用于任何计时结论；"主机时间 vs 应用自报时间 4 倍差"的证据仍然成立，
  依据是 `bringup_longrun_probe_20261029_r03`（41 轮 / 1950 s 主机）与
  `longrun_probe_step_prints_20261029_r01/uart_output.txt`（带主机时间戳的 32.38 s vs 8096 ms）。
- 未上板结论以外的任何主张均不成立；未主张 G3/G4/G5。

## 5. 板卡现状

DAP 粘连（`0x30000021`）；需 12V+USB 断电 ≥10 s。收窗后主机侧已清零（无 hw_server/xsdb/vivado 进程）。