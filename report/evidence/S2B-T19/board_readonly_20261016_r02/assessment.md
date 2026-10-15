# S2B-T19 板卡只读识别（r02）

## 结果

2026-10-16（南京时间）通过 Vivado 2026.1 Hardware Manager 只读枚举到一个 Digilent JTAG target，序列号 `210512180081`。链上返回 `arm_dap_0` 和 `xc7z020_1`；FPGA 属性为 `PART=xc7z020`、`IDCODE_HEX=23727093`。这只确认 Z-020 系列/密度层面的 JTAG 可见性，不能独立确认完整订货型号 `XC7Z020-2CLG400I`。

`pnputil /enum-devices /class Ports /connected` 返回 CP210x USB-UART 桥 `COM4`、状态 `Started`。未打开串口，没有发送数据或验证协议。

## 操作边界

- 只执行 Hardware Manager target/device 枚举和只读属性查询，并调用 `close_hw_target`、`disconnect_hw_server`、`close_hw_manager`。
- 未调用 `program_hw_devices`，未下载 bitstream 或 PS 初始化文件；没有 DDR 读写、训练、模型运行、黄金比对、连续任务或非易失存储写入。
- Vivado 在本会话启动了本地 `hw_server` 与 `cs_server`。随后于 2026-10-16 02:52:05 +08:00 执行本机全局进程名快照，结果未发现 `vivado`、`hw_server` 或 `cs_server` 进程。查询无法判断工作树归属，也不能回溯证明具体退出时刻；此前交接还报告过另一 Vivado PID `25196` 活动，现有证据不能解释其与该采样的时间关系。因此本包不将此快照视为某一会话已关闭的独立确认。原始结果见 `local_process_snapshot.txt`。

## 限制与后续

- `PART` 与 IDCODE 不提供封装、速度等级、温度等级或 PCB 版本证明；完整器件目标沿用 Wong 的确认值。
- DDR 暂按用户从手册提供的 `MT41K256M16TW-107`，实际安装料号尚待厂家明日确认；在料号及 PCB/电源/时序对应关系核实前，不执行 DDR 初始化或访问。
- 此探针只覆盖 USB-UART/JTAG 可见性，不代表 G0、G3、G4、G5 通过。
