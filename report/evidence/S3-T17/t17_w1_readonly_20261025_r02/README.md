# 阶段3只读 W1 授权后复查 r02

- RunId：`t17_w1_readonly_20261025_r02`
- 时间：2026-10-25 20:11（UTC+8）
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，基线 `78f2bde6aabed1159b8c47b006a59313bb233cac`
- 授权：复用 Wong 于 2026-10-25 批准的 30 分钟只读 W1 范围，原授权记录见 `../t17_w1_readonly_20261025_r01/hw_authorization.json`；本次无范围扩展。
- 状态：`BLOCKED_BEFORE_WINDOW_NO_JTAG_ENUMERATION`；W1 未启动，实际硬件窗口时长 0 分钟。

## 最新主机检查

- Wong 补充端口为 `COM4`。`.NET SerialPort.GetPortNames()` 返回 `COM4`，注册表将 `\\Device\\Silabser0` 映射到 `COM4`。
- Windows `Ports` 类和 `Win32_SerialPort` 查询为空；按 FTDI/Xilinx/Digilent 常见 VID 查询也未发现 JTAG 设备。
- 四树 `index.lock` 均不存在；无 `hw_server`、`xsdb`、`vivado`、`vitis` 引擎进程；TCP 3121 无监听；Vivado MCP 报告无活动 Vivado 会话。可用内存约 3542 MiB。没有发现常见串口监视器进程；这不等同于对 COM4 占用句柄的证明。

## 自动审批结果与停止

在用户授权 W1 后，尝试以 Tcl/general 模式启动 Vivado，仅为核验目标 JTAG。自动审批拒绝该调用，理由是目前只枚举到 COM4、未枚举 JTAG；启动重型会话在当前设备状态下不必要，并超出“设备未就绪即不启动”的范围。遵守该拒绝，没有改用命令行、其他 MCP 或间接方式探测。

没有启动 Vivado/hw_server/XSDB，没有打开 COM4，没有连接 JTAG，没有读取或写入板上寄存器，没有重启应用、烧录、改线或改变板卡状态。未核对当前板上部署身份，未采集 VDMA `S2MM_SR` 或运行期地址，未作真彩目视判定。用户报告板卡已接上且给出 COM4 与上述主机检查并列记录；当前缺少 JTAG 枚举，W1 仍阻塞。旧 r01 的“无 COM 设备”检查是 20:08 时点状态，保留不改写。

后续选择：Wong 选择“先让 JTAG 在 Windows 枚举”；该条件满足前不重试 Vivado 探测。

## 收窗与恢复

W1 未开窗、无本方硬件进程或连接需要释放，无板上状态需要恢复。继续前需主机枚举出目标 JTAG 设备；随后重新核锁、进程、端口和资源，并遵循已批准只读范围。该结果不关闭 VDMA 根因或阶段3 G5。
