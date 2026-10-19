# S3-T01 厂商工程精读调查报告（14_vdma_hdmi_out / 22_ov5640_single）

- RunId：`survey_20261020_r01`；时间：2026-10-20（UTC+8）
- 任务性质：**只读调研**。未写业务代码、未启动 Vivado/Vitis、未接板、未 git add/commit。
- 唯一写入：本目录 `report/evidence/S3-T01/survey_20261020_r01/`。
- 写前核验：`git -C D:\codex-worktrees\dbdf rev-parse --show-toplevel` → `D:/codex-worktrees/dbdf`，分支 `codex/stage3-video`，HEAD `896e6c7a6bae9571303cd65e08c6176c6baebd12`。
- 来源（只读）：`tmp/stage3_reference/AX7020_2023.1`。其自带 `.git` 的 `HEAD` = `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327`（"V1.01"，2024-02-23），`git status` 干净。**注意**：该提交在 dbdf 工作树对象库中不存在（`bad object`），因 `tmp/` 被 `.gitignore` 忽略、属文件副本。故"固定提交"以该来源树自身 `.git` 为准。
- 标注约定：`[已读]` = 实际读了源文件/目录并给出路径行号；`[未验]` = 推测，未跑工具验证。

---

## 1. `14_vdma_hdmi_out` 构建流程

### 1.1 入口与从零到比特流的确切序列

入口 `Vivado/auto_create_project/create_project.bat`：`CALL D:\Xilinx2023.1\Vivado\2023.1\bin\vivado.bat -mode batch -source create_project.tcl`。
**该 .bat 硬编码 `D:\Xilinx2023.1`**（本机不存在），不能直接运行。 `[已读]`

`create_project.tcl`（96 行）执行序列，路径变量先算出：`tclpath`=`auto_create_project`，`cd ..`→`projpath`=`Vivado`，再 `cd ..`→`Vitispath`=`14_vdma_hdmi_out`；`bdname`=`design_1`（L30–36）。 `[已读]`

| 步骤 | 行 | 命令要点 |
|---|---|---|
| 建工程 | L39 | `create_project -force vdma_hdmi_out $projpath/vdma_hdmi_out -part xc7z020clg400-2` |
| 建 fileset | L41–56 | `sources_1` / `constrs_1` / `sim_1`；`file mkdir` srcs 下 `ip`/`new`/`bd`/`constrs_1/new`/`sim_1/new` |
| 自定义 IP 库 | L58–59 | `set_property ip_repo_paths $tclpath/my_ip`；`update_ip_catalog` |
| 建 BD | L62 | `create_bd_design design_1` |
| 打开 BD | L64 | `open_bd_design <proj>.srcs/sources_1/bd/design_1/design_1.bd` |
| PS | L65–67 | `create_bd_cell -vlnv xilinx.com:ip:processing_system7:5.5`；`source ps_config.tcl`；`set_ps_config processing_system7_0` |
| PL | L68 | `source pl_config.tcl`（**平铺脚本，无 proc，直接建 cell/连线/分配地址**） |
| 收尾 | L69–78 | `regenerate_bd_layout`；`validate_bd_design`；`save_bd_design`；`make_wrapper -top`；`add_files` 包装器；`set_property top design_1_wrapper` |
| 约束 | L82 | `add_files -fileset constrs_1 -copy_to .../constrs_1/new -force [glob src/constraints/*.xdc]` |
| **自动综合/实现** | L84–86 | `launch_runs synth_1 impl_1 -jobs 5`；`wait_on_run synth_1`；`wait_on_run impl_1` |
| **再跑一遍非工程流程** | L87–91 | `synth_design -top design_1_wrapper`；`opt_design`；`place_design`；`route_design`；`write_bitstream -force <proj>.runs/impl_1/design_1_wrapper.bit` |
| 导出 XSA | L93 | `write_hw_platform -fixed -include_bit -force -file $Vitispath/Vitis/design_1_wrapper.xsa` |
| 复制 bit | L94 | `add_files -fileset sources_1 -copy_to $projpath`（把 `.bit` 拷到 `Vivado/`） |

`ps_config.tcl`（594 行）= 单个 `proc set_ps_config {bd_cell_name}`（L28），L29–593 为一个巨型 `set_property -dict [...]` 施加到 `[get_bd_cells $bd_cell_name]`（L593），L594 收 `}`。 `[已读]`

### 1.2 会创建的目录与产物

- 工程：`Vivado/vdma_hdmi_out/`，含 `vdma_hdmi_out.srcs/{sources_1,constrs_1,sim_1}`、`.gen`、`.runs`、`.cache`。
- 产物：`Vivado/design_1_wrapper.bit`、`Vitis/design_1_wrapper.xsa`（模板中已各存在一份，来自厂商 2023.1 构建）。 `[已读]`

### 1.3 IP VLNV 与版本（全部来自 pl_config.tcl / create_project.tcl） `[已读]`

- PS：`xilinx.com:ip:processing_system7:5.5`（L65 create_project.tcl）
- 自定义：`digilentinc.com:ip:axi_dynclk:1.0`（pl L40）、`digilentinc.com:ip:rgb2dvi:1.3`（pl L43）
- 标准：`proc_sys_reset:5.0`×2（L52/L55）、`smartconnect:1.0`（L58）、`axi_vdma:6.3`（L63）、`axi_interconnect:2.1`（L76）、`v_axi4s_vid_out:4.0`（L81）、`v_tc:6.2`（L90）、`xlconcat:2.1`（L99）
- 接口：`digilentinc.com:interface:tmds_rtl:1.0`、`xilinx.com:interface:iic_rtl:1.0`、`xilinx.com:interface:ddrx_rtl:1.0`、`xilinx.com:display_processing_system7:fixedio_rtl:1.0`
- `my_ip/tmds_v1_0/` **不是 IP**，只有 `tmds.xml` + `tmds_rtl.xml`，是 `digilentinc.com:interface:tmds(_rtl):1.0` 总线定义（vendor=`digilentinc.com`, library=`interface`）。 `[已读]`
- 关键模块参数：`axi_vdma_0` = 仅 MM2S（`c_include_s2mm=0`）、`c_m_axis_mm2s_tdata_width=24`、`c_mm2s_genlock_mode=1`、linebuffer 4096、burst 16；`v_axi4s_vid_out_0` `C_ADDR_WIDTH=11`、`C_HAS_ASYNC_CLK=1`。 `[已读]`

### 1.4 约束

仅 1 个：`src/constraints/hdmi_out.xdc`（20 行，1188 B，SHA-256 前 16 = `D8FD1B1AD450BC44`）。TMDS：clk_p=N18、data_p[0..2]=V20/T20/N20（仅约束 `_p`，`_n` 只给 IOSTANDARD TMDS_33，靠差分自动配对）；`hdmi_oen`=V16；`hdmi_ddc_scl_io`=R18、`hdmi_ddc_sda_io`=R16（LVCMOS33）。L13–14 的 `hdmi_hpd` 被注释掉。**无 `create_clock`**。

### 1.5 Vitis 结构

`build_vitis.bat` → `xsct build_vitis.tcl`（同样硬编码 2023.1）。`build_vitis.tcl`：`setws $projpath`；`set xsaName design_1_wrapper`；`appName vdma_hdmi`；`platform create -hw .../design_1_wrapper.xsa -proc ps7_cortexa9_0 -os standalone -arch 32-bit`；`importsources .../zynq_fsbl -path src/fsbl`；`app create -template "Empty Application"`；`importsources -path src/vdma_hdmi`；`platform generate`；`sysproj build`。
源码：`src/fsbl/fsbl_debug.h` + `src/vdma_hdmi/{main.c, display_demo.h, display_ctrl/*, dynclk/*, pic_800_600.h}`；**入口 `main()` 在 `main.c`**。 `[已读]`

---

## 2. `22_ov5640_single` 构建流程与差别

`create_project.tcl` 与 14 的 **唯一差别**是 L2 注释与 L30 `set proj_name "ov5640_single"`（`git diff --no-index` 确认，共 2 行）。**构建流程、脚本顺序、综合/实现副作用完全相同**。 `[已读]`

### 2.1 相对 14 的变化

- **约束**：新增 `an5642.xdc`（2116 B）、`system.xdc`（158 B，`BITSTREAM.GENERAL.COMPRESS TRUE` / `CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3`）；`hdmi_out.xdc` 缩为 822 B（去掉 `hdmi_ddc` 两行，因 DDC 改用 PS IIC 接摄像头）。
- **PL 新增 IP**：`www.alinx.com.cn:user:alinx_ov5640:5.4`（pl L60）、`xilinx.com:ip:axi_gpio:2.0`（`cmos_rst`，1 位全输出）、第二个 `axi_vdma:6.3`（`axi_vdma_1`，**仅 S2MM**、`c_m_axi_s2mm_data_width=64`、linebuffer 4096、burst 128、`c_use_s2mm_fsync=2`）、`axis_subset_converter:1.1`（16→24 位重映射）、`xlconstant:1.1`。
- **`axi_smc`(smartconnect) → `axi_mem_intercon`(axi_interconnect 2.1，2 SI/1 MI)**；`ps7_0_axi_periph` → `processing_system7_0_axi_periph`，`NUM_MI` 3→5。
- `axi_vdma_0` 参数变：`c_mm2s_genlock_mode` 1→0、linebuffer 4096→512、burst 16→128。
- `v_axi4s_vid_out_0`：`C_ADDR_WIDTH` 11→12，新增 `C_S_AXIS_VIDEO_DATA_WIDTH=8`、`C_S_AXIS_VIDEO_FORMAT=2`。
- 新增 BD 端口：`cmos1_d[9:0]`、`cmos1_href`、`cmos1_pclk`、`cmos1_vsync`、接口 `cmos1_i2c`(iic)、`cmos_rstn`(gpio)；`FCLK_CLK1` 域承载摄像头 AXIS 与 S2MM。
- **PS 侧差异**（`ps_config.tcl`）：`PCW_FPGA1` 142→150、`PCW_FPGA2` 50→25、`PCW_APU_PERIPHERAL_FREQMHZ` 666.666666→767、`PCW_GP0/GP1_EN_MODIFIABLE_TXN` 1→0、MIO 1/2/3/4/5/6/40–45 slew slow→fast。**DDR 输入参数亦不同**：`PCW_PACKAGE_DDR_BOARD_DELAY0..3`、`PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_*`、`PCW_UIPARAM_DDR_CLOCK_*_PACKAGE_LENGTH`、`PCW_UIPARAM_DDR_DQS_*_PACKAGE_LENGTH`（见 §4-R2）。相同项：DDR 型号 `MT41J256M16 RE-125`、`PCW_UIPARAM_DDR_FREQ_MHZ 533.333333`、`PCW_PACKAGE_NAME clg400`、`PCW_USE_S_AXI_HP0 1`。 `[已读]`
- `PCW_ACT_*` 在 14/22 中**逐值相同**（如 `ACT_FPGA1=142.857132`、`ACT_APU=666.666687`），而请求值不同 → 这些 `ACT_*` 是模板带过来的**陈旧快照值**，由 Vivado 施加时重算，不应作为事实依据。 `[已读]`
- **Vitis**：`appName an5642_single`；源码 `src/an5642_single/{display_demo.c, display_demo.h, ov5640.c/.h, vdma.c/.h, i2c/PS_i2c.c/.h, display_ctrl/*, dynclk/*}`。**无 `main.c`，入口 `main()` 在 `display_demo.c`**。 `[已读]`
- `注意.txt`（GBK）= "本例程使用双目摄像头模块AN5642" — 即 22 用 AN5642 双目模组只做单通道。
- `my_ip/i2c_extender/`（component.xml 23691 B）在 22 的仓库中存在，但 **pl_config.tcl 未实例化它**（diff 中无 `i2c_extender` cell）→ 疑似冗余，待核。 `[已读]`

### 2.2 摄像头约束 `an5642.xdc` 关键内容（39 行，SHA-256 前 16 `87A0FA21F88EE073`） `[已读]`

- 引脚：`cmos1_i2c_sda_io`=T16、`cmos1_i2c_scl_io`=T15；`cmos1_d[9:0]` = V18,V17,**T14(d5)**,V13,U13,W13,V12,U12,T12,T10（按 d9…d0）；`cmos1_pclk`=T11、`cmos1_href`=A20、`cmos1_vsync`=B19、`cmos_rstn_tri_o[0]`=B20。
- 全部 `IOSTANDARD LVCMOS33`（L19–34）；`cmos1_i2c_scl_io`/`sda_io` 加 `PULLUP true`（L36–37）。
- L39：`set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]`。
- **PCLK 处理：整个板级约束中没有 `create_clock`**。全树唯一的 `create_clock` 是 IP 内部的 `rgb2dvi_ooc.xdc:1`（`create_clock -period 6.060 [get_ports PixelClk]`，OOC 专用）。故 `cmos1_pclk` 域**处于未约束状态**；`CLOCK_DEDICATED_ROUTE FALSE` 表明该时钟未走专用时钟布线资源。

### 2.3 `alinx_ov5640.v` 内部（7099 B，214 行） `[已读]`

- `cmos_pclk` 是真实时钟域：L54/67/85/112/136 均为 `always @(posedge cmos_pclk)`；L96 取 `cmos_d[9:2]`（8 位）经 `cmos_8_16bit` 转 16 位。
- 跨域：`xpm_fifo_async`（L164–213，`BUFFER_DEPTH` 参数、写侧 `cmos_pclk` L187、读侧 `m_axis_video_aclk` L197）；`axis_reset`/`fifo_ready_maxis` 标 `ASYNC_REG`（L47–48）。
- 复位逻辑用 `cmos_pclk` 计数到 200_000_000 / 100_000_000（L56/L74）才放开 → **上电后需约 2 s 才出画**。
- **L146–158：`if(DEBUG_OV5640)` 例化 `ila_0 ila_0_m0(.clk(cmos_pclk), probe0..5)`**；`component.xml` L339/L415 中 `DEBUG_OV5640` 默认 `true`、`BUFFER_DEPTH` 默认 `2048`（.v 默认 4096，以 component.xml 生效值 2048 为准）。`ila_0.xci`（412 KB，C_DATA_DEPTH=1024、C_NUM_OF_PROBES=6）与 `ila_0.xml`（4.7 MB）为**预生成 2023.1 产物**。

---

## 3. part 改动点（核心结论）

### 3.1 `[已读]` 结论：**厂商缓存源本身已经是 `xc7z020clg400-2`，无需改任何文件**

- `14`/`22`/`23` 三个 `create_project.tcl` 的 **L39 全部为** `-part xc7z020clg400-2`。
- 对全树 `*.tcl` 做 `xa7z020|XA7Z020|clg400|azynq|zynq` 检索：**没有任何 `XA7Z020` 或 `xa7z020` 写法**；`clg400` 仅出现在 `ps_config.tcl` 的 `CONFIG.PCW_PACKAGE_NAME {clg400}`（14 L419、22 L419、23 L425）。
- 因此"把 part 改成 `xc7z020clg400-2`"在**当前固定来源上是一个空操作**。

### 3.2 `[已读]` XA/-1I 是**前序工作人为覆盖**的，不是厂商模板写法

- `scripts/s3_validate_vendor_bd.tcl` **L17** `expected_commit fcf1e4a2...`；**L36** `get_parts -quiet xa7z020clg400-1I`，**L37–38** 强制唯一匹配否则 `EXACT_XA_PART_NOT_AVAILABLE`；**L66** 用该 part 建工程；**L44** 断言 `family ne "azynq"` 即报错。
- `scripts/s3_probe_vendor.tcl` L25：未找到唯一 `XA7Z020/CLG400/-1I` 即报错，"禁止回退 XC 或 -2"。
- `board/stage3/README.md` **L113**：原厂未修改 IP 在 XA/-1I 上失败 `BD 5-683`，`axi_dynclk:1.0` 不支持当前 part；Vivado 查询目标家族为 `azynq`；L118 的 `azynq_metadata` 只在新副本的三个 `component.xml` 注入 `azynq/Pre-Production`。
- 因果链：**人为指定 XA 器件 → family=azynq → 自定义 IP 未声明 azyqn → BD 5-683**。与厂商模板无关。

### 3.3 `[已读]` 换回标准 zynq 器件后，**那些元数据补丁不再需要，且不应保留**

四个自定义 IP 的 `component.xml` 家族声明（全树 `xilinx:family` 检索）：

| IP | 文件:行 | 家族 |
|---|---|---|
| `axi_dynclk_v1_0` | `my_ip/axi_dynclk_v1_0/component.xml:809` | `zynq`（另有 artix7/kintex7/virtex7 等） |
| `rgb2dvi_v1_3` | `my_ip/rgb2dvi_v1_3/component.xml:661` | `zynq` |
| `ov5640_ip`(alinx_ov5640:5.4) | `my_ip/ov5640_ip/component.xml:426` | `zynq`（**仅此一条**） |
| `i2c_extender` | `my_ip/i2c_extender/component.xml:507`（另有 L509 `azynq`） | `zynq` + `azynq` |

判断依据：`D:\Xilinx\2026.1\Vivado\data\installed.devices` 中 `{"devices":[... "xc7z020" ...],"name":"zynq"}` 与 `{"devices":["xa7z030","xa7z010","xa7z020","xa7z020_LR"],"name":"azynq"}`；`data/parts/xilinx/zynq/devint/zynq/xc7z020/clg400` 目录存在，`devint/zynq` 下有 `delayL-1/-1L/-2/-2L/-3.dst`（故 `-2` 合法），而 `devint/azynq` 只有 `delayL-1I/1Q`。
→ 标准 `xc7z020` 家族 = `zynq`，与四个 IP 的原生声明**匹配**，BD 可实例化；再注入 `azynq` 是**写入错误家族元数据**，应全部丢弃，不得带入阶段 3 正式工程。 `[已读]`

---

## 4. 风险清单

- **R1 IP 兼容性（目录层通过）** `[已读]`：11 个标准 VLNV 的**精确版本目录全部存在**于 `D:\Xilinx\2026.1\Vivado\data\ip\xilinx\`：`processing_system7_v5_5`、`proc_sys_reset_v5_0`、`smartconnect_v1_0`、`axi_vdma_v6_3`、`axi_interconnect_v2_1`、`v_axi4s_vid_out_v4_0`、`v_tc_v6_2`、`xlconcat_v2_1`、`xlconstant_v1_1`、`axi_gpio_v2_0`、`axis_subset_converter_v1_1`。**目录存在 ≠ 2026.1 下 BD/综合/时序通过** `[未验]`。
- **R2 DDR 输入参数两工程不一致** `[已读]`：14 与 22 的 `PCW_PACKAGE_DDR_BOARD_DELAY*` / `PCW_UIPARAM_DDR_*_PACKAGE_LENGTH` 数值不同（例：`BOARD_DELAY0` 0.075 vs 0.080；`CLOCK_0_PACKAGE_LENGTH` 76.428 vs 54.563）。同一块 AX7020 出现两套 DDR 长度补偿值，**哪一套匹配实际 PCB 未定**；T03 只出 HDMI 画面可回避，T04/T05 用 DDR 缓冲前必须先定论。
- **R3 `cmos1_pclk` 无 `create_clock`** `[已读]`：该域不被时序分析，且 `CLOCK_DEDICATED_ROUTE FALSE`。T04 需补 PCLK 约束（或改用 `set_clock_groups` 正确声明异步），否则时序"通过"无意义。
- **R4 `DEBUG_OV5640=true` → 内嵌 ILA** `[已读]`：会引入 `ila_0` 与 `dbg_hub`，正对应 `board/stage3/README.md` L138 的历史 `UNRESOLVED_BLACKBOXES:dbg_hub`。T03/T04 应显式设 `DEBUG_OV5640=false` 或明确处理调试核。
- **R5 自动脚本副作用严重** `[已读]`：L39 `create_project -force` 会**覆盖同名工程**；L84–86 自动综合+实现，L87–91 **再重复**跑一遍 synth/place/route + `write_bitstream`，L93 自动出 XSA。**禁止**对厂商树或长路径直接执行该脚本。
- **R6 Windows 路径长度** `[已读]`：厂商模板工程根绝对长 **112** 字符，`.gen` 深层实测达 **214** 字符；MAX_PATH=260，深层生成物（IP sim netlist 等）有触顶风险。必须在短路径（如 `D:\codex-worktrees\dbdf\tmp\s3t03_<runid>\`）复制后构建。
- **R7 .bat 不可用** `[已读]`：`create_project.bat`/`build_vitis.bat` 硬编码 `D:\Xilinx2023.1`，本机为 `D:\Xilinx\2026.1`；必须绕过 .bat，走 2026.1 `vivado.bat` 且只 `source ps_config.tcl` + `pl_config.tcl`。
- **R8 预生成 IP 产物跨版本** `[已读]`：`ov5640_ip` 内含 2023.1 生成的 `ila_0.xci`(412 KB)+`ila_0.xml`(4.7 MB)；2026.1 打开会触发 IP 升级流程，可能产生迁移提示与产物差异。`[未验]`
- **R9 `i2c_extender` 冗余** `[已读]`：存在于 22 的 `my_ip` 但 pl_config 未实例化 → 迁移时可剔除（需 T04 确认是否需要）。
- **R10 许可 `[未验]`**：`D:\Xilinx_licenses\basic_only.lic`（1211 B）含 `Vivado_Basic_Package` 及 `Vivado_Simulation`/`Vivado_Synthesis`/`Vivado_Implementation` 增量，到期 2027.08。Zynq-7020 的 synth/impl/bitstream 是否被该 BASIC 档覆盖，**须由工具实跑确认**（工作树已有未提交的 `scripts/s3_license_part_probe.tcl`，非本报告产出）。`XILINXD_LICENSE_FILE` 环境变量当前为空。

---

## 5. 未知项

1. `xc7z020clg400-2` 在本机 BASIC 许可下 `synth/place/route/write_bitstream` 是否全通 `[未验]`（只能实跑）。
2. 2026.1 对 `axi_dynclk:1.0` / `rgb2dvi:1.3` / `alinx_ov5640:5.4` 三个 2023.1 自定义 IP 的 BD 实例化与 OOC 综合是否成功 `[未验]`。
3. 14 与 22 两套 DDR 长度补偿值孰为实际 PCB 匹配值 `[未验]`，需厂商手册/PCB 资料定论。
4. `PCW_FPGA1` 请求 150 而 `ACT_FPGA1` 陈旧值 142.857132，重算后实际 FCLK1 频率 `[未验]`（影响摄像头 AXIS/VDMA 时钟预算）。
5. AN5642/OV5640 DVP 的 PCLK 频率与像素时序是否与 `axis_subset_converter` 重映射及 VDMA S2MM 参数匹配 `[未验]`。
6. 模板中 `design_1_wrapper.bit`(4045676 B) 与 `.xsa`(540610 B) 是 2023.1 产物，**不能作为阶段 3 交付**，仅作结构参照。

---

## 6. 给总控的下一步建议

1. **不要再做 part 改写与 azynq 元数据补丁**：二者对当前固定来源都不需要，且 `azynq` 注入属错误元数据，应在正式工程创建时明确排除。
2. **不要在厂商树内构建**：复制 `my_ip` 与 `src/constraints`、`ps_config.tcl`、`pl_config.tcl` 到短路径隔离目录（如 `tmp/s3t03_<runid>/`），自写最小 Tcl：`create_project -part xc7z020clg400-2` → `set_property ip_repo_paths` → `update_ip_catalog` → `create_bd_design` → PS cell → `source ps_config.tcl`+`set_ps_config` → `source pl_config.tcl` → `validate/save` → `make_wrapper` → `add_files *.xdc` → `set_property top`。**不要 source `create_project.tcl`**，避免 R5。
3. T03「HDMI 独立画面」建议**先只迁 14 的 HDMI 路径**（依赖最少：`axi_dynclk`+`rgb2dvi`+`v_tc`+`v_axi4s_vid_out`+`axi_vdma`+`smartconnect`），先证明 2026.1 能出比特流与画面，再叠加 22 的摄像头路径。
4. 先跑许可/器件探针（`scripts/s3_license_part_probe.tcl`）拿到 `xc7z020clg400-2` 的 synth→bitstream 结论，再决定是否需要 Wong 追加授权。
5. 为 T04 预备：PCLK 约束方案、`DEBUG_OV5640=false`、DDR 参数取值定论，三项均为前置未知项。

---

## 7. 关键文件哈希（SHA-256 前 16 hex）与路径

根：`tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/`

| 文件 | 14_vdma_hdmi_out | 22_ov5640_single |
|---|---|---|
| `Vivado/auto_create_project/create_project.tcl` | `D5F7D288AE76A0CA` | `E67A7862527FDF42` |
| `Vivado/auto_create_project/ps_config.tcl` | `E0F8D41E1948B9B1` | `1C5D71CBDA919256` |
| `Vivado/auto_create_project/pl_config.tcl` | `093F95520FB5D8AB` | `B7BE18E09327C411` |
| `src/constraints/hdmi_out.xdc` | `D8FD1B1AD450BC44` | `71EDC7805065612A` |
| `src/constraints/an5642.xdc` | — | `87A0FA21F88EE073` |
| `src/constraints/system.xdc` | — | `08ECF39E700BDFF5` |
| `create_project.bat` | `49FA4E7B82D43B57` | `49FA4E7B82D43B57` |
| `my_ip/axi_dynclk_v1_0/component.xml` | `C487D32040C34F9E` | `C487D32040C34F9E` |
| `my_ip/rgb2dvi_v1_3/component.xml` | `74A54532188E0BEA` | `74A54532188E0BEA` |
| `my_ip/ov5640_ip/component.xml` | — | `2E5B590035C74C96` |
| `my_ip/i2c_extender/component.xml` | — | `642B49AD834BB1A5` |

本次实际读取/比对的文件（区分"全文读"与"差异比对"）：

- **逐行全文读**：`14` 的 `create_project.tcl`(96 行)、`pl_config.tcl`(135 行)；`22` 的 `create_project.tcl`(经 `git diff --no-index` 全量比对，仅 2 行差异)、`an5642.xdc`(39 行)、`hdmi_out.xdc`、`system.xdc`、`alinx_ov5640.v`(214 行)、`注意.txt`(GBK)、`build_vitis.tcl`×2、`create_project.bat`×2、`D:\Xilinx_licenses\basic_only.lic`、`scripts/s3_license_part_probe.tcl`。
- **差异比对（非全文）**：`ps_config.tcl` 14↔22（`--unified=1` 全部变更 hunk；另对 22 单独读取 proc 头 L28–63、尾部 L583–594、关键 PS 行）；`pl_config.tcl` 14↔22（`--unified=0` 全部变更 hunk）。
- **节选/字段检索**：`ov5640_ip`、`i2c_extender`、`axi_dynclk_v1_0`、`rgb2dvi_v1_3` 的 `component.xml`（`xilinx:family` 段 + ov5640 的 DEBUG/BUFFER 参数段）；`tmds.xml`/`tmds_rtl.xml` VLNV 段；`ila_0.xci` 型号参数段；`14` 的 `hdmi_out.xdc` 全文(20 行)。
- **仅字节哈希（未读内容）**：§7 表中列出的全部文件。
- **其他**：`board/stage3/README.md`(L100–139)、`scripts/s3_validate_vendor_bd.tcl`(L1–100)、`scripts/s3_probe_vendor.tcl`(L25)、`D:\Xilinx\2026.1\Vivado\data\installed.devices`、`data/ip/xilinx/*` 与 `data/parts/xilinx/zynq/**` 目录枚举、`23_ov5640_dual` 的 `create_project.tcl` L39 与 `ps_config.tcl` L425（仅 part/CLG400 行）。
- **未读**：`23_ov5640_dual` 其余文件、`Hardware/` 目录、Vitis 源码正文（仅列目录与定位 `main()`）。