# 阶段3只读 W1 窗口预检 r01

- RunId：`t17_w1_readonly_20261025_r01`
- 时间：2026-10-25 20:08（UTC+8）
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，基线 `584b07664e88a18bf786ba9565a138861e136d76`
- 状态：`BLOCKED_BEFORE_WINDOW_NO_HOST_DEVICE_ENUMERATION`；用户批准了 30 分钟只读 W1，但窗口没有启动，实际占用时长 0 分钟。

## 用户授权范围

Wong 于 2026-10-25 回复“授权只读 W1（推荐）”。授权内容限于：核对部署身份；由 Wong 现场确认真彩；只读采集 VDMA `S2MM_SR`（`0x00015810`）及运行期 `ADDR_S2MM`/`ADDR_MM2S`。单次窗口上限 30 分钟。明确不重启应用、不写寄存器、不烧录、不改线。若主机不枚举设备或只读流不能复现根因，记录阻塞并收窗。

## 开窗前检查与结果

- 四个阶段工作树的 Git `index.lock` 均不存在。
- `hw_server`、`xsdb`、`vivado`、`vitis` 进程均未发现；TCP 3121 无监听。
- Windows 未枚举 COM 端口，也未枚举匹配 FTDI、CP210、Xilinx、Digilent 或 USB Serial/UART 的设备。Wong 报告板卡已接上；此处记录的是主机当前可见状态，不否定物理连接。
- 可用内存查询因 `Get-CimInstance Win32_OperatingSystem` 返回“拒绝访问”而不可用。由于设备未枚举，不启动 Vivado/XSDB 或其他重型会话。
- 因设备枚举前置不满足，未启动 `hw_server`、未连接 JTAG/COM、未读取/写入板上寄存器，未核对当前板上 bit/XSA/ELF，未采样 VDMA 地址/状态，未作目视判定，也未改变板卡状态。

## 收窗与恢复

窗口未启动，无本方进程/会话需要释放，无板上状态需要恢复。W1 仍未完成；重新开窗前须主机能枚举目标 JTAG/串口设备，并重新核实锁、进程、端口和资源。不得将这次阻塞记录解释为 VDMA 根因已定位或排除。
