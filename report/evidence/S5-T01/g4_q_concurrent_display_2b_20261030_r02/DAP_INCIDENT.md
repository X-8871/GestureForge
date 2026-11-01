# DAP 卡死事件记录（P3q 并发对照窗口 r02）

- 时间：2026-10-30 19:10:01–19:10:04（UTC+8）
- RunId：`g4_q_concurrent_display_2b_20261030_r02`
- 阶段：S8_dual_dow（双核 `dow`：core0=M4-b ELF，core1=显示长跑 ELF）

## 现象

`rst -processor -stop`（core #0）返回：

```
Cannot reset ARM Cortex-A9 MPCore #0. APB AP transaction error, DAP status 0xF0000021
```

随后独立恢复测试（`dap_recovery_test.py`）枚举结果：

```
1  DAP (APB AP transaction error, DAP status 0x30000021)
2  xc7z020
```

即 **A9 两核 target 已消失、DAP 处于 APB AP transaction error / DAP status 0x30000021** —— 与项目既有记录中的"DAP 卡死"同型。

## 已执行的安全动作

- 立即停手：不再重试 `rst`、不改用其它复位方式、不执行 `rst -system`；
- 只做只读枚举确认（上述），未再写任何寄存器/内存；
- 已停 hw_server：`stopped_pid`（最后确认 3121 无 LISTENING）。

## 之前已完成的步骤（本窗口）

- IDENT PASS（P3q bit `4d6ea2ef…`、XSA `dfefc883…`、M4-b ELF `553fbf7e…`、显示长跑 `6aab2473…`）
- loadhw / 停两核 PASS → SLCR 0xA PASS → `xsdb fpga -file` P3q PASS → SLCR 0xF PASS
- init.elf 跑 ps7_init PASS（`INIT_DONE`）
- M4-b 预置（head13/head26/input/weights）与投毒 PASS
- UART 打开 PASS
- 双核 `dow` 阶段触发上述 DAP 错误

## 结论与建议

- **需要一次整板断电重启**（拔电/断电等待 5 s 再上电）才能恢复 A9 DAP；这是既有结论：`0x30000021` 只有全断电可恢复；
- 恢复后建议重跑并发窗口（RunId r03），并**避免在 PL 重配后对 core#0 再做一次 `rst -processor`**：
  改为在 init 之后直接 `dow`（核已处于 stop 状态），减少 DAP 复位次数；
- 本事件与设计/位流无关，属调试链路状态问题；不影响已完成的三窗计算回归与三窗显示 G3 结果。

## 另一条（同一窗口 r01 的脚本缺陷，非硬件问题）

r01 崩溃原因：脚本未在 `con` 前打开 UART（`drv._SER["ser"]` 为 None），采集时 `AttributeError` 退出；已修（新增 `S7b_uart_open` 步骤与采集前兜底）。r01 已保留为作废记录。