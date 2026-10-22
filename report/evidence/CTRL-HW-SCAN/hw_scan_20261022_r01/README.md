# CTRL-HW-SCAN hw_scan_20261022_r01 — 板卡连接性极短只读扫描

- 时间（UTC+8）：2026-10-22 13:41–13:44
- 授权：Wong 2026-10-22 明确授权「极短只读扫描，做完立刻退出」
- 执行：DSH 项目总控（主目录 `D:\FPGA_Competition`）
- 方法：自起 `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe -s tcp::3121` → `xsdb scan.tcl` / `scan2.tcl`（仅 `connect` → `targets`/`jtag targets` → `disconnect`）→ 立即 `taskkill` 自起的 `hw_server`
- **未做**：未 program、未烧录、未重配板卡、未写任何寄存器、未开 COM4、未结束他人进程

## 结论：板卡已接、已上电、JTAG 链可见，PS 正在运行

原始输出（`scan2_stdout.txt`，一字未改）：

```
SCAN2_CONNECTED=1
SCAN2_TARGET_COUNT=16
SCAN2_JTAG_CHAIN=1  Digilent JTAG-HS1 210512180081
     2  arm_dap (idcode 4ba00477 irlen 4)
     3  xc7z020 (idcode 23727093 irlen 6 fpga)
SCAN2_DISCONNECTED=1
```

目标清单（`scan2_stdout.txt`）：`APU` / `ARM Cortex-A9 MPCore #0 (Running)`、`#1 (Running)`、`xc7z020`（共 16 个条目）。

- JTAG 电缆：**Digilent JTAG-HS1**，序列号 `210512180081`（与 USB `VID_0403&PID_6014\210512180081` 一致）
- 器件：`xc7z020`，idcode `23727093`
- 两个 A9 核均为 **Running**（未 halt）⇒ PS 上电并在执行（与阶段3「实时灰度、无 HALT」的板上状态一致）
- 另见 UART：`Silicon Labs CP210x` → `COM4`，存在且可用

## 清理状态（已核实）

- 自起的 `hw_server` 已终止（扫描后 `hw_server` 进程数 = 0）
- `3121` 无 LISTENING（仅 TCP `TIME_WAIT` 残留，属正常四次挥手，`OwningProcess=0`）
- JTAG 已释放，本次扫描未改变板上任何状态

## 重要陷阱（各窗口判定"是否接上"必须避开）

第一次扫描 `scan.tcl` 里写的是裸 `targets`，在**输出重定向**下它不打印表格，`scan_stdout.txt` 看起来"没有目标"，极易被误判为"板子没接上"。**正确判定必须用程序化取值**：

```
set tg [targets]
puts "COUNT=[llength $tg]"     ;# >0 即链上有目标
jtag targets                   ;# 打印 JTAG 链（电缆/器件/idcode）
```

或直接用 `report_property [lindex $tg 0]`。**不要**以裸 `targets` 在重定向下的空白输出作为"未连接"的证据。

## 文件

- `scan.tcl`、`scan_stdout.txt`：第一版（裸 `targets`，空白输出的反例）
- `scan2.tcl`、`scan2_stdout.txt`：第二版（显式计数 + `jtag targets`，结论依据）