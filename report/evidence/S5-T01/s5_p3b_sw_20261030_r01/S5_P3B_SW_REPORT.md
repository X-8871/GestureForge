# S5 P3b-sw：HDMI 显示链 PS 侧显示软件报告

- 任务：阶段5 HDMI 显示链 · PS 侧显示软件（P3b-sw）
- 日期：2026-10-30（UTC+8）　版本：**r06**
  （r01→r02 布局/VTC/帧存；r02→r03 帧缓冲迁址 + 有界 RESULT；r03→r04 真实数据源 ABI；
   r04→r05 回退优先级 + 时间戳 0 + vcnt 修正；
   r05→r06：**fps_dis / fps_upd 拆分**、**30 min 长跑模式**、**box_crc / fb_crc**、
   低成本渲染优化（BGR 32 位读、面板/视频按需重绘）——G3 上板验收版）
- 边界：**离线编写 + 编译通过 + 主机端自检（渲染 PNG / 假寄存器堆跑寄存器序列）**。未接触板卡 / JTAG / COM4 / hw_server，未运行 Vivado，未修改 `w4` 仓库文件（只读引用），未 git 提交。
- 工作目录：`D:\tmp\lead\p3b_display_sw_20261030_r01\`

---

## 0. 结论摘要

| 项目 | 结果 |
|---|---|
| ARM 编译/链接 | **exit 0**（compile 0 / link 0 / size 0 / nm 0；警告 0） |
| ELF（有界/默认） | `build/s5_display_app.elf`，**sha256 `62f3595c950ddc24cf4ccb2307e7c35d5777f571ffa42993d92d456367c486f6`**，**309,700 B**（text 47,784 / data 68 / bss 2,354,784） |
| ELF（30 min 长跑） | `build/s5_display_app_longrun.elf`（`-DS5_LONG_RUN=1`），**sha256 `ad1d2e6926edfffbaef1d8f6bd627e858d92df207fe306401b548d269740bb37`**，312,892 B |
| fps 语义（r06） | **`fps_dis` = 显示刷新率**（VDMA 读帧存切换周期实测 ≈60；测不到填 0，不虚填）；**`fps_upd` = 软件渲染速率**（frames/elapsed，如实报告 ≈35） |
| G3 校验字段（r06） | `box_crc` = 绘制用框（映射后 960×720，u16 `[x,y,w,h]` 序列）CRC32；`fb_crc` = 显示用 FB（`0x20000000`，3,686,400 B）CRC32；结束前各算一次 |
| 长跑模式（r06） | `-DS5_LONG_RUN=1`：取消 180 帧上限，只按 1800 s 退出；每 60 s 打 `S5DISP tick t=.. frames=.. vcnt=.. err=..` |
| 真实数据源 | **已接入**：结果块 `0x20800000`（magic `0x53355253`）+ raw `0x12000000`（640×480 BGR888）（§2.5/§2.6） |
| 回退优先级（r05） | `real`（结果块有效）→ `real_nobox`（结果块无效 + raw 有效，无框）→ `test`（raw 全 0，**pass=1 合法上屏自检**）→ `sim`（仅强制模拟或测试图案也失败，pass=0）（§2.6） |
| 时间戳语义（r05） | 结果块 `cap/inf` 全 0 → `age_ms=0`/`latency_ms=0`（未知，不用 now−0 算巨大值）（§2.5） |
| `vcnt` 结论（r05） | **SR 里没有硬件帧计数**（`XAXIVDMA_FRMCNT_MASK` 是 CR[23:16] 的调试字段，需 genlock 语义）→ `vcnt` 改为**纯软件观测** `PARKPTR.READSTR` 切换次数；板上 r04 的 `vcnt=1` 即误读 SR 保留位（§2.2/§6.3） |
| 帧缓冲地址 | **A=`0x20000000`、B=`0x20384000`**，终点 `0x20708000`（**已迁出 `[0x12C08000,0x20000000)` 禁区**，§3.1） |
| 有界运行 + 结果行 | **已实现**：默认 180 帧或 60 s 先到者停机，结束打印单行 `S5DISP RESULT={...}`（失败带 `reason`），进度行 `S5DISP frame=` 独立（§5.3、§8.3） |
| VTC 生成器 | **已实现**（VTC 6.2，720p60）：12/12 寄存器回读校验 OK，负例可检出 MISMATCH（§2.4） |
| VDMA | **2 帧存**（与 BD `c_num_fstores=2` 一致），A/B 双缓冲，只写 0x5C/0x60 两个地址（§2.2） |
| 布局 | **已裁决：无重叠方案**（视频 `x=0..959` + 信息栏 `x=960..1279`），字面 160 黑边方案仅作实验分支（§3.2） |
| 主机渲染自检 | **PASS**，同一份绘图源码渲染出 10 张 1280×720 PNG（两套布局 ×5）+ 180 帧有界运行 → 示例 RESULT |
| 真实源自检 | **PASS**：`real`（真实画面+3 框）、`real_nobox`（真实画面无框，pass=1）、`test`（结果块有效但 raw 空；无生产者）两种 test、stale、时间戳 0；均有离线 RESULT/PNG（§8.4） |
| 寄存器序列自检 | **PASS**（假寄存器堆跑 `vtc_ctrl.c` + `vdma_ctrl.c`：VTC 校验、负例、双缓冲 6 帧决策，§8.2） |
| VDMA 寄存器用法 | **有把握**：逐条来自本机 Vitis 2026.1 的 `axivdma_v6_17` 驱动源码（`xaxivdma_hw.h` + `xaxivdma_channel.c`），非 SG 写序列与驱动实现一一对应；题面里两处猜测已被纠正（§2.3） |
| 未验证 | 全部上板行为：VDMA 实际搬数、VTC 实际时序输出、rgb2dvi/TMDS、DDR 带宽、撕裂/闪烁；真实源只在主机用 fixture 验证，板上需生产端实际写结果块；`src:"sim"` 时 RESULT 的 fps/latency/age 为模拟值（§5.3） |

---

## 1. 交付物

| 文件 | 作用 | sha256 |
|---|---|---|
| `src/s5_display_app.c` | 绘图核心（纯函数）+ 模拟源（仅强制模拟时用）+ 裸机 `main()`（VTC→测试图→VDMA→有界乒乓→真实源回退/RESULT） | `3056ede3785a4f5befa5a4d31c3470b7f3bd33d7963e14d2783c637db04ab432` |
| `src/s5_display_app.h` | 布局/颜色/数据结构/API + 结果行契约（`S5RunStats` 含 `src`）+ `S5_SRC_*` | `e5eb4f08a9eaaffcbae6792bf5354133915d24f201189b13e93c694336eacc6b` |
| `src/s5_result_abi.h` | **结果块 ABI**（0x20800000）+ raw 画面（0x12000000）+ 编译期尺寸断言 | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c` |
| `src/s5_real_source.h/.c` | 真实源：块解析/一致性检查、时间戳→age/latency（0=未知）、BGR→画布、空白检测、FPS 窗口 | `69893792604e156ec33de551ae152f92c8f494b9d0c152c1924e1a5085463720` / `4fc1fc04a17e0d7289a2439958d79acc48ab824920276bb035ecbeae7f7a3521` |
| `src/vdma_ctrl.c` | axi_vdma 6.3 MM2S 非 SG 寄存器级初始化/启动/状态（r05 移除错误的“硬件帧计数”读法） | `7adba3a04113f17ec9bf093c35bc0a609be17025c5f13b4780fe6226ac56fd41` |
| `src/vdma_ctrl.h` | 寄存器偏移表 + 依据注释 + API（含 r05 帧计数结论） | `3197a087595966a3200cee63380400ca7d6671382834b929d01e15d911d673c6` |
| `src/vdma_ctrl.h` | 寄存器偏移表 + 依据注释 + API（含 FRMCNT_EN/帧计数） | `e0bc10050626f665e5e89c0bf02cba2234c09d2af702117c08e4534c7a498bce` |
| `src/vtc_ctrl.c` | v_tc 6.2 生成器初始化（720p60）+ 回读校验 + 文本摘要 | `8ba7d212b4f5d5ec2781bc84b9041cbe218dd935596644acd72de5bf532b6fa6` |
| `src/vtc_ctrl.h` | VTC 寄存器偏移/位域/结构 + 依据注释 | `68d1555cd3a78aff5d206a90229c1184cdd096b3c00f09b441ecb42c24162458` |
| `src/s5_timebase.h/.c` | 全局定时器 64 位读取、宏括号坑的编译期断言 | `3a2e9c8e3da8b4f6c2ea72755d5b428d241788d5da18d15e4b688072d469d64a` / `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/s5_font8x16.h` | 自带 8×16 ASCII 点阵字库（95 字符 ×16 B，自动生成） | `2f26b78b1098b974c60ee2a1d173107c5b44ef8f8f19dbdc4b599ef93a2d50d3` |
| `tools/gen_font8x16.py` | 字库生成器（DejaVu Sans Mono 11 px 栅格化，可复现） | `b9c5a583435d7120f76ae36b17df4a761f347cd1983866fefc66a0b2e3c04b87` |
| `tools/host_render_test.c` | 主机端离线渲染自检 + 180 帧有界运行（同一份绘图/结果行代码） | `8d63ac1cf8cadccd8d2be39394c6cc4862a522bdccba9bc18e35d16401b070a5` |
| `tools/real_source_selftest.c` | **真实源自检**：6 个用例（real / real_nobox / test×2 / stale / 时间戳 0） | `e141c68282327e8c847a3f03db592c59ae7bdb3463bf3044d16801726d816ca2` |
| `tools/vtc_vdma_selftest.c` | 假寄存器堆离线自检：VTC 校验 + 负例 + VDMA 双缓冲决策 | `b8b546bfa08a910dd04b61075ebfecb05adc9e7feda8db0df0e247c0f7b8f808` |
| `tools/host_xil_shim/xil_io.h` | 主机自检用 `Xil_In32/Xil_Out32` 替身声明（不进 ARM 构建） | `1844e41d2b61f00af0a278d7d7147bdaca605318e24bf7e65155cc40f566e263` |
| `fixtures/fixture_fist_000_640x480_bgr888.raw` | 真实画面 fixture 副本（640×480 BGR888，921,600 B，来自 S4-T34 bringup） | `ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4` |
| `build_s5_display_app.py` | 一键构建 + 四方自检（渲染/寄存器/真实源）+ 证据记录 | `e7847d0de177516dac2adddb20c6f0f9d18d5adcf9f25ea7f74693ac0124889a` |
| `build/` | ELF、map、build_record.json、构建日志、`selftest_*.txt`、15 张 PNG | — |

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

**帧计数（结果行 `vcnt`）——r05 结论：axi_vdma 6.3 没有可用的硬件帧计数**
（本机 `axivdma_v6_17` 驱动源码核对）：
- `xaxivdma_hw.h` 的 **SR 掩码只到 bit14**（HALTED/IDLE/ERR[11:4]/IXR[14:12]），**没有帧计数字段**；
- `XAXIVDMA_FRMCNT_MASK (0x00FF0000)` 是 **CR（0x00）的 bit[23:16]**，且
  `XAxiVdma_ChannelGetFrmCnt()` 读的是 **CR** 并受 `XAXIVDMA_ENABLE_DBG_FRM_CNTR`（IP 调试特性）门控；
  它是配合 genlock 的“帧计数/延时计数”调试字段，**不是** MM2S 每帧递增的进度计数。
- 因此 r04 用 `SR[23:16]` 当帧计数是**读错位置**；板上 `vcnt=1` 正是读到了 SR 保留位/未定义位。
- r05 起 `vcnt` **只做软件观测**：主循环每帧读 `PARKPTR.READSTR`（当前读帧存号），变化次数即“VDMA 消耗帧数”的代理
  （2 帧存时每个显示帧切换一次）。`S5Vdma_UpdateFrameCount()/EnableFrameCounter()` 已删除，`Start()` 也不再置 `FRMCNT_EN`。

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

**时间戳 0 的语义（r05，lead 定）**：`cap_lo/cap_hi` 与 `inf_lo/inf_hi` 全 0 表示**生产者尚未拿到时间戳**，
读端按“未知”处理：`age_ms=0`、`latency_ms=0`（**不得**用 `now−0` 算成几十秒的巨大值）；`cap` 或 `inf` 单独为 0 时只把对应那一项置 0。
时间戳“在未来”（时钟还没走到）同样按 0 处理，避免无符号回绕。面板显示 `AGE 0 ms OK`、`LAT 0 ms`。

### 2.6 真实源与回退逻辑（**r05 优先级**）

```
每帧：
  invalidate(结果块 0x120 B) → S5Real_Parse()
  invalidate(raw 921,600 B，空白时每 15 帧复检) → S5Real_IsBlank()
  ├─ 结果块有效 + raw 有内容  → src="real"        ：真实画面 + 结果框
  ├─ 结果块有效 + raw 全 0    → src="test"        ：测试图案 + 结果框（reason="raw_frame_blank"）
  ├─ 结果块无效 + raw 有内容  → src="real_nobox"  ：真实画面、无框（reason=解析失败原因；pass 仍为 1）
  ├─ 结果块无效 + raw 全 0    → src="test"        ：测试图案（pass=1：无生产者时的合法上屏自检）
  └─ 仅 S5_SOURCE_REAL=0 或测试图案也画不出来 → src="sim"（pass=0）
```

- **r05 关键点**：`test` 不再是 `pass=0`。P3b 冒烟阶段生产端未实现，"无输入源时用测试图案证明上屏链路"是**合法通过态**；
  判据没有放宽——显示健康（VDMA 无错 + ≥1 帧完整显示 + 面板刷新）三条仍然逐条检查，只是 `sim` 才是失败态。
- **面板**：`SRC REAL/REAL_NB/TEST/SIM` 一行可见；`status.bit2` → AGE 行显示 `STALE`（黄色），`bit1` → `SRC ... OVR`。
- **时间戳**：`cap/inf` 为 0 视为“未知”→ `age_ms=0`/`latency_ms=0`；非 0 才用 `now−t` 换算（先乘后除，64 位）。
- **缓存一致性**：结果块/raw 都是 DMA 写、CPU 读 → 读前 `Xil_DCacheInvalidateRange`（`S5_DCACHE_FLUSH=1` 时生效）。
- **编译期开关**：`S5_SOURCE_REAL=1`（默认）；置 0 强制纯模拟（此时 `src="sim"`、`reason="real_source_disabled"`、pass=0）。
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
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"src":"sim"}
```

| 字段 | 单位/取值 | 说明 |
|---|---|---|
| `pass` | 1 / 0 | 链路健康（VDMA 无错 + ≥1 帧完整显示 + 信息栏刷新成功）**且** `src≠"sim"`；`src="test"` 仍算通过（显示可用）但带 `reason` |
| `fps_cap` | **整数 fps 0..60**（不是 ×10） | 采集口径；真实源取时间戳窗口，模拟源取模型值 |
| `fps_inf` | **整数 fps 0..60** | 推理口径；真实源取 `inf` 时间戳窗口，模拟源固定 0（契约允许） |
| `fps_dis` | **整数 fps 0..60** | **显示刷新率**（r06：VDMA 读帧存切换周期实测 ≈60；测不到填 0，见 §11） |
| `fps_upd` | 整数 fps | **软件更新（渲染）速率** = frames / elapsed，如实报告（r06 新增，G3 板上 ≈35；优化后见 §11） |
| `latency_ms` | 整数毫秒 | 显示延迟 = now − t_infer_done；真实源由 ticks 换算（**时间戳 0 = 未知 → 0**），模拟源为模型值 |
| `age_ms` | 整数毫秒 | 结果年龄 = now − t_capture_end；真实源由 ticks 换算（**时间戳 0 = 未知 → 0**），模拟源为模型值（每 47 帧注入超龄） |
| `vdma_err` | 计数 | 运行期间 SR 错误位（`XAXIVDMA_SR_ERR_ALL`）累计次数 |
| `frames` | 计数 | 实际渲染帧数 |
| `vcnt` | 计数 | **软件观测**：`PARKPTR.READSTR` 变化次数（r05；SR 无硬件帧计数，见 §2.2） |
| `box_crc` | u32（十进制） | **r06 G3**：绘制所用检测框（映射到画布 960×720 的 `x,y,w,h` 各 u16 顺序拼接）CRC32 |
| `fb_crc` | u32（十进制） | **r06 G3**：显示用 framebuffer `0x20000000`（1280×720×4 = 3,686,400 B）CRC32，结束前算一次 |
| `src` | `"real"` / `"real_nobox"` / `"test"` / `"sim"` | 本窗口数据源；回退优先级见 §2.6（r05 增加 `real_nobox`） |
| `reason` | 字符串（非 NULL 即输出） | `result_magic_mismatch` / `result_not_valid` / `result_torn` / `result_shape_invalid` / `raw_frame_blank` / `real_source_disabled` / `vdma_init_failed` / `vdma_error` / `no_frame_rendered` / `frame_check_failed` |

**各 src 的判据差异**（r05）：

| | `src="real"` | `src="real_nobox"` | `src="test"` | `src="sim"` |
|---|---|---|---|---|
| 触发条件 | 结果块有效 + raw 有内容 | 结果块无效 + raw 有内容 | raw 全 0（结果块有无均可） | 仅 `S5_SOURCE_REAL=0` 或测试图案也失败 |
| 画面 | 真实 raw | 真实 raw | 测试图案（棋盘 + 红字） | 模拟画面 |
| 检测框 | 结果块 | **无**（无结果块） | 有结果块时仍画 | 模拟源 |
| `pass` | 1 | **1** | **1**（合法上屏自检） | **0** |
| `reason` | 无 | 解析失败原因 | `raw_frame_blank` 或解析失败原因 | `real_source_disabled` 等 |
| age/latency | 真实 ticks | 0/0（时间戳未知） | 真实 ticks 或 0/0 | 模型值 |

**通过判据实现**（`S5Display_CheckFrame()` 抽点自检）：视频区（摄像头/棋盘）抽样 ≥8 个非黑点；
信息栏**标题条**（y=6..20、x=970..1160）抽样 ≥20 个非面板底色点 —— 标题条是实心填色带，用它判断“信息栏确实刷新过”，
比随机抽文字像素稳健（文字覆盖率低会误判）。

**进度行**（与 RESULT 行分开，绝不拼在同一行）：
```text
S5DISP frame=60 lat=... age=... st=... sr=...
```
每 60 帧一行；结束后另有 `S5DISP done frames=... vcnt=...(sw) vdma_err=...` 一行，再打 RESULT 行。

**失败也打 RESULT**（`pass:0` + `reason`，同样单行）：
```text
S5DISP RESULT={"pass":0,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"src":"sim","reason":"vdma_init_failed"}
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
12. **`vcnt` 的现场观察（r05 结论）**：r04 上板 `vcnt=1`，与本机驱动源码比对后确认是**读错寄存器**——SR 里没有帧计数，
    `XAXIVDMA_FRMCNT_MASK` 是 CR[23:16] 的调试字段（需 `XAXIVDMA_ENABLE_DBG_FRM_CNTR` + genlock 语义）。
    r05 已删除该读法与 `CR.FRMCNT_EN`，`vcnt` 改为软件观测 `PARKPTR.READSTR` 变化次数；若后续联调发现
    `READSTR` 在 circular 模式下也不更新，则 `vcnt` 只能反映“软件看到的帧存切换”，届时需用 VDMA 帧中断计数替代（§6.2-5）。

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
| 真实数据源自检（real / real_nobox / test×2 / stale / ts=0） | **0**（PASS，见 §8.4） |

产物：`build/s5_display_app.elf`（**294,932 B，sha256 `8b40c3a8…` 见 §0**）、`build/s5_display_app.map`、`build/build_record.json`（输入/输出哈希、命令、退出码、限制项、四方自检结果）、`build/selftest_vtc_vdma.txt`、`build/selftest_real_source.txt`、`build/host_*_test*.exe`、`build/*.png`。

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
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"src":"sim"}
```

失败路径（同一函数，`pass:0` + `reason`，仍为单行）：
```text
S5DISP RESULT={"pass":0,"fps_cap":30,"fps_inf":0,"fps_dis":59,"latency_ms":19,"age_ms":31,"vdma_err":0,"frames":180,"vcnt":180,"src":"sim","reason":"vdma_init_failed"}
```
说明：`fps_cap=30 / fps_dis=59 / latency_ms=19 / age_ms=31` 均来自**模拟数据源**（`S5Sim_NextFrame`），
`fps_inf=0` 按契约（无真实推理源）；`vcnt=180` 是离线模拟值（板上取硬件帧计数，见 §2.2）。
`pass=1` 的成立依据：`S5Display_CheckFrame()` 对最后一帧的抽点自检通过（视频区 36/64 非黑点、
信息栏标题条 80/80 非底色点，远高于阈值 8 / 20）。

### 8.4 真实数据源自检（r05，`tools/real_source_selftest.c`）

同一份 `s5_real_source.c` + `s5_display_app.c` 在主机跑，假时钟由测试推进（60 Hz 显示、30 Hz 新结果）：

```text
case1 (real): S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":59,"latency_ms":7,
                             "age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"src":"real"}
case1 status=0x0003 det=3 age=31 lat=7
case (magic_bad=1 raw_blank=0): S5DISP RESULT={"pass":1,...,"latency_ms":0,"age_ms":0,
                             "frames":1,"vcnt":0,"src":"real_nobox","reason":"result_magic_mismatch"}
case (magic_bad=0 raw_blank=1): case3 det=1（测试图案上仍画框）→
  S5DISP RESULT={"pass":1,...,"latency_ms":7,"age_ms":31,"frames":1,"vcnt":0,"src":"test","reason":"raw_frame_blank"}
case (magic_bad=1 raw_blank=1): S5DISP RESULT={"pass":1,...,"latency_ms":0,"age_ms":0,
                             "frames":1,"vcnt":0,"src":"test","reason":"result_magic_mismatch"}
case5 (stale): status=0x004B stale_bit=1 age=49 ms
case6 (ts=0): age=0 ms latency=0 ms（应为 0/0）
==== real-source selftest: PASS ====
```

| 用例 | 验证点 | 产物 |
|---|---|---|
| case1 `real` | 3 框坐标/分数解析、`age=now−cap`、`latency=now−inf`、fps 窗口、`pass=1` | `build/frame_real.png`（真实画面 + 3 框 + `SRC REAL`，FPS C 30.6 / I 29.9 / D 59.9） |
| case2 `real_nobox` | magic 错 + raw 有效 → 真实画面、**无框**、`pass=1`、`reason=result_magic_mismatch`、age/latency=0 | `build/frame_real_nobox.png`（`SRC REAL_NB`、`DET 00`） |
| case3 `test`（有结果、raw 空） | 测试图案 + 仍画结果框、`pass=1`、`reason=raw_frame_blank` | `build/frame_test_with_boxes.png` |
| case4 `test`（无生产者，magic 错 + raw 空） | 测试图案、`pass=1`、`reason=result_magic_mismatch`、age/latency=0 | `build/frame_test_no_producer.png`（棋盘 + 红字提示） |
| case5 stale | `status.bit2` → `S5_ST_STALE`、面板 AGE 行 STALE | `build/frame_stale.png` |
| case6 时间戳 0 | `cap=inf=0` → `age_ms=0`、`latency_ms=0`（不用 now−0） | —（printf 断言） |

> 说明：fixture 为 `fixtures/fixture_fist_000_640x480_bgr888.raw`（S4-T34 bringup 的 640×480 BGR888，sha256 `ce37aa77…`，副本）。
> 图上真实画面/框/文字都在，说明 **ABI 解析 → 坐标映射 → 960×720 缩放 → 面板**整条链路在主机侧是通的；上板差异只在数据来源与缓存一致性。

---

## 9. 真实数据源接线（r04 已接，r05 调整回退优先级）

**已实现**：`src/s5_real_source.c` 每帧读结果块 + raw，板上一旦没有生产端，就按 §2.6 落到 `test`（合法通过态）或 `real_nobox`。
板上接线只剩“地址与缓存”两件事，均由宏/常量给出：

| 项 | 值 / 位置 | 说明 |
|---|---|---|
| 结果块 | `0x20800000`（`S5_RESULT_BASE`） | 生产端（chain-lite A 派生）写；读端每帧 invalidate 0x120 B |
| raw 画面 | `0x12000000`（`S5_RAW_FRAME_BASE`） | 640×480 BGR888；读端每帧 invalidate 921,600 B |
| 时间戳 | 结果块 cap/inf（全局定时器 ticks） | `age=now−cap`、`latency=now−inf`，`S5_GT_HZ=333333343` 换算；**0 = 未知 → age/latency=0** |
| 结果年龄上限 | 33 ms | 超限 → `AGE OVER`；`status.bit2` → `STALE` |
| `vcnt` | 软件观测 `PARKPTR.READSTR` 切换 | **无硬件帧计数**（§2.2 结论） |
| 开关 | `S5_SOURCE_REAL`（默认 1） | 0 = 强制纯模拟（`src="sim"`、pass=0） |

| `S5FrameInfo` 字段 | 真实源来源 | 模拟回退 |
|---|---|---|
| `frame_id` | 结果块 `frame_id` | 自增 |
| `fps_*_x10` | cap/inf/dis 时间戳窗口（×10，面板用） | 模型值 |
| `latency_ms` / `age_ms` | `now − inf` / `now − cap`（ticks→ms） | 17 ms / 30 ms + 抖动 |
| `det[]` | 结果块 16×16 B（原图 640×480 坐标） | 1~3 个移动框 |
| `status` | VALID/OVERRUN/STALE + 超龄判定 | CAM_OK/INF_OK/AGE_OVER |
| `src_kind` | REAL / REAL_NOBOX / TEST / SIM | SIM |

> 原来的“替换 `S5Sim_NextFrame()`”动作**不再需要**；现在只需要生产端按 §2.5 的 ABI 写块、相机/DMA 填 raw。
> **r05 现场观察回填**：P3b 冒烟（2026-10-30，PL/VTC/VDMA/渲染都在跑，`fps_dis=59`、180 帧、`vdma_err=0`、2.6 s 收到 RESULT）
> 但 `pass=0` —— 原因是当时“结果块无效 ⇒ 直接 sim ⇒ pass=0”。按 lead 裁决改为：无生产者时 `src="test"` 是**合法通过态**（见 §2.6）。

---

## 10. 待办（按优先级）

1. ~~裁决 §3.2 布局~~ —— **已完成**：默认 L0（无黑边、无重叠），L1 仅作实验分支。
2. ~~补 VTC 编程~~ —— **已完成（离线）**：`vtc_ctrl.c` 720p60 + 回读校验 + 负例；上板仍需验证实际时序输出。
3. ~~确认 `c_num_fstores`~~ —— **已按 2 实现**（与 BD 对齐）；上板读回 0x18 复核一次。
4. ~~有界运行 + 结果行~~ —— **已完成**：180 帧/60 s 停下 + 单行 `S5DISP RESULT=`（失败带 `reason`），离线示例见 §8.3。
5. ~~帧缓冲迁出禁区~~ —— **已完成**：A/B = `0x20000000`/`0x20384000`。
6. ~~接真实数据源~~ —— **已完成**：结果块 ABI + raw 画面 + 回退（`src`/`reason`）。
7. ~~回退优先级 + 时间戳 0 + `vcnt`~~ —— **r05 已完成**：`test` 为合法通过态、新增 `real_nobox`；`cap/inf=0 → age/latency=0`；`vcnt` 改纯软件观测（§2.2/§2.6/§8.4）。
8. **上板第一步（先做便宜的）**：①对 `[0x20000000,0x20708000)` 做 64 B 对齐写-回读校验并留原始字节；②确认 `[0x12C08000,0x20000000)` 禁区未被本应用触碰（只读核验地址常量与 map）；③读回 `0x18` 确认 2 帧存；④复测 `vcnt`：现在应接近 `frames`（软件观测 read-store 切换次数），若恒 0 说明 `PARKPTR.READSTR` 在 circular 模式不更新（转 §6.2 的帧中断方案）；⑤**与生产端对 dump 结果块前 0x60 B**，确认 16 B/项步进一致（§6.1 ①）。
9. **上板联调（最高优先）**：①`PARKPTR.READSTR` 在 circular 模式是否随帧更新（决定写侧同步是否可用）；②`vid_out` locked；③VDMA 启动/状态与 SR 错误位；④撕裂观察；⑤DDR 带宽与帧耗时（GT 打点，决定 180 帧能否在 60 s 内跑完）；⑥rgb2dvi/TMDS 出图；⑦真实源是否出现 `src:"real"`（而非 `real_nobox`/`test`）。
10. 性能优化（如需 60 fps）：面板局部重绘、按行 flush、必要时把画布改成 RGB565 减半带宽（会改冻结格式，需批准）。
11. 类别名/颜色表（`s5_class_name`/`s5_class_color`）等阶段5 类别定义冻结后替换；`score_q8→百分比` 的换算若阶段5 有定标需复核。

---

## 11. r06（G3 上板验收版）：fps 拆分、长跑、CRC、渲染优化

### 11.1 `fps_dis`（显示刷新）与 `fps_upd`（软件更新）的测量方法

| 字段 | 定义 | 测量方法 | 本机样例 |
|---|---|---|---|
| `fps_dis` | **显示刷新率**（VDMA 每输出一帧 = TMDS 一次刷新） | 启动后 `S5Vdma_MeasureReadPeriod()` 轮询 `PARKPTR.READSTR`，取 6 个切换边沿、相邻边沿平均间隔即显示帧周期 → `fps = GT_HZ / 周期`；200 ms 内凑不够边沿则 `fps_dis=0` 并打印 WARN（**不虚填 60**） | 板上冒烟 60（≈16.7 ms）；离线自检写 60 |
| `fps_upd` | **软件更新（渲染）速率**：每秒完成多少帧“取数+绘制+flush” | `frames / elapsed_ms`（整段运行统计，RESULT 用）；面板用最近窗口（`S5FpsWin`，每帧打点） | 板上 r02 冒烟 35；离线自检 60（假时钟 16.667 ms/帧） |
| `fps_cap` / `fps_inf` | 采集/推理结果速率 | 结果块 `cap`/`inf` 时间戳窗口（只在 `frame_id` 变化时计入） | 离线 30 / 29 |
| `latency_ms` / `age_ms` | 显示延迟 / 结果年龄 | `now − inf` / `now − cap`；**时间戳 0 = 未知 → 0**（r05 语义不变） | 7 / 31 |

> 为什么之前 `fps_dis=35`：r05 的 `fps_dis` 实际统计的是“软件主循环频率”，与显示刷新混用了同一字段。P3b 里
> VDMA 以 60 Hz 从 framebuffer 取帧，**显示刷新恒 60**，而软件画一帧要 ~28 ms → 35 fps。r06 把两者分开，
> 现场应以 `fps_dis≈60`（J-4）与 `fps_upd` 如实值分别判读。

### 11.2 长跑模式（S6-F 30 min）

- 编译期开关：`-DS5_LONG_RUN=1`（默认 0）。开启后帧数上限取消，只受 `S5_RUN_MAX_MS_LONG=1800000`（1800 s）约束。
- 心跳：每 60 s 打一行（与 RESULT/进度行分开）
  `S5DISP tick t=0 frames=1980 vcnt=1980 err=0`（`t` 秒、累计帧、vcnt、错误数）——用于判断是否死锁/停滞。
- 交付两个 ELF：默认有界 `s5_display_app.elf`（180 帧/60 s）与长跑 `s5_display_app_longrun.elf`（1800 s）。

### 11.3 G3 校验字段与进度行（r06）

- `box_crc`：**绘制所用检测框**（映射到画布 960×720 的 `x,y,w,h`，各按 u16 顺序拼接）的 CRC32（IEEE，`0xEDB88320`，初值/结果异或 `0xFFFFFFFF`）。
  与 `S5Draw_Boxes` 同映射（含 `S5_VID_X/Y` 偏移）；宽/高 ≤0 的框不画也不入 CRC。
- `fb_crc`：**显示用 framebuffer** `0x20000000` 整帧 3,686,400 B 的 CRC32；在最后一帧写完后（先 `Xil_DCacheInvalidateRange`）算一次。
- 进度行追加现场信息（每 60 帧）：`S5DISP frame=60 lat=.. age=.. st=.. sr=.. src=real nbox=3`。
- 实现自检：CRC32 已知答案 `"123456789" → 0xCBF43926`；`box_crc` 确定性/灵敏度检查；优化版 BGR→RGB 与逐像素参考实现逐像素一致（均 PASS，§8.4）。

### 11.4 低成本渲染优化（不改语义）

1. **BGR888→RGB 32 位读**：4 像素/12 B 一组，3 次 `memcpy` 32 位读 + 4 次写（原为 12 次字节读）；输出与参考实现逐字节一致（主机自检）。
2. **行级/列级映射 LUT**：letterbox 列/行源索引预计算一次（此前已实现），内层循环无乘除。
3. **D-cache 只按帧维护**：每帧 1 次结果块 invalidate + 1 次 raw invalidate（不逐像素）；fb 每帧 flush 一次。
4. **面板/视频按需重绘**：信息栏按数值签名缓存——同一 buffer 上数值未变则整栏跳过；仅数值变化时清 y=28..372 动态区重画（标题条/图例/页脚只画一次）；静态测试图案且无框时视频区不重复绘制（真实画面每帧重画）。
5. 效果：离线无法测 A9 实际 fps；按像素/内存访问量估算，视频区与面板的重复绘制分别省去（测试图案场景）与约 1/4 逐像素工作量，目标 `fps_upd≥45` 需板上实测确认（本报告不虚报）。

### 11.5 r06 离线示例 RESULT（含新字段）

```text
case1 (real): S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":60,"fps_upd":60,"latency_ms":7,"age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"box_crc":1255179135,"fb_crc":2461129793,"src":"real"}
```
（`fps_dis=60` 为离线假设值，板上由 VDMA 帧周期测量；`fps_upd=60` 由假时钟 36×16.667 ms 算得。）

构建：`python build_s5_display_app.py` → **exit 0**，零告警；主 ELF sha256 `62f3595c…` / 309,700 B；
长跑 ELF sha256 `ad1d2e69…` / 312,892 B；主机四方自检（渲染/寄存器/真实源）全 PASS。


### 11.6 box_crc 口径（r06b，G3-B 对齐，ABI 的一部分）

- **字段**：绘制所用检测框，映射到**显示坐标 960×720** 的 x,y,w,h（**边界裁剪后**；宽/高≤0 的框不画也不入 CRC）。
  映射与 `S5Draw_Boxes` 完全一致：`x_disp = S5_VID_X + x_src*3/2`（L0 下 `S5_VID_X=0`），y 同理，w/h 同乘 3/2 后裁剪到 `[0,959]×[0,719]`。
- **顺序**：每框 x,y,w,h 依次；框顺序 = 结果块 index 0..n-1。
- **打包**：每字段 **u16 小端**，连续无填充，共 `nbox×8` 字节。
- **CRC 参数**：CRC-32/ISO-HDLC（poly 0x04C11DB7，init/xorout 0xFFFFFFFF，refin/refout=true）= zlib `crc32`。
- **范围**：只算有效框，不含 magic/nbox/时间戳等头字段。

**G3-B 给定 3 框的离线复算（与 lead 期望一致）**：
`(100,80,120,200) (500,300,100,100) (0,0,640,480)` → 映射 `(150,120,180,300) (750,450,150,150) (0,0,960,720)`
→ 24 B 序列 `96 00 78 00 B4 00 2C 01 | EE 02 C2 01 96 00 96 00 | 00 00 00 00 C0 03 D0 02`
→ **`0x2D949C0C` = 764,713,996**（`build/selftest_real_source.txt` 的 `G3-B box_crc` 行，`PASS`）。
说明：若板上实报不同，则差异在**解析到的框坐标**而非 CRC 约定（已排除 12 B/10 B 步进、BE、u32 字段等布局；这些都给不出 0x16F1116D）。
r06b 起 RESULT 前多打一行诊断（直接给出 CRC 用的映射后坐标，便于对字节）：

`S5DISP boxes n=3 crc=764713996 hex=96 78 b4 12c ee2 c2 96 96 0 0 3c0 2d0`（示例，%x 无前导零）

**r06b ELF**：默认 `e392aa9676b783955c8a70d32040919e457d125959a1c1fa156f2f34ceb6810d` / **310,740 B**（text 48,192 / data 68 / bss 2,354,784）；
长跑 `ab96f6e890676e4d500d5c6192cd2b218a23e2fa693738f7985516b3be269bc3` / 313,940 B。
