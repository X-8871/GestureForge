# 阶段 3：AN5642 原始视频链路

更新：2026-10-03（UTC+8）。状态：离线准备中，硬件接口 G0 未冻结；不是可烧录交付。

实物资料入口：[hardware_photo_evidence.md](hardware_photo_evidence.md)。AN5642 已到手；板卡正反面照片已在用户指定 Vault 目录读取并记录哈希，不再要求用户提供板卡照片。

## 目标及与原计划的差别

本阶段只完成 AN5642 → 经核实的扩展口 → PL 视频采集/DDR 缓冲 → HDMI → 显示器的原始画面链路，不加入 CNN、检测框或手势交互。

依据 `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` 第 3 阶段：可独立穿插，不等待 2A/2B 推理验收；至少 30 分钟无采集/显示死锁，像素计数与配置一致，检查测试图案、运动场景、花屏、撕裂和停帧。丢帧策略及口径仍须在 G0 明确。

| 项目 | 原计划 | 当前执行路线 |
|---|---|---|
| 视频输入 | 优先 HDMI 摄像头，替代接口由 Wong 选择 | Wong 已选择 AN5642 双目模块，采用厂商 DVP 例程 |
| 软件来源 | 未指定可复用例程 | 固定 AX7020 官方仓库提交；复用传感器初始化、视频 IP 和 VDMA/显示代码 |
| 首轮排障 | 原始画面 | 建议先单通道，再验证双通道；不代表取消双目，最终双目画面语义待冻结 |
| 工程目标 | 板卡身份核实后适配 | XA7Z020/CLG400/-1I；不得沿用厂商模板 XC/-2 |
| 分辨率 | G0 确定 | 候选采集 1280×720、RGB565、30 fps；HDMI 先独立验证后确定模式，不采用显示器 260 Hz 作为 FPGA 目标 |
| 验收 | 30 分钟稳定、明确丢帧口径 | 保持原标准，不能用工具目录通过代替编译、时序或板测 |

## 路线及依赖

| 顺序 | 任务 | 交付及验收 | 当前状态 |
|---|---|---|---|
| S3-T01 | 固定资料和工具基线 | 源仓库提交、PDF 哈希、源工程清单、版本差异 | 资料已核对；器件/IP 目录实测通过；离线准备静态独立审查 PASS（不含 PDF 独立视觉） |
| S3-T02 | 接口 G0 | 实物 PCB 对应图纸、逐针电平/方向、复位时序、视频模式、缓冲/丢帧语义 | 到手模块版本/Pin1/连接方式需断电核对；候选表不是接线授权 |
| S3-T03 | HDMI 独立画面 | 在 XA/-1 目标验证 BD、综合/时序，Wong 上板验证颜色、运动与计数 | 参考单路综合网表已生成；整体诊断因调试黑盒失败，完整时序/最终构建待完成 |
| S3-T04 | 摄像头输入 | 厂商初始化加错误检查、传感器 ID、测试色条、帧/行/像素计数与恢复测试 | 厂商错误处理补丁主机测试及独立审查通过；底层接收截止时间、实际 BSP/板测未通过 |
| S3-T05 | 原始画面直通 | VDMA 缓冲所有权、采集/显示帧号、双通道语义、撕裂与背压检查 | 依赖 T03/T04；不能直接认可示例的缓冲策略 |
| S3-T06 | 耐久与归档 | ≥30 分钟真实记录、配置/计数/错误/丢帧/视频、干净副本重建、G4/G5 | 待前序全部通过 |

工程修改后逐小任务验证、独立审查、提交；实物操作由 Wong 执行。阶段 2A 的进程、日志和运行证据不属于本轮范围。

## 资料基线

官方仓库：<https://github.com/alinxalinx/AX7020_2023.1>，固定提交 `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327`。

- `course_s2_vitis/14_vdma_hdmi_out`：独立 HDMI/VDMA 参考。
- `course_s2_vitis/22_ov5640_single`：首轮采集与显示参考；含 Vivado Tcl、约束、自定义 IP 和 Vitis 源码。
- `course_s2_vitis/23_ov5640_dual`：双通道参考；不以单通道结果证明双通道通过。
- `Hardware/01_SCH/AX7020开发板原理图V2.0.pdf`：329858 B，SHA-256 `e35eb1b654774a6f314de0140f5608d38a1c6be72d1c3e1008f5e288ac83c87e`。文件名 V2.0，而图框标记 Rev 1.0 / 2018-10-08；不得据文件名推定实物 PCB 版本。
- 用户手册原件 `D:\FPGA_Competition\摄像头资料\01_AN5642_原始资料\AN5642_UG.pdf`：1565440 B，SHA-256 `53b4fe327c58d0f6f7fe315ccc6079603c5c7bfce30262e0227a2e8c1596856d`。

本工作树的官方源缓存为 `tmp/stage3_reference/AX7020_2023.1`，未纳入项目 Git；可删除缓存不等于可删除厂商原件。固定提交与以下命令支持重新取回，不声称已有永久备份：

```powershell
git clone --filter=blob:none --no-checkout https://github.com/alinxalinx/AX7020_2023.1.git <新的空目录>
git -C <新的空目录> sparse-checkout set Hardware/01_SCH course_s2_vitis/14_vdma_hdmi_out course_s2_vitis/22_ov5640_single course_s2_vitis/23_ov5640_dual
git -C <新的空目录> checkout --detach fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327
```

已有摄像头资料包的 `18_ov5640_dual` / `19_an5642_lwip_double` / `05_video_show_single` 是旧 AX7Z020 2017.4 / `xc7z020clg400-2` 来源，CMOS 与 HDMI 引脚不同；仅作为算法和旧接口参考，不复制为 AX7020 的最终 XDC。Linux 示例的 BOOT/HDF 不等于当前板卡的可编辑、可重建工程。此次厂商网站的板卡手册下载返回 HTML，未认定为有效 PDF。

## 接口证据与未冻结项

AN5642 手册 PDF 第 3–4 页说明两颗 OV5640、DVP、板载供电/时钟及候选 720p RGB565 配置；第 6–7 页为 40 针定义，第 7 页说明 RGB 用 D[9:2]、PCLK 上升沿采样、HREF 高有效及 Pin1 对齐。手册模块名称有 OV5642 字样，不能因此把内部传感器改成 OV5642；Pin8 原文为 `CMOS_D2`，双通道冻结前须进一步核对模块原理图，不能自动补成 `CMOS2_D2`。

AX7020 原理图 PDF 第 15 页：J10 使用 EX_IO1 网络，J11 使用 EX_IO2 网络，经 33 Ω 电阻到 FPGA；第 5 页为 FPGA BANK34/35 引脚；第 14 页为 HDMI 输出电路。官方单路 XDC 与这份图纸的 CMOS1 网络映射一致，见 `cmos1_candidate.csv`；但实物 PCB 尚未绑定，J10/J11 不能互换。该表没有替代实物检查，亦未冻结第二通道。

已取得：板卡正反面照片、Wong 确认 AN5642 到手。仍需内部核对既有照片的 PCB 丝印与图纸绑定、模块版本、Pin1 方向/排线方式、实际 bank 电压、摄像头 I/O 电平证据、复位/上电条件、显示器实际接受的 HDMI 模式；然后才能出最终 XDC 与接线步骤。G0 还须明确单/双通道验收范围、采集/显示帧率、丢帧原因分类与缓冲所有权。显示器有两个 HDMI 接口是输入数量，不证明 FPGA 有 HDMI 接收能力。不要再以这些核对项为由重复索要板卡照片。

示例仍待审：采集与显示可能使用同一当前帧缓冲，不能视为无撕裂方案；I2C 初始化/写寄存器错误不能被忽略；PCLK 的 `CLOCK_DEDICATED_ROUTE FALSE` 不能替代输入时钟及延迟约束。迁移后需验证配置、CDC、背压、复位、DDR/缓存一致性和完整时序。

## 工具目录实测及复现

本机可执行文件：`D:\Xilinx\2026.1\Vivado\bin\vivado.bat`。2026-10-02 实测识别 `xa7z020clg400-1I`，13 个精确 VLNV 全部可找到；退出码 0、`PASS_TOOL_CATALOG_ONLY`。首个受限启动在加载用户应用时失败（退出 1），经批准在受限环境外重新启动成功；未改变系统策略。结果摘要见 `report/stage3_vendor_probe_20261002.json`。

```powershell
& 'D:\Xilinx\2026.1\Vivado\bin\vivado.bat' -mode batch -source '<工作树绝对路径>\scripts\s3_probe_vendor.tcl' -log '<已存在隔离目录>\probe.log' -journal '<已存在隔离目录>\probe.jou' -tclargs '<官方仓库绝对路径>' '<已存在隔离目录>\新的结果.txt'
```

目录与文件必须先精确验证；结果文件必须不存在。预计 1–2 分钟，只创建内存工程并查目录，不 source 厂商构建模板（该模板会自动综合/实现/生成 bitstream）。失败时保留日志并诊断，不回退 XC/-2 或静默替换 IP 版本。目录通过不是 BD、综合、时序、Vitis 编译或 G3/G4/G5 通过。原始日志只留本地临时目录，不混入代码提交。

## BD 迁移诊断（不是可烧录工程）

2026-10-02 进一步实际创建 BD，原厂未修改 IP 在 XA/-1I 上失败：`BD 5-683`，`axi_dynclk:1.0` 不支持当前 part。Vivado 查询目标家族为 `azynq`；三个自定义视频 IP 的原 XML 仅列 `zynq` 等家族，没有 `azynq`。所以目录检查的 13/13 不等于目标上可实例化。

`scripts/s3_validate_vendor_bd.tcl` 在固定提交且单路来源 Git 状态干净时，创建全新的隔离工程，只 source `ps_config.tcl` / `pl_config.tcl`，不 source 自动构建脚本。默认阶段 `bd` 不生成 HDL；显式阶段 `hdl` 仅生成 IP/BD 源文件和顶层包装器。不加载最终板卡 XDC，不综合或连接硬件；HDL 生成会产生 IP 内部 XDC，报告中的 `NO_XDC` 不能解读为没有任何约束文件。

- 默认 `native`：保留原厂 IP 封装，诊断原生兼容性。
- 显式 `azynq_metadata`：只在新副本的三个 `component.xml` 中增加 `azynq / Pre-Production` 声明；这是诊断实验，不是正式支持声明或生产迁移批准。没有改 HDL、接口和视频参数。
- 实测实验 `bd_metadata02` 创建/校验并保存 16 个 BD cell，退出码 0、`PASS_BD_METADATA_EXPERIMENT_ONLY`；33 个源文件中 30 个副本字节相同，另外 3 个 XML 除换行规范外仅增加该声明。原仓库仍干净。
- 首次实验报告终态为空是包装器自身错误，已修复重跑；失败工程/日志均保留，不充作通过结果。证据见 `report/stage3_bd_experiment_20261002.json`。

复现：沿用上节已精确验证的 Vivado/源目录，在 `-source` 使用 `<工作树绝对路径>\scripts\s3_validate_vendor_bd.tcl`；`-tclargs` 为 `<官方仓库绝对路径> <新输出目录绝对路径> native` 或显式 `azynq_metadata`。输出目录必须不存在、父目录存在，日志另用新名字；预计 1–2 分钟、单线程。失败保留产物，禁止原地覆盖或自动回退器件。

仍需解决：实际 PCB/DDR/电平对应、PCLK 与视频完整约束、自定义 IP 在 XA/-1 的 HDL/时序兼容性、Windows 路径长度提示、旧 xlconcat/xlconstant 的工具迁移提示、Vitis 软件迁移，以及缓冲/丢帧口径。实验通过不能关闭硬件 G0，也不能代替综合、时序或 G3/G4/G5。

## HDL 生成诊断与下一步

2026-10-02 在新短路径 `tmp/s3h01` 实测 `azynq_metadata hdl`，52 秒、退出码 0，16-cell BD 及顶层包装器生成完成。摘要和日志/包装器哈希见 `report/stage3_hdl_generation_20261002.json`。这不是语法、仿真、综合或时序通过；三个自定义 IP 的家族声明仍是实验。

复现时在上一节 `-tclargs` 后增加第四参数 `hdl`，例如 `<官方仓库绝对路径> <新输出目录绝对路径> azynq_metadata hdl`；省略第四参数仍为 `bd`。保持新目录、新日志、单线程和失败保留原则。生成时出现五条不同的 AXI ID 1/6 位宽连接警告 `BD 41-2384`，需要逐项验证事务 ID 和生成连接；在关闭前不得把工程视为可直接上板。

另外已用 read-pdf-reliably 的 diagram 模式实际读取旧资料 `D:\FPGA\AX7Z020\AX7Z020\01_hardware\hardware\01_原理图\ax7z010_ax7z020原理图.pdf` 第 1、14 页（14 页总数，SHA-256 `e51ffd1677bc2387f86c6123951486fd2a5c90faee4f59a91e9fceb9750aaf78`）。第 1 页为核心板加底板架构，含 CAN/RS485/MIPI；第 14 页为 J28/J29 调整 VCCIO_35。它不能用来证明现有 AX7020 单板的端口或 bank 电压，禁止把该图的跳线操作用于实物。没有改动或复制厂商原件到正式工程。

后续语法检查、静态连接及综合诊断结果见下节。最终约束和接线步骤仍需硬件 G0，不能直接下载隔离实验产物。

## 2026-10-03 离线结果与首次实物关口

原综合在会话中断后留下排队/运行标记。本轮只读确认本阶段对应进程已不存在，保留 13 个已完成 IP；备份中断产物后仅恢复四个未完成 IP 和顶层。实际 `synth_1` 完成，但整体诊断 `FAILED=1`，结果为 `UNRESOLVED_BLACKBOXES:dbg_hub`，不宣称综合诊断通过。该标志不是进程退出码；日志请求 `exit 2`，启动器实际退出码未归档为本地证据。只读网表查询确认唯一黑盒为 `dbg_hub_CV`、Vivado 调试核心 `dbg_hub`，另有厂商 ILA；没有把它当作功能 IP 源码缺失，也没有白名单屏蔽检查。摘要见 `report/stage3_synth_diag_20261003.json`。

该综合网表的资源为 7724 Slice LUT、11924 Slice Registers，仅代表本次原厂视频参考，不是实现后资源或 CNN 资源。未加载最终板卡 XDC，DRC 有 NSTD-1/UCIO-1 以及三个 RAM 异步控制警告；打开网表另有 `Timing 38-249` 生成时钟关键警告。没有降低 DRC 等级、没有实现/完整时序/bitstream 或板测通过。AXI ID 五处静态连接及五个检查器测试通过，仍不能代替事务验收。

传感器适配入口 `software/sensor/ADAPTATION.md`：只保存厂商差异补丁及固定源准备脚本，不重新编写寄存器表。主机四组合各 968 cases / 847246 checks / 302 writes，303 项表值一致；独立 Reviewer 复验和冻结检查通过。证据 `report/stage3_sensor_host_20261003.json`。底层 `MasterRecvPolled` 仍有无限等待，主机进程 30 秒限时不等于 I2C 超时；真实 BSP/VDMA/显示集成未完成。

首次需要 Wong 的实物操作是 [prepower_check.md](prepower_check.md) 的断电模块核对：AN5642 型号/版本、Pin1 和直插/排线方式。不是立即烧录上板，不要求重发板卡照片，不授权猜方向或带电测量。模块与板卡电气绑定后，才冻结最终接口、约束和接线；后续仍须解决调试核心/生成时钟、底层接收截止时间、缓存/缓冲所有权、视频背压/复位及帧行像素观测，完成正式构建和审查后再发可执行板测步骤。G0/G3/G4/G5 尚未通过。
