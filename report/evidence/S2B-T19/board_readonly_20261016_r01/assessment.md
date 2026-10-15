# S2B-T19 板卡只读识别

## 结果

2026-10-16（南京时间）通过 Vivado 2026.1 的 Hardware Manager 只读枚举到一个 Digilent JTAG target，序列号为 `210512180081`。链上有 `arm_dap_0` 与 `xc7z020_1`；FPGA 的 `PART` 为 `xc7z020`，`IDCODE_HEX` 为 `23727093`。这证明当前 JTAG 链能识别 Z-020 系列器件，与用户确认的 XC7Z020 目标在系列/密度层面一致。

此读回不含 `CLG400`、`-2` 或 `I` 信息，不能独立确认完整订货型号 `XC7Z020-2CLG400I`，也不能区分用户已确认的 XC 型号与板卡历史 XA/-1 记录。COM4 上枚举到 CP210x USB-UART 桥，但没有打开串口或进行功能测试。

## 操作边界

- 只执行了硬件管理器连接、target/device 枚举、`list_property` 和 `get_property` 只读查询，并关闭了本次 target/server 连接。
- 未调用 `program_hw_devices`，未下载 PL bitstream 或 PS 初始化文件；未访问 DDR，未执行模型、黄金比对或连续任务；未写 QSPI 或其他非易失存储。
- `Get-PnpDevice` 因 Access Denied 失败，随后用 `pnputil /enum-devices /class Ports /connected` 成功查询，完整输出见 `pnputil_ports.txt`。
- Vivado stop 返回 PID 可能仍在运行的警告；紧接着的进程查询中 PID 26204 已不存在，Vivado 会话列表中本次会话也已消失。另一工作树的既有 Vivado 会话保持原样。

## 阻断与限制

- 串口设备枚举不等于 UART 引脚、电平或协议正确。
- JTAG 的 `PART=xc7z020` 和 IDCODE 不提供封装、速度等级、温度等级或 PCB 版次的证明。
- DDR 实装料号和 PCB 版次仍待厂家确认。`MT41K256M16TW-107` 仅按用户要求作暂定离线输入；本次没有 DDR 初始化、读写或训练。
- 本证据仅覆盖 USB-UART/JTAG 可见性，不代表 PS/DDR/HP0/cache 通路、模型部署或阶段 G3/G4/G5 通过。
