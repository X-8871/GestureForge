# 阶段 3：AN5642 原始视频链路

更新：2026-10-03（UTC+8）。状态：离线准备中，硬件接口 G0 未冻结；不是可烧录交付。

实物资料入口：[hardware_photo_evidence.md](hardware_photo_evidence.md)。Wong 已确认 AX7020 板卡、AN5642、显示器和 HDMI 线均已齐全，尚未进行实物测试。板卡正反面照片已在用户指定 Vault 目录读取并记录哈希，不再要求用户提供板卡照片。

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
| S3-T01 | 固定资料和工具基线 | 源仓库提交、PDF 哈希、源工程清单、版本差异 | 资料已核对；器件/IP 目录实测通过；离线准备静态独立审查 PASS；固定官方源的 J10/AN5642 32 路映射与 LVCMOS33 已静态核对；Pin8 信号名差异作为资料边界记录 |
| S3-T02 | 接口 G0 | 实物 PCB 对应图纸、逐针电平/方向、复位时序、视频模式、缓冲/丢帧语义 | AX7020 官方 2023 手册与固定官方双目例程静态匹配 J10 Pin3–18/20–35 的完整 32 路映射，均为 LVCMOS33；Pin19/36 为 NC。仍未确认现有工程是否加载该 XDC、`AX701020.3.0` 与图纸修订绑定、实物 J10 Pin1 朝向和板上电压；视频 G0 仍阻断，不要求 Wong 插接或上电 |
| S3-T03 | HDMI 独立画面 | 在 XA/-1 目标验证 BD、综合/时序，Wong 上板验证颜色、运动与计数 | 隔离副本 `opt_design` 已验证综合阶段的调试 hub 黑盒被解析；最终 XDC、完整时序和 T03 bitstream 尚未完成；2026-10-03 时钟候选复验因 Vivado 启动时无有效许可证而未执行；须先解决 Vivado 授权并完成正式构建、完整时序与 HDMI bitstream，之后再给 Wong 精确板测步骤 |
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
- 先前记录的手册副本 `D:\FPGA_Competition\摄像头资料\01_AN5642_原始资料\AN5642_UG.pdf`：1565440 B，SHA-256 `53b4fe327c58d0f6f7fe315ccc6079603c5c7bfce30262e0227a2e8c1596856d`。该副本与 Wong 指定的官方资料目录内 PDF 哈希不同，二者来源/版本等价关系未核实；后续不得用它覆盖或替代指定目录中的官方基线。ALINX 官方公开入口：[AN5642 双目摄像头用户手册](https://www.alinx.com/public/upload/file/AN5642_UG.pdf)。

### Wong 指定的官方资料优先级

AN5642 官方资料根目录（严格按 Wong 给出的路径）：`D:\FPGA_Competition\摄像头资料\官方资料`。已核实其中光盘资料实际根目录为 `D:\FPGA_Competition\摄像头资料\官方资料\AN5642\AN5642_CD\CD`。模块规格、连接器和传感器资料优先从该目录取证；AI 搜集或第三方材料仅作辅助线索，不能覆盖官方原件。AX7020 板卡的端口、电气和 FPGA 引脚仍以 AX7020 对应官方原理图/工程为准，不能拿 AN5642 模块手册或其他开发板例程替代。

指定目录中已核验文件（SHA-256 均按原件计算）：

| 文件 | 大小 | SHA-256 |
|---|---:|---|
| `AN5642\AN5642_CD\CD\黑金开发板之双目摄像头用户手册.pdf` | 1551870 B | `626827e98f6d7b4afbfeecddb91756c00d86b581b191cf2be469fc21b2bb745b` |
| `AN5642\AN5642_CD\CD\原理图\AN5642-2016-12-14.pdf` | 54381 B | `31543f328764707f14cb0e341f16705d77485dfd8cf50a1539bb49fa210e21f1` |
| `AN5642\AN5642_CD\CD\datasheet\camera\OV5640_datasheet.pdf` | 1711217 B | `b7059c287dd23ab36730da5fdb93f1d921bb1509fce37af1884c09dcda06ace7` |
| `AN5642\AN5642_CD\CD\datasheet\camera\SCCB接口时序.pdf` | 303497 B | `aadf37940ce3fddad2e258f37b5c5c8e5c88acee3d4556085afb4131e85136aa` |

官方光盘 `Project` 下可见 AX301、AX415、AX515、AX516、AX530、AX545、AX845 示例目录；未见 AX7020 示例目录。其他板卡示例不能直接证明 XA7Z020/CLG400 板上的连接器、引脚或电平。

**AN5642 官方资料针脚复核（2026-10-03）：** 指定官方用户手册 p.6 将模块 Pin1 标为 GND、Pin2 为 `+5V`、Pin3 为 `CMOS2_D9`；p.7 将 Pin19、Pin36 标为空脚。官方模块原理图 `AN5642-2016-12-14.pdf` p.1 的 J3 也标 Pin1=GND、Pin2=+5V、Pin3=`CMOS2_D9`、Pin19/36=NC，CMOS1 信号为 Pin20–35；两份官方资料在这些针脚定义上相符。唯一已知信号名简写差异是手册 p.6 Pin8=`CMOS_D2`、原理图 Pin8=`CMOS2_D2`，p.7 又用 `CMOSx_D0~D9` 表示通道通用数据名。Pin2 是 +5V 供电针，不是 5V 容忍的 I/O；接线前须在断电状态确认 Pin1 对齐及整排无偏移，禁止错位、强插或带电插拔。

AN5642 手册第 3 页称接口为“40针母座”、第 6 页称模块为“40针的排针”；AX7020 官方 2023 用户手册的 J10 表与固定官方双目例程 XDC 静态给出 CMOS2 模块 Pin3–18→J10 Pin3–18、CMOS1 Pin20–35→J10 Pin20–35，Pin19/36 为 NC。手册第 6 页 Pin8 写 `CMOS_D2`，J3 原理图 Pin8 为 `CMOS2_D2`，第 7 页用 `CMOSx_D0~D9` 表示通道通用数据名；这是信号名简写差异，不是针号映射冲突。实物 PCB 与图纸/手册修订绑定、实际模块 Pin1 朝向仍需核实；静态示例不证明本工程已加载该约束、构建通过或物理触点已测试。

本工作树的官方源缓存为 `tmp/stage3_reference/AX7020_2023.1`，未纳入项目 Git；可删除缓存不等于可删除厂商原件。固定提交与以下命令支持重新取回，不声称已有永久备份：

```powershell
git clone --filter=blob:none --no-checkout https://github.com/alinxalinx/AX7020_2023.1.git <新的空目录>
git -C <新的空目录> sparse-checkout set Hardware/01_SCH course_s2_vitis/14_vdma_hdmi_out course_s2_vitis/22_ov5640_single course_s2_vitis/23_ov5640_dual
git -C <新的空目录> checkout --detach fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327
```

已有摄像头资料包的 `18_ov5640_dual` / `19_an5642_lwip_double` / `05_video_show_single` 是旧 AX7Z020 2017.4 / `xc7z020clg400-2` 来源，CMOS 与 HDMI 引脚不同；仅作为算法和旧接口参考，不复制为 AX7020 的最终 XDC。Linux 示例的 BOOT/HDF 不等于当前板卡的可编辑、可重建工程。此次厂商网站的板卡手册下载返回 HTML，未认定为有效 PDF。

## 接口证据与未冻结项

AN5642 手册 PDF 第 3–4 页说明两颗 OV5640、DVP、板载供电/时钟及候选 720p RGB565 配置；第 6–7 页为 40 针定义，第 7 页说明 RGB 用 D[9:2]、PCLK 上升沿采样、HREF 高有效及 Pin1 对齐。手册模块名称有 OV5642 字样，不能因此把内部传感器改成 OV5642。手册 p.6 的 Pin8 名为 `CMOS_D2`，J3 原理图 Pin8 为 `CMOS2_D2`，p.7 又以 `CMOSx_D0~D9` 表示通道通用数据名；这是命名差异。J3 原理图 p.1 的 Pin19、Pin36 为 NC，CMOS1 信号从 Pin20 到 Pin35。当前实物 Pin1 对齐方向仍须上板前目视确认。

AX7020 官方 2023 用户手册 [AX7020_UG.pdf](https://www.alinx.com/public/upload/file/AX7020_UG.pdf) p.37/43（J10）与 p.38/43（J11）提供针脚表；固定官方项目提交 `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327` 的板卡原理图 p.15 将 J10 使用 EX_IO1、J11 使用 EX_IO2（经 33 Ω 电阻到 FPGA），第 5 页为 FPGA BANK34/35 引脚、第 14 页为 HDMI 输出电路。固定双目例程 `course_s2_vitis/23_ov5640_dual/Vivado/auto_create_project/src/constraints/an5642.xdc` 的 SHA-256 为 `3B57CF39B9E78FEEF8E76B1BA4EB1F63C0A3AD979768589EB807CCF946719E64`；该文件 CMOS1/CMOS2 各有 16 个 `PACKAGE_PIN` 映射与 16 个 `IOSTANDARD LVCMOS33` 约束。逐项静态匹配 J10 Pin3–18、20–35 共 32 路，完整触点与 FPGA 封装脚见下表；CMOS1 封装脚也与 `cmos1_candidate.csv` 一致。此为官方示例静态接线依据，不是本工程已加载约束、已构建、已测量板上电压或实物已验证的证据。J10/J11 网络不可互换。

### 2026-10-03 官方接口资料增补（尚未实物测试）

- Wong 确认 AX7020 板卡、AN5642、显示器和 HDMI 线已齐全；当前均未测试。本节资料核对不构成插接、上电或烧录授权。
- 指定目录内 AN5642 官方用户手册第 6 页为 Pin1=`GND`、Pin2=`+5V`、Pin3=`CMOS2_D9`；p.7 的 Pin19、Pin36 是空脚。模块 J3 原理图 p.1 同样标 Pin1=GND、Pin2=+5V、Pin3=`CMOS2_D9`、Pin19/36 为 NC，CMOS1 信号占 Pin20–35；两份官方资料的针号定义相符。仅 Pin8 存在 `CMOS_D2`/`CMOS2_D2` 信号名简写差异。模块原理图中的 `CMOSx_DOVDD_2V8` 是传感器内部供电轨，不应误认为外部 I/O 电平或据此推断外部接口冲突。Pin2 为 +5V 供电针，严禁将其当作信号 I/O；插接前断电并确认 Pin1 对齐、不得偏移。
- 固定官方项目提交 `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327` 的 `Hardware/01_SCH/AX7020开发板原理图V2.0.pdf` 第 15 页标注 J10/J11 Pin2=`VCC5V`。ALINX 官方公开 [AX7020 用户手册（J10 p.37/43、J11 p.38/43）](https://www.alinx.com/public/upload/file/AX7020_UG.pdf)给出 J10/J11 针脚表、J11 Pin1=GND/Pin2=+5V，并说明 BANK35 默认 I/O 为 3.3V、不可接入 5V I/O。AN5642 官方手册第 6–7 页提供模块针脚及 Pin1 对齐提示；与下述双目工程针脚表共同确认厂商预期连接器是 J10。
- 固定提交中的官方双目约束 `course_s2_vitis/23_ov5640_dual/Vivado/auto_create_project/src/constraints/an5642.xdc`（SHA-256 见上）与 AX7020 官方 2023 用户手册 J10（J10 p.37/43）逐项静态匹配：CMOS2 模块 Pin3–18 对 J10 Pin3–18，CMOS1 模块 Pin20–35 对 J10 Pin20–35，合计 32 路完整信号均为 `LVCMOS33`。AN5642 J3 p.1 的 Pin19、Pin36 为 NC，不属于 CMOS1；CMOS1 只占 Pin20–35。下表是已核实的官方源映射及静态接线依据，不代表当前 AX7020 实物修订/连接器方向已匹配，也不代表本工程已加载 XDC、完成构建或实测通过：

| 通道 | AN5642 模块 Pin | AX7020 J10 Pin | FPGA 封装脚（按触点序号） |
|---|---|---|---|
| CMOS2 | 3–18 | 3–18 | `W19, W18, R14, P14, Y17, Y16, W15, V15, Y14, W14, P18, N17, U15, U14, P16, P15` |
| CMOS1 | 20–35 | 20–35 | `T16, V18, V17, T15, T14, V13, U13, W13, V12, U12, T12, T10, T11, A20, B19, B20` |

AN5642 手册 p.6 和 AX7020 J10 手册均将 Pin2 定义为 `+5V`；Pin2 是供电而非 5V I/O。任何后续实物插接必须在断电状态确认 Pin1 对齐、40 针无偏移，禁止错位或强插。

- 厂商官方源证据已确认 AN5642 双目→AX7020 J10 的 32 路静态映射和 LVCMOS33，Pin19/36 NC、CMOS1 Pin20–35；这不是当前 PCB/手册修订绑定、本工程加载 XDC、板上电压测量、构建/时序或实物测试证据。ALINX [AX7020 官方产品页](https://www.en.alinx.com/Product/SoC-development-Boards/Zynq-7000-SoC/AX7020.html)列两组 40-pin 扩展口、ALINX 双目摄像头模块及一个 HDMI（in 或 out）。官网当前 `AX7020_V3.0_User Manual` 条目要求邮箱验证/验证码；本轮未提交任何信息，也未取得或核验该 PDF。因此不能证明照片记录的 `AX701020.3.0` 与 2023 图纸/手册或 V3.0 手册一致。指定本地 AN5642 官方资料仍是依据；[AN5642 官方公开手册入口](https://www.alinx.com/public/upload/file/AN5642_UG.pdf)便于查阅。
- 当前仍阻断：`AX701020.3.0` 与适用 PCB/手册修订绑定、实物 J10 Pin1 对齐方向、当前工程是否加载官方映射约束及板上电压、视频接口 G0、S3-T03 最终 bitstream 与完整时序。AN5642 手册与 J3 原理图的 Pin1/2/3/19/36 针号定义相符，Pin8 仅有网名简写差异。Pin2 为 +5V 供电针，实物插接前必须断电并确认 Pin1 对齐，避免偏移。当前不要求 Wong 插接摄像头或上电；待 HDMI artifact 完成且具备实物验证条件时，再提供明确板测步骤。

已取得：板卡照片及 Wong 对板卡、AN5642、显示器、HDMI 线均已齐全但尚未测试的确认。AX7020 官方 2023 用户手册与固定官方双目例程静态确认 J10 Pin3–18/20–35 共 32 路信号映射，全部 LVCMOS33；AN5642 J3 Pin19/36 为 NC，CMOS1 仅 Pin20–35。模块内部 `CMOSx_DOVDD_2V8` 不代表外部接口冲突。AN5642 手册与原理图的 Pin1/2/3/19/36 针号定义相符；Pin8 仅有 `CMOS_D2`/`CMOS2_D2` 网名简写差异。该证据不绑定 `AX701020.3.0` 与 2023 图纸/V3.0 手册，不确认当前工程加载了 XDC、板上电压或实物已经测试。V3.0 手册条目要求邮箱验证/验证码；未提交任何资料、未取得 PDF。Pin1 实物朝向与整排对齐、Pin2 +5V 安全检查、视频 G0、T03 bitstream 与完整时序仍未关闭；当前不要求 Wong 插接或上电，待 HDMI artifact 可验证时给出精确步骤。G0 仍须明确单/双通道验收范围、采集/显示帧率、丢帧原因分类与缓冲所有权。显示器两个 HDMI 接口是显示器端口信息，不证明 FPGA 有 HDMI 输入能力。不要再以这些核对项为由重复索要板卡照片。

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

原综合在会话中断后留下排队/运行标记。本轮只读确认本阶段对应进程已不存在，保留 13 个已完成 IP；备份中断产物后仅恢复四个未完成 IP 和顶层。实际 `synth_1` 完成，但原补充检查器在综合阶段以 `UNRESOLVED_BLACKBOXES:dbg_hub` 标记未通过；该结果不是进程退出码。只读网表查询确认当时唯一黑盒为 `dbg_hub_CV`、Vivado 调试核心 `dbg_hub`，另有厂商 ILA；没有把它当作功能 IP 源码缺失，也没有白名单屏蔽检查。摘要 `report/stage3_synth_diag_20261003.json` 保留为综合阶段历史证据。

AMD UG908 说明 7-series 的 debug hub 在 `opt_design` 阶段由 Vivado 插入/实现，因此综合 DCP 中的 debug-hub blackbox 本身不能判作 `synth_design` 失败（[Debug Hub](https://docs.amd.com/r/en-US/ug908-vivado-programming-debugging/Debug-Hub)，[Implementing the Design Containing the Debug Cores](https://docs.amd.com/r/2025.1-English/ug908-vivado-programming-debugging/Implementing-the-Design-Containing-the-Debug-Cores)）。新隔离复验使用相同 SHA-256 的综合 checkpoint 副本，固定 Vivado 2026.1 / `xa7z020clg400-1I`，只运行到 `opt_design`：综合前 `dbg_hub=1`，优化后 `dbg_hub=0`、blackbox 查询为空；run 状态 `Not started place_design`、进度 40%。`.opt_design.end.rst` 存在，而 `.place_design.begin.rst`、`.route_design.begin.rst`、`.write_bitstream.begin.rst` 均不存在；此前的 `.vivado`、`.init_design` 和 `.opt_design.begin` 标记存在。工具退出码 0，日志报告 `opt_design completed successfully`、DRC 0 errors；完整摘要与证据哈希见 `report/stage3_debug_hub_opt_20261003.json`。这仅关闭“debug hub 在 opt_design 中解析”这一诊断项，不代表整个工程通过。探针随后增加了隔离根路径拒绝和空查询静默；路径矩阵/调用次序静态检查通过，但 Vivado 在脚本载入前启动失败，未用加固后哈希重放。报告区分记录了成功运行版与当前脚本哈希，不把前者冒充为后者的执行证据。

该综合网表的资源为 7724 Slice LUT、11924 Slice Registers，仅代表本次原厂视频参考，不是实现后资源或 CNN 资源。优化阶段有 13 个 critical warnings，其中 HDMI `SerialClk` 的 `Timing 38-249` 尚未解决；自动生成的 debug-hub `xsdbm` XDC 还报告对象/时钟变量缺失。普通 warning 的日志汇总由 link 后 9 条增至 opt 后 11 条，但 `runme.log` 仅定位到 9 条单项记录，另 2 条原因未定位，均保留为未关闭。已定位项包括 IP cache 路径过长（完整构建前缩短路径复验）、`axis_subset_converter` XCI 与上次写入内容不一致（需重新同步输出产物并复验 BD）、空目标列表的 `CDC-10` waiver（不算覆盖，须按最终时钟审计），以及 6 条 XPM 同源/目的时钟告警（须追踪端点后再判断）。未加载最终板卡 XDC，DRC 有 NSTD-1/UCIO-1 critical warnings 以及三个 RAM 异步控制 warning；没有降低 DRC 等级、没有 place/route/完整时序/bitstream 或板测通过。AXI ID 五处静态连接及五个检查器测试通过，仍不能代替事务验收。逐条证据和处置见上述 JSON 报告。

传感器适配入口 `software/sensor/ADAPTATION.md`：只保存厂商差异补丁及固定源准备脚本，不重新编写寄存器表。主机四组合各 968 cases / 847246 checks / 302 writes，303 项表值一致；独立 Reviewer 复验和冻结检查通过。证据 `report/stage3_sensor_host_20261003.json`。底层 `MasterRecvPolled` 仍有无限等待，主机进程 30 秒限时不等于 I2C 超时；真实 BSP/VDMA/显示集成未完成。

当前无需 Wong 插接摄像头或上电。官方 2023 手册与固定双目示例的 J10/AN5642 32 路映射及 LVCMOS33 已作静态源核验；AN5642 手册与原理图的 Pin1/2/3/19/36 定义相符，Pin8 仅有网名简写差异；CMOS1 为 Pin20–35。此证据不证明 `AX701020.3.0` 与 2023 图纸/V3.0 手册修订一致，不确认当前工程已加载 XDC、板上电压或实测通过。保留实物 PCB/手册修订绑定、Pin1 对齐、Pin2 +5V 安全核查、视频 G0、T03 bitstream/完整时序阻断；V3.0 手册因要求邮箱验证/验证码而未取得，未提交任何信息。待 HDMI artifact 完成并能安全验证时，再给出精确板测步骤，不要求重发板卡照片。仍须解决 HDMI 生成时钟与 debug-hub XDC 告警、普通 warning 清单、底层接收截止时间、缓存/缓冲所有权、视频背压/复位及帧行像素观测。G0/G3/G4/G5 尚未通过。
2026-10-03 时钟候选隔离复验 `tmp/s3clkfix01` 在 Vivado 2026.1 启动前因无有效许可证退出（exit 42）；该次 Tcl 未执行，尚未验证移除 `PixelClk → SerialClk ×5` 候选约束后的时钟树，不能标记为修复通过。错误日志 `tmp/s3clkfix01/attempt01/launcher.stderr.log`，SHA-256 `475C270DA07EE18FCE7B94909F3E6BE6F21815FADA3348300FA2E383AFAC3762`。AMD 自 2026.1 起要求 Vivado 启动前有可用授权；BASIC 免费年许可覆盖 7 Series/Zynq-7000，但每年须续期；本机尚无可用授权，未代 Wong 登录账号或配置许可证。[AMD Vivado 2026.1 授权说明](https://docs.amd.com/r/en-US/ug973-vivado-release-notes-install-license/Supported-Devices-and-Features)、[许可分级与设备支持](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html)。BASIC 的仿真/ChipScope 调试功能有限，工程所需调试功能仍需按特性表确认。
显示器标称 1920×1080。固定官方 AX7020 源 `course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/display_ctrl/vga_modes.h` 定义 `VMODE_1920x1080`（`1920x1080@60Hz`），可作为首次 HDMI 测试模式候选，而非 260Hz；这不证明当前工程已有对应时序/bitstream，也不证明显示器实物接受该模式。正式采集/显示分辨率、帧率与缩放/丢帧语义仍须在视频 G0 冻结。

AXI4-Stream 背压适配 S3-VAXIS-01：WinPS 5.1 策略自测 5/5 通过；真实厂商顶层 host 仿真 `xvlog/xelab/xsim` 均退出 0，12 beats、6 个停顿周期、12 次 FIFO 弹出。launcher 退出码缺失或读取失败时，即使 sentinel 为 0 也会 fail-closed。结果及源码哈希见 `report/stage3_vaxis01_host_20261003.json`；原始日志留在本地 `tmp`。该回归使用同钟 FWFT mock，不证明异步 CDC 或板级行为。

## 2026-10-26 TIMING-36 隔离工程实现复核

阶段3 新 RunId `report/evidence/S3-T05/t05_timing36_project_impl_20261026_r01/` 的 XDC 对象查询返回 0，脚本在 reset/synth 前安全退出；不代表设计实现失败。后续 R02 在 `tmp/s3r06/t04_sof_fix_20261020_r01/` 的新副本中，仅从本地 `rgb2dvi_clocks.xdc` 及生成副本删除错误的 `PixelClk → SerialClk ×5` 声明，重新生成 BD targets、完整综合和 route，再生成 bitstream。独立复审确认 TIMING-36/30=0、`SerialClk` 保留自动时钟 `I=2.000 ns`；证据及归档输入/输出位于 `report/evidence/S3-T05/t05_timing36_project_impl_20261026_r02/`，bitstream SHA-256 `6b23e209effd55a440447c59608f76bbb03cd4f06b3832f0777843cc54a67b01`。

该结果只验证隔离副本，未修改正式工程/IP 源、未应用或合并 `board/stage3/hardware/hdmi_clock_relation_candidate.patch`、未烧录/板测，不能称为正式修复或阶段冻结。路由后仍有 TIMING-17=240、TIMING-18=1、TIMING-9=1、DRC 8 warnings；STA 有 `no_clock=240`、520 个未约束端点、9 个缺失输入延迟和 5 个缺失输出延迟。因此完整时序签核、I/O delay 和 G5 仍未通过。
