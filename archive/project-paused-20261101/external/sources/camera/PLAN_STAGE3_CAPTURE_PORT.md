# 阶段3 采集子图移植方案（build11h）· 只写不跑

> 触发条件：**仅当 build11g 仍失败**（r52 判据：`0x43D60000+0x00` bit0=1 但 `CR` 写 1 读回仍含 bit2）。
> 参考源（已在板上验证可用）：`D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r01\vendor_src\pl_config.tcl`
> 即厂商 `22_ov5640_single` 的 BD 生成脚本（171 行，完整）；对应 BD：`...\project\ov5640_single.srcs\sources_1\bd\design_1\design_1.bd`
> 本次已产出可执行脚本：`bd_p3r_b11h.tcl`（**未运行**）

## 1) 参考设计的采集子图完整清单（逐字取自 pl_config.tcl）

### 1.1 单元
| 单元 | VLNV | 关键参数（原文） |
|---|---|---|
| `alinx_ov5640_0` | `www.alinx.com.cn:user:alinx_ov5640:5.4` | **不设参数**（用默认） |
| `axis_subset_converter_0` | `xilinx.com:ip:axis_subset_converter:1.1` | `M_HAS_TKEEP 1`、`M_HAS_TLAST 1`、`M_TDATA_NUM_BYTES 3`、`M_TUSER_WIDTH 1`、`S_HAS_TKEEP 1`、`S_HAS_TLAST 1`、`S_TDATA_NUM_BYTES 2`、`S_TUSER_WIDTH 1`、`TDATA_REMAP {tdata[4:0],3'b000,tdata[10:5],2'b00,tdata[15:11],3'b000}`、`TKEEP_REMAP {1'b1,tkeep[1:0]}`、`TLAST_REMAP {tlast[0]}`、`TUSER_REMAP {tuser[0:0]}` |
| `axi_vdma_1`（S2MM） | `xilinx.com:ip:axi_vdma:6.3` | `c_include_mm2s 0`、`c_include_s2mm_dre 1`、`c_m_axi_s2mm_data_width 64`、`c_num_fstores 1`、`c_s2mm_genlock_mode 0`、`c_s2mm_linebuffer_depth 4096`、`c_s2mm_max_burst_length 128`、**`c_use_s2mm_fsync 2`**（**未设** `C_S2MM_SOF_ENABLE`/`C_FLUSH_ON_FSYNC` ⇒ 默认 **1**） |
| `axi_mem_intercon` | `xilinx.com:ip:axi_interconnect:2.1` | `NUM_MI 1`、`NUM_SI 2`、`SYNCHRONIZATION_STAGES 2`（S00=MM2S 显示、S01=S2MM 相机 → M00 → `S_AXI_HP0`） |

### 1.2 连接（原文行号）
```
L153 alinx_ov5640_0/m_axis_video        -> axis_subset_converter_0/S_AXIS
L158 axis_subset_converter_0/M_AXIS    -> axi_vdma_1/S_AXIS_S2MM
L157 axi_vdma_1/M_AXI_S2MM             -> axi_mem_intercon/S01_AXI
L154 axi_mem_intercon/M00_AXI          -> processing_system7_0/S_AXI_HP0
L164/L167 vdma_0/vdma_1 的 S_AXI_LITE  <- processing_system7_0_axi_periph/M00/M03
L196/L197 地址：axi_vdma_0=0x43000000、**axi_vdma_1=0x43010000**（各 0x10000）
L200/L201 数据空间：各 `Data_* -> HP0_DDR_LOWOCM` 0x00000000 + 0x40000000
```

### 1.3 时钟（参考：FCLK0=100 MHz、FCLK1=150 MHz）
```
L182 FCLK_CLK0(100M) -> axi_vdma_0/s_axi_lite_aclk, axi_vdma_1/s_axi_lite_aclk,
                         axi_periph/*, cmos_rst, v_tc, rst_100M/slowest_sync_clk
L183 FCLK_CLK1(150M) -> alinx_ov5640_0/m_axis_video_aclk, axi_mem_intercon/*,
                         axi_vdma_0/m_axi_mm2s_aclk+m_axis_mm2s_aclk,
                         axi_vdma_1/m_axi_s2mm_aclk+s_axis_s2mm_aclk,
                         axis_subset_converter_0/aclk, v_axi4s_vid_out_0/aclk,
                         rst_150M/slowest_sync_clk, S_AXI_HP0_ACLK
```

### 1.4 复位（参考）
```
L184 FCLK_RESET0_N -> rst_100M/ext_reset_in, rst_150M/ext_reset_in
L187 rst_100M/peripheral_aresetn -> axi_vdma_0/axi_resetn, **axi_vdma_1/axi_resetn**,
                                    axi_periph/*_ARESETN, cmos_rst, v_tc, axi_dynclk
L188 rst_150M/interconnect_aresetn -> axi_mem_intercon/ARESETN
L189 rst_150M/peripheral_aresetn  -> alinx_ov5640_0/m_axis_video_aresetn,
                                     axi_mem_intercon/{S00,S01,M00}_ARESETN
L192 xlconstant_1/dout(1) -> axis_subset_converter_0/aresetn
```
**要点：`axi_vdma_1/axi_resetn` 在参考里来自 AXI-Lite 时钟域（100M）的复位。**

## 2) 本工程与参考的差异（逐项）

| 项 | 参考 | 本工程 build11f | 是否影响 |
|---|---|---|---|
| VDMA IP 版本 | `axi_vdma:6.3` | `axi_vdma:6.3` | **相同**（"阶段3 用 v6.17"是驱动版本号，非 IP） |
| `c_use_s2mm_fsync` | **2** | **0**（build11a 改的） | 参数已偏离 |
| `C_S2MM_SOF_ENABLE` | 默认 1 | **0**（build11c 改的） | 参数已偏离 |
| `C_FLUSH_ON_FSYNC` | 默认 1 | **0**（build11c 改的） | 参数已偏离 |
| `axi_vdma_1/axi_resetn` | AXI-Lite 域(100M) | `rst_100`(数据面域，build11e 改的) | 域已偏离 |
| 数据面时钟 | FCLK1 **150 MHz** | FCLK1 **100 MHz** | 频率不同（带宽足够） |
| AXI-Lite 时钟 | FCLK0 100 MHz | FCLK0 50 MHz | 频率不同（时序正常） |
| 数据通道 | `axi_interconnect 2.1` → HP0 | `smartconnect(smc_vis)` → HP2 | 元件/端口不同 |
| 相机 VDMA 地址 | 0x43010000 | **0x43C60000** | 保持本工程（软件已适配） |
| 显示 VDMA | 同子图内 MM2S→HP0 | 独立 `vdma_0`→HP2 | 本工程既有，不动 |

## 3) build11h 脚本（已生成，未运行）

`bd_p3r_b11h.tcl` = **build11f 脚本 + 3 处回归参考值**（最小改动、最高命中率）：
1. `CONFIG.c_use_s2mm_fsync {2}`（L431）
2. 删除 `C_S2MM_SOF_ENABLE=0` / `C_FLUSH_ON_FSYNC=0` 覆盖 ⇒ 恢复默认 1
3. `axi_vdma_1/axi_resetn` 改接 `rst_all/peripheral_aresetn`（= 本工程 AXI-Lite 时钟域）
+ 自检打印：`P3R11H_CHECK FSYNC/SOF_EN/FLUSH/SG/DRE/TDATA_W`（期望 `2/1/1/0/1/24`）与 `P3R11H_NET axi_resetn`

**运行命令（等你指令）**
```bat
cd /d D:\tmp\lead\p3r_camera_20261031_r01
vivado -mode batch -notrace -log s5_p3r_build11h_vivado.log ^
       -journal s4d_p3r_b11h.jou -source bd_p3r_b11h.tcl -tclargs build
```
预估 **45–55 min**（无新 IP，仅参数/复位变化）。

## 4) 预期的"整段移植"加强版（build11i，若 11h 还不够）

若 11h 仍失败，则做**元件级**替换（真正"整段移植"）：
1. 新增 `axi_interconnect:2.1`（`NUM_MI=1/NUM_SI=1/SYNC_STAGES=2`，名 `axi_mem_cam`），`M00_AXI → ps7_0/S_AXI_HP2`（保持本工程用 HP2），复位 = `rst_100`
2. `axi_vdma_1/M_AXI_S2MM → axi_mem_cam/S00_AXI`（替换现在的 `smc_vis/S01_AXI`）
3. `axi_mem_cam/{ACLK,S00_ACLK,M00_ACLK}` = FCLK1；`{ARESETN,S00_ARESETN,M00_ARESETN}` = `rst_100`
4. 其余同 11h
预估 **50–60 min**（新增 1 个 IP，OOC 综合略增）。

## 5) 影响面评估

| 对象 | 影响 |
|---|---|
| 显示链（`vdma_0`+`s4d_0`+`pack_0`+`smc_vis`+`pc_hp2`） | **不动**（11h 只改相机 VDMA 参数与复位源）|
| PS7 配置（DDR 1 GiB、FCLK0/1、UART0/1、GPIO） | **不动** |
| 地址映射 | 相机 VDMA 保持 `0x43C60000`，观测寄存器 0x43C8..0x43D6 全保留 ⇒ **软件不用改** |
| 资源 | 11h ≈ build11f（LUT 29.8k/FF 23.2k/BRAM 43.5/DSP 158），无新 IP |
| 时序 | 预期 WNS ≥ +0.2（与 build11f 同量级）；11i 需重看 `pc_hp2`/`smc_vis` 周边 |
| 软件/ELF | `v29d`/`v27e` 可直接用（地址、ABI 不变） |
