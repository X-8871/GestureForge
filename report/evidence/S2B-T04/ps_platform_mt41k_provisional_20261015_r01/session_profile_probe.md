# S2B-T04 MT41K 暂定输入：只读 profile 探测

状态：`BLOCKED`。本记录仅证明输入资料范围和只读环境探测结果；不表示 DDR 配置通过、XSA 已生成或硬件已运行。

## 基线与范围

- 仓库基线：`14928578ec08d257cc19f6ece684887e3e294ed3`。
- 目标候选：用户批准将 `MT41K256M16TW-107` 暂作后续离线配置输入；不据此确认当前板卡的实物料号或 PCB 版本。
- 本轮未改动 `vivado/s2b_ps_platform.tcl`、`board/ps_platform_fields.json`、`board/ps_platform.md`；没有提交。
- 新生成的页级解析产物位于 `source_manual/` 与 `source_schematic/`。解析状态均为 success，manifest 保留页码、源文件 SHA、渲染参数及结果路径。

## 输入证据

| 资料 | SHA-256 | 可支持的结论 | 边界 |
|---|---|---|---|
| `D:\FPGA\AX7Z020\AX7Z020\AX7Z020开发板用户手册.pdf` | `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf` | 第 8 页标注 XC7Z020-2CLG400I；第 12 页列 U8/U9 为 MT41K256M16TW-107、单颗 256M×16、总线 32 位、最高 533 MHz/1066 Mbps；第 13 页为颗粒照片。 | 手册和照片不证明用户当前板卡的实物料号、板卡版本或照片对应关系。 |
| `D:\FPGA\AX7Z020\AX7Z020\01_hardware\hardware\01_原理图\ac7z010_ac7z020原理图.pdf`，Rev1.0 | `5d810e712666839df18692ce05c3e280d39f9226de336315dab13b17b22339cc` | 第 8 页列 AC7Z020 的 U8/U9 可用 H5TQ4G63AFR-PBI 或 MT41K256M16TW-107；第 6/8 页可见 32 条 DQ、A0-A14、BA0-BA2、VCC1V5、DDRVTT/VTTREF。 | 该原理图对应性仅限其自身标注的 AC7Z020/Rev1.0；未独立确认当前 PCB 版次。VCC1V5 不能单独证明暂定颗粒在该电源下满足工作规格。 |
| Micron 官方产品目录：<https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw-107-m-p> | 在线页面，本次未取得可核对的完整数据表文件 | 该 `-M-P` 目录变体页列 4Gb、x16、DDR3、1.35V、933MHz/1866MTPS、CL13；页面数据只作族/该变体背景。 | 后缀并非本次暂定输入本身的物理身份；公开页面未提供本次所需 533.333MHz 下的 tAA/tRCD/tRP 表行。完整数据表需登录访问，本次未取得。 |

容量/几何的交叉核对：Micron 目录将 MT41K256M16 系列列为 `32 Meg x 16 x 8 banks`；两个 x16 颗粒组成 32-bit 总线，每颗 4Gb、合计 1GB。每 bank 深度 `32 Meg = 2^25` 个 x16 地址；任务指定 `15` 行地址与 `10` 列地址相加为 25，BA0-BA2 为 3 个 bank 地址位，即 8 banks。此为型号/资料下的候选几何推导，不是工具实际 readback。

## 时序与电源阻断

- 目标 533.333333 MHz 对应 `tCK = 1.875 ns`。当前官方资料不足以确认目标颗粒在该频率下的最小 `tAA`、`tRCD`、`tRP`，因此不能确认旧 profile 的 CL7/tRCD7/tRP7 安全，也不能把旧 `MT41J256M16 RE-125` 冒充成目标颗粒的时序规格。
- 官方目录中的 CL13 是 933MHz 目录规格，不能直接推导 533.333MHz 下可使用的 CL；本轮未自行推算或降低频率。
- Rev1.0 原理图可见 `VCC1V5`、`DDRVTT`、`VTTREF`，Micron 目录显示该 `-M-P` 变体 I/O Voltage 为 1.35V。由于未取得适用于暂定料号的电气规格表，无法判定 1.5V VDD/VDDQ 是否在其允许工作范围内；不得据颗粒名称猜测 1.5V 兼容性。
- 因为时序表和供电范围未被核实，候选保持阻断，不产生成功配置读回或可供下游冻结的 XSA。

## Vivado 2026.1 只读探测与会话范围

Vivado 子代理启动返回 `status=success`、`session_id=vivado-20261015-232644-566616f1`、PID `25196`、工作目录 `D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r01`、日志 `D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r01\.vivado-ai\vivado_78004815_0dd60c44.log`。子代理自己的 `vivado_status` 对该 ID 返回 `Idle`、`process_running=true`、相同 D: 工作目录；只读环境查询返回 Vivado `2026.1`、安装目录 `D:/Xilinx/2026.1/Vivado`、当前工作目录为上述 tmp 路径、无打开工程。

会话身份存在工具作用域限制：子代理自己的 `vivado_list_sessions` 同时显示一个被采用的旧 T19 条目（ID `vivado-20261014-133318-6fec06f6`，同 PID 25196，工作目录在另一个 C: T19 worktree）和本任务条目（上述 ID，PID 25196，D: T04 tmp，proxy `127.0.0.1:7862`）。父会话列表此前只解析出旧 T19 命名空间；父会话对本任务 ID 的状态查询返回 not found。系统进程路径查询 `Get-CimInstance Win32_Process -Filter "ProcessId = 25196"` 返回拒绝访问，无法用 OS 级路径消除别名歧义。后续只使用本子代理返回且工作目录匹配的 session ID；未调用旧 T19 ID，未停止或重连任何会话。

只读 Tcl 命令与结果：

1. `list [version -short] $env(XILINX_VIVADO) [pwd] [current_project -quiet]`：退出码 0；返回 `2026.1`、`D:/Xilinx/2026.1/Vivado`、本任务 D: tmp 路径、空工程。
2. `list [version -short] $env(XILINX_VIVADO) [pwd] [current_project -quiet] [get_parts xc7z020clg400-2] [get_ipdefs -all xilinx.com:ip:processing_system7:*]`：退出码 1，`No open project`；不据此判断器件/IP 不支持。
3. `get_ipdefs -all xilinx.com:ip:processing_system7:*`：退出码 1，`No open project`；没有创建工程来绕过该限制。

对只读安装目录 `D:\Xilinx\2026.1\Vivado\data\ip\xilinx\processing_system7_v5_5` 的文字搜索显示：`PCW_UIPARAM_DDR_PARTNO` 在 XGUI 中是 comboBox，IP-XACT 初始值为 `NA`，静态 IP 目录中未搜到 `MT41K256M16TW-107` 或 `MT41K256M16`。目录中的 preset 示例出现 `MT41J128M16 HA-15E`、`MT41J256M8 HX-15E` 与 `Custom`。由于 PS7 需要有工程/IP 实例才能读取动态选择项，静态文件搜索不能证明实际 comboBox 不支持目标料号；目标 PartNo、PS7 支持 profile、几何及 CL/CWL/readback 均仍为 `UNKNOWN`。

本轮没有调用 Vivado 配置写入命令，没有创建或打开项目/BD/IP，没有 PS 配置、综合、实现、XSA、bitstream、PS 初始化、DDR 初始化或任何板卡操作：`hardware_execution=NOT_RUN`。首个 Tcl 查询错误是无项目条件下的只读查询错误，不能当作目标配置测试失败或通过。

## 验收状态

- 目标物理器件/PCB：未确认；`MT41K256M16TW-107` 仅为用户批准的暂定离线输入。
- PS7 精确 PartNo/profile 支持与时序 readback：`UNKNOWN`。
- Micron tAA/tRCD/tRP 及 1.5V VDD/VDDQ 兼容：`BLOCKED`，待取得适用的 Micron 原始规格表。
- BD/XSA/bitstream：未生成。
- G3/板卡运行：`NOT_RUN`。
- 总体结果：`BLOCKED`，不能作为阶段2B通过证据或下游冻结输入。
