# S2B-T06 连接与启动状态诊断

本次已识别 COM4 和唯一 Digilent JTAG-HS1，完成串口采集开关、双核停止及状态/PC/三个寄存器读回。BOOT_MODE 实际值为 `0x00000001`，未满足固定操作包要求的冷 JTAG 条件，因此未下载、初始化或运行任何 ARM 程序。阶段2B G0/G3/G4/G5 均未通过。

运行标识为 `ps_connection_debug_20261009_113002_r01`，源码基线为 `aae7fb6e54f10729fa93429cfc81546cf2a736b5`；授权、全部实际命令及返回分别保存在 `authorization.json`、`connection_execution_record.json` 和 `ps_state_and_cleanup_execution.json`。后续重试使用全新 Run，不覆盖本目录。

## 实际结果

| 范围 | 判定 | 实际证据与边界 |
|---|---|---|
| USB/COM/JTAG 接入 | PASS | COM4 为 Silicon Labs CP210x；FTDI `VID_0403&PID_6014` 序列号 `210512180081`，状态 OK。JTAG 枚举唯一同序号 Digilent JTAG-HS1、APU、同 parent CPU0/CPU1 和 xc7z020，共4个目标；名称不能证明系列或速度级。 |
| 串口采集打开/关闭 | PASS | 115200/8N1、无流控、DTR/RTS false、200ms 读取超时；11:36:48.1997284 开启，11:45:33.2033714 因 stop_flag 关闭，Stopwatch 记录525.0109092秒，未到600秒上限，无清理错误。 |
| 板端 UART 功能 | NOT_RUN | `uart_raw.bin` 实际0字节；没有执行 smoke，也没有 BEGIN/END，不能把串口打开成功当成板端 UART 通过。 |
| 双核停止及读回 | PASS | 两核 Running→`Stopped: (Suspended)`，两次 stop；CPU0/CPU1 PC 原始打印分别为 `pc: 00102030`、`pc: ffffff34`，rrd 返回 None。 |
| 冷 JTAG 前提 | BLOCKED | BOOT_MODE=`0x00000001`，低3位为1，固定包要求0；CPU0 PC 位于已有应用地址范围，结合读回提示不是本包要求的冷 JTAG 环境，不能跳入初始化。 |
| PS 初始化与 DDR smoke | NOT_RUN | 实际下载数0；无 dow/reset/con/mwr/断点，没有初始化 ready、smoke状态2、PATTERN_PASS 或 DDR 零不匹配结果。 |

CPU0 单 word 读取的原始返回为：BOOT_MODE 地址 `0xF800025C` → int `1`（`0x00000001`）；MCTRL 地址 `0xF8007080` → int `813695232`（`0x30800100`，只保留原值，不推断硅版本）；OCM_CFG 地址 `0xF8000910` → int `24`（`0x00000018`，低4位8与离线候选一致，这不证明初始化安全）。完整调用参数、真实 stdout/stderr 与 return_repr 在 `ps_state_result.json`。

`CAPTURE_CLOSED` 自报脚本 exit_code=0；外层关闭观察命令退出0，但父工具的 process.ExitCode 是 null，未将它解释为0。原始空文件 SHA-256 为 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

## 失败记录与恢复

第一次按严格 UTF-8 读取 `jtag_probe_stdout.log` 返回1；日志实际编码为 CP936。随后按严格 CP936 解码生成独立 UTF-8 派生视图 `jtag_probe_stdout_utf8.txt`，原始 log 保留，枚举 JSON 的成功记录也保留。

启动串口后，首次 ReadAllText 就绪观察返回1，因为 stdout 正由采集进程写入而发生共享访问拒绝。没有再次启动采集；按已核实的同一 PID/完整命令改用 FileShare.ReadWrite 读取 CAPTURE_OPEN，恢复命令退出0。这是宿主观察失败和恢复，不是 UART 功能测试失败或成功。

JTAG 与 PS 状态探针均在独立静态审查 PASS、源 SHA 重新核对后执行一次；实际 Vitis wrapper 均退出0，并另以完整结果 JSON 和清理状态判定。静态审查收据是源码范围审查，不能替代冷启动、PCB、UART/DDR 或阶段验收。

## 日志编码、版本和耗时

`jtag_probe_stdout.log` 是 CP936 原始字节；`jtag_probe_stdout_utf8.txt` 是严格转码派生视图。PS 状态 stdout 与串口采集控制文本为 UTF-8。`uart_raw.bin` 只保留串口原字节，不转码，不加入完成标记；ASCII 屏幕观察文本不是原始设备数据。

| 来源 | SHA-256 |
|---|---|
| 本 Run `jtag_targets_probe.py` | `201dc67de8427662fdf1852309c270eda24f2a9bf70cc2670802b152208c3dc6` |
| 本 Run `ps_state_probe.py` | `cd3c8dfd24baa9c6b65563152dcde750e730d001077649a7e39e08c436c0a8bf` |
| 前置 Run `ps_smoke_hw_20261009_101728_r01/capture_uart.ps1` | `3b78f5b54dc7413821400e2c5df3bc1c73a93375b9b71ede9bec42a99e16605d` |

枚举探针记录7条 calls，其中5次 XSDB API、2次宿主归属查询；自身起止6.081866秒，wrapper9.0518974秒。状态探针记录22条 calls，其中20次 XSDB API、2次宿主归属查询；自身起止4.002587秒，wrapper5.5089146秒。两探针共25次已记录 XSDB API，不包含 SDK 内部调用；各执行1次，串口采集1次。服务启动就绪1.7565332秒，关闭命令工具耗时1.1479728秒；峰值内存与全部工具调用总量未测。

固定离线 XSA、两份 ELF、布局和已冻结接口继续引用前置 Run 的实际文件及 SHA，delivery 清单已列出，不复建。它们本次没有下载到板卡。`authorized_STATE_snapshot.md` 是本轮更新后 `.codex/STATE.md` 的原字节副本；它和实际源码、接口、日志、结果的哈希均由 `delivery_manifest.json` 绑定。

## 清理状态与下一次操作入口

11:44:53（UTC+8）本次观测 CPU0/CPU1 均停止，此后总控未 resume/reset；没有持续观测板卡，用户后续断电上电后必须重新核验。探针只断开本次连接并 dispose；随后总控按 PID、创建时间、路径、父链及可执行文件 SHA 核对后结束 native hw_server PID23120 和 launcher PID34568，11:46:48.5414897 的实际关闭记录显示二者退出、3121监听为空。串口采集 PID41268 已正常退出，COM4已释放。以上是本次保存的观察，不代表未来电源或进程状态无需复核。

用户已收到物理动作请求，尚待回传。保持既有固定 PS-only 检查授权；按厂商 V2.2 手册纸面/PDF第14页表4-1核对 J13：JTAG 是图示右侧两个引脚，须以当前实板对应丝印和手册方向为准，不能凭照片旋转方向猜针脚。对应原页为 `report/evidence/S2B-T04/ps_platform_20261008_r01/source_proof/page-0014.png`；提取文本 `v22_document.md` 同目录，原页图与文本 SHA 均在清单。

1. 先断电，再按实际 PCB/丝印核对并调整 J13 至 JTAG；记录 PCB版本、跳帽照片、供电、UART接线/电平及 PS时钟来源，重新上电完成冷启动。
2. 另建全新人工 Run，重新核实设备、唯一JTAG链、BOOT_MODE低3位0、BootROM结束及CPU0/CPU1停止；同时确认没有旧应用、其他调试客户端、PS/外设DMA或活跃PL writer。不得续用本次原始串口文件。
3. 全部固定输入哈希与现场条件吻合后，按 `vitis/s2b_ps_smoke.md` 原操作包先采集串口，再执行 OCM 初始化与 UART/DDR smoke。非0启动模式、未知CPU状态、身份/PCB/接线冲突或寄存器读取异常时停止并保留证据，不能用reset/force/mwr绕过本次阻碍。

本包的 evidence 包装检查只确认目录与哈希绑定；inputs 因 BLOCKED/NOT_RUN 和已保留的失败步骤应退出2。任何 CHECKS_OK 均不代表冷 JTAG、G3/G4/G5 或 UART/DDR 已通过。
