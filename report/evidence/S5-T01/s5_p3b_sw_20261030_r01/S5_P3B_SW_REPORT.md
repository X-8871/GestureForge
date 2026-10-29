# S5 P3b-sw：HDMI 显示链 PS 侧显示软件报告

- 任务：阶段5 HDMI 显示链 · PS 侧显示软件（P3b-sw）
- 日期：2026-10-30（UTC+8）　版本：**r04**
  （r01 → r02：布局裁决落地、补 VTC 生成器初始化、帧存改 2；
   r02 → r03：帧缓冲迁出 must_not_access 禁区到 0x20000000、有界运行 180 帧 + `S5DISP RESULT=` 结果行；
   r03 → r04：**真实数据源适配**——结果块 ABI（0x20800000）+ raw 画面（0x12000000）+ 回退逻辑 + `src` 字段，
   `S5Sim_NextFrame` 降为回退路径）
- 边界：**离线编写 + 编译通过 + 主机端自检（渲染 PNG / 假寄存器堆跑寄存器序列）**。未接触板卡 / JTAG / COM4 / hw_server，未运行 Vivado，未修改 `w4` 仓库文件（只读引用），未 git 提交。
- 工作目录：`D:\tmp\lead\p3b_display_sw_20261030_r01\`

---

## 0. 结论摘要

| 项目 | 结果 |
|---|---|
| ARM 编译/链接 | **exit 0**（compile 0 / link 0 / size 0 / nm 0；警告 0） |
| ELF | `build/s5_display_app.elf`，**sha256 `acca2cf7e22c496e0e0c14d68830029b23ac3daccfaec1143ef6b766e4c8ce9d`**（重建可复现，同 sha） |
| ELF 大小 | **296,352 B**；text 44,868 / data 72 / bss 2,353,504（berkeley） |
| 真实数据源 | **已接入**：结果块 `0x20800000`（magic `0x53355253`）+ raw `0x12000000`（640×480 BGR888）；magic/valid 失败回退模拟源（`src:"sim"`），raw 全 0 回退测试图案（`src:"test"`）（§2.5/§2.6） |
| 回退判据 | `src` ∈ {real,sim,test}；`pass` 要求链路健康**且** `src≠sim`（test 回退算通过但保留 `reason`）；面板可见 `SRC`/`STALE`/`OVR`（§5.3） |
| 帧缓冲地址 | **A=`0x20000000`、B=`0x20384000`**，终点 `0x20708000`（**已迁出 `[0x12C08000,0x20000000)` 禁区**，§3.1） |
| 有界运行 + 结果行 | **已实现**：默认 180 帧或 60 s 先到者停机，结束打印单行 `S5DISP RESULT={...}`（失败带 `reason`），进度行 `S5DISP frame=` 独立（§5.3、§8.3） |
| VTC 生成器 | **已实现**（VTC 6.2，720p60）：12/12 寄存器回读校验 OK，负例可检出 MISMATCH（§2.4） |
| VDMA | **2 帧存**（与 BD `c_num_fstores=2` 一致），A/B 双缓冲，只写 0x5C/0x60 两个地址（§2.2） |
| 布局 | **已裁决：无重叠方案**（视频 `x=0..959` + 信息栏 `x=960..1279`），字面 160 黑边方案仅作实验分支（§3.2） |
| 主机渲染自检 | **PASS**，同一份绘图源码渲染出 10 张 1280×720 PNG（两套布局 ×5）+ 180 帧有界运行 → 示例 RESULT |
| 真实源自检 | **PASS**：合法块+fixture → `src:"real"`（含真实画面/框/面板 PNG）；magic 错 → `src:"sim"`+reason；raw 全 0 → `src:"test"`；stale 位 → 面板 STALE（§8.4） |
| 寄存器序列自检 | **PASS**（假寄存器堆跑 `vtc_ctrl.c` + `vdma_ctrl.c`：VTC 校验、负例、双缓冲 6 帧决策，§8.2） |
| VDMA 寄存器用法 | **有把握**：逐条来自本机 Vitis 2026.1 的 `axivdma_v6_17` 驱动源码（`xaxivdma_hw.h` + `xaxivdma_channel.c`），非 SG 写序列与驱动实现一一对应；题面里两处猜测已被纠正（§2.3） |
| 未验证 | 全部上板行为：VDMA 实际搬数、VTC 实际时序输出、rgb2dvi/TMDS、DDR 带宽、撕裂/闪烁；真实源只在主机用 fixture 验证，板上需生产端实际写结果块；`src:"sim"` 时 RESULT 的 fps/latency/age 为模拟值（§5.3） |

---

## 1. 交付物

| 文件 | 作用 | sha256 |
|---|---|---|
| `src/s5_display_app.c` | 绘图核心（纯函数）+ 模拟源（回退）+ 裸机 `main()`（VTC→测试图→VDMA→有界乒乓→真实源/RESULT） | `51164a14494ee64f9ffb024f7bf1ff283c924397c7c8b78bda8f4d6ea059bfcc` |
| `src/s5_display_app.h` | 布局/颜色/数据结构/API + 结果行契约（`S5RunStats` 含 `src`） | `456f6b9da5cf089f6cc96d7ce5f9e72cf133b94a8867c47fa00525897ecb7ab0` |
| `src/s5_result_abi.h` | **结果块 ABI**（0x20800000）+ raw 画面（0x12000000）+ 编译期尺寸断言 | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c` |
| `src/s5_real_source.h/.c` | 真实源：块解析/一致性检查、时间戳→age/latency、BGR→画布、空白检测、FPS 窗口 | `69893792604e156ec33de551ae152f92c8f494b9d0c152c1924e1a5085463720` / `3e128ef610e38854050f5609242b61343bb076d82c972c1b11de0908d2720c24` |
| `src/vdma_ctrl.c` | axi_vdma 6.3 MM2S 非 SG 寄存器级初始化/启动/状态/帧计数 | `11478655196062585107515ec3a940fa61dbfb3b0dd0828be0a8b3944b2e2558` |
| `src/vdma_ctrl.h` | 寄存器偏移表 + 依据注释 + API（含 FRMCNT_EN/帧计数） | `e0bc10050626f665e5e89c0bf02cba2234c09d2af702117c08e4534c7a498bce` |
| `src/vtc_ctrl.c` | v_tc 6.2 生成器初始化（720p60）+ 回读校验 + 文本摘要 | `8ba7d212b4f5d5ec2781bc84b9041cbe218dd935596644acd72de5bf532b6fa6` |
| `src/vtc_ctrl.h` | VTC 寄存器偏移/位域/结构 + 依据注释 | `68d1555cd3a78aff5d206a90229c1184cdd096b3c00f09b441ecb42c24162458` |
| `src/s5_timebase.h/.c` | 全局定时器 64 位读取、宏括号坑的编译期断言 | `3a2e9c8e3da8b4f6c2ea72755d5b428d241788d5da18d15e4b688072d469d64a` / `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/s5_font8x16.h` | 自带 8×16 ASCII 点阵字库（95 字符 ×16 B，自动生成） | `2f26b78b1098b974c60ee2a1d173107c5b44ef8f8f19dbdc4b599ef93a2d50d3` |
| `tools/gen_font8x16.py` | 字库生成器（DejaVu Sans Mono 11 px 栅格化，可复现） | `b9c5a583435d7120f76ae36b17df4a761f347cd1983866fefc66a0b2e3c04b87` |
| `tools/host_render_test.c` | 主机端离线渲染自检 + 180 帧有界运行（同一份绘图/结果行代码） | `8d63ac1cf8cadccd8d2be39394c6cc4862a522bdccba9bc18e35d16401b070a5` |
| `tools/real_source_selftest.c` | **真实源自检**：ABI 块构造/解析、真实画面渲染、三条回退路径、STALE 显示 | `990a92e100660f3eb9dc8db160842070c054ed47775b09117168503ed558e0d8` |
| `tools/vtc_vdma_selftest.c` | 假寄存器堆离线自检：VTC 校验 + 负例 + VDMA 双缓冲决策 | `b8b546bfa08a910dd04b61075ebfecb05adc9e7feda8db0df0e247c0f7b8f808` |
| `tools/host_xil_shim/xil_io.h` | 主机自检用 `Xil_In32/Xil_Out32` 替身声明（不进 ARM 构建） | `1844e41d2b61f00af0a278d7d7147bdaca605318e24bf7e65155cc40f566e263` |
| `fixtures/fixture_fist_000_640x480_bgr888.raw` | 真实画面 fixture 副本（640×480 BGR888，921,600 B，来自 S4-T34 bringup） | `ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4` |
| `build_s5_display_app.py` | 一键构建 + 四方自检（渲染/寄存器/真实源）+ 证据记录 | `e7847d0de177516dac2adddb20c6f0f9d18d5adcf9f25ea7f74693ac0124889a` |
| `build/` | ELF、map、build_record.json、构建日志、`selftest_*.txt`、14 张 PNG | — |

---

## 2. VDMA 寄存器依据（**先查文档/源码，不猜**）

### 2.1 证据来源（本机可复核）

1. **寄存器映射**：`D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\xaxivdma_hw.h`
   该驱动随 Vitis 2026.1 发布、支持 axi_vdma 6.x；头文件即官方寄存器偏移/位域定义。
2. **非 SG（direct register）写序列**：同目录 `xaxivdma_channel.c`
   - `XAxiVdma_ChannelSetBufferAddr()`：写 `StartAddrBase + 0x0C + 4*i`（`Loop16` 作索引）
   - `XAxiVdma_ChannelDmaSetup()`：写 `HSIZE`、`STRD_FRMDLY`，并重建 CR
   - `XAxiVdma_ChannelStart()`：CR 置 `RUNSTOP`，**随后写 VSIZE 启动**（源码注释：*“Direct register mode: Update vsize to start the channel”*）
   - `XAxiVdma_SetFrmStore()`：写 0x18 前检查 `XAXIVDMA_ENABLE_DBG_FRMSTORE_REG`（→ 本设计**不写**该寄存器）
3. **P3a BD 实参**：`report/evidence/S5-T01/s5_p3a_video_bd_20261030_r01/bd_p3a.bd`
   `c_include_sg=0`、`c_include_mm2s=1`、`c_include_s2mm=0`、`c_m_axi_mm2s_data_width=64`、`c_m_axis_mm2s_tdata_width=32`、`c_addr_width=32`。

### 2.2 本应用实际使用的偏移（基址 `0x43C40000`）

| 偏移 | 名称 | 值/用途 | 依据 |
|---|---|---|---|
| `0x00` | MM2S_VDMACR | bit0 RUNSTOP、bit1 TAIL_EN、bit2 RESET、bit[11:8] RD_PTR | `XAXIVDMA_CR_OFFSET` + `XAXIVDMA_CR_*_MASK` |
| `0x04` | MM2S_VDMASR | bit0 HALTED、bit1 IDLE、bit[11:4] 错误 | `XAXIVDMA_SR_OFFSET` |
| `0x18` | MM2S_FRMSTORE | **只读回记录**，不写 | `SetFrmStore` 的 debug 位门控 |
| `0x28` | PARKPTR | bit[20:16] READSTR = 当前读帧存 | `XAXIVDMA_PARKPTR_READSTR_*` |
| `0x2C` | VERSION | major/minor/rev，用于确认 IP 活着 | `XAXIVDMA_VERSION_*` |
| `0x50` | MM2S_VSIZE | 720（0x2D0），**写它 = 启动** | `XAXIVDMA_VSIZE_OFFSET`（相对 0x50 为 0） |
| `0x54` | MM2S_HSIZE | 每行**字节数** = 1280×4 = 5120 | `XAXIVDMA_HSIZE_OFFSET`，驱动注释“Horizontal size”按字节 |
| `0x58` | MM2S_STRD_FRMDLY | `(FRMDLY<<24) | STRIDE` = 0x00001400 | `XAXIVDMA_STRD_FRMDLY_OFFSET` + `XAXIVDMA_FRMDLY_SHIFT` |
| `0x5C+4i` | MM2S_START_ADDR[i] | 帧存 i 起始地址（32 位地址） | `XAXIVDMA_START_ADDR_OFFSET + 4*i`（驱动 `Loop16` 索引） |

初始化序列（`S5Vdma_Init`）：
`读 VERSION 判活 → 复位(CR.RESET=1 轮询自清) → 写帧存地址 → 写 HSIZE/STRD_FRMDLY → 读回 0x18 → CR=RUNSTOP|TAIL_EN → 写 VSIZE 触发 → 轮询 HALTED 清零（5 ms 超时）`。

**帧存：2 个**（与 BD `c_num_fstores=2` 一致）—— 只写 `0x5C`（缓冲 A）与 `0x60`（缓冲 B），**不写** `0x64` 及以后；`0x18` 只读回记录（期望 2，不符则打印 WARN，不写）。

**帧计数（结果行 `vcnt`）**：`S5Vdma_Start()` 在 CR 里置 `FRMCNT_EN`（bit4，依据 `XAXIVDMA_CR_FRMCNT_EN_MASK` + 驱动 `EnableFrameCounter`），
之后 `SR[23:16]`（`XAXIVDMA_FRMCNT_MASK`）每完成一帧 +1（8 位回绕，SW 用无符号差累计）。若上板发现该字段恒 0（IP 未实现/被忽略），
`vcnt` 自动退回“软件观测到的读帧存切换次数”，两条路径在 `S5Vdma_UpdateFrameCount()` 里已实现。

### 2.3 对题面中“待核对”猜测的纠正

| 题面猜测 | 实际（有依据） |
|---|---|
| “`MM2S_VDMACR` 在 0x30、`MM2S_DMACR`？” | **0x30/0x34 是 S2MM 的 CR/SR**；MM2S 的 CR/SR 在 **0x00/0x04**（`XAXIVDMA_TX_OFFSET=0x00`，`XAXIVDMA_RX_OFFSET=0x30`）。本设计只开 MM2S。 |
| “`MM2S_SA`(0x5C) / `MM2S_LENGTH`(0x58)？” | 0x5C 确实是帧存起始地址（第 0 个）；但 **0x58 不是 LENGTH，而是 STRIDE/FRMDLY**。非 SG 模式**没有** LENGTH 寄存器（那是 AXI DMA 的语义）；长度 = VSIZE × HSIZE 隐式给出，写 VSIZE 即启动。 |
| “描述符区 0x5C../0x6C?” | 非 SG 模式不碰描述符（0x08 CDESC / 0x10 TDESC 是 SG 专用，本设计不写）。 |

> 备注：0x18 FRMSTORE **未写入**。驱动把写该寄存器包在 `XAXIVDMA_ENABLE_DBG_FRMSTORE_REG` 里（IP 调试参数 `Mm2SFrmStoreRegEn`），P3a BD 未打开，写入可能被忽略或读回值无意义，故只在 init 时读回并记录（`dma.fs_hw_readback`）。
> **帧存个数已由 lead 2026-10-30 裁决：BD 的 `c_num_fstores` 改为 2**，SW 与之对齐——只编程 A/B 两个地址（0x5C/0x60），不再写第三个，见 §2.2 与 §3.2。

### 2.4 VTC 生成器初始化（v_tc 6.2，720p60）——本次新增

**依据**（本机可复核）：
1. 偏移/位域：`D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_8\src\xvtc_hw.h`
   （`CTL=0x000`、`VER=0x010`、`GASIZE=0x060`、`GFENC=0x068`、`GPOL=0x06C`、`GHSIZE=0x070`、
   `GVSIZE=0x074`、`GHSYNC=0x078`、`GVBHOFF=0x07C`、`GVSYNC=0x080`、`GVSHOFF=0x084`、
   `GVSYNC_F1=0x08C`、`GASIZE_F1=0x094`；字段 `SB_START=0x3FFF` / `SB_END=0x3FFF0000<<16`、
   `ASIZE_HORI/VERT`、`VSIZE_F0/F1`、`POL_*`、`ENC_PROG(bit6)`、`CTL: SW(0)/RU(1)/GE(2)/RESET(31)`）
2. 写序列：同目录 `xvtc.c` 的 `XVtc_SetGenerator()`（GHSIZE/GVSIZE/GASIZE/GASIZE_F1/GHSYNC/GVSYNC/GVSYNC_F1/GFENC）、
   `XVtc_SetPolarity()`（GPOL）、`XVtc_SetGeneratorHoriOffset()`（GVBHOFF/GVSHOFF）、
   `XVtc_Reset()`（CTL.RESET 自清）、`XVtc_Enable()`（CTL.SW）、`XVtc_EnableGenerator()`（CTL.GE）
3. 几何：lead 2026-10-30 给定 —— H: total 1650 / sync 40 / back 220 / active 1280（前肩 110，同步 1390..1430）；
   V: total 750 / sync 5 / back 20 / active 720（前肩 5，同步 725..730）
4. 与 P3a BD 预设对照：`GEN_HFRAME_SIZE=1650`、`GEN_HSYNC_START/END=1390/1430`、
   `GEN_F0_VFRAME_SIZE=750`、`GEN_F0_VSYNC_VSTART/VEND=724/729`、极性全 High

**写序列**（`S5Vtc_Init`）：`读 VER 判活 → CTL.RESET=1 轮询自清（10 ms 超时）→ 写 11 个生成器寄存器 → CTL |= SW|GE → 逐寄存器回读校验`。
返回码：`0` 成功；`-1` 复位超时；`-2` 版本无效/几何非法；**`-3` 回读校验失败**（不静默，调用方必须打印）。

**实际写入/回读值**（720p60，`S5_VIDEO_720p60`）：

| 寄存器 | 偏移 | 值 | 含义 |
|---|---|---|---|
| GHSIZE | 0x070 | `0x00000672` (1650) | 行总周期 |
| GVSIZE | 0x074 | `0x02EE02EE` | 场总行数 F0=F1=750 |
| GASIZE | 0x060 | `0x02D00500` | 行有效 1280 / 场有效 720 |
| GASIZE_F1 | 0x094 | `0x02D00000` | 场 1 有效 720 |
| GHSYNC | 0x078 | `0x0596056E` | 行同步 1390..1430 |
| GVSYNC | 0x080 | `0x02D902D4` | 场同步 724..729 |
| GVSYNC_F1 | 0x08C | `0x02D902D4` | 逐行扫描同值 |
| GVBHOFF | 0x07C | `0x05000500` | 场消隐水平起止 = 行有效宽 1280 |
| GVSHOFF | 0x084 | `0x056E056E` | 场同步水平起止 = 行同步起点 1390 |
| GPOL | 0x06C | `0x0000003F` | H/V Sync、ActiveVideo、H/V Blank 全正极性 |
| GFENC | 0x068 | `0x00000000` | 逐行扫描（PROG=0）、RGB、无 chroma 跳过 |
| CTL | 0x000 | `0x00000005` | SW=1、GE=1（核 + 生成器使能），RESET=0 |

> **场同步 724..729 而非 725..730 的原因（有据，非笔误）**：v_tc 驱动的寄存器编码是
> `GVSYNC = (V0SyncStart + vactive - 1)`（`XVtc_SetGenerator` 源码），水平侧则是 `HSyncStart + hactive`（无 -1）。
> 因此 lead 给的 720/5/5/20 几何在该 IP 里就是 **724..729**，与 P3a BD 的 IP 预设完全一致。
> 若上板发现场同步差 1 行，把 `S5_VTC_VSYNC_USE_IP_PRESET` 置 0 即按几何原值 725..730 写入。

**负例（证明校验不是摆设）**：离线自检里人为把 GHSIZE 写成 `0x1234`，`S5Vtc_Verify()` 立刻报
`GHSIZE ... want=00000672 got=00001234 **MISMATCH**`，`S5Vtc_Init()` 返回 `-3`。输出见 §8.2。

**未验证**：寄存器写入/回读只证明 AXI-Lite 通路与位域正确，**不证明实际视频时序输出正确**（需上板用示波器/显示器或
`vid_out` 状态确认）；`v_axi4s_vid_out` 是否已锁定（`locked`）、VTC 极性输出是否符合 TMDS 侧要求，均归 P3b 上板联调。

### 2.5 结果块 ABI（0x20800000）+ raw 画面（0x12000000）——r04 新增

**依据**：lead 2026-10-30 冻结的 ABI（写死，见 `src/s5_result_abi.h`）。

| 偏移 | 类型 | 字段 | 说明 |
|---|---|---|---|
| `0x00` | u32 | magic | 固定 `0x53355253`（"S5RS"）；不符即回退 |
| `0x04` | u32 | frame_id | 采集帧号 |
| `0x08` | u32 | n_dets | 0..16；>16 视为 ABI 形状非法 |
| `0x0C` / `0x10` | u32 | cap_lo / cap_hi | `t_capture_end`（全局定时器 0xF8F00200 ticks，64 位拼接） |
| `0x14` / `0x18` | u32 | inf_lo / inf_hi | `t_infer_done`（同上） |
| `0x1C` | u32 | status | bit0=valid、bit1=overrun、bit2=stale |
| `0x20` 起 | 16×16 B | 检测项 | 每项：`u16 x,y,w,h`（原图 640×480）+ `u8 cls` + `u8 score_q8` + `u16 reserved` + 4 B 填充 |

**⚠ ABI 尺寸歧义（必须与生产端对齐）**：文字写“每项 16 B”，但字段合计 **12 B**（8+1+1+2），差值 4 B 只能是填充。
本实现按 **16 B 步进**读取、`cls/score` 取第 3 个 u32 的低 16 位（`w2 = cls | score<<8 | reserved<<16`），忽略 `w3`；
若生产端按 12 B 紧凑排布，第 2 项起会整体错位 4 B。已写入报告 §6 风险项，**联调第一件事是对一次真实块的双向 dump**。

**读取与一致性**：读 `magic` → 读 `status`（valid）→ 读 `frame_id` → 解析 → **再读 `frame_id`**，前后不一致判 `torn`（生产端正在写），
本帧回退不渲染中间态。返回码：`0` 成功、`-1` magic、`-2` valid=0、`-3` torn、`-4` 形状非法 —— 全部映射到 `reason` 字符串。

**raw 画面**：`0x12000000` 起 640×480 **BGR888** 紧排（921,600 B），属阶段4 裁决允许的 `raw_frame`（禁区已缩到 `[0x12C08000,0x20000000)`）。
读端做 `BGR→0x00RRGGBB` 转换后送 letterbox；**全 0 检测**用“命中首个非 0 字节即返回”的早退扫描，全 0 时才扫满整幅。

### 2.6 真实源与回退逻辑（r04）

```
每帧：
  invalidate(结果块 0x120 B) → S5Real_Parse()
    ├─ 失败（magic/valid/torn/shape）→ src="sim"    ：S5Sim_NextFrame + 模拟画面；reason=对应原因
    └─ 成功：
         invalidate(raw 921,600 B) → S5Real_IsBlank()
           ├─ 全 0   → src="test"：视频区画测试图案（框仍来自结果块）；reason="raw_frame_blank"
           └─ 有内容 → src="real"：BGR→RGB 转 640×480，letterbox 到 960×720
         S5Real_ToFrameInfo(now) → age = now−cap、latency = now−inf（ms）
         时间戳窗口喂 cap/inf/dis 三口径 FPS
```

- **面板**：`SRC REAL/SIM/TEST` 一行可见；`status.bit2` → AGE 行显示 `STALE`（黄色），`bit1` → `SRC ... OVR`。
- **缓存一致性**：结果块/raw 都是 DMA 写、CPU 读 → 读前 `Xil_DCacheInvalidateRange`（`S5_DCACHE_FLUSH=1` 时生效）。
- **编译期开关**：`S5_SOURCE_REAL=1`（默认）；置 0 强制纯模拟（无生产端时做版式自检用）。
- **FPS 口径**：`cap/inf` 只在 `frame_id` 变化（新结果）时计入窗口，避免同一结果被显示多次而高估；`dis` 每帧计入。

---

## 3. 帧缓冲与画布布局

### 3.1 帧缓冲地址（**r03 已迁出禁区**）与尺寸

**为什么迁**：原定 `0x13000000` 落在阶段4 冻结的 `must_not_access` 禁区 `[0x12C08000, 0x20000000)` 内
（依据 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage4_raw_address_d1_optionA_20261027_r01.md`：
D1 只把禁区从 `[0x12000000,0x20000000)` 缩到 `[0x12C08000,0x20000000)`，`0x13000000` 仍在其中）。
**lead 2026-10-30 裁决：帧缓冲迁到 `0x20000000`** —— 禁区上界之外、应用 ELF 之上（`end≈0x0034A840`）、PS DDR 低 1 GiB 内且空闲。

| 项 | 值 | 计算 |
|---|---|---|
| 画布 | 1280×720，32-bit/像素，`0x00RRGGBB` | — |
| 单帧字节 | **3,686,400 B = 0x384000** | 1280×720×4 |
| 缓冲 A | **`0x20000000`** | lead 裁决 |
| 缓冲 B | **`0x20384000`** | A + 0x384000 |
| 两帧合计 | **7,372,800 B = 0x708000** | 2 × 0x384000 |
| 终点 | **`0x20708000`** | B + 0x384000 |
| 与禁区关系 | `[0x12C08000,0x20000000)` 之外 | 上界恰好 `0x20000000`，不重叠 |
| 结果块（r04） | **`0x20800000`**（预留 8 MiB，实际只读 0x120 B） | 在 FB 末端 `0x20708000` 之后 |
| raw 画面（r04） | **`0x12000000`**，640×480 BGR888 = 921,600 B | 阶段4 允许的 `raw_frame`（禁区已缩到 `[0x12C08000,…)`） |
| 链接脚本内存区 | `0x00100000..0x01100000`（app）、`0x10000000..0x12000000`（r13 tensor） | 帧缓冲在两区之外，用绝对地址访问，链接器不分配 |

实测 ELF 内存布局（`arm-none-eabi-nm`）：`__bss_start=0x0010C010`、`__bss_end=0x0023903C`、`_heap_end=0x00339040`、`_stack=0x00349040`、`end=0x0034A840` —— 全部低于 `0x01100000`（链接脚本 `ASSERT(app budget)` 通过），与 `0x20000000` 帧缓冲无重叠。

### 3.2 布局裁决（已由 lead 2026-10-30 定案）

G0 冻结原文里三个数字不可能同时成立：**160（左黑边）+ 960（视频）+ 320（信息栏）= 1440 > 1280**。
**裁决：以“无重叠”为准，不要黑边**，即视频 `x=0..959`、信息栏 `x=960..1279`（`S5_LAYOUT_BARS=0`，当前默认）。
理由：960×720 与 640×480 同为 4:3，`3/2` 整数最近邻缩放到 720 高正好填满 960 宽，画面完整、不变形、不重叠。

| 方案 | 宏 | 几何 | 用途 |
|---|---|---|---|
| **L0（默认，已采纳）** | `S5_LAYOUT_BARS=0` | 视频 `x=0..959`（无黑边）+ 信息栏 `960..1279` | 正式版式，`build/frame_full.png` |
| L1（字面方案，**仅实验**） | `-DS5_LAYOUT_BARS=1` | 视频 `x=160..1119`（左右各 160 黑边），信息栏覆盖右侧 160 px | 保留作对照，**不作为默认**；`build/frame_full_bars.png` 可见画面被裁 1/6 |

两套都实现、都渲染了 PNG；切换只改编译宏一行，绘制/框映射/面板代码完全共用。

### 3.3 坐标映射（检测框）

摄像头坐标 `(x,y,w,h)`（640×480）→ 画布：
```
cx = S5_VID_X + (x * 3) / 2        cy = (y * 3) / 2
cw = (w * 3) / 2                   ch = (h * 3) / 2
```
整数乘除截断，单轴误差 ≤ 1 px；检测框按 `S5_BOX_LINE_W = 2` px 线宽绘制（`S5Draw_RectLine`）。
水平/垂直方向缩放比相同（1.5），无各向异性畸变。

---

## 4. 绘图算法

### 4.1 8×16 ASCII 字库（自带，不依赖系统字体）

- 生成器：`tools/gen_font8x16.py`；字体：**DejaVu Sans Mono**（matplotlib 随附，Bitstream Vera 派生，许可宽松），**字号 11 px、基线 12**，8×16 单元内 `anchor="ls"` 栅格化，阈值 128 二值化。
- 选字号判据：`ascent+descent ≤ 15`、所有字符墨迹宽度 ≤ 7 列（右侧留 1 列，避免相邻字符粘连）、不越上下边界。
- 位序：**bit7 = 最左列**（与经典 VGA 8×16 字库一致）；表 `s5_font8x16[95][16]`（ASCII 0x20..0x7E，1520 B，`.rodata`）。
- 渲染：`S5Draw_Text(fb,x,y,text,fg,bg)`；`bg == S5_COLOR_TRANSPARENT` 时只写前景像素（用于叠加在画面上）。
- 可读性已目视确认：`build/font_preview.png`（生成器自带字样预览）。

### 4.2 摄像头 640×480 → 960×720 最近邻缩放

- 比值 960/640 = 720/480 = **3/2**；源坐标 = `目标 × 2/3`，用整数 `(dst*640)/960` 计算。
- 预计算列/行 LUT（`sx_lut[960]`、`sy_lut[720]`，首次调用初始化），每像素一次查表 + 一次拷贝，避免每像素两次乘除。
- 先 `S5Draw_Clear(BLACK)` 清整屏，再覆盖视频区；信息栏最后绘制。默认 L0 下视频区正好铺满 `x=0..959`（无黑边）；若用实验分支 L1（`S5_LAYOUT_BARS=1`），左侧 160 px 保持黑色、右侧越界部分由面板覆盖。

### 4.3 检测框

- 2 px 线宽：上/下边各 2 行、左/右边各 2 列（`S5Draw_RectLine` 用 4 条 `RectFill` 叠加，裁剪在 `s5_put`/`RectFill` 内做）。
- 颜色按类别：`s5_class_color[5]` = 红/绿/蓝/黄/紫；类别名 `s5_class_name[5]` = `C0..C4`（**占位**，等阶段5 类别定义冻结后只改这两张表，绘制逻辑不动）。
- 标签：`"<类别> <分数>"`（整数百分比），黑底彩字，画在框上方；顶部空间不足时画到框内。
- 面板同时列出最多 5 条明细：`类别 分数 @x,y wxh`（摄像头原始坐标）。

### 4.4 信息栏（右侧 320×720）

深色底 `0x00101820`、左侧 2 px 高亮分隔线、标题条。字段（20 px 行距，8×16 字）：

```
S5 P3B DISPLAY 720p60      （标题）
FRAME 00001234             （帧号，零填充 8 位）
FPS C 30.0 I 28.1          （采集/推理两口径，×10 定点，无浮点 printf）
FPS D 60.0                 （显示口径）
LAT 17 ms                  （显示延迟 = t_display_start − t_infer_done）
AGE 31 ms  OK / OVER       （结果年龄 = t_display_start − t_capture_end，超限转红）
LIM 33 ms (1f+16.7)        （G0 上限 = 1 帧 + 16.7 ms ≈ 33 ms）
VDMA RUN / OFF / ERR       （绿/黄/红）
ST 00000003                （S5_ST_* 状态位，十六进制，便于上板对照）
DET 03                     （检测数）
C0  87 @120,90 160x140     （逐框明细，最多 5 条）
CLASS  C0 C1 C2 C3 C4      （类别图例色块）
960x720 + 320 panel        （版式脚注，一眼确认跑的是哪个版本）
P3B-SW r01
```

- 字符串一律手写格式化（`s5_u32`/`s5_dec1`/`s5_hex8`），**不依赖 printf 浮点/宽度**；`xil_printf` 只用 `%d/%x/%s`（其格式支持有限，且已验证不传宽度修饰符）。
- 每帧重绘整块面板（32 万像素）。

### 4.5 三条测试图（证明上屏通路）

- `mode 0` 棋盘（80 px 格，叠加文字 “TEST PATTERN 0: CHECKER 1280x720”）；
- `mode 1` 8 根 75% 幅度彩条（贯穿整屏，含信息栏区域 —— 用来证明 **1280 全宽**都有数据）；
- `mode 2` 水平灰阶。

`main()` 启动时先分别把棋盘/彩条写入 A/B 两个缓冲并 flush，再启动 VDMA，随后才进入动画循环 —— 上板时若屏幕出现棋盘/彩条即证明“DDR→VDMA→vid_out→(rgb2dvi/TMDS)”整链通。

---

## 5. 时间基座与测量口径

### 5.1 BSP 宏括号坑（阶段4 已踩，本次显式防住）

`BSP/include/xtimer_config.h`：
```c
#define XSLEEPTIMER_FREQ    XPAR_CPU_CORE_CLOCK_FREQ_HZ/2   /* 无括号 */
#define COUNTS_PER_SECOND   XSLEEPTIMER_FREQ                /* 无括号 */
```
`XPAR_CPU_CORE_CLOCK_FREQ_HZ = 666666687`。若写 `ticks * 1000 / COUNTS_PER_SECOND`，预处理后是
`ticks * 1000 / 666666687 / 2`（`*`、`/` 同优先级左结合）→ **有效分母 1,333,333,374 = GT 频率的 4 倍**，所有 ms 被压小 4 倍。

本模块的处理：
- 计数直读 Zynq 全局定时器 `0xF8F00204`（高）/ `0xF8F00200`（低），**hi-lo-hi 双读**防低位回绕；
- 频率用**自带显式常量** `S5_GT_HZ = 333333343ULL`（= 666666687/2 向下取整），换算全部先乘后除（64 位）；
- 编译期双断言：`((uint64_t)(COUNTS_PER_SECOND)) == S5_GT_HZ` 且 `S5_GT_HZ == 333333343`；BSP 频率或宏写法一变就**编译失败**而不是静默算错。
  （`s5_timebase.c` 里 `_Static_assert` 实际通过，说明 BSP 侧 `(uint64_t)(666666687/2)` = 333333343 与常量一致。）

### 5.2 三个测量口径（G0 冻结）

| 口径 | 定义 | 本应用落点 |
|---|---|---|
| `t_capture_end` | 采集帧结束时刻 | `S5FrameInfo` 输入；真实实现由 PL 帧计数/中断打时间戳 |
| `t_infer_done` | 推理完成时刻 | 同上 |
| `t_display_start` | 本帧开始写显示缓冲时刻 | `S5Display_RenderFrame()` 调用点 |
| 显示延迟 | `t_display_start − t_infer_done` | `info.latency_ms`，面板 `LAT` |
| 结果年龄 | `t_display_start − t_capture_end` | `info.age_ms`，面板 `AGE`；`> 33 ms` 置 `S5_ST_AGE_OVER` 并转红 |
| FPS 三口径 | 采集 / 推理 / 显示 | `info.fps_*_x10`（×10 定点，面板按 `xx.x` 打印） |

---

### 5.3 有界运行与结果行契约（**r03 新增，runner 判据写死**）

**有界运行**（`main()`）：`while (frames < S5_RUN_FRAMES && elapsed < S5_RUN_MAX_MS)`，默认
`S5_RUN_FRAMES = 180`、`S5_RUN_MAX_MS = 60000`（先到者停机，可用 `-DS5_RUN_FRAMES=N` 覆盖）。
循环结束后先 `S5Vdma_Stop()` 停机，再打印结果行 —— UART 采集器可据此收尾，不会遇到无限运行。

**结果行**（单行、固定前缀，**只由 `S5Display_FormatResult()` 产生**，主机自检与板上共用同一份实现）：

```text
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180}
```

| 字段 | 单位/取值 | 说明 |
|---|---|---|
| `pass` | 1 / 0 | 链路健康（VDMA 无错 + ≥1 帧完整显示 + 信息栏刷新成功）**且** `src≠"sim"`；`src="test"` 仍算通过（显示可用）但带 `reason` |
| `fps_cap` | **整数 fps 0..60**（不是 ×10） | 采集口径；真实源取时间戳窗口，模拟源取模型值 |
| `fps_inf` | **整数 fps 0..60** | 推理口径；真实源取 `inf` 时间戳窗口，模拟源固定 0（契约允许） |
| `fps_dis` | **整数 fps 0..60** | 显示口径（每帧计入窗口） |
| `latency_ms` | 整数毫秒 | 显示延迟 = now − t_infer_done；真实源由 ticks 换算，模拟源为模型值 |
| `age_ms` | 整数毫秒 | 结果年龄 = now − t_capture_end；真实源由 ticks 换算，模拟源为模型值（每 47 帧注入超龄） |
| `vdma_err` | 计数 | 运行期间 SR 错误位（`XAXIVDMA_SR_ERR_ALL`）累计次数 |
| `frames` | 计数 | 实际渲染帧数 |
| `vcnt` | 计数 | VDMA 消耗帧计数：优先硬件帧计数（SR[23:16]），读不到则软件观测读帧存切换次数 |
| `src` | `"real"` / `"sim"` / `"test"` | 本窗口数据源；回退判据（r04 新增，见 §2.6） |
| `reason` | 字符串（非 NULL 即输出） | `result_magic_mismatch` / `result_not_valid` / `result_torn` / `result_shape_invalid` / `raw_frame_blank` / `vdma_init_failed` / `vdma_error` / `no_frame_rendered` / `frame_check_failed` |

**真实源 vs 模拟源的判据差异**（r04）：

| | `src="real"` | `src="test"` | `src="sim"` |
|---|---|---|---|
| 触发条件 | magic/valid 全通过 + raw 有内容 | 结果块通过但 raw 全 0 | 结果块不可用（magic/valid/torn/shape） |
| 画面 | 真实 raw（BGR→RGB，letterbox） | 视频区测试图案（棋盘 + 红字提示） | 模拟画面 |
| 检测框 | 结果块 | 结果块（仍画，验证 ABI 通路） | 模拟源 |
| `pass` | 1 | 1（显示可用） | **0** |
| `reason` | 无 | `raw_frame_blank` | 解析失败原因 |
| fps/latency/age | 真实时间戳窗口 | 真实 ticks（画面除外） | 模型值 |

**通过判据实现**（`S5Display_CheckFrame()` 抽点自检）：视频区（摄像头/棋盘）抽样 ≥8 个非黑点；
信息栏**标题条**（y=6..20、x=970..1160）抽样 ≥20 个非面板底色点 —— 标题条是实心填色带，用它判断“信息栏确实刷新过”，
比随机抽文字像素稳健（文字覆盖率低会误判）。

**进度行**（与 RESULT 行分开，绝不拼在同一行）：
```text
S5DISP frame=60 lat=... age=... st=... sr=...
```
每 60 帧一行；结束后另有 `S5DISP done frames=... vcnt=... vdma_err=...` 一行，再打 RESULT 行。

**失败也打 RESULT**（`pass:0` + `reason`，同样单行）：
```text
S5DISP RESULT={"pass":0,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"reason":"vdma_init_failed"}
```

> 离线示例由 `tools/host_render_test.c` 跑满 180 帧（真渲染 + 抽点自检，无 MMIO）后用**同一函数**生成，见 §8.3；
> 真实源示例（`src:"real"`）与两条回退示例见 §8.4。板上真实数值需生产端实际写结果块。`main()` 里的 `S5_RESULT_FPS_INF_FROM_SIM`
> 只影响**模拟源分支**的 `fps_inf`（真实源分支由 `inf` 时间戳窗口计算）。

---

## 6. 未验证项与风险

### 6.1 高风险（阻断上板联调）

**① 结果块 ABI 的 12 B vs 16 B 歧义（r04 新增，最优先核对）**：lead 的 ABI 文字写“每项 16 B”，但字段合计 12 B，差 4 B 只能是填充。
   本实现按 **16 B 步进**（`cls/score` 取第 3 个 u32 的低 16 位，忽略第 4 个 u32）；若生产端（chain-lite A）按 12 B 紧凑写，第 2 项起全部错位 4 B，
   表现为“框整体偏移/尺寸乱”。**联调第一步**：让生产端写一份已知 3 框的块，双方 dump 0x20800000 前 0x60 B 对字段。
1. **帧存个数已按 2 对齐，但 BD 侧改动未由本卡核验**：lead 2026-10-30 已把 BD 的 `c_num_fstores` 改为 2，本 SW 只编程 A/B 两个地址（`0x5C/0x60`），与 BD 一致。若实际硬件仍是 3（BD 未重新生成/未综合），第 3 个帧存会读地址寄存器复位值（0）→ 周期性花屏。
   - 本 SW 的防护：init 读回 `0x18`，不等于 2（且非 0）时打印 `WARN FRMSTORE readback != 2`；`0x18` 本身是否可读取决于 IP 调试参数，读回 0 时只记录、不据此决策。
   - 上板第一步：确认 `c_num_fstores=2` 的新 BD 已生效（读回 / 看综合报告参数），再观察帧序列。
**② 真实数据源只有主机验证，板上未验**：`s5_real_source.c` 用 fixture + 合成块在主机跑通（§8.4），但板上依赖：
   ①生产端真的在写 `0x20800000`（magic/valid）；②raw 区真的由相机/DMA 填 `0x12000000`；③D-cache 无效化时序正确（DMA 写→CPU 读）。
   任一条不成立 → 会看到 `src:"sim"`（`result_*` reason）或 `src:"test"`（`raw_frame_blank`），这正是设计好的可读回退，不是崩溃。
2. **未上板**：VDMA 实际搬数、`vid_out` 的 `tready` 反压、VTC 实际时序输出、rgb2dvi/TMDS、DDR 带宽全部未验证。本 ELF 只证明“能编译链接 + 寄存器序列逻辑正确（假寄存器堆自检）+ 图形逻辑正确”。
3. **VTC 已实现但只验证到寄存器层**：`vtc_ctrl.c` 按 720p60 写生成器并在写后逐寄存器回读（12/12 OK，负例可检出 MISMATCH）。**未验证**：真实 VTC 输出时序（HS/VS/DE/极性）、`v_axi4s_vid_out` 是否 `locked`、`rgb2dvi`/TMDS 是否出图。若上板无图，排查顺序：`vid_out` locked 位 → VTC 极性 → VDMA 是否在跑（SR/CR）→ 帧缓冲内容（JTAG 看 0x20000000）。
4. **缓存一致性**：帧缓冲 3.7 MB ≫ 32 KB D-cache。`main()` 每帧调用 `Xil_DCacheFlushRange()`（`S5_DCACHE_FLUSH=1`）。若 bring-up 时 D-cache 关闭，可置 0；若开启，必须保证 0x20000000 区按 write-back 正常维护，且 flush 的耗时（~115k cache line）计入帧预算。
4b. **帧缓冲新地址（0x20000000）本身未经板上写入-回读实测**：只在链接/文档层面确认它不在 `[0x12C08000,0x20000000)` 禁区内、在 ELF `end` 之上、在 PS DDR 低 1 GiB 内；上板第一步应做 64 B 对齐的写-回读校验（与阶段4 的候选区核验同口径）。

### 6.2 中风险

5. **撕裂/闪烁**：写侧只按 `PARKPTR.READSTR`（“当前读帧存”）判断安全窗口，未与 VTC 场同步对齐（无 vsync 中断）。最坏情况仍可能撕裂；`S5Vdma_WaitNotReading` 超时（100 ms）会置 `S5_ST_TEAR` 并在面板 `ST` 位可见。彻底解决需接 `vid_out`/VTC 的 vsync 或 VDMA 帧中断（P3b 联调再做）。
   **且 `READSTR` 在循环（circular）模式下的有效性尚未从 pg020 正文核实**：该字段在驱动注释里标为 “Current read frame”，但驱动自己只在 park 模式读它（`XAxiVdma_ChannelDmaSetup` 的 Park 分支）。若上板发现它不随帧更新，应改为用 VDMA 帧中断里的帧计数做写侧同步。这是本次联调第一优先要验证的寄存器行为。
6. **帧率/节流**：主循环按 CPU 速度自由跑（模拟源），**未按 60 Hz 节流**。真实实现要么等 VDMA 帧中断，要么用定时器把 `t_display_start` 对齐到 16.7 ms 网格。
7. **性能未实测**：每帧写像素 ≈ 920k（视频区 691k + 面板 230k）+ 3.7 MB flush，Cortex-A9 @667 MHz 下的实际帧耗时**未测**（预计 30–60 ms 量级，可能达不到 60 fps；需上板用 GT 计时打点，必要时优化：面板只重绘变化区、flush 只刷脏行）。
8. **类别名/颜色是占位**：`C0..C4`，等阶段5 类别定义冻结后替换（只改 `s5_class_name`/`s5_class_color`）。

### 6.3 低风险 / 说明

9. **像素格式**：VDMA 流宽 32-bit，`vid_data[23:0]` 由 xlslice 取低 24 位（P3a BD 已如此接）；本 SW 写 `0x00RRGGBB`，高 8 位为 0。若 P3b 改成 RGB565 或字节序变化，需同步改 `S5_RGB` 与 VDMA `c_m_axis_mm2s_tdata_width`。
10. **VDMA RD_PTR 切换未实现**：本 SW 用“循环模式 + 写前等安全窗口”，没有用 `CR.RD_PTR`/PARKPTR 主动切帧。若联调证明循环模式抖动不可接受，可加 `S5Vdma_SetReadPointer()`（CR bit[11:8]），但该切换的时序语义（是否立即生效/需等帧边界）**尚未从 pg020 正文确认**，故未实现，只留接口位置说明。
11. **`0x18` 读回值的解释**：调试寄存器未开时读回值可能是 0 或常数，不能作为帧存个数依据（init 只记录、不据此决策）。

---

## 7. 构建方法、命令与退出码

### 7.1 一键构建

```bat
cd /d D:\tmp\lead\p3b_display_sw_20261030_r01
python build_s5_display_app.py
:: 退出码 0 = ARM ELF 构建成功 + 主机自检通过
```

脚本内部实际命令（可从 `build/build_s5_display_app.log` 逐条复核）：

```text
# 编译（4 个源文件：s5_display_app.c / vdma_ctrl.c / vtc_ctrl.c / s5_timebase.c）
arm-none-eabi-gcc.exe -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -DSDT \
  -Wall -Wextra -O2 -g3 -std=gnu11 -ffunction-sections -fdata-sections -U__clang__ \
  -specs=<BSP>/Xilinx.spec -I<BSP>/include -Isrc \
  -o build/s5_display_app.o -c src/s5_display_app.c      # 其余三文件同理

# 链接
arm-none-eabi-gcc.exe <同上 flags> \
  -Wl,-Map=build/s5_display_app.map,--cref,--gc-sections \
  build/s5_display_app.o build/vdma_ctrl.o build/vtc_ctrl.o build/s5_timebase.o \
  -o build/s5_display_app.elf \
  -L<BSP>/lib -Wl,-T -Wl,<w4>/tmp/4/S4-T34/ps_app_build/lscript_s4t34.ld \
  -Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group
```

工具链与依赖（均只读引用，未修改）：
- gcc：`D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\`（**13.4.0**，`arm-xilinx-eabi-gcc.exe`）
- BSP：`D:/codex-worktrees/w4/tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r13/bundle_extract/bundle/workspace/ps7/export/ps7/sw/cpu0`
  （`lib/` 只有 `libxil.a` / `libxilstandalone.a` / `libxiltimer.a`，**没有 axivdma 驱动** → 本 SW 用寄存器级实现，正好绕开驱动缺失）
- 链接脚本：`D:/codex-worktrees/w4/tmp/4/S4-T34/ps_app_build/lscript_s4t34.ld`

### 7.2 退出码与产物

| 步骤 | 退出码 |
|---|---|
| 编译 app / vdma / vtc / timebase / real_source | 0 / 0 / 0 / 0 / 0 |
| 链接 | **0** |
| size / nm | 0 / 0 |
| 主机渲染自检（两套布局） | 0 / 0（PASS，各 5 张 PNG） |
| 主机 180 帧有界运行 → RESULT 行 | 0（PASS，示例见 §8.3） |
| VTC/VDMA 寄存器序列自检 | **0**（PASS，见 §8.2） |
| 真实数据源自检（真实/回退/空白/STALE） | **0**（PASS，见 §8.4） |

产物：`build/s5_display_app.elf`（**296,352 B，sha256 `acca2cf7…` 见 §0**）、`build/s5_display_app.map`、`build/build_record.json`（输入/输出哈希、命令、退出码、限制项、四方自检结果）、`build/selftest_vtc_vdma.txt`、`build/selftest_real_source.txt`、`build/host_*_test*.exe`、`build/*.png`。

### 7.3 符号检查（防止“链接成功但内容被 gc 掉”）

断言 ELF 中存在：`main`、`S5Draw_Text`、`S5Draw_CameraLetterbox`、`S5Vdma_Init`、`S5Vdma_Start`、`S5Vdma_WaitNotReading`、`S5Vtc_Init`、`S5Real_Parse`、`S5Ticks_Now` —— **missing = []**。
说明：`-O2` 会内联只在本单元调用的函数并由 `--gc-sections` 回收副本，故 `S5Display_RenderFrame`/`S5Sim_NextFrame`/`S5Vtc_Verify` 可能不在符号表（构建记录里已注明该行为，不是缺函数）。

---

## 8. 主机端离线自检（渲染 PNG + 寄存器序列）

### 8.1 绘图渲染（PNG 证据）

`tools/host_render_test.c` + `src/s5_display_app.c` 用 **MinGW gcc** 编译（`-DS5_HOST_TEST`，屏蔽 MMIO/VTC/VDMA 部分，`S5Ticks_Now` 用假实现），渲染 1280×720 后写 PPM，脚本再转 PNG：

| 图 | 验证内容 |
|---|---|
| `build/pattern_checker.png` | 棋盘测试图 + 文字，证明整屏 1280×720 都可写 |
| `build/pattern_colorbars.png` | 8 根彩条（贯穿含信息栏区域），全宽数据正确 |
| `build/pattern_grayramp.png` | 灰阶线性（0..255 映射） |
| `build/frame_full.png` | **默认 L0 版式**：960×720 视频区（4:3 不变形）+ 320 信息栏 + 3 个检测框（2 px、类别色、标签）+ 全字段面板 |
| `build/frame_age_over.png` | AGE 超限红色告警 + `VDMA ERR` 路径 |
| `build/frame_full_bars.png` | 字面方案 L1：左 160 黑边可见、右侧 160 px 画面被面板遮住（**用于说明 §3.2 的取舍**） |
| `build/font_preview.png` | 字库可读性预览（生成器自检） |

> 这些图证明的是**绘图逻辑**（几何/颜色/字体/框映射），**不能**替代上板验证。

### 8.2 VTC 初始化 + VDMA 双缓冲（寄存器序列自检）

做法：`tools/host_xil_shim/xil_io.h` 提供 `Xil_In32/Xil_Out32` 替身，`tools/vtc_vdma_selftest.c` 用一块
假寄存器堆（0x43C00000..0x43C4FFFF）实现 pg020/xaxivdma_hw.h 的寄存器语义（RESET 自清、写 VSIZE 后清 HALTED、
PARKPTR.READSTR 随帧推进），然后**把真正上板的 `vtc_ctrl.c` + `vdma_ctrl.c` 原样编译进去跑**。
输出原文见 `build/selftest_vtc_vdma.txt`，要点如下：

**VTC（720p60）—— 12/12 回读一致：**
```text
VTC: version=0x00060000
  GHSIZE @43C30070 want=00000672 got=00000672 OK
  GVSIZE @43C30074 want=02EE02EE got=02EE02EE OK
  GASIZE @43C30060 want=02D00500 got=02D00500 OK
  GASIZE_F1 @43C30094 want=02D00000 got=02D00000 OK
  GHSYNC @43C30078 want=0596056E got=0596056E OK
  GVSYNC @43C30080 want=02D902D4 got=02D902D4 OK
  GVSYNC_F1 @43C3008C want=02D902D4 got=02D902D4 OK
  GVBHOFF @43C3007C want=05000500 got=05000500 OK
  GVSHOFF @43C30084 want=056E056E got=056E056E OK
  GPOL @43C3006C want=0000003F got=0000003F OK
  GFENC @43C30068 want=00000000 got=00000000 OK
  CTL     @43C30000 want=00000005 got=00000005 OK
  VTC verify: 12/12 OK
  VTC timing 1280x720 Htotal=1650 Hsync=1390..1430 Vtotal=750 Vsync=724..729
VTC: init OK (SW|GE enabled, 720p60 generator)
VTC negative test: OK（检测到 1 项不一致）
  GHSIZE @43C30070 want=00000672 got=00001234 **MISMATCH**
VTC: re-init after negative test -> OK
```

**VDMA（2 帧存）初始化 + 双缓冲乒乓决策：**
```text
VDMA: init OK, version=0x60300000 (major 6 minor 3 rev 0), FRMSTORE readback=2 (expect 2)
VDMA: CR=0x00000013 SR=0x00000002 HSIZE=5120 VSIZE=720 STRIDE=5120
VDMA: store0=0x20000000 store1=0x20384000
frame 0: VDMA reads B(0x20384000) -> draw into A(0x20000000) wait=ok PASS
frame 1: VDMA reads A(0x20000000) -> draw into B(0x20384000) wait=ok PASS
frame 2: VDMA reads B(0x20384000) -> draw into A(0x20000000) wait=ok PASS
frame 3: VDMA reads A(0x20000000) -> draw into B(0x20384000) wait=ok PASS
frame 4: VDMA reads B(0x20384000) -> draw into A(0x20000000) wait=ok PASS
frame 5: VDMA reads A(0x20000000) -> draw into B(0x20384000) wait=ok PASS
==== selftest: PASS ====
```
解读：`CR=0x13` = RUNSTOP|TAIL_EN|**FRMCNT_EN**（帧计数使能，供 `vcnt`）；`SR=0x2` = IDLE（已启动、无错误位）；
每帧都选“当前不被读”的缓冲写入并 `wait=ok`，6/6 帧无冲突 → 乒乓逻辑正确。
**注意**：这是假硬件的逻辑验证，`READSTR` 的真实行为仍是联调第一优先（§6.2-5）。

### 8.3 有界运行 180 帧 → 示例 RESULT 行（离线打印）

`tools/host_render_test.c` 在主机上跑满 `S5_RUN_FRAMES=180` 帧（真渲染 + 信息栏抽点自检，无 MMIO），
再用**与板上同一份** `S5Display_FormatResult()` 生成结果行。实际 stdout：

```text
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180}
```

失败路径（同一函数，`pass:0` + `reason`，仍为单行）：
```text
S5DISP RESULT={"pass":0,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"reason":"vdma_init_failed"}
```
说明：`fps_cap=30 / fps_dis=59 / latency_ms=19 / age_ms=31` 均来自**模拟数据源**（`S5Sim_NextFrame`），
`fps_inf=0` 按契约（无真实推理源）；`vcnt=180` 是离线模拟值（板上取硬件帧计数，见 §2.2）。
`pass=1` 的成立依据：`S5Display_CheckFrame()` 对最后一帧的抽点自检通过（视频区 36/64 非黑点、
信息栏标题条 80/80 非底色点，远高于阈值 8 / 20）。

### 8.4 真实数据源自检（r04，`tools/real_source_selftest.c`）

同一份 `s5_real_source.c` + `s5_display_app.c` 在主机跑，假时钟由测试推进（60 Hz 显示、30 Hz 新结果）：

```text
case1 (real): S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":59,"latency_ms":7,
                             "age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"src":"real"}
case1 status=0x0003 det=3 age=31 lat=7
case2 (magic bad): parse_rc=-1 reason=result_magic_mismatch
case2 (fallback sim): S5DISP RESULT={"pass":0,"fps_cap":29,"fps_inf":0,"fps_dis":59,"latency_ms":17,
                                    "age_ms":33,"vdma_err":0,"frames":1,"vcnt":0,"src":"sim","reason":"result_magic_mismatch"}
case3 (raw blank): S5Real_IsBlank=1
case3 (fallback test): S5DISP RESULT={"pass":1,"fps_cap":0,"fps_inf":0,"fps_dis":0,"latency_ms":7,
                                     "age_ms":31,"vdma_err":0,"frames":1,"vcnt":0,"src":"test","reason":"raw_frame_blank"}
case4 (stale): status=0x004B stale_bit=1 age=49 ms
==== real-source selftest: PASS ====
```

| 用例 | 验证点 | 产物 |
|---|---|---|
| case1 真实源 | magic/valid 通过、3 框坐标/分数解析、`age=now−cap`、`latency=now−inf`、fps 窗口、`src:"real"`、`pass=1` | `build/frame_real.png`（真实 fixture 画面 + 3 框 + 面板 `SRC REAL`，FPS C 30.6 / I 29.9 / D 59.9） |
| case2 magic 错 | 回退模拟源、`pass=0`、`reason=result_magic_mismatch` | `build/frame_fallback_sim.png` |
| case3 raw 全 0 | `S5Real_IsBlank=1`、测试图案回退、`src:"test"`、`pass=1`+reason | `build/frame_test_fallback.png`（棋盘 + 红字 + 框 C1） |
| case4 stale | `status.bit2` → `S5_ST_STALE`、面板 AGE 行显示 STALE | `build/frame_stale.png` |

> 说明：fixture 为 `fixtures/fixture_fist_000_640x480_bgr888.raw`（S4-T34 bringup 的 640×480 BGR888，sha256 `ce37aa77…`，副本）。
> 图上真实画面/框/文字都在，说明 **ABI 解析 → 坐标映射 → 640×480 → 960×720 缩放 → 面板**整条链路在主机侧是通的；上板差异只在数据来源与缓存一致性。

---

## 9. 真实数据源接线（r04 已接，替代原“替换清单”）

**已实现**：`src/s5_real_source.c` 每帧读结果块 + raw，`S5Sim_NextFrame()` 降级为**回退路径**。
板上接线只剩“地址与缓存”两件事，均由宏/常量给出：

| 项 | 值 / 位置 | 说明 |
|---|---|---|
| 结果块 | `0x20800000`（`S5_RESULT_BASE`） | 生产端（chain-lite A 派生）写；读端每帧 invalidate 0x120 B |
| raw 画面 | `0x12000000`（`S5_RAW_FRAME_BASE`） | 640×480 BGR888；读端每帧 invalidate 921,600 B |
| 时间戳 | 结果块 cap/inf（全局定时器 ticks） | `age=now−cap`、`latency=now−inf`，`S5_GT_HZ=333333343` 换算 |
| 结果年龄上限 | 33 ms | 超限 → `AGE OVER`；`status.bit2` → `STALE` |
| 开关 | `S5_SOURCE_REAL`（默认 1） | 0 = 强制纯模拟（无生产端时版式自检） |

| `S5FrameInfo` 字段 | 真实源来源 | 模拟回退 |
|---|---|---|
| `frame_id` | 结果块 `frame_id` | 自增 |
| `fps_*_x10` | cap/inf/dis 时间戳窗口（×10，面板用） | 模型值 |
| `latency_ms` / `age_ms` | `now − inf` / `now − cap`（ticks→ms） | 17 ms / 30 ms + 抖动 |
| `det[]` | 结果块 16×16 B（原图 640×480 坐标） | 1~3 个移动框 |
| `status` | VALID/OVERRUN/STALE + 超龄判定 | CAM_OK/INF_OK/AGE_OVER |
| `src_kind` | REAL / TEST / SIM | SIM |

> 原来的“替换 `S5Sim_NextFrame()`”动作**不再需要**；现在只需要生产端按 §2.5 的 ABI 写块、相机/DMA 填 raw。

---

## 10. 待办（按优先级）

1. ~~裁决 §3.2 布局~~ —— **已完成**：默认 L0（无黑边、无重叠），L1 仅作实验分支。
2. ~~补 VTC 编程~~ —— **已完成（离线）**：`vtc_ctrl.c` 720p60 + 回读校验 + 负例；上板仍需验证实际时序输出。
3. ~~确认 `c_num_fstores`~~ —— **已按 2 实现**（与 BD 对齐）；上板读回 0x18 复核一次。
4. ~~有界运行 + 结果行~~ —— **已完成**：180 帧/60 s 停下 + 单行 `S5DISP RESULT=`（失败带 `reason`），离线示例见 §8.3。
5. ~~帧缓冲迁出禁区~~ —— **已完成**：A/B = `0x20000000`/`0x20384000`。
6. ~~接真实数据源~~ —— **已完成**：结果块 ABI + raw 画面 + 回退（`src`/`reason`），模拟源降级为回退；离线四用例 PASS（§8.4）。
7. **上板第一步（先做便宜的）**：①对 `[0x20000000,0x20708000)` 做 64 B 对齐写-回读校验并留原始字节；②确认 `[0x12C08000,0x20000000)` 禁区未被本应用触碰（只读核验地址常量与 map）；③读回 `0x18` 确认 2 帧存；④确认 `vcnt` 是否由硬件帧计数推进（若恒 0 则走软件兜底，属预期行为）；⑤**与生产端对 dump 结果块前 0x60 B**，确认 16 B/项步进一致（§6.1 ①）。
8. **上板联调（最高优先）**：①`PARKPTR.READSTR` 在 circular 模式是否随帧更新（决定写侧同步是否可用）；②`vid_out` locked；③VDMA 启动/状态与 SR 错误位；④撕裂观察；⑤DDR 带宽与帧耗时（GT 打点，决定 180 帧能否在 60 s 内跑完）；⑥rgb2dvi/TMDS 出图；⑦真实源是否出现 `src:"real"`（而非 sim/test）。
9. 性能优化（如需 60 fps）：面板局部重绘、按行 flush、必要时把画布改成 RGB565 减半带宽（会改冻结格式，需批准）。
10. 类别名/颜色表（`s5_class_name`/`s5_class_color`）等阶段5 类别定义冻结后替换；`score_q8→百分比` 的换算若阶段5 有定标需复核。
