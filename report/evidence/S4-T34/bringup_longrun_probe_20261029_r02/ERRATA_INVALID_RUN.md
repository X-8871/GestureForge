# ERRATA：本次"停住"是执行顺序缺陷造成的自伤，**不是**产品缺陷复现

- RunId：`bringup_longrun_probe_20261029_r02`
- 记录时间：2026-10-29 15:1x（UTC+8）
- 性质：**本轮结论作废（INVALID_RUN）**；`window_close.txt` 的 `DIAG_NOT_CAPTURED` 与"停住"观察**不得**用作长跑停住定位证据，也不得用于任何验收/判据。

## 1. 事实（按时间）

1. 14:55:58 开窗；IDENT/P0/枚举 PASS。
2. 14:56:51 W0 恢复：候选区与快照差异 **11,850,821 B**（→ 已按快照重写，restore_diff 0）。说明开窗前候选区已被此前的窗口大幅改写，非本次写入。
3. 14:58:21 `PL_program.log`：`PROGRAM_OK`（2B 位流 `555a70c2…` 装载成功）。
4. 14:59:02 `W2_preload` PASS（RAW 230,400 字 → 0x12000000；权重 1,475,775 字 → 0x10100000）。
5. 14:59:08 `W2_load.log` 第一条命令是 **`rst -system -stop`**（其后 dow init.elf → con → 2.5 s → rst -processor -stop → dow 探针 ELF → 四动作 → con）。
6. 应用 UART 打印：`PREPROC_SRC=0`、`STEP=0`、`STEP=1 tensor_crc32=0x5B183B50`（预载正确）、`PROBE slcr ...` 之后**再无任何输出**（静默 150 s → STALL_EARLY）。
7. 15:02 保全阶段：`mrd 0x11B00000 8` → `Memory read error ... AP transaction timeout`；随后 `mrd 0x12000000` → `Cannot read memory if not stopped. Context ... state: APB AP transaction error, DAP status 0xF0000021`。
8. 收窗后只读 JTAG 探测（`dap_probe_after_stall.log`）：`1 DAP (APB AP transaction error, DAP status 0x30000021)`，A9 目标消失 ⇒ **DAP 粘连确认**。

## 2. 根因（本次执行器缺陷）

`run_probe_longrun.py` 复用了 `run_bringup_driver.load_elf_ddr()`，但**没有**在 `base.program_pl()` 之后置位该模块的 `_PL_STATE["programmed"]=True`
（原设计由 `stage_pspl_setup_and_load()` 在内部置位）。于是 `load_elf_ddr` 走了 `rst -system -stop` 分支——
**系统复位清除了刚刚装载的 PL 配置**（与硬规则 3「rst -system -stop 会清 PL 配置」一致），
探针应用随后访问 `0x43C00000`（未配置的 PL AXI-Lite 从设备）→ 事务永不完成 → CPU 挂死 → 停核也失败 → DAP 粘连。

对照组：2026-10-29 14:38 的同类探针窗口（`D:/tmp/lead/probe_long_20261029_r01`）顺序是
`rst -system -stop → dow init → con → rst -processor → 编程 PL → 四动作 → dow app → con`，
同一支探针 ELF 的首次 CSR 读成功（`id=0x53324250`、`status=0x00000400`）。
⇒ 差异只在"编程 PL 之后是否发生系统复位"，判定本次停住为自伤。

## 3. 因此本轮不作废的、可保留的事实

- 预载路径可用：`tensor_crc32=0x5B183B50` 在板上复现（与离线一致）。
- 探针 ELF `f9095655…` 的五步打印在板上可用（`slcr` 行可见）。
- W0 打开时候选区与 M3 快照差异 11,850,821 B；已恢复 diff 0（但见下条）。

## 4. 未闭合 / 必须补做

- **候选区最终状态未复核**：W4 恢复因 DAP 粘连失败（`W4_dump`/`W4_dump2` 均"bin 缺失"）。
  下个窗口第一步必须做 W0 式 dump 对比（diff 应为 0；若不为 0 则按快照重写并留证）。
- **DAP 粘连需要整机断电**（12V+USB ≥10 s）。本轮**未**使用 `-force`、未尝试任何"清除粘连"的写操作。
- `dsg.preserve_evidence()` 的两处缺陷（与本次无关但会污染后续判读）：
  ① `csr_tri_read()` 使用 `loadhw -memrange`（无效选项，正确为 `-mem-ranges`）⇒ 三读从未真正执行；
  ② `parse_first_value()` 会把 xsdb 回显命令行里的**地址**当作寄存器值（本次因此输出
     `0x43C00010/0x43C00064/0x43C0000C`）⇒ 该三读结果**无效**，判读时必须丢弃。
- 候选区记录区 `0x11B00000` 因 DAP 粘连未能读取（NOT_CAPTURED ≠ 未写入）。

## 5. 修正方案（下一窗口执行器）

按 14:38 已验证的顺序自建执行器，不再依赖 `_PL_STATE`：
`rst -system -stop → dow init.elf → con → 2.5 s → rst -processor -stop → 编程 PL → 四动作(0xF 读回) → preload RAW/权重 → dow 探针 ELF → 四动作(0xF 读回) → con`；
并把 `drv._PL_STATE["programmed"]` 显式置位作为双重保险；停住保全前先 `rst -processor -stop` 并确认 `state` 可读，不可读即记 DAP_WEDGED 并停窗。

## 6. 边界

未写 QSPI、未改线、`ENABLE=0`、未 push、未用 `-force`；不主张 G3/G4/G5。