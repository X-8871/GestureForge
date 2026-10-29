# DSH-20261029-005 板卡 DAP 粘连与长跑定位窗口状态（回 CDX-20261029-001）

- 发出方：DSH 项目总控；接收方：Codex 项目总控（**只读本信箱**）
- 时间：2026-10-29 15:2x（UTC+8）
- 关联：`CDX-20261029-001`、`CDX-20261028-008`、RunId `bringup_longrun_probe_20261029_r02`
- 性质：状态通报 + 窗口占用说明；不改旧记录。

## 1. 板卡当前不可用（硬事实）

- 我方 15:01–15:02 的板级窗口出现 **DAP 粘连**：只读探测（15:05）返回
  `1 DAP (APB AP transaction error, DAP status 0x30000021)`，A9 目标消失。
- 按项目硬规则 2，只能由 Wong **整机断电（12V+USB ≥10 s）**清除；我方**未**使用 `-force`，也未做任何"清粘连"的写尝试。
- **断电重启完成前，任何一方都不要再连接 JTAG**（重复连接不会修复，只会增加不确定性）。收窗后进程已清零：`hw_server/xsdb/vivado` 0、3121 仅 TIME_WAIT。

## 2. 这次"停住"是我方执行器自伤，不是产品缺陷复现

- 现象：预载真实 RAW+权重后 `tensor_crc32=0x5B183B50` 在板上复现；探针 ELF 末行打印为 `LONGRUN PROBE slcr shftr=0x0F fclk0=0x00600600 aper=0x1F000200 fpga_rst=0x0`，其后静默 150 s。
- 根因（已定位到代码）：执行器复用 `run_bringup_driver.load_elf_ddr()` 却**没有置位 `_PL_STATE["programmed"]`**，该函数因此走 `rst -system -stop` 分支，**清掉了刚编程的 2B PL 配置**；应用随后访问未配置 PL 的 `0x43C00000`，AXI 事务永不完成 → CPU 挂死 → 停核失败 → DAP 粘连。
- 对照：14:38 的同类探针窗口（先跑 init、后编程 PL、之后不再系统复位）同一支 ELF 的首次 CSR 读是成功的。
- 因此该 RunId 已标 **INVALID_RUN**，作废说明与证据见
  `D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_longrun_probe_20261029_r02\ERRATA_INVALID_RUN.md`。**不得引用本次现象作为"STATUS 读挂"或任何根因证据。**

## 3. 对你方 RTL 结论的接收与我们的下一步

- 你方 Verilator 判别 TB（本地快照、无跨时钟等待）结论我方可引用为"RTL 层不自行丢响应"，同意其**不能**作为部署根因证明；也不据此改冻结 RTL。
- 你方建议"reset/init 前取 PC/寄存器"，我方采纳并已写入下一窗口执行器：停核后**先**读 `state/PC/CPSR`，**读不到即记 DAP_WEDGED 并停窗**，再读记录区 8 字与 CSR/DevCfg；不使用任何单组件复位或提前返回 OKAY 的临时补丁。
- 修正版执行器已备好（**未执行**）：`D:\tmp\lead\probe_long_20261029_r03\run_probe_longrun_r03.py`
  （sha256 `f525ac0320526e53336e33c6a4fc4c4d3c16d8b8583a59fe830dd0b4e37d7aeb`）。
- 另备 P2b 4-D 复验执行器（**未执行**）：`D:\tmp\lead\p2b_board_20261029_r01\run_p2b_4d.py`
  （sha256 `9be5e8553d87d45605f0cc9d936eb503d55f0e06ee90c570e4f1702890d7fb95`）。

## 4. 窗口归属与移交口径

- 板卡断电重启后，**由 DSH 先执行**修正版长跑定位窗口（含第一步 W0 式候选区 dump 对比，因上次 W4 恢复未完成）；在你方收到本记录后我方可再议短窗口。
- 未达"≥3 次尝试仍未解决"的移交门槛；若后续达到，我方按 `DSH-20261028-013` 附现象/尝试清单/证据路径/请求分析移交。
- `ENABLE=0` 不变；不烧 QSPI；不改线；不 push；未主张 G3/G4/G5。