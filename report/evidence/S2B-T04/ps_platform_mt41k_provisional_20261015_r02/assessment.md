# S2B-T04 PS7 DDR 离线候选记录

## 结论与边界

本包记录一个 Vivado 2026.1 离线 scratch 工程中的 PS7 DDR 参数候选及逐项读回。候选输入暂按 Wong 授权使用 `MT41K256M16TW-107`；这不证明当前实板装配了该料号，也不证明手册、原理图与实板 PCB 版次对应。Vivado 接受并读回参数，只证明该 IP 当前配置对象保存了这些属性，不等于 DDR 电气、时序或启动验证。

当前状态：几何和频率的候选值已读回；Micron 精确时序表与板卡 DDR 电源兼容性尚未核实，因此硬件资格 **BLOCKED**。没有生成或接受 XSA，没有生成 bitstream，没有初始化 PS/DDR，没有连接、读取或操作板卡。不能将本包作为 G3/G4/G5 通过证据。

## 基线与输入绑定

- 仓库基线 HEAD：`7ae90a5d7d7d2b40349925fb86feac97feb827a8`。
- `vivado/s2b_ps_platform.tcl` SHA-256：`B70871097F2E434F54B35EF4A13EFE070D64B08254707E9D66D0DBF32E23CEA9`。
- `board/ps_platform_fields.json` SHA-256：`ACC6307C709C55AE09D9B8223BFEAC96D3163A5A2D7F37DBD29C5ABFA399446B`。
- `board/ps_platform.md` SHA-256：`42B9ABA545527AD4DC50570DB1B88625409C7B08B4F0569570133B6672E7344E`。
- 临时器件配置输入为 `XC7Z020-2CLG400I`，Vivado part 为 `xc7z020clg400-2`。
- 手册只读来源：`D:\FPGA\AX7Z020\AX7Z020\AX7Z020开发板用户手册.pdf`，SHA-256 `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`。手册第 8 页写 AC7Z020 核心板及器件；第 12 页列 U8/U9 `MT41K256M16TW-107`、双颗 16-bit 组成 32-bit、总容量 1 GB、Bank 502 及 533 MHz/1066 Mbps 建议；第 13 页有芯片图片。手册及其图像不能独立证明当前实板或 PCB 版次。
- 原理图只读来源：`D:\FPGA\AX7Z020\AX7Z020\01_hardware\hardware\01_原理图\ac7z010_ac7z020原理图.pdf`，SHA-256 `5d810e712666839df18692ce05c3e280d39f9226de336315dab13b17b22339cc`。Rev 1.0 第 8 页列 U8/U9 `H5TQ4G63AFR-PBI or MT41K256M16TW-107`；第 6、8 页显示 32 条 DQ、A0-A14、BA0-BA2、VCC1V5 与 DDRVTT/VTTREF。该原理图不是当前 PCB 版次或实装料号的证明，电源轨也未在实物测量。
- Micron 官方料号目录：[MT41K256M16TW-107-M-P](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw-107-m-p)仅作为型号族/后缀特定产品信息来源。当前没有获取适用于裸料号输入的精确 timing table，故未用它推断本候选的 CL/CWL 或时序是否满足条件。
- AMD 原始文档：[PG082 Processing System 7 v5.5](https://docs.amd.com/api/khub/documents/5SmKudM_4jpvP8OtqGslWA/content)与[UG898 IP Integrator 示例](https://docs.amd.com/api/khub/documents/llJyAK1kzaa~JC1cpF1lyw/content)用于核对 PS7 IP 与配置接口；它们不证明当前 DDR 参数适配此板。

## 工具会话与隔离

- Vivado：`D:/Xilinx/2026.1/Vivado`，版本 2026.1；PS7 IP 定义 `xilinx.com:ip:processing_system7:5.5`。
- 本任务 Vivado 会话：`vivado-20261015-232644-566616f1`，PID `25196`，session type `ipi`。MCP 会话及 Tcl 解释器实际 cwd 为 `D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r01`；项目文件位于 R02 的 `project` 子目录，三份 Tcl 输入文件位于 R02 scratch 根目录并通过 R02 绝对路径 source。会话 `.log` 与 `.jou` 原件仍在 R01 的 `.vivado-ai`；未把 R01 目录当成本次项目或 RunId，亦未使用 root 可见的 T19 旧会话。
- 项目：`D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r02\project\s2b_ps7_mt41k_r02.xpr`，SHA-256 `9692CEA788C53E2B7B1C6EE69F74F411D9AD7AD9C972153649399B5DDECCF21B`。
- 已保存 BD：`D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r02\project\s2b_ps7_mt41k_r02.srcs\sources_1\bd\design_1\design_1.bd`，SHA-256 `606EBFDB4D79A375389317F4734DA0F0C88480043F3279A114922E821245F6FC`。
- 三份本次 Tcl 输入的 SHA-256：`baseline_verify.tcl` `95589FF4DC28B8E6905C31C46F473ED98425EDE6998285870B7ABCFDC2FEC608`；`configure_candidate.tcl` `CC748670C34D49A268D1660FC68EAFC864C58327CE138B1035541F5AE0AB2ED6`；`final_audit.tcl` `25F9D47C5FDF9E593C190FD0B40CAEBB9272EF7C319E0C71D8F1BCD5BB3AB838`。三份 Tcl 原件与完整 Vivado 工程位于 R02 scratch；本包有脚本副本、readback、捕获记录及两份完整会话日志的字节副本。完整日志原件未移动、未改写。
- 原生日志归属和证据副本：`.log` 原件 `D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r01\.vivado-ai\vivado_78004815_0dd60c44.log`；`.jou` 原件 `D:\FPGA_Competition\w2b\tmp\2B\S2B-T04\ps_platform_mt41k_provisional_20261015_r01\.vivado-ai\vivado_78004815_0dd60c44.jou`。两原件在复核时仍被 Idle Vivado 进程持有，直接打开计算 hash 被操作系统拒绝；通过 `Copy-Item -LiteralPath` 成功逐字节复制到本目录中同名文件，源/副本长度与最后写入时间一致。副本 SHA-256 分别为 `.log` `F4C9E9CBBC0CD53152AAAF093166DFFF08D8B76624F70864781A451853493D2F`（24,907 字节）和 `.jou` `7EB17C84C5D904172900CF584609FF608B20C8D40834AFD2DAB991A31DB531A5`（10,807 字节）；清单 hash 绑定的是这些 evidence 副本。完整源原件仍在上述 R01 `.vivado-ai` 精确路径。

## 配置意图与实际读回

PS7 的 DDR 配置对象成功保存并读回以下字段：

| 参数 | Vivado 读回 |
|---|---:|
| `PCW_UIPARAM_DDR_ENABLE` | `1` |
| `PCW_UIPARAM_DDR_PARTNO` | `MT41K256M16TW-107` |
| `PCW_UIPARAM_DDR_MEMORY_TYPE` | `DDR 3` |
| `PCW_UIPARAM_DDR_BUS_WIDTH` | `32 Bit` |
| `PCW_UIPARAM_DDR_DRAM_WIDTH` | `16 Bits` |
| `PCW_UIPARAM_DDR_DEVICE_CAPACITY` | `4096 MBits` |
| `PCW_UIPARAM_DDR_ROW_ADDR_COUNT` | `15` |
| `PCW_UIPARAM_DDR_COL_ADDR_COUNT` | `10` |
| `PCW_UIPARAM_DDR_BANK_ADDR_COUNT` | `3`（8 banks） |
| `PCW_UIPARAM_DDR_FREQ_MHZ` | `533.333333` |
| `PCW_UIPARAM_DDR_SPEED_BIN` | `DDR3_1066F` |
| `PCW_UIPARAM_DDR_CL` | `7` |
| `PCW_UIPARAM_DDR_CWL` | `5.000000` |
| `PCW_UIPARAM_DDR_T_FAW` | `25` |
| `PCW_UIPARAM_DDR_T_RAS_MIN` | `34.0` |
| `PCW_UIPARAM_DDR_T_RC` | `48.91` |
| `PCW_UIPARAM_DDR_T_RCD` | `7` |
| `PCW_UIPARAM_DDR_T_RP` | `7` |
| `PCW_UIPARAM_ACT_DDR_FREQ_MHZ` | `533.333374` |

`PCW_UIPARAM_DDR_DEVICE_CAPACITY`、速度档、CL/CWL 和各 timing 数值是 Vivado 的属性读回，不是独立厂商时序核验。533.333 MHz 下的 CL7/CWL5、tFAW/tRAS/tRC/tRCD/tRP 与指定输入料号之间的适配仍 **BLOCKED**；未通过降频、改时序或其他方式规避。没有配置或推定 DDR 电压。

## 实际命令状态

1. 创建隔离项目：`create_project s2b_ps7_mt41k_r02 {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/project} -part xc7z020clg400-2`，Vivado MCP 调用退出码 `0`，读回 part 为 `xc7z020clg400-2`。工具提示 Windows 路径长度超过 80 字符，记录为环境警告。
2. PS7 DDR 参数发现：`ipcfg::discover_params {xilinx.com:ip:processing_system7:5.5} DDR {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/discover_ddr}`，退出码 `0`，列出 DDR 几何、频率及 timing 参数名。两次更早的参数探测调用因临时目录参数格式错误而返回 `DISCOVER_ERR`；成功的第三次调用和原始记录均保留。
3. 初始候选 capture 脚本 `source -notrace {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/configure_candidate.tcl}` 退出码 `1`：脚本把 `verify_intent` 的三元组需求误作为预期/实际两元组传入，捕获记录显示 `verify_intent` 失败；随后脚本还读取了不存在的 capture 字段 `tcl_code`。该失败已保留，不能据此单独判为成功。
4. 修正参数形状后的候选核验 capture `source -notrace {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/baseline_verify.tcl}` 内部返回 `status=OK`、`code=0`，`verify_stuck={}`、`verify_intent={}`，19 项读回；随后该 Tcl 外层包装因读取不存在的返回字段退出码 `1`。另有一个长 BD 名警告（`BD 41-1753`）。
5. 最终只读 audit `source -notrace {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/final_audit.tcl}` 退出码 `0`，打印 `VALUES:19 VERIFY:PASS DISABLED:EMPTY`；19 项 readback 无配置意图 mismatch，禁用参数扫描为空。最终审计同时保留了早先配置 capture 失败状态，未把它覆盖为 PASS。
6. 交付包检查命令及实际退出码见 `delivery_manifest.json` 中的 checks；包装检查不替代语义审查。

## 未解决项

- 缺少对应精确 DDR 器件/速度档、533.333 MHz 下的官方 tAA/tRCD/tRP 与 CL/CWL 表，时序兼容性仍 BLOCKED。
- 当前板卡的实装 DDR 芯片、PCB 版次、VDD/VDDQ/VTT 与候选 profile 之间没有可追溯实物确认或测量；原理图标注不是测量结果。
- 没有 XSA/bitstream、PS 初始化、DDR 训练或任何板上执行；实物测试为 NOT_RUN。
- PS7 readback 仅证明离线配置对象属性；不证明其行为、时序裕量或模型部署能力。
