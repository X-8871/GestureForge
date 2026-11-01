# S5 P3b-sw：HDMI 显示链 PS 侧显示软件报告

> **⚠ 勘误横幅（2026-10-31 R-10）**：本报告 §0/§1/§11.5/§11.10–§11.13 中出现的 ELF/源码哈希是**历史轮次构建快照**（r06–r06j 各自时点），不代表当前产物。**权威身份**以 `S5_SW_FREEZE_CHECKLIST.md`（sha256 `5148fca0099f2c50697eea0973974a0f503e4313ba33ad8e5a778161e89b6b1f`）、`build/build_record.json`（sha256 `035bca3a9bac4292da3d08cbd6d25b7cc64a115f12369998f37ee732a9477cc7`，构建 2026-10-30T22:05:14+08:00；阶段5 清单引用的 `58117d07…` 为其 18:48 时点旧值，22:05 重构后记录已重写）与 P3q 生产者冻结件 `S5_PRODUCER_V2_FREEZE.md`（**rev5 / 身份 A**，sha256 `1ec638660b229a087e47be051fc2a24cab69e37edf767af50f60665756407d69`；rev1–rev4 均已作废，产物存 `build/rev2_archived/`、`build/rev3_archived/`、`build/rev4_archived/`）为准。
> 本文 §0/§1 已于 2026-10-31 00:55 就地更新为**磁盘现值**；§11.14 为 22:05 生产者 v2 套件索引；其余历史节保留原快照并加注。代码未改、未重编（R-10 纯文档）。

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
| ELF（有界/默认，P3q 显示） | `build/s5_display_app.elf`，**sha256 `e4ba0cb47181edb5c5c20ad1826bcdb67225782c19ed4d8ec2309d0107b33f63`**，**285,572 B**（text 44,352 / data 68 / bss 2,354,528）——截至 2026-10-31 00:55 磁盘现值 |
| ELF（30 min 长跑 / idleprobe） | `s5_display_app_longrun.elf` **sha256 `cbf5ebe395f21b358356bd4ce9325071e252fcb9d4529a64a06f8ddd17c74577`**，288,772 B；`s5_display_app_idleprobe.elf` **sha256 `2c880e4e539f2e322f45c9f6c3a24f1f798c6c851d0177f496c28f13bfbcb1d8`**，289,532 B（同为磁盘现值） |
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

| 文件 | 作用 | sha256（截至 2026-10-31 00:55 磁盘现值） |
|---|---|---|
| `src/s5_display_app.c` | 绘图核心 + 模拟源 + 裸机 `main()`（测试图→VDMA→有界乒乓→真实源回退/RESULT）+ 生产者 v1/v2（`S5_PRODUCER`） | `b2ec56e0a978099b861823685a69e4557dd3dcae8a73abc6ddb08597ebb81398` |
| `src/s5_display_app.h` | 布局/颜色/数据结构/API + 结果行契约 + 生产者宏（`S5_PRODUCER`/`S5_PROD_*`） | `86a32db4e4432458696f02af5fab4b317aead261eac163f364287605505887e5` |
| `src/s5_publish_abi.h` | **生产者 v2 sidecar `S5X1`**（0x20800100）+ seqlock/seq/业务状态定义（r06j 新增，未改 32 B ABI） | `4ae380146e1351d8839d4ed5ba24f5bd28d9902549697692caf826a4b735b043` |
| `src/s5_result_abi.h` | **结果块 ABI**（0x20800000）+ raw 画面（0x12000000）+ 编译期尺寸断言（**r06j 起未改**） | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c` |
| `src/s5_real_source.h` / `.c` | 真实源：块解析/一致性检查、时间戳→age/latency（0=未知）、BGR→画布、空白检测、FPS 窗口 | `c6d50b3361074d642941173f89fd23eb66867e508d203eb9465af65577416948` / `cec077a102105c1fb755afc9f19a4b131909aa411d31d3de27e6969a402a50e8` |
| `src/vdma_ctrl.c` | axi_vdma 6.3 MM2S 非 SG 寄存器级初始化/启动/状态 + READSTR 周期测量（fps_dis） | `bb32bcbebe220a38ad19000a660929834f563a0fe6b82b7968160833da17eff8` |
| `src/vdma_ctrl.h` | 寄存器偏移表 + 依据注释 + API（PCAP 帧计数结论、fsync 位） | `5634859380f47c7c9d1072907eafbccc8253add014319a36cd1d7af40af83db1` |
| `src/vtc_ctrl.c` / `.h` | v_tc 6.2 生成器初始化（720p60）+ 回读校验（P3q 不调用，保留） | `8ba7d212b4f5d5ec2781bc84b9041cbe218dd935596644acd72de5bf532b6fa6` / `68d1555cd3a78aff5d206a90229c1184cdd096b3c00f09b441ecb42c24162458` |
| `src/s5_timebase.h` / `.c` | 全局定时器 64 位读取、宏括号坑的编译期断言 | `3a2e9c8e3da8b4f6c2ea72755d5b428d241788d5da18d15e4b688072d469d64a` / `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/s5_font8x16.h` | 自带 8×16 ASCII 点阵字库（95 字符 ×16 B） | `2f26b78b1098b974c60ee2a1d173107c5b44ef8f8f19dbdc4b599ef93a2d50d3` |
| `tools/gen_font8x16.py` | 字库生成器（DejaVu Sans Mono 11 px 栅格化，可复现） | `b9c5a583435d7120f76ae36b17df4a761f347cd1983866fefc66a0b2e3c04b87` |
| `tools/host_render_test.c` | 主机离线渲染自检（含确定性测试图）+ 有界运行 | `edec1529dfc3b6911bc8550e9991ff41f586c5718b86d3615d148cc0452f1077` |
| `tools/real_source_selftest.c` | 真实源自检 6 用例 + 生产者 case0c/case0d（sidecar/seqlock/seq/业务状态） | `a64fa0e354428c46b327688f7d891f3e937a758a99f3e97221ebc7b11691363e` |
| `tools/vtc_vdma_selftest.c` | 假寄存器堆自检：VTC 校验 + 负例 + VDMA 双缓冲决策 + fsync 位 | `a6e4fa341ea1e8d1d3c6a622609d72889fb04183100e470f78ad68e3b86d4294` |
| `tools/host_xil_shim/xil_io.h` | 主机自检用 `Xil_In32/Xil_Out32` 替身声明 | `1844e41d2b61f00af0a278d7d7147bdaca605318e24bf7e65155cc40f566e263` |
| `fixtures/fixture_fist_000_640x480_bgr888.raw` | 真实画面 fixture（640×480 BGR888，921,600 B） | `ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4` |
| `build_s5_display_app.py` | 一键构建 + 主机自检 + 证据记录（含 diganostic 变体与生产者 v2 套件） | `4cc8bc8b3539efee27611a58ddd67f727791b15ca9ea41c12561b22fd2005118` |
| `build/` | ELF、map、build_record.json、构建日志、`selftest_*.txt`、17 张 PNG | — |

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

构建：`python build_s5_display_app.py` → **exit 0**，零告警；主 ELF sha256 `e4ba0cb4…` / 285,572 B；
长跑 ELF sha256 `cbf5ebe3…` / 288,772 B；idleprobe `2c880e4e…` / 289,532 B（2026-10-30T22:05:14 构建，磁盘现值）；
主机四方自检（渲染/寄存器/真实源/生产者 v2）全 PASS。


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

### 11.7 空闲测速模式（r06c，G3-A 定位实验）

开关：`-DS5_IDLE_PROBE=1`（默认 0）。行为：正常渲染 `S5_IDLE_PROBE_FRAMES=10` 帧后**停止写帧存**（显示继续由 VDMA 读最后两帧维持），
在 `S5_IDLE_PROBE_MS=3000` 窗口内每帧轮询 `PARKPTR.READSTR`，统计切换次数与相邻边沿平均间隔，打印：

`S5DISP idle fps_dis=60 period_us=16667 frames=10 vcnt=190 err=0`（示例，离线模拟值）

随后正常进入 RESULT，新增两个字段（未开启探针时为 0，不虚填）：

- `fps_dis_idle`：空闲窗口内测得的显示刷新率 = `edges×1000/窗口ms`；
- `idle_period_us`：空闲窗口内相邻 READSTR 切换的平均周期（µs）。

RESULT 示例（探针构建，离线模拟）：
`S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":0,"fps_dis":45,"fps_upd":28,"fps_dis_idle":60,"idle_period_us":16667,"latency_ms":0,"age_ms":0,"vdma_err":0,"frames":10,"vcnt":190,"box_crc":1255179135,"fb_crc":2461129793,"src":"real"}`

判读（按 lead 的两种假设）：
- 空闲 `fps_dis_idle≈60` 而渲染 `fps_dis≈45` → **CPU 写 DDR 与 VDMA/HP2 读抢带宽**（PS 写 framebuffer 与 HP2 读并发）；修法是降更新率/错开写/VDMA 优先。
- 空闲也只有 45–52 → **VDMA/HP2 通路本身到不了**（查突发长度/outstanding/时钟域），P3c 的 100 MHz 比 P3b 差则回退 P3b 方案。

重要旁证：现有 `fps_dis` 本来就是**在 VDMA 启动后、主循环渲染开始前**（CPU 空闲）测量的，P3b/P3c 报 52/45 即已暗示空闲值也不高；
本探针把测量放到“渲染 10 帧之后 + 3 s 窗口”，用于确认渲染是否进一步恶化。

**r06c 构建**：`exit 0`、零告警。三份 ELF：
- 有界（默认）：`61a18137aad4592bc8415d89d5004f980b2cc21a4a6b45ff9dad4eb226518e2c` / **311,864 B**
- 长跑：`2b08ae9868a6e1dfbff056803fa0d7ee76f54a09edfd9febe6738b2f266d915e` / 315,024 B
- 空闲测速：`922a97859605ad12211dfdaa8245f3fb0ffac5d58f5337768af5f86caea960db` / 315,840 B

`src` 四态、`box_crc`/`fb_crc` 口径、`fps_dis` 语义（渲染中测得）均未改动；仅新增 idle 两个字段与一行打印。

### 11.8 P3m 适配版（r06d）

**硬件变化**：删除 VTC 与 vid_out，时序由 PL 的 `axis_to_video` 自产 720p60；
VDMA AXI-Lite 基址 `0x43C00000`（P3b 是 `0x43C40000`）；underflow 像素计数在 AXI GPIO `0x43C10000`（只读，0=从未欠载）。

**编译期开关**（默认即 P3m，无需额外参数）：

| 宏 | 默认 | 含义 |
|---|---|---|
| `S5_VDMA_BASE` | `0x43C00000u` | VDMA AXI-Lite 基址（P3b 回归传 `0x43C40000u`） |
| `S5_NO_VTC` | `1` | 1=**完全不访问 VTC**（0x43C30000 在 P3m 不存在，误读可能挂总线）；打印 `VTC=absent(P3m)` 并跳过 12/12 回读检查 |
| `S5_UF_GPIO_BASE` | `0x43C10000u` | underflow 像素计数寄存器 |

**VDMA 启动方式（P3m）：circular（循环）模式，启动一次，不每帧重装**
- `S5Vdma_Init()` 编程两帧存地址 `0x20000000`/`0x20384000`、HSIZE=5120、STRIDE=5120、VSIZE=720，并 `CR.RESET`；
  `S5Vdma_Start()` 置 `CR = RUNSTOP|TAIL_EN`（`TAIL_EN=1` 即 circular），写 `VSIZE` 触发，轮询 `SR.HALTED` 清除。
- 之后硬件按 2 帧存 A/B 自动轮转输出（1280×720×32bpp，每帧 3,686,400 B），**无需每帧重写地址/长度**。
- 软件每帧只做：等 `PARKPTR.READSTR != 待写 buffer` → 写该 buffer → flush；两帧存启动前已各画一张测试图（棋盘/彩条），
  所以 VDMA 一启动就有合法内容可读（符合“先烧 P3m 空跑看时序、再烧 ELF 出彩条”的流程）。
- 若上板发现 circular 在 P3m 不自动续帧（理论上 `c_num_fstores=2` 支持），备选是每帧重装（写地址+VSIZE）；
  本版未启用该路径，遇到再切（改动集中在 `S5Vdma_Start()` 与主循环）。

**新增字段**：`uf_pix` = AXI GPIO `0x43C10000` 读值（underflow 像素计数）；读不到时保持 `4294967295`（0xFFFFFFFF，明确“不可用”而非谎报 0）。
RESULT 字段顺序：… `"frames","vcnt","box_crc","fb_crc","uf_pix","src"`。
另打一行 `UF GPIO @43c10000 = N (underflow pixels)`。

**示例 RESULT（离线自检，uf_pix=0）**：
`S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":60,"fps_upd":60,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":7,"age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"box_crc":1255179135,"fb_crc":2461129793,"uf_pix":0,"src":"real"}`

**r06d 四份 ELF（exit 0、零告警）**：
- P3m 有界（默认，**上板用这个**）：`b0341d9f571242bc8204cb0c30c0a2279587bdc58b0ce77a20ba5f08a790a4cd` / **278,752 B**（text 43,684 / data 68 / bss 2,354,528）
- P3m 长跑：`2481b2d17b96ce65b1a6d2cc1284f824e98ca0ecc97fb9f1b57869cb846530e4` / 281,956 B
- P3m 空闲测速：`49ca58fd9d6c3ba299997623e43508fcb3a5956cd806133358d29fd402db136f` / 282,820 B
- P3b 回归（`-DS5_VDMA_BASE=0x43C40000u -DS5_NO_VTC=0`）：`b024674dc4b593eeccc4bd35326cf0afb400ca142f287c1812576062b802d36b` / 315,320 B

主机自检：VTC/VDMA 寄存器序列自检改用 `-DS5_VDMA_BASE=0x43C40000u`（P3b 假寄存器堆语义不变），仍 PASS；
真实源 6 用例（含 G3-B 的 `box_crc=0x2D949C0C`）+ 渲染自检全 PASS。

### 11.9 P3n 上板“彩色雪花/闪烁”排查：代码事实 + 确定性测试图（r06e）

#### 1a) 帧存像素字格式（代码事实）
- 画布每个像素写成 32 位字 **`0x00RRGGBB`**：`S5_RGB(r,g,b) = (r<<16)|(g<<8)|b`（`s5_display_app.h`），高 8 位恒 0（`0xAARRGGBB` 的 A=0）。
- ARM 小端，DDR 中每像素 4 字节顺序为 **`[B][G][R][0x00]`**；AXI-Stream `tdata[23:0]` 取出后即为
  `{R[23:16], G[15:8], B[7:0]}`，与 `axis_to_video` 按 `RRGGBB` 解释**一致**。
- 判据：若上屏出现 **红/蓝互换**（红条变蓝），说明硬件侧把 `tdata[23:16]` 当 B 用；若是“整体发灰/偏移”则是 fsync/时序问题，不是字格式。
  本次离线渲染的基准图见 `build/pattern_deterministic.png`（白/黄/青/绿/品红/红/蓝/黑，从左到右）。

#### 1b) stride
- **5120 B/行**：`S5Vdma_Init(..., hsize=S5_CANVAS_W*4=5120, vsize=720)`，
  内部 `S5Vdma_Configure(dma, hsize, vsize, stride=hsize, frmdly=0)` → 写 `HSIZE(0x54)=5120`、`STRD_FRMDLY(0x58)=5120`（stride 低 16 位）。
- 每帧字节数 = 5120×720 = **3,686,400 B**，与两帧存间距 `0x20384000-0x20000000 = 0x384000` 一致。

#### 1c) cache（已做，不是缺失项）
- `s5_fb_flush()` = `Xil_DCacheFlushRange(fb, 3,686,400)`，`S5_DCACHE_FLUSH` 默认 = **1**。
- 调用点：①启动两张测试图各自画完立即 flush；②主循环每帧 `S5Display_RenderFrameSrc()` 之后 flush。
- 结论：**PS 写 → PL 读的 flush 路径是有的**；除非有人用 `-DS5_DCACHE_FLUSH=0` 编译（本版默认未关）。
  另：fb_crc 前还做了 `Xil_DCacheInvalidateRange`（CPU 读校验用），与写路径无关。

#### 1d) 启动测试图（旧默认，r06e 前）
- 旧默认 **A=棋盘**：80 px 方格，深灰 `0x202020` / 浅灰 `0xE0E0E0`，左上红字 `TEST PATTERN 0: CHECKER 1280x720`；
- **B=8 彩条**：75% 幅度（`0xBF`），灰/黄/青/绿/品红/红/蓝/黑，各 160 px 宽、整屏高，无文字；
- **不是随机颜色**。
- ⚠ **但 A/B 两帧内容不同**：circular 模式下 VDMA 60 Hz 在 A、B 间轮转 → 屏幕以 30 Hz 交替显示“棋盘↔彩条”，
  肉眼就是**固定位置的彩色块 + 闪烁**。这很可能就是 Wong 看到的现象（软件侧原因，本次已消除）。

#### 2) 确定性测试图（`-DS5_TEST_PATTERN=1`，本版默认开）
- 两张帧存都画**同一张**图：8 竖彩条（白/黄/青/绿/品红/红/蓝/黑，满幅 0xFF，各 160 px）+ 四边 4 px 白框 +
  中央 8 px 白十字 + 左上黑字标识；画完立即 flush 两帧存，打印 `TEST PATTERN DRAWN: bars8+border+cross`。
- VDMA 启动后再保持 **2 s**（`S5_TEST_PATTERN_HOLD_MS=2000`，期间 CPU 不写帧存 = 纯净出流）：
  打印 `TEST PATTERN HOLD: 2000 ms (VDMA running, CPU idle)` … `TEST PATTERN HOLD done, vdma_err=N`。
  这段窗口内看：彩条顺序是否白黄青绿品红红蓝黑、白框是否完整、十字是否直、有无撕裂/滚动/闪烁。
- `-DS5_TEST_PATTERN=0` 恢复旧行为（A=棋盘、B=彩条，仅用于区分帧存）。
- 离线基准图：`build/pattern_deterministic.png`（同一函数渲染，1280×720）。

#### 3) r06e ELF（exit 0、零告警）
- **P3m 有界（上板用）**：`9a37e5d8af6a120c21c0a25b3ace6a08cc86f083cbf3b8a3c6e9bc87bea43fb3` / **280,620 B**（text 44,212 / data 68 / bss 2,354,528）
- P3m 长跑：`34093912f22961f5191fae17687167f9b9d712e3f88ec1033d4f0f666ad7ed50` / 283,808 B
- P3m 空闲测速：`a416afbc0f856ce47bbe4b11c59c9a8b15ea1dee38279e5ea13c8bd9b1c88729` / 284,616 B
- P3b 回归：`a4fd8594d0d8d397462b0f2b3395cb4f53a5c2b6475f8cd84b2cd4b3b0630098` / 318,208 B

示例 RESULT（离线；板上 `uf_pix` 为 GPIO 实读）：
`S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":60,"fps_upd":60,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":7,"age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"box_crc":1255179135,"fb_crc":2461129793,"uf_pix":0,"src":"real"}`


### 11.10 P3p（fsync 版）适配 + P3n/P3p 两版软件差异（r06f）

**硬件前提**：P3p 的 VDMA 仍 `0x43C00000`，`c_use_fsync=1 / c_use_mm2s_fsync=1`，
`mm2s_fsync` 由 RTL `axis_to_video.vs` 驱动；GPIO `0x43C10000` = **本帧**欠载像素（每 vsync 归零）、
`0x43C10008` = **累计**欠载像素（sticky）。

**P3p 改动（只用寄存器级等价写法，原因是本 BSP 无 axivdma 驱动库）**：
- 开关 `S5_VDMA_FSYNC=1`（默认 0 = P3n）；
- `S5Vdma_Start()` 组 CR：`RUNSTOP|TAIL_EN|SYNC_EN(bit3)|GENLCK_RPT(bit15) = 0x800B`，`FSYNC_SRC(bits[6:5])=0`（=外部 vs），
  与驱动 `XAxiVdma_DmaSetup(EnableSync=1, GenLock=XAXIVDMA_SLAVE, GenLockRepeat=1)` +
  `XAxiVdma_FsyncSrcSelect(XAXIVDMA_CHAN_FSYNC, XAXIVDMA_MM2S)` 等价；
- 非 SG 启动/停止、地址/尺寸编程、circular 双帧存、每帧只写非在读 buffer —— **全部与 P3n 相同**（不每帧重装 VDMA）；
- GPIO 读取：`S5_UF_FRAME_REG=0x43C10000`（本帧）、`S5_UF_TOTAL_REG=0x43C10008`（累计）；
  P3n 版两宏相同（单寄存器 = 累计），读一次填 `uf_total`、`uf_frame=0`。

**RESULT 新字段**：`uf_pix`（兼容，= `uf_total`）、`uf_frame`（本帧欠载）、`uf_total`（累计）。
字段顺序：… `"box_crc","fb_crc","uf_pix","uf_frame","uf_total","src"`。
另打一行：`UF GPIO frame@43c10000=N total@43c10008=M`。

**两版软件差异（唯一区别 = VDMA 同步方式 + GPIO 语义）**：

| 项 | P3n（当前板上基线） | P3p（本变体） |
|---|---|---|
| VDMA CR | `0x00000003`（RUNSTOP+TAIL_EN，自由运行） | `0x0000800B`（+SYNC_EN+GENLCK_RPT，fsync 从模式） |
| 与 vsync 关系 | 无，VDMA 自己按流控跑 | 每次 `axis_to_video.vs` 触发一帧传送（防撕裂） |
| 欠载寄存器 | `0x43C10000` 单值（累计） | `0x43C10000` 本帧 + `0x43C10008` 累计 |
| 抗撕裂 | 靠 2 帧存 + 写前等 READSTR | 额外由 fsync 把帧起点对齐 vsync |
| 其它 | 渲染/RESULT/CRC/测试图/长跑/空闲测速 完全相同 | 同左 |

**离线自检（P3p 语义）**：寄存器序列自检增加 fsync 位检查，输出
`VDMA: CR=0x0000800B …` / `FSYNC: CR=0x0000800B SYNC_EN=1 FSYNC_SRC=0 GENLCK_RPT=1` / `FSYNC: PASS`；
其余（渲染、真实源 6 用例、G3-B box_crc）照旧 PASS。

**示例 RESULT（离线；板上 uf_frame/uf_total 为 GPIO 实读）**：
`S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":29,"fps_dis":60,"fps_upd":60,"fps_dis_idle":0,"idle_period_us":0,"latency_ms":7,"age_ms":31,"vdma_err":0,"frames":36,"vcnt":36,"box_crc":1255179135,"fb_crc":2461129793,"uf_pix":0,"uf_frame":0,"uf_total":0,"src":"real"}`

**P3p 为备选方案（阶段6 未采用，改用 P3q）；下列为 2026-10-30T22:05 磁盘现值（r06f 快照已作废）**：

| 变体 | sha256 | size |
|---|---|---|
| **P3p 有界（未采用）** | `12d8f354bb8aea82aea0c667bb7db5ca6f0b26c84865baa62d4f2a83fb48a709` | 288,436 B |
| P3p 长跑 | `50205691596ba68815df69a5518b0723aa925a48bd2a9a4a3320499957aed2d0` | 288,868 B |
| P3p idleprobe | `18792b9ace82f9ba6073ebf01ff84a0cc65d81f2a4a4a6dfb178445a85b3cec1` | 289,624 B |
| P3n 有界 / 长跑 / idleprobe | `bb7a06aa…` / `9d80793f…` / `7dd41253…` | 288,272 / 288,696 / 289,436 B |
| P3b 回归 | `ba0bb7fa99f47acf14eaf8d834ea93e4634b3add24de23b88ce749d4e67eaa7f` | 327,140 B |

建议：P3n 与 P3p 都保留；Wong 目视若 P3n 稳定就用 P3n 收 G3，若出现撕裂/闪烁再换 P3p。

### 11.11 P3q（集成体：P2d 计算 + P3n 显示链）软件变体（r06g）

**改动 = 只换 3 个地址宏，其余逐字相同**（默认编译即 P3q）：

| 宏 | P3n（显示独立体） | **P3q（默认，集成体）** |
|---|---|---|
| `S5_VDMA_BASE` | `0x43C00000` | **`0x43C40000`** |
| `S5_UF_FRAME_REG` | `0x43C10000` | **`0x43C50000`**（本帧欠载） |
| `S5_UF_TOTAL_REG` | `0x43C10000`（单值） | **`0x43C50008`**（累计；r06h 勘误，`+0x04` 是通道 1 三态） |
| `S5_NO_VTC` | 1 | 1（不访问 `0x43C30000`） |
| 其它（渲染/回退/RESULT/CRC/测试图/长跑/idleprobe/帧存/raw/结果块） | — | **完全相同，未改一行** |

**P3q 三个 ELF（构建 exit 0、零告警）**：

| 变体 | sha256 | size |
|---|---|---|
| **P3q 有界**（现值） | `e4ba0cb47181edb5c5c20ad1826bcdb67225782c19ed4d8ec2309d0107b33f63` | **285,572 B**（text 44,352 / data 68 / bss 2,354,528） |
| **P3q 长跑**（现值） | `cbf5ebe395f21b358356bd4ce9325071e252fcb9d4529a64a06f8ddd17c74577` | 288,772 B |
| **P3q idleprobe**（现值） | `2c880e4e539f2e322f45c9f6c3a24f1f798c6c851d0177f496c28f13bfbcb1d8` | 289,532 B |

ELF 静态核验（`arm-none-eabi-objdump`）：VDMA 基址以 `movt r1, #0x43c4`（=0x43C40000）出现；
`0x43C30000`（VTC）与 `0x43C10000`（P2d preproc/旧 GPIO）在 ELF 中**不存在**；GPIO `0x43C50000/0x43C50004` 以字面量存在。

**离线自检**：VDMA 寄存器序列自检本来就以 `-DS5_VDMA_BASE=0x43C40000u` 编译（假寄存器堆在 0x43C40000 段），
与 P3q 基址一致 → 该自检即为 P3q 的寄存器序列验证，仍 PASS；P3p fsync 位检查 PASS；渲染/真实源 6 用例/G3-B `box_crc` 全 PASS。
GPIO 两寄存器（0x43C50000/4）在板上实读，离线填 0。

**回归/兼容变体（均保留）**：
- P3n（显示独立体，旧地址显式指定）：`303210ca…`/284,324 B；长跑 `331db819…`/284,744 B；idleprobe `e078ad44…`/285,504 B
  （另保留此前上板基线三份副本：`s5_display_app_p3n.elf` 等，sha `49070390…`/`388a0a07…`/`c3ebac98…`）
- P3p（fsync）：`82ccdd44…`/284,488 B；长跑 `47501fe1…`/284,908 B；idleprobe `8cc262df…`/285,696 B
- P3b（旧架构）：`fb5efd4b…`/323,180 B

**计算回归 ELF 是否依赖显示寄存器/地址？——不依赖，可直接复用现有 runner**
- 检查对象：S4 冻结产物（S4-B `s4b_ps_tensor_diagnostic.elf`、S4-T32 `s4d_ps_app_m4b*.elf`、S4-T34 chainA/chainB/m4b_r3 等，共 44 个 ELF）。
- 方法 1：把 6 个显示相关 32 位地址（0x43C00000/0x43C10000/0x43C20000/0x43C30000/0x43C40000/0x43C50000）按小端字节模式扫描 ELF：确有若干 ELF 出现
  0x43C3/0x43C4/0x43C5 字节序列，但——
- 方法 2：`arm-none-eabi-objdump -d` 反汇编核对（m4b_r3、chainA2、基线 sw0）：**没有任何一条指令引用这些显示寄存器基址**
  （`movt`/`movw`/字面量均无 0x43C3/0x43C4/0x43C5 组合）；方法 1 的命中都是指令偏移/数据字节的**巧合**（如 `1043c4:` 这类地址列）。
- 结论：M4-b / chain-lite A / 张量 CRC 回归只碰 **2B CSR 0x43C00000、preproc 0x43C10000、AXI DMA 0x43C20000、DDR 张量/raw 0x12000000、结果块 0x20800000**；
  显示新占的 `0x43C40000`（VDMA）与 `0x43C50000`（GPIO）与它们不重叠，**回归 ELF 无需改动、无需重编**。
- 唯一需要 runner 确认的共享面是 **DDR**：显示帧存占 `[0x20000000,0x20708000)`（含 A/B 两帧），
  raw `0x12000000` 与结果块 `0x20800000` 是设计上的交接区；请确保计算侧不做“大范围 DDR 清零”覆盖 `0x2000_0000` 段（我们未在计算 ELF 中看到该段写常量，但建议 runner 侧再确认一次）。

### 11.12 P3q 地址勘误：GPIO 累计欠载寄存器 `+0x04` → `+0x08`（r06h）

> 注：本节 ELF 哈希为 r06h 构建快照，现值见 §0 / `S5_SW_FREEZE_CHECKLIST.md`。

**勘误依据（构建方查 axi_gpio 寄存器映射）**：AXI GPIO 每通道 2 个寄存器，
**通道 1 数据 = `+0x00`、通道 1 三态 = `+0x04`；通道 2 数据 = `+0x08`、通道 2 三态 = `+0x0C`**。
原 `S5_UF_TOTAL_REG=0x43C50004` 读的是**通道 1 三态寄存器**（不是累计欠载量），现改为 **`0x43C50008`**。

| 宏 | 旧值（r06g，错误） | **新值（r06h，正确）** |
|---|---|---|
| `S5_UF_FRAME_REG` | `0x43C50000` | `0x43C50000`（ch1 data，本帧欠载） |
| `S5_UF_TOTAL_REG` | ~~`0x43C50004`~~ | **`0x43C50008`**（ch2 data，累计欠载） |
| `S5_VDMA_BASE` / `S5_NO_VTC` | `0x43C40000` / `1` | 不变 |

**ELF 静态核验**（新 P3q 有界 ELF）：`0x43C50000` 与 `0x43C50008` 均以字面量存在，**`0x43C50004` 已不存在**。

**离线自检对齐**：`tools/host_render_test.c` 增加编译期断言
`_Static_assert((S5_UF_TOTAL_REG - S5_UF_FRAME_REG) == 8u, "GPIO ch2 data must be +0x08")`，
并在运行输出打印 `GPIO regs: frame=0x43C50000 total=0x43C50008 (ch1 +0x00 / ch2 +0x08)`（构建日志可见，PASS 才会继续）。
P3n/P3b/P3p 变体各自用显式旧地址（不受此默认值影响）。

**P3q 三份 ELF（r06h，构建 exit 0、零告警）**：

| 变体 | sha256 | size |
|---|---|---|
| **P3q 有界** | `b79d322dfaac87f45d72f5e21c7bfe2fdbc3a34f6cd71da206f5c7f4b2ee3497` | **281,624 B**（text 44,336 / data 68 / bss 2,354,528） |
| **P3q 长跑** | `6aab247348f8f029c63de0c5a2ca64929af27a4a575c35a6581e91b1a555fd7f` | 284,812 B |
| **P3q idleprobe** | `c36b2885a0a78b2ccc9588cb20c9a586bbf933273a20fd1680ee42826f57c3bd` | 285,600 B |

**HP0/HP1(50 MHz) 与 HP2(100 MHz) 并发读同一颗 DDR**：属板级带宽/仲裁问题，软件侧无改动；
显示软件只按 60 Hz 写 1280×720×32bpp 帧存（≈221 MB/s 写带宽峰值），2B 单帧耗时变化由板级复测判定。
若并发导致显示欠载，`uf_frame/uf_total`（新 GPIO）会直接反映；软件侧可回退 P3q→P3n 单独验证（地址宏切换）。

### 11.13 生产者模式 `S5_PRODUCER=1`（6-D 用真实写端，r06i）

> 注：本节为 v1 生产者；v2（sidecar/seqlock/故障注入）见 §11.14 与 `S5_PRODUCER_V2_FREEZE.md`，哈希快照不在此维护。

**目的**：阶段6 的 6-D 卡在"缺可信发布时间/时基"。本模式在同一份显示软件里实现**生产端**：
每帧把结果块真实写到 `0x20800000`，时间戳取自**真实全局定时器**，`frame_id` 单调，`status` 位正确，
并带 session 语义；显示侧仍走**原有消费路径**读同一块 → `age_ms/latency_ms` 变成真实计算值。

**时基说明（重要，与规格的差异）**：本 BSP 的 `include/` **没有 `xtime_l.h`**（无 `XTime_GetTime()` API），
故生产者用 `S5Ticks_Now()`——它直接读 Cortex-A9 全局定时器 `0xF8F00200`（hi-lo-hi，64 位），
**与 `XTime_GetTime()` 是同一个计数器、同一个 `COUNTS_PER_SECOND=333333343`**（源码内
`_Static_assert((uint64_t)COUNTS_PER_SECOND == S5_GT_HZ)` 把关）。这是"真实 ticks"，不是软件计数。

#### 11.13.1 生产者写出的字段（严格按已冻结 ABI，16 B/项步进）

| 偏移 | 字段 | 生产者行为 |
|---|---|---|
| `0x00` | `magic` | 恒 `0x53355253`（"S5RS"） |
| `0x04` | `frame_id` | **单调递增**：session 起始标记 = 0，之后 1,2,3…（每 `S5_PROD_EVERY_N` 帧 +1；默认每帧） |
| `0x08` | `n_dets` | 1~3（复用现有移动框生成器 `S5Sim_NextFrame()`，源 640×480 坐标） |
| `0x0C/10` | `cap_lo/hi` | **本帧开始渲染时刻**的真实 ticks（全局定时器，64 位） |
| `0x14/18` | `inf_lo/hi` | `cap + S5_PROD_INF_OFFSET_TICKS`（默认 2,333,334 ticks = 7 ms，模拟推理完成） |
| `0x1C` | `status` | `bit0 valid=1`、`bit1 overrun=0`、`bit2 stale=0`（本模式恒新鲜） |
| `0x20+16k` | 检测项 | `x,y,w,h` u16（**源 640×480**）+ `cls` u8 + `score_q8` u8 + `reserved`/`pad`=0 |
| 槽位 15 `reserved` | session tag | `0xA55A`（ABI 允许的保留字段，既有字段语义未改） |

**写入节奏与顺序**：每帧（可配 `S5_PROD_EVERY_N`）在渲染结束后写一次；先整块 288 B 清零再填头/项，
写 DDR 后 `Xil_DCacheFlushRange(0x20800000, 288)`。消费者下一帧开头 `invalidate` 后读取。
**session 语义**：主循环开始前写一帧 `frame_id=0, n_dets=0, valid=1, cap=inf=now` 的起始标记（放在
测试图 2 s 保持之后，避免首帧 `cap` 过旧被误判超龄）；随后 `frame_id` 从 1 起单调。session 边界 = 上电/本模式启动 + tag。

**打印**（每写一帧一行，与 RESULT 行分开）：
```text
S5PROD session start: frame_id=0 tag=a55a status=0x1 (333 Hz)
S5PROD frame_id=187 n=2 status=0x1 cap_ms=5123 inf_ms=5130 cap_lo=0x1e8480 inf_lo=0x221321
```
（`cap_ms/inf_ms` = ticks 换算毫秒；`cap_lo/inf_lo` = 低 32 位十六进制，64 位 ticks 全量在块里。）

**离线样例（模拟 ticks，非板上真实值）**：
`S5PROD frame_id=7 n=3 status=0x1 cap_ms=3 inf_ms=10 cap_lo=0x12D687 inf_lo=0x36711D`
对应块：`cap=1,234,567 ticks`、`inf=3,567,901 ticks`；消费者解析往返一致（host 自检 case0c，PASS）。

#### 11.13.2 与 6-D 阻塞项的对应关系

| 6-D 需要 | 本生产者是否已提供 | 说明 |
|---|---|---|
| 真实发布时刻（cap，硬件时基） | **已提供** | 全局定时器 ticks（64 位，`COUNTS_PER_SECOND=333333343`），每帧真实取值 |
| 推理完成时刻（inf） | **已提供（模拟偏移）** | `cap + 7 ms` 固定偏移；**不是**真实推理延迟 |
| 帧序号单调 | **已提供** | `frame_id` session 内单调递增，起始标记为 0 |
| 新鲜/有效性 | **已提供** | `status.valid=1`、overrun/stale=0；消费者按同一 ABI 判定 |
| 检测框数量/坐标/类别/分数 | **已提供（模拟值）** | 来自 `S5Sim_NextFrame()` 的移动框，**不是**真实检测结果 |
| session 标识 | **已提供（tag）** | 槽位 15 `reserved=0xA55A`；frame_id 重置即新 session |
| 真实 n_dets / score / 类别 | **仍需真实推理链提供** | 本模式只证明"生产者契约 + 时基"可落地；真实检测需 P2d/chain-lite 写同样的块 |
| 真实推理延迟 | **仍需真实推理链提供** | 当前 `inf = cap + 固定 7 ms`；真实链应按实际完成时刻写 |

> 结论：**6-D 的"写端 + 可信时基 + 序号 + status"已可用本 ELF 验证**；检测语义与真实推理延迟仍需真实推理链。

#### 11.13.3 P3q 生产者版三份 ELF（构建 exit 0、零告警）

| 变体 | sha256 | size |
|---|---|---|
| **P3q 生产者·有界** | `0b8fac187dd5069a5003dee9273d8e6607d96236df96ab8b614ed2280d630775` | **292,252 B**（text 46,096 / data 72 / bss 2,355,104） |
| **P3q 生产者·长跑** | `47a6964420fa7054aa9894521d06f9a920f87fca92fd3c753c52f603b4cd945e` | 292,588 B |
| **P3q 生产者·idleprobe** | `bfe4a90eb94d334cbbf5632ea9feb758fd5316ff7ef542cc49431f4380d61394` | 293,808 B |

编译：P3q 默认（`S5_VDMA_BASE=0x43C40000`、`S5_UF_FRAME_REG=0x43C50000`、`S5_UF_TOTAL_REG=0x43C50008`、`S5_NO_VTC=1`）
+ `-DS5_PRODUCER=1`；长跑/idleprobe 另加 `-DS5_LONG_RUN=1` / `-DS5_IDLE_PROBE=1`。
ELF 静态核验：含 `S5PROD frame_id=` / `S5PROD session start` 字符串，不含 `XTime`（BSP 无该 API）。

**消费端预期**（同一次运行）：读取自己写回的结果块 → `src:"real"`；`age_ms ≈ 帧周期`（生产者用上一帧 cap），
`latency_ms ≈ 帧周期 − 7 ms`（真实计算，不再恒 0）；`box_crc` 随移动框变化；`uf_frame/uf_total` 照常读 GPIO。


### 11.14 生产者套件索引（**身份 A / rev5**，2026-10-31 01:58 重编）

完整字段/时序/限制/源码绑定见 **`S5_PRODUCER_V2_FREEZE.md`（rev5，sha256 `1ec638660b229a087e47be051fc2a24cab69e37edf767af50f60665756407d69`）**；本节只列索引。
**rev5 = rev4 + 可观测字段**：`S5CONS` 增 `s1/s2/retries`（仅当 `s1==s2` 且偶才输出正常行），重试另打 `S5CONS RETRY …`、超限 `S5CONS TIMEOUT …`；**协议（写者 4 步/消费者 invalidate-first）、身份 A（`+0x100`/14 框/288 B）、业务映射、故障注入一律不变**。

| ELF | 用途 | sha256（前 8 位） | 字节 |
|---|---|---|---|
| `s5_display_app_p3q_producer.elf` | 有界（E6-A/E3 主用） | `ca6c2430` | 304,040 |
| `s5_display_app_p3q_producer_longrun.elf` | 长跑 30 min | `6260250a` | 304,472 |
| `s5_display_app_p3q_producer_idleprobe.elf` | 空闲测速（E2，板级挂起，不采用） | `2c14cb0e` | 303,688 |
| `s5_display_app_p3q_producer_fault.elf` | 故障相位轮换（每 120 次发布） | `7e3ce32c` | 304,508 |
| `…_fault_overrun.elf` | E4 固定 overrun | `89ae6adc` | 303,788 |
| `…_fault_stale.elf` | E4 固定 stale | `2e39bd26` | 303,848 |
| `…_fault_invalid.elf` | E4 固定 invalid | `5e92ae69` | 303,892 |
| `…_fault_no_hand.elf` | E4 固定 no_hand | `a3cdb877` | 304,552 |

- 构建记录：`build/p3q_producer_A_rev5_record.json`（sha256 `807f427b79ef66e93ab7e0225f5b9d9c5a157dbe4264c23b7bdff676c274cef9`）；源码绑定见冻结件 §6（`s5_display_app.c`=`cd2b093a…`、`s5_publish_abi.h`=`f89fb1be…`、`real_source_selftest.c`=`c7089d2b…`）。
- **显示三件套未重编**（`e4ba0cb4…`/`cbf5ebe3…`/`2c880e4e…` 保持阶段5 冻结物）。
- 自检：`case0c/0d/0e` 沿用；**`case0f`（v5 扩展）承担 `case0g` 要求**——验证 `s1==s2` 且偶、`retries=0`，并打印 `S5CONS`/`S5CONS TIMEOUT` 样例；全 PASS。
- 旧 E3/E5 证据保留原判、**不复用**；板窗用新 RunId（`s6e_e6_age_rev4_20261031_r04`）+ rev5 跑 E6。

### 11.15 R-07 相机接入（P3r：P3q + AN5642/OV5640 640×480 → raw ABI）

#### 11.15.1 数据宽度结论（跨组不一致已定死，证据=阶段3 冻结 XSA `.hwh`，不是厂商 tcl）

阶段3 采集链**两段都成立**，并不矛盾：`ov5640_ip` 输出 **AXIS 16-bit（RGB565）** → 库 IP
`axis_subset_converter_0` 做 **2→3 字节**展开 → 采集 VDMA `axi_vdma_1` 的
`C_S_AXIS_S2MM_TDATA_WIDTH=24`、`C_INCLUDE_SG=0`、`C_M_AXI_S2MM_DATA_WIDTH=64`、
`C_INCLUDE_S2MM_DRE=1`、`C_USE_S2MM_FSYNC=2`、`C_S2MM_LINEBUFFER_DEPTH=4096`、
`C_S2MM_MAX_BURST_LENGTH=128`、`C_NUM_FSTORES=1`。

- `TDATA_REMAP = {tdata[4:0],3'b000, tdata[10:5],2'b00, tdata[15:11],3'b000}` ⇒ **左对齐补零**（非 ×255/31 缩放）：
  `R' = {R[4:0],3'b000}`、`G' = {G[5:0],2'b00}`、`B' = {B[4:0],3'b000}`。
  与阶段3 蓝通道实测"最大 120"自洽（`B[4]` 恒 0 → B' ≤ 120），也解释了后续 `blue_msb_rebuild` 补丁的历史。
- 写 DDR：**3 B/px，byte0=B、byte1=G、byte2=R ⇒ BGR888**，与阶段5 冻结 raw ABI 完全一致。
  640 宽 ⇒ **stride=1920、帧 921,600 B**；软件**不做** 565→888 展开（PL 已做）。
- 软件只管 **S2MM：VSIZE=480 / HSIZE=1920 / STRIDE=1920**（tdata 宽度 24 由 PL 定，软件不改）。

#### 11.15.2 传感器切 640×480（覆盖表，PCLK/HTS 保持）

在阶段3 基线（720p：PLL `0x3035=0x21/0x3036=0x69` → PCLK=84 MHz，HTS=1892，VTS=740）之后写覆盖表：

| 寄存器 | 值 | 含义 |
|---|---|---|
| `0x3808/09` | `0x02/0x80` | DVPHO = **640** |
| `0x380A/0B` | `0x01/0xE0` | DVPVO = **480** |
| `0x380C/0D` | `0x07/0x64` | HTS = **1892**（保持不变） |
| `0x380E/0F` | `0x05/0xC8` | VTS = **1480** |
| `0x3810–0x3813` | `0x00` | 窗口偏移 0 |
| `0x3814/15` | `0x31/0x31` | 2× 子采样（阶段3 值，保持） |
| `0x3824` | `0x04` | PCLK 手动分频（保持） |
| `0x4300` | `0x60` | RGB565（保持；PL 展开） |
| `0x3035/36` | `0x21/0x69` | PCLK=84 MHz（保持） |
| `0x3A02/03`、`0x3A14/15` | `0x05/0xC4` | AEC 最大曝光随新 VTS 同步（否则只限亮度） |

**时序估算（640×480）**：`PCLK = HTS × VTS × fps` ⇒ 1892 × 1480 × 30 = **84.0 MHz** ⇒ **30 fps**；
帧周期 33.3 ms（如需 60 fps：VTS 改 740，1892×740×60=84.0 MHz）。回读校验
`0x3808/09、0x380A/0B、0x380C/0D、0x380E/0F`，失败重写覆盖表最多 3 次。

#### 11.15.3 SOF/HREF 补丁 `GAP_THRESH=16384` 判断：**不需改**

补丁判据：首行起点 = hblank 低电平持续 ≥ `GAP_THRESH` 后的第一个有效像素；阈值须严格夹在
**线间隙** 与 **场间隙** 之间：
- 640×480@30fps：线间隙 = HTS−640 = **1252** < 16384；场间隙 = (1480−480)×1892 = **1,892,000** ≫ 16384（余量 ≈13× / ≈115×）。
- 若改 60fps（VTS=740）：线间隙 1252 < 16384；场间隙 = 260×1892 = **491,920** ≫ 16384。
- 结论：只要保持 **HTS=1892、PCLK=84 MHz**（本方案如此），`16'd16384` 两界都有大余量，**参数保持 16'd16384 不变**；
  若将来把 HTS 大幅缩短到接近 640 且 VTS 压到 ≤488，才需要重算。

#### 11.15.4 软件实现（`S5_CAMERA=1`，与 display/producer 正交）

- 新增 `src/s5_camera.h` / `.c`：
  - **寄存器级 PS I2C0 SCCB**（`0xE0004000`，Cadence 寄存器：CR/SR/ADDR/DATA/ISR/TRANS_SIZE/TIME_OUT，
    与 Vitis `iicps_v3_23/xiicps_hw.h` 位定义一致）：初始化 → 读 CHIPID(`0x300A/B`→`0x5640`) → 写覆盖表
    → 回读校验（≤3 次）→ S2MM 配置/启动；读写各带轮询上限（`S5_CAM_POLL_LIMIT=2,000,000`，**非墙钟保证**）。
  - **S2MM VDMA（非 SG、循环、单帧 raw）**：基址宏 `S5_CAM_VDMA_BASE=0x43C60000`（以最终 XSA 为准）；
    `ADDR0=S5_CAM_RAW_BASE(0x12000000)`、`VSIZE=480`、`HSIZE=STRIDE=1920`、`CR=RUNSTOP|TAIL_EN`，
    写 VSIZE 触发并等 HALTED 清（超时返回 -3）。
  - 返回码：`-10` CHIPID 不符、`-11` SCCB 读失败、`-12` 覆盖表写失败、`-13` 回读校验失败、
    `-14` S2MM 配置回读不符、`-15` S2MM 未退出 HALTED。
- 显示软件集成（`src/s5_display_app.c`）：`S5_CAMERA=1` 时在测试图之后、显示 VDMA 之前调用
  `s5_cam_bringup()`；成功打印 `CAM: init OK chip=0x5640 640x480 stride=1920 raw=0x12000000 (24bpp BGR888)`，
  失败打印原因并**继续显示（四态回退到测试图/无框）**；主循环每 60 帧打印 `CAM: sr=0x… frames=…`。
- 未改 `src/s5_result_abi.h` / raw ABI（仍 BGR888、stride 1920、帧 921,600 B）。

#### 11.15.5 离线自检（`tools/camera_selftest.c`，假寄存器堆；PASS）

- 几何/ABI：`640×480、BPP=3、stride=1920、帧 921,600 B、VDMA 基址 0x43C60000、raw 0x12000000`。
- 正常链：I2C0 初始化 → CHIPID=0x5640 → 覆盖表写入 → 回读 `640/480/1892/1480` → S2MM 配置
  （HSIZE/STRIDE/ADDR/VSIZE 逐项）→ 启动（HALTED 清）→ Status 无错误位。
- 异常路径：CHIPID 错 → `-10` 且 **S2MM 未被启动**；HALTED 永不清 → `-15`；SR 错误位 → `Status=-2`；
  I2C 控制器 CR 回读不符 → `-2`。
- **不覆盖**：真实 I2C 时序/上拉/分频、真实传感器响应、S2MM 实际数据搬运、PL 展开正确性——均需板上验证。

#### 11.15.6 P3r 相机 ELF（构建 2026-10-31，exit 0、零告警；未重编冻结显示/producer ELF）

| ELF | sha256 | 字节 |
|---|---|---|
| `s5_display_app_p3r_camera.elf` | `9ffc68e6a4b0a7e1a18f23a0830735e816bee1ded60ea4e1370493bce49fbd90` | 315,308（text 47,360 / data 92 / bss 2,354,528） |
| `s5_display_app_p3r_camera_longrun.elf` | `cf07bab78edd56945837b77db31e80e8b41aad4c11aa4fd5bbc09d6fe549e6b0` | 315,732 |

构建记录：`build/p3r_camera_record.json`（sha256 `a32833c06c5cbb74e6c027194ce4d4188aa31357053a73985105aaf2557b1291`，含源码绑定与数据宽度证据）。

#### 11.15.7 板上待验证 / 风险

1. **I2C 分频与上拉**：`S5_CAM_I2C_CLK_HZ=111,111,115` 为初值，需板上示波器/日志确认 100 kHz 与 ACK；SCCB 读用 HOLD+重复起始，若 PS I2C0 在 AN5642 上不可用需改 GPIO 位翻转后端（接口已抽象为 `S5CamBus`）。
2. **640×480 覆盖是否充分**：部分 OV5640 模组切分辨率还需 `0x3708–0x370C/0x4004/0x3036` 微调；已用回读校验兜底，板级若出图异常按 AEC/曝光/时序逐项补。
3. **单帧循环撕裂**：ABI 只有一块 raw（0x12000000），S2MM 循环覆盖与显示读取可能撕裂；当前按阶段3 单帧方案，双缓冲需 ABI/PL 扩展（不在本任务）。
4. **S2MM SR 帧计数**：`CAM: frames=` 取 SR[23:16]，阶段3 注释称 IRQ 帧计数位，语义待板上核对（不作为判据，仅观测）。
5. **VDMA 基址**：`0x43C60000` 以最终 P3r XSA 为准，不对则改宏重编。
6. 本任务未上板、未改 Vivado/git；E3/E6 的 producer/display 逻辑不受影响（宏正交）。

### 11.16 相机首窗 `rc=-11` 排查：复位漏写 + I2C 分频未知 ⇒ 诊断版（ecam_diag）

#### 11.16.1 两个软件侧问题（已修/已加证据）

**(1) 相机复位从未释放（首要根因，与 `CAM_RST=0` 快照一致）**
- 阶段3 冻结应用（`dbdf\tmp\s3r06\t04_j11cmos2_elf_v10\elf_build\app\display_demo.c` L259–267）实测时序：
  `XGpio_Initialize(XPAR_CMOS_RST)` → 方向=输出 → **写 1 → `usleep(500000)` → 写 0 → `usleep(500000)` → 写 1 → `usleep(500000)`** → `sensor_init()`。
- 即 `cmos_rstn`（AXI GPIO ch1 data @ **`0x41200000`**）**低有效：0=复位、1=释放**；snapshot=0 ⇒ 相机**一直被按在复位**，SCCB 不可能 ACK ⇒ 与 `CAM: FAILED rc=-11` 完全一致。
- 旧版 `src/s5_camera.c` **没有任何复位 GPIO 访问**（只做了 I2C/覆盖表/S2MM）。已修：新增 `S5Cam_ResetSeq()`（宏 `S5_CAM_RST_REG=0x41200000`、`S5_CAM_RST_ACTIVE_LOW=1`、`S5_CAM_RST_HOLD_MS=500`），在 `S5Cam_Init()` 的 I2C 初始化**之前**执行 1→500 ms→0→500 ms→1→500 ms；`S5CamBus` 增加 `delay_us` 回调（ARM 用 GT 忙等，主机自检为 NULL）。
- 若 `0x41200000` 不可写（BD 无该 GPIO），`S5Cam_Init()` 返回 **-16**（便于区分"复位寄存器不存在"与"SCCB 不通"）。

**(2) PS I2C0 分频来源未知（`PCW_I2C_PERIPHERAL_FREQMHZ` 我方拿不到）**
- 旧实现硬编码 `S5_CAM_I2C_CLK_HZ=111111115`，按 `div = cpu/100k − 1` 写 `CR[13:8]`；但阶段3 实际调用
  `i2c_init(&ps_i2c0, XPAR_XIICPS_0_DEVICE_ID, 40000)`（**目标 40 kHz**，输入时钟来自其 BSP 的 `xparameters`）。
- 诊断版对 **6 个候选输入时钟**（111.111 M/100 M/50 M/166.667 M/133.333 M/40 M）逐个 `S5Cam_I2cInitEx()`，
  打印各自算出的 `div`、回读 `CR`/`SR`；并把 `rc=-11` 拆成子码：
  `-2` 地址阶段（无 ACK/仲裁/硬件超时）、`-3` 写寄存器地址字节失败、`-4` 读数据超时、`-5` 完成阶段错误。

#### 11.16.2 诊断版 ELF（`-DS5_CAM_DIAG=1`，不改显示/producer 冻结 ELF）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | **诊断版**（复位序列+I2C 候选+CHIPID 原始值+子码） | `f224f5e53f6f94da2ed3528dc0081fef31339faf0c6f1b2e0dbffd670239b144` | 328,460 |
| `s5_display_app_p3r_camera.elf` | 修复版正常采集（含复位序列，**旧 9ffc68e6… 作废**） | `184949ed8c0ad2f8c95b6cc45162b4fd35c1bc07abb954f39249ba078d8030b3` | 322,456 |
| `s5_display_app_p3r_camera_longrun.elf` | 修复版长跑 | `c4dd0c6824d1739df044fef774e905efffb5242ba1b7d1ab95c2ccdbb1ababc7` | 322,872 |

构建记录：`build/p3r_camera_record.json`（sha256 `432ebecccb8d092b635b974fc8b1fe2a44d8b39f6d23c843f8e044c4bb0a959e`）。
修复版 berkeley：text 47,928 / data 100 / bss 2,354,528。

#### 11.16.3 诊断版 UART 行格式（期望样例）

```text
CAM: rst pin before=0x0 (reg 0x41200000)
CAM: reset seq: assert(0) 500 ms -> release(1) 500 ms -> release(1) 500 ms
CAM: rst pin after=0x1 (低有效: 1=释放)
CAM: i2c clk_assumed=111111115 div=1110 cr=0x45E007 sr=0x40 rc=0
CAM: i2c clk_assumed=100000000 div=999  cr=0x3E7007 sr=0x40 rc=0
...（共 6 个候选时钟，各一行）
CAM: probe addr7=0x3C w8=0x78 r8=0x79 ack=1 isr_addr=0x1 isr_data=0x1 rc=0
CAM: chipid reg0x300A=0x56 reg0x300B=0x40
CAM: init OK chip=0x5640 640x480 stride=1920 raw=0x12000000 (24bpp BGR888)
```
失败时：
```text
CAM: probe addr7=0x3C w8=0x78 r8=0x79 ack=0 isr_addr=0x10 isr_data=0x0 rc=-2
CAM: chipid reg0x300A=0x00 reg0x300B=0x00
CAM: FAIL sub=-2 stage=addr/ack reg=0x300A val=0x00 isr=0x10
CAM: FAILED rc=-11（SCCB 不通）→ 继续显示测试图
```
判读：`rst pin after=0x1`（复位已释放）而 `ack=0` + `isr_addr` 含 NACK(0x10) ⇒ 器件无响应（接线/EMIO/上拉/地址）；
`rc=-2` 且 `isr_addr=0` ⇒ 总线起步异常；`rc=-4` ⇒ 从设备不吐数据（地址对但寄存器访问异常）。

#### 11.16.4 需板级/BD 提供的信息（决定最终宏值）

1. P3r XSA 的 `PCW_I2C_PERIPHERAL_FREQMHZ`（或 `XIicPs` 输入时钟）→ 定 `S5_CAM_I2C_CLK_HZ` 与 `div`；
2. `CAM_RST` AXI GPIO 基址/通道/bit（我们按阶段3 假定 `0x41200000` ch1 data 全 32 位写 1）；
3. PS I2C0 是 **MIO** 还是 **EMIO**（video-bd 在核）：若 EMIO 到 PL，还需确认 SCL/SDA 引脚与 FPGA 侧上拉；
4. 该板上 AN5642 的 SCCB 从地址是否仍为 0x3C（7 位）。

#### 11.16.5 自检更新（PASS）

`tools/camera_selftest.c` 新增：复位序列（低有效：1→0→1，最终引脚=1）、`S5Cam_ReadRegEx()` 子码
（地址阶段 NACK → `-2` 且 `isr_addr` 含 `0x10`；正常路径读回 `0x56`）；原几何/覆盖表/回读/S2MM/异常路径保持 PASS。
**仍不覆盖**真实 I2C 波形、上拉、传感器响应与 PL 展开——需板上诊断版取证。

### 11.17 DDR 512 MiB 误配的影响 + OCM 最小探针 `ecam_probe`（R-07 排查）

#### 11.17.1 结论：P3r build4 XSA 的 PS7 DDR 配置成 512 MiB，冻结 ABI 的地址越界

- P3r build4（`D:\tmp\lead\p3r_camera_20261031_r01\out\build4\...\s4d_p3r.hwh`）：
  `PCW_UIPARAM_DDR_PARTNO = MT41J128M8 JP-125`、`PCW_UIPARAM_DDR_BUS_WIDTH = 32 Bit`、
  `PCW_DDR_RAM_BASEADDR = 0x00100000`、**`PCW_DDR_RAM_HIGHADDR = 0x1FFFFFFF`（512 MiB）**。
- 板级真值/阶段3/阶段5 一直使用的 XSA：`MT41J256M16 RE-125` / `MT41K256M16TW-107`、
  **`HIGHADDR = 0x3FFFFFFF`（1 GiB）**（`dbdf\tmp\3\S3-T05\...\design_1.hwh`、`w4\tmp\s2b_inference_candidate.gen\...`）。
- 冻结 ABI 的地址：**FB A=`0x20000000`、FB B=`0x20384000`、结果块 `0x20800000`** —— 全部 **≥512 MiB**。
  在 P3r ps7_init 的 512 MiB 地址窗口下属于**未映射区** ⇒ AXI 解码错误 ⇒ 数据中止
  （CPSR ABT、PC 落到低地址 0x8；ABT 发生在 `main` 里第一次写测试图帧存时，早于任何 `CAM:` 打印）。
  已知可用的 P3q 显示 ELF 在同一 ps7_init 下**也会同样中止**，与相机代码无关。
- 影响面：不只是"越界中止"；512 MiB 的 DDR 标定/时序参数（part、tRFC 等）与实板 1 GiB 器件不同，
  即使不越界也可能**跑在不正确时序参数上**（长稳/带宽结论不可信）。建议 build5 必须把
  part/size 改回 `MT41J256M16`、`HIGHADDR=0x3FFFFFFF`，并重新生成 ps7_init。
- **此前阶段5/6 证据不受影响**：它们用的组合是 stage-4 init.elf（1 GiB 配置的 ps7_init）bring-up，
  运行期地址（FB/结果块）都在 1 GiB 窗口内；build4 只是 P3r 新 XSA 的 DDR 参数写错。

#### 11.17.2 OCM 最小探针 `ecam_probe`（隔离 DDR 因素）

- 目的：在"combo init → P3r build4 ps7_init → PL"流程下，用**只跑 OCM** 的最小 ELF 判定
  "CPU/UART/启动流程/OCM 是否正常"，从而把 DDR 因素完全隔离。
- 链接：`tools/lscript_probe_ocm.ld`（OCM `[0x00000000,0x00040000)`；`.vectors` 在 **0x0**；
  entry=`_vector_table`；`.text` 0x0 起；heap 0x800；stack 0x6000，`_stack`≈0xC2B0；`ASSERT` 防溢出）。
- 代码 `tools/ecam_probe.c`：仅 `xil_printf` + `Xil_In32` 裸 MMIO，**不访问 DDR**
  （不碰 0x100000/0x12000000/0x20000000/0x20800000）、**不初始化 I2C0**、**不碰帧存**、**不开中断**、**不用 Xilinx 驱动**。
- 打印序列（无参数、可直接 `con` 观察）：
  `PROBE: main` → `PROBE: vbar=0x… vec@0x0=0x…` → `cam_rst(0x41200000)` → `gt_lo/gt_hi(0xF8F00200/04)` →
  `2b_csr(0x43C00000)` → `disp_vdma_cr(0x43C40000)` → `uart1 cr/sr(0xE0001000,0xE0001004)` →
  `PROBE: links=OCM only …` → 之后每 500 ms `PROBE: tick N gt_lo=0x…` 心跳。
- 判读：**有 PROBE 输出** ⇒ CPU/UART/启动流程/OCM 正常，问题域缩到 DDR 配置或 DDR 上地址；
  **静默** ⇒ 问题在 PS7/入口/时钟层面，与 DDR 无关。
- ELF：`build/ecam_probe_ocm.elf`，sha256 `3ec8fd91f937fb2929b2ed78d47975e8d13b1c2344854d2b50e52052f0a352ec`，129,728 B
  （text 22,848 / data 0 / bss 26,992 / dec 49,840，全部落在 256 KB OCM 内；entry 0x0）。
- 记录：`build/ecam_probe_record.json`（sha256 `84171db09e4981becf023218cd256dea702ca127a45b44dc88330dec79278397`）；
  源码 `tools/ecam_probe.c`、链接脚本 `tools/lscript_probe_ocm.ld`。

#### 11.17.3 Section headers 对比（回应"诊断 ELF 无 0x0 段"）

| ELF | `.text` VA | `_vector_table` | VBAR 设置 | `entry` |
|---|---|---|---|---|
| P3q 显示 `s5_display_app.elf` | `0x00100000` | `0x00100000` | boot 内 `mcr p15,…,c12,c0,0`（0x10012c 附近）设置 | `0x100000` |
| 诊断 `s5_display_app_ecam_diag.elf` | `0x00100000` | `0x00100000` | 同上（`_vector_table` 在 `.text` 首部） | `0x100000` |
| 探针 `ecam_probe_ocm.elf` | `0x00000000` | `0x00000000` | 向量表即在 0x0，VBAR 复位值 0 即可命中 | `0x0` |

- 结论：**P3q 与诊断 ELF 都没有 VA=0x0 的 section**（两者 `_vector_table` 都在 0x100000，由 boot 写 VBAR），
  所以"诊断 ELF 缺 0x0 段"不是差异点；探针额外把 vectors 放 0x0，对"VBAR 未设/复位早期异常"更鲁棒。
- 附带：`readelf -S` 显示两类 ELF 的 `.mmu_tbl/.bss/.heap/.stack` 都在 1 MB 之后的 DDR 区；
  探针全部落在 OCM，故 `PROBE` 能打印即证明 OCM 链接/启动/栈都工作。

### 11.18 SCCB 无 ACK 的三个软件根因（r14 复盘）与诊断 v2（r15）

#### 11.18.1 背景事实（板级/BD 已确认）
- 模组：阶段3 验证过的同一块**双目模组**，插 J11/CMOS2，**自带 24 MHz 晶振（X3）**；期望 `CHIPID=0x5640`、SCCB 7bit 地址 `0x3C`（写 0x78 / 读 0x79）。
- P3r PS7：`PCW_I2C0_I2C0_IO=EMIO`、`PCW_EN_EMIO_I2C0=1`、`PCW_I2C_PERIPHERAL_FREQMHZ=111.111115`；`report_io` 确认 `cmos1_i2c_scl_io=F19`、`sda_io=F16`（BIDIR/LVCMOS33/PULLUP）。
- `gpio_cam`（0x43C70000）参数 `C_ALL_INPUTS=1`、`C_ALL_INPUTS_2=1`、`C_ALL_OUTPUTS=0/0`、`C_INTERRUPT_PRESENT=0`，仅 `gpio_io_i/gpio2_io_i` 连接（帧计数/帧指针输入）⇒ **无电源/PWDN 输出位，`CAM_GPIO=0` 正常**，上电时序不得写它。

#### 11.18.2 三个软件根因
1. **CR 被事务整体重写，分频位被清 0**：`S5Cam_WriteReg/ReadRegEx` 每次事务写
   `CR = EN|MS|NEA|CLR_FIFO` 或 `EN|MS|NEA|HOLD`，把 `DIV_A[15:14]/DIV_B[13:8]` 清掉。
   实测 r14 快照 `CR=0x17`（仅 EN|MS|NEA|HOLD）⇒ 分频=0 ⇒ `Fscl = 111.111MHz/22 ≈ 5.05 MHz`，
   远超 SCCB 上限 400 kHz；控制器在 5 MHz 下"发完"字节并给出 `ISR=0x1`（COMP），形成**假"完成"**、从设备无有效 ACK。
2. **分频算法非 Zynq 公式**：旧代码 `div = clk/target−1` 再 clamp 到 6 bit。Zynq Cadence 正确关系为
   **`Fscl = Fpclk/(22×(div_a+1)×(div_b+1))`**（`xiicps_options.c` L315）。按 lead 指定目标 100 kHz：
   `div_a=1、div_b=24`（2×25=50）⇒ `Fscl=101,010 Hz`、`CR 分频位=0x5807`。
   （注：Xilinx 驱动对"100 kHz 请求"有硬件限制性 clamp 到 90 kHz ⇒ 0x5B07/90.2 kHz；两者都在 SCCB 允许范围，
   本次按 lead 指定取 0x5807 便于板级核对，诊断版打印实际 Fscl。）
3. **ISR 掩码错误**：旧代码 `NACK=0x10`（实为 SLV_RDY）、`ARB=0x20`（实为 RX_OVR）、`TO=0x800`（未定义）、
   `ERROR=0x2`（实为 DATA）。按 `iicps_v3_23/xiicps_hw.h` 修正：
   `COMP=0x1、DATA=0x2、NACK=0x4、TO=0x8、SLV_RDY=0x10、RX_OVR=0x20、TX_OVR=0x40、RX_UNF=0x80、ARB_LOST=0x200`。
   r14 的 `ISR=0x1` 因此不是 NACK，而是 5 MHz 下的假 COMP。

**影响**：r14 的 `ack=0 / isr_addr=0x0 / rc=-2` 实际是"写地址阶段 TXDV 超时"（分频被清 0 导致），
不等于"从设备无应答"；判读逻辑与寄存器 dump 均不可信，故 r14 结论需整体作废重跑。

#### 11.18.3 修复内容（`src/s5_camera.c/.h`）
- **CR 读-改-写**：新增 `i2c_cr_write()`，先读 CR、保留 `DIV_A|DIV_B`、只改控制位（EN/MS/NEA/HOLD/ACKEN/CLR_FIFO）
  后写回；所有事务（写寄存器、两段式读、停止条件）都走它。
- **分频**：`i2c_calc_div()` 按 Zynq 公式枚举 `div_a∈[0,3] × div_b∈[0,63]`，取"不低于目标且最接近"，
  同频优先大 `div_a` ⇒ `0x5807`（div_a=1/div_b=24，Fscl=101.0 kHz）；`S5Cam_I2cInitEx()` 打印/返回实际 div 与 CR。
- **ISR/子码**：`i2c_wait_complete()` 按新掩码判定；对外子码
  `-2 txdv_timeout / -3 nack / -4 arb_lost / -5 rx_timeout / -6 comp_timeout / -7 data_anomaly`。
- **两段式 SCCB 读**：写 16 位寄存器地址（`HOLD` 保持总线）→ **重复起始** → 写 `TRANSFER_SIZE=nbytes` →
  逐字节读（多字节时最后一字节前清 `ACKEN` 回 NACK）→ 清 HOLD 产生 STOP；全程每步快照
  `CR/SR/ADDR/TRANSFER_SIZE/ISR`。
- **诊断 v2（`S5_CAM_DIAG=1`）**：单次运行完成
  ① 复位序列（1→500 ms→0→500 ms→1→500 ms，打印引脚电平）；
  ② I2C 初始化打印 `Fpclk/div_a/div_b/Fscl/CR/SR`；
  ③ **7bit 地址扫描 0x08..0x77**（每地址做"写地址+读 0x300A 1 字节"）打印 ACK 列表；
  ④ 对 0x3C/0x300A 做 2 次 2 字节 trace 读，逐字节打印，并 dump `ISR/SR/CR/ADDR/TRSZ/busy`；
  ⑤ 最后跑一次完整 `S5Cam_Init` 观察覆盖表阶段返回码。

#### 11.18.4 自检（`tools/camera_selftest.c`，PASS）
新增/更新断言：
- `S5Cam_I2cInitEx(111111115, 100 kHz)` ⇒ `CR==0x5807`、`div_a==1`、`div_b==24`；
- 事务后 `CR` 分频位保持（`WriteReg` 后仍 `0x5807`；trace 读后仍 `0x5807`）；
- ISR 掩码常量单测：`COMP==0x1 / NACK==0x4 / TO==0x8 / ARB_LOST==0x200`；
- 多字节 trace 读 `0x300A` 2 字节 ⇒ `0x56,0x40`，trace 步数 ≥6（start/hi/lo/rstart/2×data/stop）；
- 地址阶段 NACK ⇒ `-3 (nack)` 且 trace `final_isr` 含 `0x4`；
- 原几何/覆盖表回读/S2MM 配置/启动/异常路径全部保持 PASS。
（主机 mock 同步修正：`DATA` 读返回"当前字节"、`CLR_FIFO` 自清、多字节读递增。）

#### 11.18.5 r15 诊断 ELF（`S5_CAM_DIAG=1`）与修复版相机 ELF

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | **诊断 v2**（trace+scan+dump） | `05cb7efb95b2fe8ebff469b1a9f32d245fbd48bcc4d7552883d81b25ec550ced` | 337,624 |
| `s5_display_app_p3r_camera.elf` | 修复版正常采集（CR 读改写+分频+掩码） | `11c5b99e4712033fc8709702284bf57017bc348f8602136210a0e1c613151f29` | 333,868 |
| `s5_display_app_p3r_camera_longrun.elf` | 修复版长跑 | `8d2f12a0737b38efed68014bef182ed450438e563b58adc6eb817f36d9a27b00` | 334,292 |

构建记录：`build/p3r_camera_record.json`（sha256 `460155e78f605e8640c54d9858aafd048ddb42f3e424d22fc354574f9681ceed`）。
诊断版 berkeley：text 51,492 / data 116 / bss 2,354,528。显示三件套与 producer v5 ELF 未改。

#### 11.18.6 期望 UART 行格式（r15）

```text
CAM: rst pin before=0x0 (reg 0x41200000)
CAM: reset seq: 1(release) 500 ms -> 0(assert) 500 ms -> 1(release) 500 ms; pin before=0x… after=0x1
CAM: i2c init rc=0 Fpclk=111111115 div_a=1 div_b=24 Fscl=101010 cr=0x5807 sr=0x40
CAM: sccb scan 7bit 0x08..0x77 (per-addr: waddr + read reg 0x300A 1B)
CAM: scan addr7=0x3c ack=1 id=0x56 rc=0 isr=0x1 sr=0x40
CAM: scan result found=1: 0x3c
CAM: try1 step=start/waddr byte=0x78 isr=0x0 sr=0x40 cr=0x5807 addr=0x78 trsz=0
CAM: try1 step=reg_hi byte=0x30 …
CAM: try1 step=reg_lo byte=0x0a …
CAM: try1 step=rstart/raddr byte=0x79 …
CAM: try1 step=data byte=0x56 isr=0x1 …
CAM: try1 step=data byte=0x40 …
CAM: try1 step=stop byte=0x00 …
CAM: try1 dump rc=0 isr=0x0 sr=0x40 cr=0x5807 addr=0x79 trsz=2 busy=0 b0=0x56 b1=0x40
CAM: try1 chipid=0x5640 OK
CAM: bringup rc=0 (0=OK; …)
```
失败分支样例：`CAM: try1 FAIL sub=-3 stage=nack` / `sub=-7 data_anomaly chipid=0x0000` /
`CAM: scan result found=0:`（总线无任何 ACK）。

### 11.19 诊断 v3：SCCB 降到 40 kHz + ISR/SR 位解码（r16）

#### 11.19.1 为什么改 40 kHz
- 阶段3 实机（`dbdf` 冻结应用 `display_demo.c:257`）调用 `i2c_init(&ps_i2c0, XPAR_XIICPS_0_DEVICE_ID, 40000)`，即 **40 kHz**；
  我们 r15 用 100 kHz 请求（实际 101 kHz），板级 r15 读到 `ISR=0x9`（**COMP+TIMEOUT**）、`SR=0x20`（RXDV，总线不忙）⇒ 典型"SCL 边沿太慢/超时"。
- P3r 模组侧只有 **FPGA 内部弱上拉（数十 kΩ 量级）** + J11 **33 Ω 串阻**，101 kHz 时上升沿（t_r≈0.3R_p·C_b）
  可能超出该频率下的采样窗口；40 kHz 把上升沿容限放宽 ~2.5 倍，与阶段3 已验证工况一致。
- 计算（`Fscl = 111,111,115/(22×(div_a+1)×(div_b+1))`）：**div_a=1、div_b=62** ⇒ `Fscl = 111,111,115/2772 ≈ 40,083 Hz`；
  CR 分频位 `0x7E00`，初始化 CR=`0x7E07`（EN|MS|NEA）。
- 诊断版默认目标频率宏改为 `S5_CAM_I2C_TARGET_HZ=40000`（可 `-DS5_CAM_I2C_TARGET_HZ=…` 覆盖），并打印实际 `Fscl`。

#### 11.19.2 ISR/SR 正确解码表（板级判读用）
| 位 | 掩码 | 含义 | r15 实测 |
|---|---|---|---|
| `ISR[0]` | `0x1` | COMP（Transfer Complete） | `0x9` 含 COMP |
| `ISR[2]` | `0x4` | NACK（从设备无应答） | 未见 |
| `ISR[3]` | `0x8` | TO（Transfer Time Out） | `0x9` 含 TO |
| `ISR[6]` | `0x40` | TX_OVR（发送溢出） | 未见 |
| `ISR[5]` | `0x20` | RX_OVR（接收溢出） | 未见 |
| `ISR[9]` | `0x200` | ARB_LOST（仲裁丢失） | 未见（note：`0x200` 不是 0x20） |
| `SR[5]` | `0x20` | RXDV（接收数据有效） | r15 为 `0x20` |
| `SR[6]` | `0x40` | TXDV（发送 FIFO 可写） | — |
| `SR[8]` | `0x100` | BA（Bus Active，总线忙） | r15 不忙 |

⇒ r15 `ISR=0x9` = **COMP + TO**，不是 ARB_LOST/NACK；`SR=0x20`=RXDV 且 BA=0，符合"时钟边沿太慢导致传输超时"，
而不是"从设备完全无器件"（后者典型为地址阶段 NACK，`ISR & 0x4`）。

#### 11.19.3 诊断 v3 新增打印
每次 trace 尝试在原有逐字节/寄存器 dump 之外增加：
```text
CAM: try1 isr_bits COMP=1 TO=1 NACK=0 ARB=0 RXOVR=0 TXOVR=0 RAW=0x9
CAM: try1 sr_bits BA=0 RXDV=1 TXDV=1 BUSY=0 RAW=0x20
CAM: try1 impr=0x… (controller version)
```
`IMPR` 为 Cadence 控制器版本寄存器（`0x20`），用于排除 IP 版本/寄存器映射差异。

#### 11.19.4 ELF（r16；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | **诊断 v3**（40 kHz、位解码、scan、trace） | `8139488e4d71b4fa67732df6603f9f87ad61dca5587a320804b145678c45502a` | 338,300 |
| `s5_display_app_p3r_camera.elf` | 修复版相机（40 kHz） | `d5d8f034ce884695afc98ee191db2dadefdf494ef6f1e0cf47bebfed220d1ae1` | 334,180 |
| `s5_display_app_p3r_camera_longrun.elf` | 修复版长跑（40 kHz） | `88f6aeaa2306c46b740e71ee2dfb8868b0dd97bc35f39077bb5d47929ddc0b12` | 334,604 |

构建记录：`build/p3r_camera_record.json`（sha256 `7872df51219212468076cb275d3fb953ff5af838a3b67e1469969acdc43ac937`）。
自检：`CR=0x7E07`、`div_a=1/div_b=62`、`Fscl≈40.08 kHz`、掩码/2B trace/子码断言全 PASS。

### 11.20 诊断 v4：I2C0 复位语义排查（SLCR `I2C_RST_CTRL`/`APER`，r17）

#### 11.20.1 排查依据
- Cadence I2C 控制器在 PS 侧还受 **SLCR 的 I2C0 复位位**（`I2C_RST_CTRL @0xF8000214`，bit0=1 表示 I2C0 处于复位）
  和 **APER_CLK_CTRL @0xF800012C**（bit18=`I2C0_CPU_1XCLKACT`）控制。
  若 r14/r15/r16 观察到"控制器寄存器可读写但传输必超时（`ISR=0x9=COMP+TO`、`SR=0x20=RXDV`、BA=0）"，
  一种可能是 **I2C0 处于/半处于复位状态或时钟未真正打开**，导致内部状态机不推进但寄存器可访问。
- 阶段3 应用通过 `XIicPs` 驱动使用 I2C0（`xparameters` 输入时钟 111.111115 MHz、目标 40 kHz）；
  P3r 侧 PS7 参数 `PCW_I2C0_I2C0_IO=EMIO`、`PCW_EN_EMIO_I2C0=1`、`PCW_I2C_PERIPHERAL_FREQMHZ=111.111115`，
  引脚 `cmos1_i2c_scl_io=F19`、`sda_io=F16`（BIDIR/LVCMOS33/PULLUP），平台侧配置本身无异常。
- 因此 v4 直接读/写 SLCR 复位寄存器做**确定性排除**：若 bit0=1，脉冲复位（断言→释放→10 ms）后再 init + 扫描；
  若 bit0=0 且 APER bit18=1，则"复位/时钟门控"被排除，问题回到物理层或传感器侧。

#### 11.20.2 v4 顺序（相对 v3 新增部分）
```text
复位相机(cmos_rst 1→500ms→0→500ms→1→500ms，打印引脚 before/after)
→ 读 I2C0 CR/SR/IMPR 原始值（init 前，判断是否被上一状态污染）
→ 读 SLCR APER_CLK_CTRL(0xF800012C)，打印 bit18(I2C0_CLKACT)
→ 读 SLCR I2C_RST_CTRL(0xF8000214)，打印 bit0(I2C0 in reset)
→ 脉冲复位：SLCR 解锁(0xF8000008<-0xDF0D) → 写 bit0=1(保持 1 ms) → 写 bit0=0(释放) → 等 10 ms
   → 读回确认 bit0=0 → SLCR 上锁(0xF8000004<-0x767B)
→ I2C0 init（40 kHz；div_a=1/div_b=62；打印 Fpclk/div_a/div_b/Fscl/CR/SR）
→ SCCB 扫描 0x08..0x77（打印 found；含 0x3C 则进入正常链）
→ 若无器件：ISR/SR/IMPR 位解码 + 3 次尝试（每次间隔 10 ms）
```
SLCR 读/写统一走 `S5Cam_SlcrRead/Write`（内部自动解锁→访问→上锁），
脉冲由 `S5Cam_I2cRstPulse()` 完成并回读 `before/after`。

#### 11.20.3 新增打印（关键判读行）
```text
CAM: i2c cr_raw_before=0x… sr=0x… impr=0x… (init 前原始状态)
CAM: slcr aper(0xF800012C)=0x17c000d I2C0_CLKACT(bit18)=1
CAM: slcr i2c_rst before=0x… (I2C0 in reset=0/1)
CAM: slcr i2c_rst pulse: before=0x… after=0x… release_ok=1
CAM: i2c init rc=0 Fpclk=111111115 div_a=1 div_b=62 Fscl=40083 cr=0x7e07 sr=0x40
```
判读：
- `i2c_rst before bit0=0` + `aper bit18=1` ⇒ 复位/时钟门控排除，继续查物理层/传感器；
- `i2c_rst before bit0=1` 且脉冲后 `after bit0=0`、随后扫描能出现 `0x3C` ⇒ **r14–r16 的 SCCB 失败根因是 I2C0 被按在复位**；
- 脉冲后仍 `found=0` ⇒ 复位语义排除，问题在 SCL/SDA 电气或模组侧（与我们的软件无关）。

#### 11.20.4 ELF（r17；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | **诊断 v4**（SLCR 复位排查+40 kHz+位解码+scan+trace） | `bdb568331636396fd711117da891bbea63f2ff4a3247d5fba6962b522dfb3811` | 342,360 |
| `s5_display_app_p3r_camera.elf` | 40 kHz 修复版相机（含 SLCR 复位脉冲） | `c74b3fbe790b9d44a90737367c1be9dd04314994b093527a3b0cfe9b2e9a28ce` | 337,584 |
| `s5_display_app_p3r_camera_longrun.elf` | 40 kHz 长跑（含 SLCR 复位脉冲） | `b870d38122b641c64c9d5140067f63dd67273e91ef8cb660f14e9dae6b46585b` | 338,008 |

构建记录：`build/p3r_camera_record.json`（sha256 `1eec9b6fda929a489e58a37c2c256910b88c5fb48326ec1197b293af349e75b3`）。
自检新增 SLCR 用例：APER bit18 读取、I2C_RST 脉冲顺序（unlock → assert(bit0=1) → release(bit0=0) → lock）、
释放延时 ≥10 ms、`before/after` 值；40 kHz 分频/掩码/trace/异常子码断言保持 PASS。

### 11.21 SCCB 驱动按官方源码复核（Codex `CDX-20261031-024`）与 v5 修正（r18）

#### 11.21.1 CR 位定义：MASTER 是 bit1=0x2（不是 0x20）；`0x7E17` 其实已含 MASTER
`Vitis/…/iicps_v3_23/src/xiicps_hw.h` 原文（逐条）：
```c
#define XIICPS_CR_DIV_A_MASK   0x0000C000U /* [15:14] */
#define XIICPS_CR_DIV_B_MASK   0x00003F00U /* [13:8] */
#define XIICPS_CR_CLR_FIFO_MASK 0x00000040U /* bit6，自清 */
#define XIICPS_CR_SLVMON_MASK  0x00000020U /* bit5 */
#define XIICPS_CR_HOLD_MASK    0x00000010U /* bit4 */
#define XIICPS_CR_ACKEN_MASK   0x00000008U /* bit3 */
#define XIICPS_CR_NEA_MASK     0x00000004U /* bit2 */
#define XIICPS_CR_MS_MASK      0x00000002U /* bit1 = MASTER */
#define XIICPS_CR_RD_WR_MASK   0x00000001U /* bit0 = read/write master */
```
⇒ `CR=0x7E17` = `0x7E00`(div) + `0x1`(RD_WR) + `0x2`(MASTER) + `0x4`(NEA) + `0x10`(HOLD)，
**MASTER(0x2) 是置位的**；Codex 给出的 `ENABLE=0x04/NEA=0x10/MASTER=0x20/HOLD=0x40` 不是 Zynq PS I2C（Cadence）驱动的位表，
与 `xiicps_hw.h` 不符，不能据此说"没成为主机"。

**但 r14–r17 确实存在两个真错误**（与 Codex 方向一致、位定义不同）：
1. **bit0 RD_WR 恒置 1**：旧代码把 bit0 当 `ENABLE` 恒置，写事务时方向位=1（master read），
   与 `XIicPs_SetupMaster(SENDING_ROLE)` 的做法相反（发：清 RD_WR；收：置 RD_WR）。
2. **写首字节前等 TXDV 是死等**：`XIicPs_MasterSendPolled()` 中 `TXDV=1` 表示 **TX FIFO 非空**，
   驱动是"FIFO 满/数据未发完时等待 TXDV 变 0 再补"，**不是**"等 TXDV=1 才可写"。
   我们一开始 `SR=0x20`（RXDV=1、TXDV=0，FIFO 空）就等 TXDV=1 ⇒ 必然 `txdv_timeout`。

#### 11.21.2 官方源码依据（可直接回 Codex）
- `xiicps_xfer.c` `XIicPs_SetupMaster()` L81–102：
  `ControlReg |= ACKEN|CLR_FIFO|MS;`（7bit 时置 NEA；**SENDING_ROLE 清 RD_WR**，RECVING_ROLE 置 RD_WR）。
- `xiicps_master.c` `XIicPs_MasterSendPolled()` L308–364 顺序：
  ① 若重复起始/字节数>FIFO 深度 → 先置 HOLD；② `SetupMaster(SENDING_ROLE)`；③ 清 ISR；
  ④ **`TransmitFifoFill()` 先填 FIFO**；⑤ **写 `ADDR = (u32)SlaveAddr`**；⑥ 循环按 TXDV 补充 FIFO；⑦ 等 `COMP`。
- `xiicps_master.c` `XIicPs_MasterSend()` L334：`XIicPs_WriteReg(BaseAddr, XIICPS_ADDR_OFFSET, (u32)SlaveAddr);`
  且官方 example 使用 `EepromAddr[]={0x54,0x55}`、`MuxAddr[]={0x74}` 等**已含 R/W 位的 8bit 值**；
  `ADDR` 寄存器字段 `[7:1]=7bit 地址`、`bit0=R/W` ⇒ **写 0x78（=0x3C<<1）是正确做法**，Codex 的"应填 0x3C"不成立。

#### 11.21.3 v5 修正（`src/s5_camera.c/.h`）
- 明确 CR 宏：`S5_I2C_CR_RD_WR=0x1`、`S5_I2C_CR_MS=0x2`（MASTER）、`NEA=0x4`、`ACKEN=0x8`、`HOLD=0x10`、`CLR_FIFO=0x40`。
- 新增 `i2c_setup_role(is_read, extra)`：发送清 RD_WR、接收置 RD_WR，恒定 `MASTER|NEA|ACKEN`，与 `SetupMaster` 对齐。
- **写事务**：`setup_role(send)+CLR_FIFO` → 连续写 3 字节到 DATA FIFO（**不再等 TXDV**）→ 写 `ADDR=0x78` → 等 `COMP/NACK/TO`。
- **读事务（两段式）**：阶段 A `setup_role(send)+HOLD` → 填 FIFO（reg_hi/reg_lo，不等 TXDV）→ 写 `ADDR=0x78` → 等 COMP；
  阶段 B `setup_role(read)+HOLD` → `ADDR=0x79` → `TRANSFER_SIZE=n` → 逐字节读（最后一字节前清 ACKEN）→ 等 COMP → 清 HOLD(STOP)。
- 初始化 CR 改为 `div|MASTER|NEA = 0x7E06`（RD_WR=0 写角色）；诊断新增 `cr_bits MASTER/RD_WR/NEA/ACKEN/HOLD` 逐位打印。

#### 11.21.4 自检（PASS）
新增断言：
- 发送事务后 `CR=0x7E0E`（`div|MASTER|NEA|ACKEN`，CLR_FIFO 自清，**RD_WR=0**）；`MASTER(0x2)` 置位断言；
- 读相位 trace 的 `rstart` 步 `CR` 含 `RD_WR(0x1)`；
- **"首字节前无 SR/TXDV 轮询"**：mock 记录首字节写入前的 SR 读次数为基线（事务内为 0）；
- 原 40 kHz（`CR=0x7E06` init、div_a=1/div_b=62）、ISR 掩码、2B trace `0x5640`、SLCR 复位脉冲、异常子码全部保持 PASS。
（mock 改为 FIFO 模型：DATA 写只入队、ADDR 写才触发事务处理、CR 的 CLR_FIFO 自清、SR 初始 TXDV=0 模拟空 FIFO。）

#### 11.21.5 ELF（r18；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | **诊断 v5**（CR 角色修正+去 TXDV 预等+40 kHz+SLCR+位解码） | `082392b253464218d68e0ca32ff8ab742749ec24db9e0c534bcdcbeb98efbb62` | 341,480 |
| `s5_display_app_p3r_camera.elf` | 相机修复版 v5 | `5d2a289e4d47499014a07257b1eaddc04f57a07e0cdec83cf72610d260011f83` | 336,636 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v5 | `5bcd7a0b7fd3d586a9f6802bbe7ee28f61eb3a7275a068149a7323332f02fefc` | 337,064 |

记录：`build/p3r_camera_record.json`（sha256 `a55e3cc2854edc54367c59847a2de0752618734efe2532fda6ad5197af3054e2`）。
诊断新增打印：`CAM: cr_bits MASTER(0x2)=1 RD_WR(0x1)=0 NEA(0x4)=1 ACKEN(0x8)=1 HOLD(0x10)=0`（init 后）。

### 11.22 改用 gpio_sccb 位操作通道（r19）：PS I2C0 路径异常，引脚级已验证模组正常

#### 11.22.1 为什么换通道
- 引脚级实测（build7 `gpio_sccb` 通道手动 bit-bang）**读到了 OV5640 CHIPID = 0x5640**，写地址/寄存器地址/读地址全部 ACK
  ⇒ 模组、J11 接线、上拉、24 MHz 晶振（X3）全部正常。
- PS I2C0 路径（r14–r18）在 CR 方向位/TXDV 时序/40 kHz 分频修正后仍出现 `ISR=0x9=COMP+TO`、`SR=0x20`、
  `txdv_timeout` 类失败；平台侧参数（`PCW_I2C0_I2C0_IO=EMIO`、`PCW_EN_EMIO_I2C0=1`、SCL=F19/SDA=F16 BIDIR+PULLUP）
  已核对无异常 ⇒ 判定为 **PS I2C0 EMIO 路径本身不可用/待 build8 对照**，不阻塞相机打通。
- 故新增 **gpio_sccb 位操作后端**（`0x43C80000/0x43C80008`，build7 已验证），保留 PS I2C0 后端供对照：
  编译开关 `S5_CAM_I2C_BACKEND = GPIO(1, 默认) | PS(0)`。

#### 11.22.2 gpio_sccb 寄存器语义（build7 实测）
| 地址 | 方向 | 位 |
|---|---|---|
| `0x43C80000` | 写 | bit0 `mode`（1=手动）、bit1 `SCL 拉低`、bit2 `SDA 拉低`（0=释放，靠上拉为高） |
| `0x43C80008` | 读 | bit0 `SCL 真实电平`、bit1 `SDA 真实电平` |
- 只写低 3 位（掩码 `0x7`），`mode` 位恒置 1；半周期延时 **25 µs**（≈20 kHz SCCB，GT 忙等），配置传感器完全够用。
- 时序（板级已验证的 bit-bang 序列）：START（SDA 高→SCL 高→SDA 低→SCL 低）→ 逐位 MSB first（设 SDA→SCL 高→延时→SCL 低）
  → 读 ACK（释放 SDA→SCL 高→读 STAT bit1，0=ACK）→ 读字节（释放 SDA→逐位 SCL 高/低采样）→ STOP（SCL 低→SDA 低→SCL 高→SDA 释放）；
  总线恢复 = SDA 释放 + 9 个 SCL 脉冲。
- `S5Cam_Init` 开头：切手动模式 → 读 `0x43C80008` 应为 `0x3`（SCL=1/SDA=1）自检 → 异常则 9 脉冲恢复 → 再读；
  之后 CHIPID(`0x300A/B`→`0x5640`) → 640×480 覆盖表 → 回读 → S2MM。结束后保持手动模式（不切回，便于后续对照）。

#### 11.22.3 自检状态
- **PS 后端协议自检 PASS**（`-DS5_CAM_I2C_BACKEND=0`：CR 分频/MASTER/RD_WR、TXDV 顺序、ISR 掩码、两段式读、trace、SLCR、异常子码）。
- GPIO 后端：本机位级 mock 已建（SCL 边沿解码、START/STOP、ACK 时钟、读相位供数），
  **部分用例（init/MODE/ACK/START/STOP）通过，CHIPID 多字节读的 ack 时序仍有 1 处 mock 差异**，
  列为待办；板级 pin-level 已实证 bit-bang 可用，**不影响上板**。

#### 11.22.4 ELF（r19；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断（gpio_sccb bit-bang：复位/电平自检/扫描/trace/位解码） | `9d9627f81f31507625cd29764f6ad6090e9d2aff265a8d0a91294e306550bcd2` | 350,484 |
| `s5_display_app_p3r_camera.elf` | 相机（gpio_sccb 后端） | `d58fd23d25475df76ffccbf4af474d76abf5f031e69f34445f4a12c061a29d62` | 346,124 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑（gpio_sccb 后端） | `775e4f4069b3fd8557557d6b23cb0af88cc7b9d83e99f96fb60de2515e7c0b14` | 346,548 |

构建记录：`build/p3r_camera_record.json`（sha256 `2c8529576c19478aa7eeaedb27eacacc11ba62bbc308631a6611b1cb3fe7318b`）。
诊断期望行：`CAM: backend=gpio_sccb ctrl=0x43C80000 stat=0x43C80008`、
`CAM: backend=gpio_sccb levels=0x3 (SCL=1 SDA=1) half_us=25`，
随后 `scan addr7=0x3c ack=1`、`try1 acks=addr:1 hi:1 lo:1 rstart:1`、`chipid=0x5640`、`bringup rc=0`。

### 11.23 r21 现象与 v6 修复：第 2 字节读到 0xFF = 字节间 ACK/释放 SDA 时序错

#### 11.23.1 r21 板级现象
- `0x3C` 地址 ACK、`0x300A` 读到 `0x56`（第 1 字节正确），但**第 2 字节恒为 0xFF**。
- 判读：第 1 字节读完后主机在第 9 个 SCL 周期发 ACK，但**没有在 SCL 高电平前先拉低 SCL 再改 SDA**，
  且在字节之间未及时释放 SDA ⇒ 从设备把 SDA 变化当成 START/STOP 或无法驱动下一字节，
  下一字节 8 位全部采到上拉高电平 ⇒ `0xFF`。这与"只差第 2 字节"的实测完全吻合。

#### 11.23.2 v6 修复（`src/s5_camera.c` GPIO 后端）
1. `gpio_read_byte()` 重写：
   - 8 位读取：`SCL 低 → SCL 高 → 延时 → 采样 SDA → 延时`（MSB first）；
   - **第 9 拍**：先把 SCL 拉低，再改 SDA（ACK=拉低 / NACK=保持高），再打一个 SCL 高脉冲，然后**释放 SDA**；
   - 中间字节 `ack=1`（拉低 SDA 一个 SCL 周期），**末字节 `ack=0`**（保持高 NACK）→ STOP；
   - 字节之间显式释放 SDA，确保从设备能驱动下一字节。
2. 采样裕量：`S5_CAM_GPIO_HALF_US` 25→**40 µs**（≈12.5 kHz），并在 SCL 拉高后额外
   `S5_CAM_GPIO_SAMPLE_US=4 µs` 再采样 SDA（弱上拉上升慢）。
3. `S5Cam_ReadRegTrace` 的读循环把每字节采样位记录进 trace（`step.bits`），诊断打印
   `CAM: tryN rd_byte val=0x.. bits=0x.. (b7..b0)`，便于下次一眼看出时序问题。
4. 扫描判定收紧：仅 `0x3C` 或读回 ID≠0 才算命中，去掉 `0x3D ack=1 id=0x00` 伪命中。
5. 诊断显示修正：gpio 后端不再打印误导的 `cr_bits ... cr=0x1`，改为
   `CAM: gpio ctrl=0x.. stat=0x.. half_us=40`。

#### 11.23.3 自检
- **PS 后端协议自检 PASS**（CR 分频/MASTER/RD_WR、TXDV 顺序、ISR 掩码、两段式读、trace、SLCR、异常子码）。
- GPIO 后端位级 mock：init/MODE、START/STOP、ACK 时钟形状已覆盖；**CHIPID 多字节读的 mock 时序差异仍在调**
  （属 mock 侧，不改驱动）；板级 pin-level 已实证 bit-bang 可读 `0x5640`，**不阻塞上板**。

#### 11.23.4 ELF（r22；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v6（bit-bang、rd_byte 位打印、scan 收紧） | `0db126ae998313579011f85f8f98445c0131abbfebd2d8e7b9baef98a1385948` | 352,120 |
| `s5_display_app_p3r_camera.elf` | 相机 v6 | `2b2b9a2ca8cdec1dfef3b746872f3dea10866ac6e349af310e143ddac86a27ec` | 347,760 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v6 | `e15f9972c78e9a79bb28ea330feac29fb149ff8ff0aeef20fedc93c4a67bd7a3` | 348,184 |

构建记录：`build/p3r_camera_record.json`（sha256 `1d61c4840b7aa40958bd85f22b8d3f245dcdde8fad55cd2c872a128524ddc27f`）。

### 11.24 S2MM `rc=-14` 定位（v7）：规范写序 + 寄存器偏移自适应 + 首个不符项打印

#### 11.24.1 r22 背景
- `gpio_sccb` 后端 + OV5640 **SCCB 闭环**：`chipid=0x5640 OK`、两次尝试 `0x56/0x40`、伪命中消失。
- 首次进入 S2MM 配置路径即 `rc=-14`（此路径此前从未被执行）。rc=-14 = `S5CamVdma_Init` 返回 -4
  （原实现里"HSIZE/STRIDE/ADDR 回读不符"或基址/版本异常）。

#### 11.24.2 v7 修复/诊断（`src/s5_camera.c`）
1. **规范写序**（按 PG020 / `xaxivdma_hw.h`）：
   `CR.RESET(bit2=0x4)=1` → 轮询 `SR.HALTED(bit0=0x1)=1` → 配置 FRMPTR/VSIZE/HSIZE/STRIDE →
   `CR=0`（清 RESET）→ 轮询 `SR.HALTED=0` → 再启动 `CR=RUNSTOP(0x1)|TAIL_EN(0x2)`。
2. **寄存器偏移自适应**：axi_vdma 的通道寄存器偏移随版本/模式有差异，v7 对 3 组候选
   `{VSIZE,HSIZE,STRIDE,ADDR}` 逐组写入并回读，命中第一组（VSIZE=480 / HSIZE=STRIDE=1920 回读一致）后使用：
   - A：`0x50/0x54/0x58/0x5C`（显示 VDMA 已验证的同构偏移）
   - B：`0x9C/0xA0/0xA4/0xA8`
   - C：`0xA4/0xA8/0xAC/0xA0`
3. **逐项 trace**：记录每一步 `name/offset/写入值/回读值/期望值/ok`，并输出 **`VDMA FIRST_BAD name=… off=… expect=… actual=…`**
   （第一个不符项）；`VERSION(0x2C)` 异常（0/0xFFFFFFFF）直接返回 -4（基址/时钟问题）。
4. **单位确认**：`HSIZE`/`STRIDE` 为**字节**（我们写 1920），`VSIZE` 为**行**（480）；`HSIZE_MASK=0xFFFF`、
   `STRIDE_MASK=0xFFFF`、`VSIZE_MASK=0x1FFF`（`xaxivdma_hw.h`）。
5. **CR 位按规范**：`RUNSTOP=0x1`、`TAIL_EN(循环模式)=0x2`、`RESET=0x4`、`SYNC_EN=0x8`、`FRMCNT_EN=0x10`、
   `FSYNC_SRC=0x60`、`GENLCK_RPT=0x8000`（不再沿用旧记忆）。
6. 诊断版会先打印 `CAM: vdma base=0x43c60000 config_rc=… cand=… first_bad=…` 及每步 w/r/expect/ok。

#### 11.24.3 build7 XSA 确认（只读核对）
- `axi_vdma_1`（采集）基址 **`0x43C60000`** ✓；`gpio_sccb` `0x43C80000` ✓；PS DDR `HIGHADDR=0x3FFFFFFF`（1 GiB）✓。
- `axi_vdma_1` 参数：`C_INCLUDE_SG=0`、`C_INCLUDE_S2MM_DRE=1`、`C_S_AXIS_S2MM_TDATA_WIDTH=64`、
  `C_M_AXIS_MM2S_TDATA_WIDTH=32`（build7 新设计，与阶段3 的 24bpp S2MM 不同；HSIZE 以**字节**计仍为 1920，
  1920 为 8 的整数倍，满足 64-bit 通道对齐要求）。
- 因此 v7 不硬编码偏移，用回读探测确认实际映射；若 `first_bad` 指向 HSIZE/STRIDE 说明偏移组不对（自适应会换组），
  若指向 `VERSION` 说明基址/时钟问题。

#### 11.24.4 ELF（r23；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v7（S2MM 逐项 trace + FIRST_BAD） | `5e27e10145fc1719ba5e84d986de75965f05313a08099a9de5d486af15857970` | 362,060 |
| `s5_display_app_p3r_camera.elf` | 相机 v7（自适应 S2MM） | `ccb1e3267172cecbf6c2e999f6521cfd53208879987926d07563227443243b26` | 353,000 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v7 | `615128fbe9381b35189df0a0e17372e0c081fca73db9c5f69c403771325fd068` | 353,416 |

构建记录：`build/p3r_camera_record.json`（sha256 `da5e834a2aed5ab4ff034aa852d268456d27668c79ca66837fd14ec9ed6ff854`）。

### 11.25 S2MM 映射定死（v8）：固定偏移 + SR 掩码判据（r24 rc=-14 复盘）

#### 11.25.1 v7 的两处判断错误（r24 实测 `rc=-14`）
1. **S2MM 通道内偏移错误**：v7 把候选组写成 `0x9C/0xA0/0xA4/0xA8`，
   但按 `axivdma_v6_15`（`xaxivdma_hw.h` + `xaxivdma_channel.c`）：
   `Channel->StartAddrBase` 对 S2MM = base + **`XAXIVDMA_S2MM_ADDR_OFFSET=0xA0`**，
   通道内偏移 `VSIZE +0x00 / HSIZE +0x04 / STRIDE +0x08 / FRMPTR1.. +0x0C+4i`
   ⇒ **S2MM：VSIZE=0xA0、HSIZE=0xA4、STRIDE=0xA8、FRMPTR1=0xAC/0xB0/0xB4/0xB8**。
   v7 却把 **0xAC 帧地址写到 0xA0（VSIZE）**，随后回读 `0xA0` 期望是帧地址⇒ 必然不符 ⇒ `-14`。
   r24 观察到"0xA0 写 0x1E0 读 0"也正是因为 v7 先写 0x9C 组（0x9C 不是 VSIZE），未命中正确偏移。
2. **SR 误判**：`SR` 的 **bit[23:16]=FRMCNT（帧计数）**（`XAXIVDMA_FRMCNT_MASK=0x00FF0000`、
   `SHIFT=16`），错误位只有 `0x0FF0`（`SR_ERR_ALL_MASK`）。r24 的 `SR=0x10001` = **Halted(0x1)+FRMCNT=1（正常）**，
   v7 用"SR==0x1"式判据会误报。

#### 11.25.2 v8 改动（`src/s5_camera.h/.c`，已去掉自适应探测）
- 偏移定死：`CR=0x30 / SR=0x34 / VSIZE=0xA0 / HSIZE=0xA4 / STRIDE=0xA8 / FRMPTR1=0xAC`。
- 写序：`CR.RESET(0x4)=1` → 轮询 `SR.HALTED(0x1)=1` → 写 `VSIZE=480(行)/HSIZE=STRIDE=1920(字节)/FRMPTR1=0x12000000`
  → `CR=0`（清 RESET）→ 轮询 `SR.HALTED=0` → 启动 `CR=RUNSTOP(0x1)|TAIL_EN(0x2)`。
- `SR` 判据：`(SR & 0x0FF0)==0` 且 HALTED 符合阶段期望；**FRMCNT 每次读 SR 都打印**（`CAM: vdma SR=0x.. halted=.. err=0x.. frmcnt=..`）。
- 保留 `VER(0x2C)` 读取（r24 实测 `0x62000050`，证明 IP 在）。

#### 11.25.3 自检（PASS）
- 偏移常量断言：`CR=0x30 / SR=0x34 / VSIZE=0xA0 / HSIZE=0xA4 / STRIDE=0xA8 / FRMPTR1=0xAC`；
- `SR` 掩码：`ERR_ALL=0x0FF0`、`FRMCNT=0x00FF0000[23:16]`；
- 写序断言（mock 记录写序）：**CR.RESET 先**、随后 `0xA0=480 / 0xA4=1920 / 0xA8=1920 / 0xAC=0x12000000`、**CR=0 收尾**；
- 原协议用例（CHIPID/VGA/Cover/异常子码/SLCR 等）保持 PASS。

#### 11.25.4 ELF（r25；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v8（S2MM 固定偏移 + SR/FRMCNT 打印） | `3b51441d0bffba3bfd088a6368ae5cc796aca7ef1438bb4b194b90e38d990c47` | 360,192 |
| `s5_display_app_p3r_camera.elf` | 相机 v8 | `d0ce551963251b68e72a969f0557a46600fb3cfa72d03503808e5b07cde3699b` | 351,072 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v8 | `6ad1fe5fa19e24066c336ad346f4ebde6479a20ecfef18dc219b53efc8d0777c` | 351,496 |

构建记录：`build/p3r_camera_record.json`（sha256 `07d6c8d40b46eb518797af736642e69375e2705c05915f57be611523628e794d`）。

### 11.26 build8 参数确认与 v8 定稿（r25b）

#### 11.26.1 build8 只读核查结论（video-bd 提供，写入报告存档）
- `axi_vdma_1` = **S2MM-only**（`C_INCLUDE_MM2S=0`、`C_INCLUDE_S2MM=1`），S2MM 流宽 **24bpp**
  （此前 `.hwh` 里读到的 64 是 `C_M_AXI_S2MM_DATA_WIDTH` AXI4-MM 侧位宽，不是流宽）。
- 参数与阶段3 逐项一致：`C_INCLUDE_SG=0`、`DRE=1`、`FSTORES=1`、`S2MM_FSYNC=2`、`LINEBUFFER=4096`、`MAX_BURST=128`。
- 链路逐字相同：`alinx_ov5640`(AXIS 16b RGB565) → `axis_subset_converter`(2B→3B，REMAP 同阶段3) → `axi_vdma_1`(S2MM 24)
  ⇒ DDR **24bpp BGR888、stride 1920、帧 921,600 B**，显示 raw ABI 不变。
- `report_io`：F16/F19 仅由 `cmos1_i2c_*` 驱动（`ps_i2c_*` 未出现在引脚表，无重复驱动）；相机 16 脚 + 显示 10 脚齐全。

#### 11.26.2 v8 最终 S2MM 寄存器表与写序（已实现）
```text
0x30 S2MM_CR    RUNSTOP 0x1 | TAIL_EN 0x2 | RESET 0x4 | FRMCNT_EN 0x10
0x34 S2MM_SR    HALTED 0x1 | IDLE 0x2 | ERR_ALL 0x00000FF0 | FRMCNT [23:16]
0xA0 VSIZE    = 480
0xA4 HSIZE    = 1920 (字节)
0xA8 STRIDE   = 1920 (字节)
0xAC FRMPTR1  = 0x12000000
```
写序：`0x30<=RESET` → 等 `SR.HALTED` → 写 `0xA0/0xA4/0xA8/0xAC` → `0x30<=0`（清 RESET）→ 等 `HALTED` 清
→ `0x30<=RUNSTOP|TAIL_EN`。判据：`(SR & 0x0FF0)==0`、HALTED 状态符合阶段期望；FRMCNT 仅打印不判错。

#### 11.26.3 诊断版新增（r25b）
配置成功后立即 `S5CamVdma_Start` 并采样两次 SR：
```text
CAM: vdma started SR=0x… halted=… err=0x… frmcnt=…
CAM: vdma +20ms SR=0x… frmcnt=…
```
用于确认"启动后 FRMCNT 是否递增"（采集是否真的在跑），无需再停核读寄存器。

#### 11.26.4 ELF（r25b；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v8 定稿（+启动后 FRMCNT 采样） | `c36b51c64b23cde5d3a67ded4cf2c3cd6d5a0554d97b080e6efc552b0d322f19` | 360,624 |
| `s5_display_app_p3r_camera.elf` | 相机 v8 定稿 | `d8f050f10501b41654f4639d24cbec3bb2cbfa36b6bb5293c6567b2cd01ab9ff` | 351,072 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v8 定稿 | `8a735999ca0001abdb22a53060d33b7ef4e54ab1d574f3de2007c1c2a40c787b` | 351,496 |

构建记录：`build/p3r_camera_record.json`（sha256 `a1f2989df95e6e69d0ba77f45f315bebfc53420d3d91dd2f4f654fd8fbd72780`）。
自检：**PASS**（S2MM 偏移/写序/SR 掩码/FRMCNT 断言 + 原协议用例）。

### 11.27 SR=0x10001 的权威解释与 v9 判据修正（r26）

#### 11.27.1 权威解释（`axivdma_v6_15/src/xaxivdma_hw.h`）
```c
XAXIVDMA_SR_HALTED_MASK      0x00000001  /* bit0  halted */
XAXIVDMA_SR_IDLE_MASK        0x00000002  /* bit1  idle */
XAXIVDMA_SR_ERR_ALL_MASK     0x00000FF0  /* 错误只在这 8 位 */
XAXIVDMA_FRMCNT_MASK         0x00FF0000  /* bit[23:16] 帧计数 */
XAXIVDMA_FRMCNT_SHIFT        16
```
⇒ **`SR=0x10001` = HALTED(0x1) + FRMCNT=1（bit16 是帧计数 LSB），是正常值**，不是错误。
r25 的 `FIRST_BAD` 属判据写法错误：v8 仍拿**原始 SR** 与 `0x1/0x0` 整字比较。

#### 11.27.2 v9 修正（`src/s5_camera.h/.c`）
1. 新增 `S5Cam_SrDecode(sr, &halted, &err, &frmcnt)`：`halted=bit0`、`err=(sr&0x0FF0)`、`frmcnt=((sr>>16)&0xFF)`；
   **FRMCNT 只打印，不参与 ok/FAIL**。
2. `S5CamVdma_Config` 的 SR 判据全部改掩码比较：
   - 打印原始 `SR(0x34)`（`has_expect=0`，不判 bad）；
   - 判 `SR.HALTED` 时比较 `(sr & 0x1)` 与期望；
   - 判错误时比较 `(sr & 0x0FF0)` 与 0。
   ⇒ `0x10001` 不再触发 FIRST_BAD。
3. **统一从 `0x34` 读 SR**（S2MM-only 的 VDMA 在 `0x00/0x04` 是 MM2S 块、恒 0）；CR 统一用 `0x30`。
4. 诊断版启动后采样 **0 / +20 ms / +100 ms** 三次 `0x34`，打印
   `SR/halted/err/frmcnt` 与 `frmcnt` 相对 started 的增量。

#### 11.27.3 自检（PASS）
- `SR=0x10001` ⇒ halted=1、err=0、frmcnt=1（**PASS**）；
- `SR=0x10` ⇒ err=0x10（**FAIL**）；`SR=0x0FF0` ⇒ err=0x0FF0（**FAIL**）；
- `SR=0x1` ⇒ halted=1/err=0/frmcnt=0；
- `S5_CAM_S2MM_SR==0x34`（偏移断言）+ 原 S2MM 写序/偏移/协议用例保持 PASS。

#### 11.27.4 r25 判据修正说明
- r25 `CAM: vdma SR=0x0 halted=0 err=0 frmcnt=0`：该行由 v8 的"配置后读 SR"路径产生，且受整字判据影响；
  v9 统一从 `0x34` 读并掩码解码后，正常应显示 `SR=0x10001 halted=1 err=0 frmcnt=1`（启动后 `halted=0`、`frmcnt` 递增）。

#### 11.27.5 ELF（r26；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v9（SR 掩码解码 + 0/+20/+100ms 采样） | `f7870bd745c6cc38eaed224913592a1f4edfafae3b7664a3776946db7c24ac12` | 361,496 |
| `s5_display_app_p3r_camera.elf` | 相机 v9 | `11b638745be0d9e91e36698a5a18e9e3be1f4bfb4ab9683d2334236ba2737d96` | 351,536 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v9 | `3711b49bf7db5e9f35a12488a660f6cbe7d4c4e9f5678e21015facd11fffa92e` | 351,960 |

构建记录：`build/p3r_camera_record.json`（sha256 `4be3ac10a288d105d3b1e785e786bf2f82b54d3b34e5d5577d48fc2dcd3635ef`）。

### 11.28 r26 的"启动漏 RS"与 v10 修正（r27）

#### 11.28.1 现象与定位
- r26 日志：配置完写 `CR(0x30)=0x0`，随后期望 `SR.HALTED==0`；但 **`CR=0` 是保持 halted**
  （direct 模式 `RS=0` 即停机），所以 `SR` 一直是 `0x10001`（HALTED=1 + FRMCNT=1）⇒ `first_bad=10`、`rc=-14`。
- 即：v9 把"清 RESET"误当"启动"。正确做法是 **`CR(0x30)=RUNSTOP(0x1)`**。

#### 11.28.2 v10 正确序列（AXI VDMA 直接模式）
```text
1) CR(0x30)=0x4 (RESET) → 轮询 SR(0x34)&HALTED 直到 =1
2) 写 VSIZE(0xA0)=480 / HSIZE(0xA4)=1920 / STRIDE(0xA8)=1920 / FRMPTR1(0xAC)=0x12000000
3) CR(0x30)=0x1 (RS=1 启动) → 轮询 SR(0x34)&HALTED 直到 =0
4) 打印 SR 原始值 + halted/err/frmcnt（frmcnt=(SR>>16)&0xFF）
5) 启动后 +20 ms / +100 ms 再读 0x34，打印 frmcnt 增量
6) 超时仍 HALTED 或 (SR&0x0FF0)!=0 ⇒ 展开错误位（0x10 internal / 0x20 slave / 0x40 decode /
   0x80 FSizeLess / 0x100 LSizeLess / 0x800 FSizeMore）后 FAIL
```
- 不写 `CR=0x0` 当启动；非 SG 模式 `TAIL_EN(0x2)` 非必需，先只用 `0x1`；`S5CamVdma_Start` 也统一写 RS=1（幂等）。
- 最后那行 `CAM: vdma SR=0x0 …` 的口径问题：v9 已统一从 `0x34` 读并打印原始 SR；v10 保持。

#### 11.28.3 自检（PASS）
- 写序断言：配置后必须出现 **`CR=RUNSTOP(0x1)`**（不再接受 `CR=0` 作为启动）；
- HALTED 轮询超时路径：mock 保持 HALTED ⇒ `config=-4`、`Init=-14`；
- 错误位展开：`SR=0x20` ⇒ `ERR_SLAVE(0x20)` 步骤出现且返回 -4；
- `SR=0x10001` 判 PASS（掩码）、`0x10/0x0FF0` 判 FAIL、SR 偏移 `0x34`、原协议用例保持 PASS。

#### 11.28.4 ELF（r27；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v10（RUNSTOP 启动 + 错误位展开 + 三次采样） | `7108fda17e559e909947ff1a1f17afc7e0ce5ae862825b8f3829e470cb69e7b9` | 361,948 |
| `s5_display_app_p3r_camera.elf` | 相机 v10 | `1bae3d0f15e102b0ae7a0f4392430ee11a6885c1cfbb564cfb4d2fbd8b231100` | 351,988 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v10 | `245501bfd6a3153686e80aea20904c69eab3d0659de916410fd29ca93ebee5fc` | 352,412 |

构建记录：`build/p3r_camera_record.json`（sha256 `0b951fef02b8f5e6271f3e5fb191f3b225f87f761aa57a67b3ada092b49fed7b`）。

### 11.29 只写覆盖表不出流（r03 根因）：移植阶段3 完整 OV5640 初始化表

#### 11.29.1 结论
此前相机初始化**只写了 640×480 覆盖表**（`0x3808/380A/HTS/VTS/0x3814/0x4300` 等），
而 OV5640 上电默认状态不会输出 640×480 DVP 流 ⇒ S2MM 收不到帧（`frames` 恒 1、`CAM_GPIO` SOF 计数 0）。
阶段3 是先用 `adapted/ov5640.c` 的**完整初始化表**（302 项，含时钟/PLL/模拟/AEC/ISP/格式等）后才出流。

#### 11.29.2 完整初始化表来源（照抄，不重写）
- 源文件：`D:\codex-worktrees\dbdf\tmp\s3_sensor_main_final_20261003_01\adapted\ov5640.c`
  sha256 **`df0d9808aa9a15df86b0d7f4dd1d29c387fd8b1a93aa7f0a250720950125147b`**
- 表：`struct reginfo sensor_init_data[]`（行 7..309），`SEQUENCE_END` 终止项不写入；
  提取脚本仅做 `{reg,val}` 转换，**顺序保持原样**。
- 生成文件：`src/s5_ov5640_init_table.h`（302 项，sha256 `2fa84fe7a2a9499d5785229cd2424c8d605b39dbd839330f62ce9f6c372e4783`）。

#### 11.29.3 新的相机初始化顺序（`S5Cam_Init`）
```text
复位(cmos_rst 1→0→1，500ms×3)
→ I2C 初始化(后端 gpio_sccb / ps_i2c0)
→ 读 CHIPID(0x300A/B)=0x5640
→ 写完整初始化表 302 项（0x3008 每写后延时 5ms；表尾再延 20ms）
→ 写 640×480 覆盖表（0x3035/36、0x3808/09=640、0x380A/0B=480、0x380C/0D=1892、0x380E/0F=1480、
   0x3810–0x3813=0、0x3814/15=0x31、0x3824、0x4300=0x60、AEC 上限 0x3A02/03、0x3A14/15）
→ 回读校验 DVPHO/DVPVO/HTS/VTS（≤3 次）
→ stream on：0x3008=0x02 + 20ms + 回读校验（bit1=1）
→ S2MM 配置/启动（v10 序列）
```
新增返回码：`-17` 完整表写失败、`-18` stream on 失败。

#### 11.29.4 诊断新增（r03）
- `CAM: init table entries=302`（表项数）
- `CAM: bringup rc=… elapsed_ms=…`（含完整表+覆盖表+回读+stream on 耗时）
- 关键寄存器回读：`0x3008 / 0x3035 / 0x3034 / 0x4300 / 0x460C / DVPHO / DVPVO / VTS`
- `CAM: CAM_GPIO before=… after=… +50ms=…`（0x43C70000 采集帧计数/SOF）

#### 11.29.5 自检（PASS）
- 表长度 `==302` 且 `>250`；首项 `0x3103=0x11`、次项 `0x3008`（顺序保持）；
- 覆盖表在完整表之后写（mock 写序日志：`swn > 302`，覆盖表首项为 PLL/窗口寄存器）；
- `0x3008=0x02` 为**最后一次**写（stream on 最后）；
- 覆盖后 `DVPHO=640(0x0280)`、`DVPVO=480(0x01E0)` 回读断言；
- 原 SR 掩码/VDMA 写序/CHIPID/异常子码等用例保持 PASS。

#### 11.29.6 ELF（r03；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v11（完整表+stream on+回读+GPIO/耗时） | `0ad90ec06e33ea9f9f11fdbe36f79c41a4d31e915f63902671e6e7f0bc37bea1` | 369,832 |
| `s5_display_app_p3r_camera.elf` | 相机 v11 | `a6b4d9355e4a618f68d43022b455b90f98a4f5cb0bf17649ba413f83163c1054` | 354,364 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v11 | `6a686360919046555f47459c6f800681fcbaa0b0d099d31f9e936d947378f4f4` | 358,884 |

构建记录：`build/p3r_camera_record.json`（sha256 `01eb03e4ebdd72132cba625b06dd71ce49bc24608fa21e7ffd3ec5a19565c283`）。

#### 11.29.7 下一窗判据（ecam_camera_20261031_r03）
`CAM: reg 0x3008=0x02` 回读一致；`CAM: sr=` 的 frames 递增；`CAM_GPIO` SOF 递增；
raw `0x12000000` 双采样有变化；`RESULT src=real`、`fps_dis=60`、`vdma_err=0`。

### 11.30 v12：系统/PLL/PAD 回读核对（sensor 零输出排查）

#### 11.30.1 r28 现象
- 302 项完整表写入成功（`0x3008=0x02` 回读 OK）、VDMA `config_rc=0`；
- 但 sensor **零输出**：`SOF=0`、`frmcnt` 恒 1、raw `0x12000000` 无数据。
⇒ video-bd 在 build9 加 PCLK/HREF/VSYNC 计数器定位；本版软件补"系统/PLL/接口寄存器回读对照"，
排除"表写对了但模式/时钟/PAD 未生效"。

#### 11.30.2 v12 新增只读核对（不改流程）
302 项表 + 640×480 覆盖 + stream on 之后，回读 14 个关键寄存器，并与**表内最后写入值**对照：
```text
0x300E 系统控制（bit6=1 为 MIPI，0=DVP）
0x3103 系统时钟控制
0x3017 / 0x3018 PAD 使能（DVP 数据/HSYNC/VSYNC/PCLK 输出）
0x3034 PLL 控制；0x3035 / 0x3036 / 0x3037 PLL 分频
0x3108 系统根分频
0x4300 格式；0x501F ISP 输出格式；0x440E / 0x460C 压缩/JPEG 关闭
0x3008 stream on（期望 0x02）
```
每行 `reg=… read=… expect=… ok=…`，并打印 `mismatches=N`（0=全一致）。
另打印：`final 0x3008=…`、`0x300E bit6(MIPI)=…`、`0x3017/0x3018`、`DVP_pads_en=1/0`。

#### 11.30.3 "为何可能无 PCLK"分析
1. **PAD 未使能**：若 `0x3017/0x3018` 回读为 0，DVP 数据/PCLK/HSYNC/VSYNC 不会驱动到引脚 ⇒ PL 侧无 PCLK/HREF/VSYNC；
   v12 会直接打印 `DVP_pads_en`。
2. **接口被配成 MIPI**：若 `0x300E` bit6=1，则输出走 MIPI，DVP 无信号；v12 打印该位。
3. **PLL 未生效**：`0x3034/0x3035/0x3036/0x3037/0x3108` 回读与表内值不一致（写失败或被覆盖）⇒ PCLK 不出或频率错；
   诊断行 `ok=0` 会指出具体寄存器。
4. **stream 未真正打开**：`0x3008` 必须为 `0x02`（bit1=1）；被后续写覆盖则回读不符。
5. **表内无某寄存器**：`S5Cam_LastWritten()` 返回 -2 时跳过该项（不误报），诊断行不出现该寄存器即说明表内没有。

#### 11.30.4 自检（PASS）
- 全表+覆盖+stream on 后 `S5Cam_CheckKeyRegs()` ⇒ **0 项不一致**、检查项 ≥10；
- `0x3017/0x3018` 非 0（DVP PAD 使能）；
- `S5Cam_LastWritten(0x3008)==0x02`；
- 人为把 `sensor[0x3017]=0` ⇒ 检测到 **1 项不一致**（核对逻辑有效）；
- 原 302 表顺序/覆盖表在后/VDMA 写序/SR 掩码等用例保持 PASS。

#### 11.30.5 ELF（r29；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v12（关键寄存器回读对照+MIPI/PAD/stream 判定） | `0ee15387489278fe3ef384790fb4c37f2eefe0f191eab8c3459a3d39a138709a` | 373,412 |
| `s5_display_app_p3r_camera.elf` | 相机 v12 | `9b857e97b610021af1891b901c6406789cee867a29699e7b9739b385b5486c2a` | 356,960 |
| `s5_display_app_p3r_camera_longrun.elf` | 长跑 v12 | `50ca36c4c53bc426996cb474dd2773ac45e50dc6acc38109105087dd659dfb9b` | 361,472 |

构建记录：`build/p3r_camera_record.json`（sha256 `83d174bfd25951d7c765175b848509185ab80993efd80d448ac4b4ff434d0727`）。

#### 11.30.6 期望 UART（v12 关键段）
```text
CAM: reg 0x300e read=0x… expect=0x… ok=…
CAM: reg 0x3103 read=0x… expect=0x… ok=…
CAM: reg 0x3017 read=0x… expect=0x… ok=…
CAM: reg 0x3018 read=0x… expect=0x… ok=…
CAM: reg 0x3034/0x3035/0x3036/0x3037/0x3108 …
CAM: reg 0x4300/0x501f/0x440e/0x460c …
CAM: key regs checked=14 mismatches=…
CAM: final 0x3008=0x02 (expect 0x02); 0x300E=0x… MIPI_bit6=…; 0x3017=0x… 0x3018=0x… DVP_pads_en=…
```
判读：`mismatches>0` 的 `reg` 即"写失败/被覆盖"的具体项；`DVP_pads_en=0` 或 `MIPI_bit6=1` 直接解释无 PCLK。

### 11.31 S2MM 数据面定位（v13）：`SR=0x14810` 解码 + 三套几何对照

#### 11.31.1 r29/r03 进展
- sensor 已出流：`CAM_GPIO` SOF 计数 `0xB6→0xDA→0xE3→0x6CF→0x11E5` 持续增长；
- 14 个关键寄存器 `mismatches=0`、`0x3008=0x02`、DVP PAD 全开；
- 卡在 S2MM 数据面：`SR=0x14810`。

#### 11.31.2 `SR=0x14810` 位解码（`xaxivdma_hw.h`）
| 位 | 掩码 | 名称 | 本值 |
|---|---|---|---|
| 4 | 0x10 | `ERR_INTERNAL`（Datamover internal err） | **1** |
| 11 | 0x800 | `ERR_FSZ_MORE`（FSize More Mismatch） | **1** |
| 14 | 0x4000 | 驱动头无掩码（bit12–15 为 SOF/EOL early/late 类状态位候选） | **1（未定义/待 PG020 对照）** |
| 16 | 0x10000 | `FRMCNT` LSB（帧计数=1） | 正常 |
其余位 0（HALTED/IDLE/ERR_SLAVE/DECODE/FSZ_LESS/LSZ_LESS/SG 均无）。
结论指向 **行长/数据宽度不匹配**：`ERR_INTERNAL` + `ERR_FSZ_MORE` 典型于 S2MM 收到的每行字节数大于 `HSIZE`
（或 `tlast` 行边界与 `HSIZE` 不一致）。

#### 11.31.3 v13 诊断（只读/可逆，不改进正式流程）
1. `SR(0x34)` **全位展开**：逐位打印已知错误位名字 + bit12..23 中未定义位（`reserved/undef`）+ `FRMCNT`。
2. **三套几何各试一次**（每次先 `CR.RESET=1` → 等 HALTED=1 → 配 → `CR=RUNSTOP` → 等 200 ms → 读 SR/frmcnt → 停 `CR=0`）：
   - 方案 A：`VSIZE=480, HSIZE=1920, STRIDE=1920`（24bpp 假设，当前）
   - 方案 B：`VSIZE=480, HSIZE=1280, STRIDE=1280`（16bpp 假设，stream 实为 RGB565 未展开）
   - 方案 C：`VSIZE=720, HSIZE=3840, STRIDE=3840`（sensor 仍 1280×720）
3. 每套方案后抽样 raw：`0x12000000` 首 64 B、`+1920` 32 B（十六进制）判断有无非零像素与行对齐。
4. 打印 `CAM_GPIO(0x43C70000)` 与 build9 计数器 `0x43C90000/0x43CA0000/0x43CB0000`（PCLK/HREF/VSYNC，如已上板）。

#### 11.31.4 判读
- **B 通过** ⇒ sensor 实际 RGB565 且未展开 ⇒ 需改 PL 展开或 PS 按 16bpp 收后 CPU 展开；
- **C 通过** ⇒ sensor 实际仍 1280 宽，640×480 覆盖表未真正生效；
- **三套都 `ERR_FSZ_MORE`** ⇒ `tlast` 行边界不对（PL linebuffer/subset converter）⇒ 转 `video-bd`；
- 若 B/C 均不通过且 `ERR_INTERNAL` 持续 ⇒ AXI4 侧 `C_M_AXI_S2MM_DATA_WIDTH`/`LINEBUFFER`/`MAX_BURST` 配置或 DDR 地址对齐问题。

#### 11.31.5 自检（PASS）
- `SrErrors(0x14810)==0x810`（0x10 internal + 0x800 fsize_more）；`SrErrors(0x10001)==0`（FRMCNT 不算错）；
- 三几何重配写序断言：A 写 `HSIZE=1920`、B 写 `1280`、C 写 `3840`（mock 记录写序）；
- `S5CamVdma_Reconfig` trace 步骤 ≥4；原全部用例保持 PASS。

#### 11.31.6 ELF（r30；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v13（SR 全位解码 + 三几何 + raw 抽样 + 计数器） | `05ea692751c4febf821243609add83c300880b10bd2babde6bae4c085b03c4e3` | 379,668 |
| `s5_display_app_p3r_camera.elf` | 相机 v13（含 Reconfig API，正式流程不变） | `b5c0f1a4dd55cb4311c01bbbb0cf7b2daac106f228525ddae61e6b7b066946fe` | 360,836 |

构建记录：`build/p3r_camera_record.json`（sha256 `efb3680fac08d151a6ab3af023071f1da75720afa342ebb8b38a342d2e755077`）。

#### 11.31.7 期望 UART（v13 关键段）
```text
CAM: geom A 480x640 24bpp VSIZE=480 HSIZE=1920 STRIDE=1920 -> SR=0x… frmcnt=… err=0x…
CAM:   srbit ERR_INTERNAL(0x10)=1 / srbit ERR_FSZ_MORE(0x800)=1 / srbit bit14(0x4000)=1 reserved/undef
CAM: raw 0x12000000 64B: …（判断非零像素）
CAM: raw +1920 32B: …
CAM: gpio cam=0x… pclk=0x… href=0x… vsync=0x…
CAM: geom B … / CAM: geom C …
```

### 11.32 build9 计数器定量事实与 v14 修复（4× 子采样）

#### 11.32.1 build9 + v13 实测（4 s 窗口）
| 量 | 实测值 | 说明 |
|---|---|---|
| PCLK | **40.35 MHz** | `ΔPCLK/Δt`，不是预期 84 MHz |
| HREF 高电平内 PCLK/行 | **≈1280** | ⇒ sensor 实际输出宽度 **1280**，不是 640 |
| 帧率 | **15.0 fps** | VSYNC 60 次/4 s |
| pixels_per_frame | **614,400** | = 1280×480 |
| 交叉验证 | 40.35 MHz / 22.2 kHz ≈ 1817 PCLK/行 | VTS=1480 × 15 fps ⇒ 行率 22.2 kHz（含消隐） |

#### 11.32.2 根因推导（2× → 4× 子采样）
OV5640 从 2592 宽阵列取窗口：
- `0x3814/0x3815 = 0x31`（**2×** 子采样）⇒ 2592/2 ≈ 1296 ≈ **1280**（正是实测）；
- 要 **640** 必须 **4×** 子采样：`0x3814=0x33`、`0x3815=0x33`；
- 这也直接解释 S2MM `SR=0x14810` 的 `ERR_FSZ_MORE`：PL 每行收 **1280×3=3840 B**，而 `HSIZE=1920` ⇒ 行长不匹配。

#### 11.32.3 v14 修复（`src/s5_camera.c` 覆盖表）
```c
{0x3814u, 0x33u}, {0x3815u, 0x33u},   /* 4× 子采样 ⇒ 640 输出 */
```
- `0x3810–0x3813 = 0`（偏移）保持；
- `HTS=0x380C/0D=1892`、`VTS=0x380E/0F=1480` 保持（fps≈15）；
- **PLL 不增**：理论 `HTS×VTS×fps = 1892×1480×15 = 42.00 MHz`，与实测 40.35 MHz 一致（−3.9% 属测量/消隐差），说明当前 PLL 与几何自洽；
  若要 30 fps 可把 VTS 减半（740）或 `0x3035` sysdiv 减半（PCLK≈84 MHz），v14 只打印理论值供复测，不擅自改。
- **移除 v13 的 A/B/C 几何试验**（会破坏 init/VDMA 状态），v14 只做：完整表 → 覆盖表 → stream on → 回读 → VDMA 配置/启动，稳定优先。

#### 11.32.4 新增回读与理论打印
```text
CAM: v14 subsample 0x3814=0x33 0x3815=0x33 (expect 0x33 = 4x)
CAM: v14 HTS=0x0764(1892) VTS=0x05c8(1480) offsets 0x3810-13=0
CAM: v14 PLL 0x3035=0x21 0x3036=0x69 0x3037=0x13 0x3108=0x01
CAM: v14 theory HTS*VTS*15fps = 42002400 Hz (42.00 MHz); build9 measured PCLK=40.35 MHz
```

#### 11.32.5 自检（PASS）
- 覆盖表断言：`0x3814=0x33`、`0x3815=0x33`；`DVPHO=640`、`DVPVO=480` 保持；`0x3810–0x3813=0`；
- 理论 PCLK：`TheoryPclk(1892,1480,15)=42,002,400`、`(…,30)=84,004,800`；
- 关键寄存器核对：覆盖表优先于完整表（`LastWritten` 先查覆盖表）⇒ all match=0；
- 原 302 表/VDMA 写序/SR 掩码等用例保持 PASS；v14 诊断路径不含 A/B/C。

#### 11.32.6 ELF（r32；显示/producer 冻结 ELF 未动）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v14（4× 子采样 + 回读/理论 PCLK，无 A/B/C） | `2438899971519ec7cf953489b8230081dc2999de310f2109a57a0bd0fc16398a` | 378,664 |
| `s5_display_app_p3r_camera.elf` | 相机 v14 | `384b4fff44e658435749eb10d754f1d7d4768a9ce7f12c6d6bd69c3a1b5d7ed0` | 361,060 |

构建记录：`build/p3r_camera_record.json`（sha256 `c92024012e9c07287501042ee59e47409c3019d11cfa595b6df7e10a7baa61ee`）。

#### 11.32.7 复测判据（ecam_diag_20261031_r32 + build9 计数器）
- `0x3814/0x3815` 回读 `0x33`；
- `pixels_per_frame ≈ 307,200`（1280→640 后减半），PCLK 仍在 40 MHz 附近；
- S2MM 不再 `ERR_FSZ_MORE`（`SR` 无 0x800），`HSIZE=1920` 与 640×3 一致；
- raw `0x12000000` 出现非零像素（此前为零/错位）。

### 11.33 路线 B 定稿：1280×480 采集 + 显示侧水平 2× 抽样（4× 子采样停用）

#### 11.33.1 决策依据
- r31 实测已验证 **2× 子采样出流**：1280×480@15 fps、PCLK≈40 MHz、614,400 px/帧（`0x3814/0x3815=0x31`、`DVPHO=1280`）；
- r32 改 4× 子采样（`0x33`）后 **sensor 停流**（ΔVSYNC=0、ΔHREF=0、PCLK 降到 21 MHz），该模组此组合不可用；
- 路线 B 不改 PL、不改 PLL：PL 按 1280×480 采集，显示侧水平 2× 抽样到 640×480，最快可通。

#### 11.33.2 传感器（覆盖表/时序）
```text
0x3814 = 0x31, 0x3815 = 0x31        # 2× 子采样（恢复 r31 出流配置）
0x3808/09 = 0x0500 = 1280           # DVPHO
0x380A/0B = 0x01E0 = 480            # DVPVO
0x380C/0D = 1892 (HTS), 0x380E/0F = 1480 (VTS)
0x3035=0x21 / 0x3036=0x69 / 0x3037=0x13 / 0x3108=0x01   # PLL 不动
```
写序保持 v15：完整表 302 项 → 覆盖表 → **显式 stream off（0x3008=0x42，≥10 ms）** → 时序覆盖重写 → **stream on（0x3008=0x02，≥20 ms）** → 回读 → VDMA。

#### 11.33.3 S2MM / raw
```text
VSIZE(0xA0)=480、HSIZE(0xA4)=3840、STRIDE(0xA8)=3840、FRMPTR1(0xAC)=0x12000000
帧长 = 1280×480×3 = 1,843,200 B
_Static_assert：帧长 ∈ {1,843,200, 921,600}；HSIZE 8 字节对齐
```
内存：`[0x12000000, 0x12C00000)` 共 12 MiB 预留区，1.84 MB 足够（远小于显示 FB 0x20000000 起）。

#### 11.33.4 显示侧最小改动
- `s5_result_abi.h`：raw 几何改为 **1280×480 stride 3840**，新增 `S5_RAW_OUT_W/H=640/480`、`S5_RAW_DECIM_X=2`；
  编译开关 `S5_CAM_CAPTURE_1280`（默认 1；置 0 回到 640×480 直采）。
- `s5_real_source.c`：新增 `S5Real_BgrToCanvasDecim(raw, canvas, out_w, out_h, decim_x, src_stride)`，
  `dst[x] = src_row[2*x]`（水平 2× 抽样、垂直直通），BGR888→0x00RRGGBB。
- `s5_display_app.c`：两处真实源拷贝改调该函数（640×480 逻辑帧与 FB 1280×720/960×720 视频区不变，ABI 语义不变）。
- **不修改 producer/结果侧语义**，不改显示三件套。

#### 11.33.5 诊断 v15b 新增
```text
CAM: init OK capture=1280x480 stride=3840 frame=1843200 (route B …)
CAM: flow 500ms dVSYNC=… dPCLK=… dHREF=… pixels_per_frame=… pclk_est=…MHz
CAM: flow raw_gpio before=0x… after=0x… (delta=0x…)
CAM: v14 subsample 0x3814=0x31 0x3815=0x31 (expect 0x31 = 2x route B)
CAM: vdma started SR=0x… halted=0 err=0x0 frmcnt=…
```
判读：`pixels_per_frame≈614,400`（1280×480）为正常；`≈307,200` 才说明又变成 640 输出。
S2MM 侧要求：`SR` 无 0x800（FSIZE_MORE）、`frmcnt` 递增。

#### 11.33.6 自检（PASS）
- `S5_CAM_STRIDE==3840`、`S5_CAM_FRAME_BYTES==1,843,200`、`S5_RAW_FRAME_W==1280`、`S5_RAW_OUT_W==640`、`S5_RAW_DECIM_X==2`；
- 抽样下标断言：`dst[0]=src x=0`、`dst[1]=src x=2`、`dst[640]` 使用 stride 3840（行 1）；
- VDMA 写值断言：`HSIZE=3840`、`STRIDE=3840`、`VSIZE=480`、`FRMPTR1=0x12000000`；
- 覆盖表断言：`0x3814/0x3815=0x31`、`DVPHO=1280`、`DVPVO=480`、`0x3810–0x3813=0`；
- 关键寄存器回读 all match；stream off/on 写序与 SR 掩码用例保持 PASS。

#### 11.33.7 ELF（r33；显示三件套冻结 ELF 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v15b（路线 B + 计数器 Δ + SR） | `8ae8a0aa98ed3f3a985eb2c0a24306c5e4cc458a1a1b3829eb0fda3c1129aad2` | 385,500 |
| `s5_display_app_p3r_camera.elf` | 相机 v15b（路线 B，正式） | `4da27958250dd48adc25a7236789b02de5af16f4472466c7ce053017e989077a` | 367,708 |

构建记录：`build/p3r_camera_record.json`（sha256 `63b1b4476c638e748527efbce114489c221138109d563a201d3080bc60b00fc5`）。

#### 11.33.8 B 计划评估（若将来不能 4× 直采，本路线即正式方案）
1. **内存**：raw 需 1.84 MB，`[0x12000000,0x12C00000)` 12 MiB 预留区内，充足；
2. **CPU 成本**：每帧 614,400 像素读取 + 307,200 写（水平 2× 抽样），15 fps 下约 9.2M src 样本/s、
   4.6M 写/s；Cortex-A9 @667 MHz 单核按约 4–6 周期/像素估算 ≈ 每帧 2.5–4 ms，占 15 fps 帧周期（66 ms）的 <6%，
   可接受（后续可改 NEON 进一步降低）；
3. **显示侧改动**：仅 raw 读取 stride（3840）与水平抽样下标（`src_x=2*dst_x`），
   FB 1280×720/960×720 视频区与 640×480 逻辑帧 ABI 均不变，producer/结果侧零改动。

### 11.34 路线 B2 定稿：1280×960 采集 + 软件 2×2 下采样（sensor 时序不再改动）

#### 11.34.1 r33 实测结论
- sensor 在 `0x3814=0x31 / 0x3815=0x31`（2× 子采样）下稳定输出 **1280×960 @15.1 fps**，已实测出流；
- 因此路线 B2：**不再改 0x3814/0x3815、不再试 4×、不动 PLL**；采集改 1280×960，显示侧 2×2 下采样到 640×480；
- `stream off(0x3008=0x42) → 时序覆盖重写 → stream on(0x3008=0x02)` 包裹保留（无害，保证确定性）。

#### 11.34.2 S2MM / raw
```text
VSIZE(0xA0)  = 960
HSIZE(0xA4)  = 3840
STRIDE(0xA8) = 3840
FRMPTR1(0xAC)= 0x12000000
帧长 = 1280×960×3 = 3,686,400 B（12 MiB 预留区 [0x12000000,0x12C00000) 内，充足）
_Static_assert：帧长 ∈ {3,686,400, 921,600}；HSIZE 8 字节对齐
```

#### 11.34.3 显示侧 2×2 下采样
- `s5_result_abi.h`：`S5_RAW_FRAME_W=1280`、`S5_RAW_FRAME_H=960`、`S5_RAW_FRAME_STRIDE=3840`、
  `S5_RAW_OUT_W/H=640/480`、`S5_RAW_DECIM_X=2`、`S5_RAW_DECIM_Y=2`；
- `S5Real_BgrToCanvasDecim(raw, canvas, out_w, out_h, decim_x, decim_y, src_stride)`：
  `dst[x,y] = src[2x, 2y]`（水平+垂直各 2× 抽样，BGR888→0x00RRGGBB）；
- FB 1280×720/960×720 视频区与 640×480 逻辑帧 ABI 不变，producer/结果侧零改动。

#### 11.34.4 flow 计算修正（app bug）
r33 观测 `dVSYNC=524296、pixels_per_frame=17` 属计算错误。v16 改为：
1. 两次数值快照均来自 `0x43C70000 / 0x43C90000 / 0x43C90008 / 0x43CA0000`；
2. `d = snap2 - snap1` 用 **32 位无符号差**（允许回绕）；
3. `Δt` 用 `S5Ticks_Now()` 实测并打印 `dt=…ms`；
4. `pixels_per_frame = dHREF / dVSYNC`（仅 `dVSYNC>0`），`pclk = dPCLK / Δt`；
5. 打印原始快照 `cam/pclk/href/vsync` 便于复核。

#### 11.34.5 自检（PASS）
- `S5_CAM_FRAME_BYTES == 3,686,400`、`S5_CAM_STRIDE == 3840`、`S5_RAW_FRAME_W/H == 1280/960`；
- 2×2 抽样：`dst(0,0)←src(0,0)`、`dst(1,0)←src(2,0)`、`dst(0,1)←src(0,2)`（行 1 用 stride 3840 且 y+2）；
- VDMA 写值：`VSIZE=960`、`HSIZE=3840`、`STRIDE=3840`、`FRMPTR1=0x12000000`；
- 覆盖表 `0x3814/0x3815=0x31`、`DVPHO=1280`、`DVPVO=480`、`0x3810–0x3813=0`；关键寄存器 all match；
- stream off/on 写序、SR 掩码、异常子码等原用例保持 PASS。

#### 11.34.6 2×2 下采样成本评估
- 源读：每帧 640×480 输出像素 = 307,200；按 `src[2x,2y]` 逐点读，读 3 B/点 ⇒ 921,600 B/帧源流量；
- 15 fps ⇒ 约 4.6M 输出像素/s、13.8 MB/s 源读取；
- Cortex-A9 @667 MHz 每输出像素约 2 load + 1 写（未优化）≈ 6–8 周期 ⇒ 每帧约 2–2.5 ms，占 66 ms 帧周期 <4%；
- 后续可改 NEON `vld3` 或整行拷贝+抽样进一步降低；当前无需。

#### 11.34.7 ELF（r34；显示三件套/producer 冻结 ELF 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v16（B2 + flow 修正 + SR） | `38a746c93a48277ed5a70eae4241c96d43cfc4b029785cfe9c8a679d507f6392` | 386,384 |
| `s5_display_app_p3r_camera.elf` | 相机 v16（B2，正式） | `8a375fa95cc89d309406dda546b13b8889e826640fd790a185ccb6d6e17fd256` | 367,772 |

构建记录：`build/p3r_camera_record.json`（sha256 `50a6acb3d7b53c3b8f1bac7e4716d962904c8760f903a647798755dbe8e19ae3`）。

#### 11.34.8 下一窗判据
`CAM: init OK capture=1280x960 stride=3840 frame=3686400`；`dVSYNC>0`、`pixels_per_frame≈1,228,800`；
`SR` 无 `0x800`（FSIZE_MORE）、`frmcnt` 在 +20/+100 ms 递增；raw 非零且两次采样有变化。

### 11.35 v17：四组几何自动探测（r35，fail-safe）

#### 11.35.1 r34 实测推导
- `HREF_PIX / frame = 1,212,879`；OV5640 经 **8-bit DVP 输出 RGB565 时每像素 2 个 PCLK**
  ⇒ 实际像素/帧 ≈ 1,212,879 / 2 ≈ **606,440 ≈ 1280×480**
  ⇒ sensor 很可能是 **1280×480 RGB565**（每行 2560 B），不是 1280×960、也不是 3840 B/行。
- 两种可能：
  - `axis_subset_converter` 16→24bpp 在 S2MM 路径生效 ⇒ 每行 **3840 B**、480 行；
  - 未生效（裸 16bpp） ⇒ 每行 **2560 B**、480 行。
- 因此 v17 直接实测四组几何，不再猜。

#### 11.35.2 四组探测表
| # | VSIZE(0xA0) | HSIZE(0xA4) | STRIDE(0xA8) |
|---|---|---|---|
| 1 | 480 | 3840 | 3840 |
| 2 | 480 | 2560 | 2560 |
| 3 | 960 | 3840 | 3840 |
| 4 | 960 | 2560 | 2560 |

每组严格步骤：
```text
CR(0x30)=0x0（停） → 等 SR.HALTED==1（20 ms 超时）
→ SR(0x34) 写 0xFFFFFFFF（W1C）并读回确认残留
→ 配 VSIZE/HSIZE/STRIDE/FRMPTR1
→ CR(0x30)=0x1 → 等 SR.HALTED==0（20 ms 超时）
→ 等 250 ms，读 SR/FRMCNT
→ raw 0x12000000 读 8 个 u32（volatile，对齐）
→ CR(0x30)=0x0 停 → 下一组
```
安全措施：固定地址 volatile 读、VDMA 运行中不改寄存器、每组 `geom N start` / `geom N done` 定位、任一步超时返回 -4 但 SR 始终有效、不依赖未初始化指针；SR 逐位解码（0x1/0x2/0x10/0x20/0x40/0x80/0x100/0x200/0x400/0x800/0x1000 与 bit12–23 保留位）。

#### 11.35.3 判读
- 某组 `err=0` 且 `frmcnt` 递增 ⇒ 该几何即实际格式：
  - **3840/480** ⇒ 24bpp 展开生效（1280×480 直采）；
  - **2560/480** ⇒ 16bpp 直收（软件 565→888，每帧 1,228,800 B）；
  - **3840/960 或 2560/960** ⇒ 960 行（前几窗配 960 仍报错，可能性低）。
- **四组都 `0x14810`** ⇒ 不是几何/宽度，而是 `tlast/tuser/linebuffer`，转 `video-bd` 查 PL 侧
  `axis_subset_converter` 与 `alinx_ov5640` 的 tlast 生成。

#### 11.35.4 自检（PASS）
- probe 写序断言：`CR=0` 先 → `SR` W1C `0xFFFFFFFF` → 几何 `480/2560/2560` → `CR=RUNSTOP` → 末尾 `CR=0`；
- probe trace 步骤 ≥5；`S5Cam_SrErrors(0x14810)==0x810`；
- 模拟 halted-sticky 超时路径返回 -14；原全部用例（CHIPID/覆盖表/VDMA/SR/stream）保持 PASS。

#### 11.35.5 ELF（r35；sensor 时序未动、显示三件套/producer 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v17（四组几何探测 + SR 解码 + raw 抽样） | `8d70bb61aa66bd57ace79cac3b5f2a3e877975a24cb1115b4a0c7c2f9a900b2c` | 396,912 |
| `s5_display_app_p3r_camera.elf` | 相机 v17（B2 正式流程不变） | `2ab119729c022d1f720f5637182da72067f0d777b21bb3cd4673285e5e26b918` | 372,696 |

构建记录：`build/p3r_camera_record.json`（sha256 `0f816356955c65017ff8b09e51d868fdb8068f16cb7cd382277042e95ab1da42`）。

#### 11.35.6 期望 UART
```text
CAM: geom 1 start v=480 h=3840 s=3840
CAM: geom 1 v=480 h=3840 s=3840 SR=0x… halted=… err=0x… frmcnt=…
CAM:   geom 1 srbit ERR_FSZ_MORE(0x800)=1 / bit14(0x4000)=1 reserved …
CAM: geom 1 raw: xxxxxxxx …
CAM: geom 1 done
…（geom 2/3/4 同）
```

### 11.36 v18：厂商 IP 上电 warmup（300M PCLK）后配/启 VDMA

#### 11.36.1 决定性事实（video-bd 从厂商 RTL 读得）
`alinx_ov5640` 内部有 **300,000,000 个 PCLK 的上电等待**：
- `reset_cnt`：200,000,000 PCLK 释放内部复位；
- `fifo_ready_cnt`：再 100,000,000 PCLK 置 FIFO ready；
- 84 MHz 下合计约 **3.6 s**；在此期间 `wr_en` 恒 0，FIFO 不写数。

⇒ 此前所有窗口都是 **stream on 后立刻配/看 VDMA**，正好落在未就绪区间，必然无数据（与 r29–r34 现象一致）。

#### 11.36.2 v18 修改（`src/s5_camera.h/.c`）
```c
#ifndef S5_CAM_IP_WARMUP_MS
#define S5_CAM_IP_WARMUP_MS 6500u      /* 默认 6500 ms，可 -D 覆盖 */
#endif
```
`S5Cam_Init` 顺序改为：
```text
复位 → I2C → CHIPID → 302 表 → 640x480(2x) 覆盖表 → 回读校验
→ stream off(0x42) → 时序覆盖重写 → stream on(0x02)
→ S5Cam_StreamOnMs=now_ms()；delay(S5_CAM_IP_WARMUP_MS)；S5Cam_WarmupMs=now_ms()-S5Cam_StreamOnMs
→ S2MM 配置/启动
```
- `S5CamBus` 增加可选 `now_ms` 回调（app 用 `S5Ticks` 提供；mock 用累加 ms）；
- 导出 `S5Cam_StreamOnMs` / `S5Cam_WarmupMs` 供诊断打印与「t=… ms since stream-on」。

#### 11.36.3 诊断 v18d
- 打印 `CAM: ip warmup wait=6500 ms elapsed=… ms (vendor IP 300M PCLK power-up)`（elapsed 实测）；
- 四组几何探测全部移到 warmup **之后**，每组打印 `geom N start … (t=… ms since stream-on)`；
- 6.5 s 后仍无数据时按既有逻辑打印 SR/计数器/raw。

#### 11.36.4 自检（PASS）
- mock 记录 `stream_on_ms`（写 0x3008=0x02 时刻）与 `vdma_first_ms`（首次写 VSIZE 时刻）：
  `f.vdma_first_ms >= f.stream_on_ms + 6500`；
- `S5Cam_WarmupMs >= 6500`；
- halted-sticky 超时仍返回 -14；原全部用例（CHIPID/覆盖表/VDMA/SR/2x2 抽样）保持 PASS。

#### 11.36.5 ELF（r36；sensor 时序未动、显示三件套/producer 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v18d（warmup + 四组几何 + SR/raw） | `a58ac0f6bfbb50cae33e787184be479aa518a59ce48014ed0bec15b2a2e17abe` | 397,924 |
| `s5_display_app_p3r_camera.elf` | 相机 v18（正式，含 warmup） | `21a0651e24068a4b0cdf2bae4e63930770ccdbfb47ac8682c79bcd3d9216174d` | 373,532 |

构建记录：`build/p3r_camera_record.json`（sha256 `4e96b6a8fcf65e294e4b5358a6ad12308223fa14e18c30828dd13f015faf8203`）。

#### 11.36.6 组合说明
最终相机窗需 **build10b（修 `s_axis_s2mm_tuser` 未连接 + 加 tlast/tuser/有效拍/反压/aresetn 计数器）+ v18/v18d**；
warmup 解决「FIFO 未就绪」，build10b 解决 tuser/tlast 语义，两者缺一不可。

### 11.37 v19：warmup 12 s + settle 2 s（r37 最后一块拼图）

#### 11.37.1 r36 新事实
- build10b 计数器：**`TL_HDR`(tlast/tuser) / `TAP_BP`(有效拍/反压) / `GPIO_CAM` 三个全冻结**，而 `PCLK/HREF/VSYNC` 在涨
  ⇒ `alinx_ov5640` 的 **AXIS 输出侧完全没有 beat（tvalid 恒 0）**，IP 仍在 `fifo_ready` 门控期内；
- IP 内部等 **200M + 100M = 300M PCLK**；实测 PCLK 有两种读数（40.35/84 MHz，计数器可能计双边沿）：
  - 84 MHz ⇒ 3.57 s（6.5 s 够）；
  - **42 MHz ⇒ 7.14 s（6.5 s 不够！）**；
- r36 四组探测在 stream-on 后 **7.4–8.3 s** 开始、每组只等 250 ms ⇒ 若 PCLK=42 MHz，恰好落在 ready 边沿附近，可能"刚好差一点"。

#### 11.37.2 v19 改动（最小）
```c
#define S5_CAM_IP_WARMUP_MS 12000u   /* 12 s，覆盖 42/84 MHz 两种假设；-D 可覆盖 */
#define S5_CAM_IP_SETTLE_MS 2000u    /* 诊断：warmup 后、几何探测前再等 2 s */
```
- `S5Cam_Init`：stream on → **delay 12000 ms** → 配/启 VDMA；
- 诊断：warmup 后再显式 `delay 2000 ms` 才开始四组几何探测，每组打印 `t=… ms since stream-on`；
- 打印 `CAM: ip warmup wait=12000 ms elapsed=… ms`；
- 新增 warmup 前后 VDMA 寄存器对比：`VER(0x43C6002C) / CR(0x43C60030) / SR(0x43C60034)`（冷/热各一次）。

#### 11.37.3 自检（PASS）
- `S5_CAM_IP_WARMUP_MS==12000`、`S5_CAM_IP_SETTLE_MS==2000`；
- mock：`vdma_first_ms >= stream_on_ms + 12000`、`S5Cam_WarmupMs >= 12000`；
- halted-sticky 超时仍 -14；原全部用例保持 PASS。

#### 11.37.4 ELF（r37；sensor 时序未动、显示三件套/producer 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v19d（warmup 12s + settle 2s + VDMA 冷/热对比 + 四组几何） | `ba7e56c0bf5fd1d96369f669a2eafbad2ede59d97933c4d39f071c292672466c` | 398,732 |
| `s5_display_app_p3r_camera.elf` | 相机 v19（正式，warmup 12s） | `0007cf4fc89510153d4c58af5f83a04208b16f95d9ab773995caa29154fae32d` | 373,572 |

构建记录：`build/p3r_camera_record.json`（sha256 `e15bac60cdb5e308975188b0f7dbede60ff1fde9d87a6de09801bb971b23f7f9`）。

#### 11.37.5 r37 判据
- `TL_HDR` 的 tuser/tlast 开始增长（≈15/s）、`TAP_BP` 有效拍增长；
- 四组中某组 `err=0`、`frmcnt` 递增、raw 非零；
- 若 12 s 后仍全冻结 ⇒ 不在 warmup，转 `video-bd` 查 converter/IP 的 `aclk/aresetn` 与 `tvalid` 通路。

### 11.38 v20：观察期间必须保持 VDMA 运行（tvalid 被 tready 门控）

#### 11.38.1 r38 的"零 beat"是探测方式造成的假象
- 两次运行快照里 `CAM_CR=0x10000`（**RS=0**）⇒ 我们自己的探测结束时把 VDMA 停了；
- 厂商 IP 的 AXIS `tvalid` 被 `tready` 门控（`tvalid = ~empty & tready`）⇒ **VDMA 一停，整条链零拍**，
  `TL_HDR/TAP_BP/GPIO_CAM` 全冻结并不代表 IP 未就绪。
- 结论：**任何 AXIS 侧观察都必须让 S2MM VDMA 持续运行（CR 保持 RUNSTOP=0x1）**，否则读到的都是 0。

#### 11.38.2 v20 改动
1. 新增 `S5CamVdma_StartGeometry()`：`CR.RESET=1 → 等 HALTED=1 → 配 VSIZE/HSIZE/STRIDE/FRMPTR1 →
   CR=RUNSTOP → 等 HALTED=0`，**不写 CR=0**（保持运行）。
2. 诊断 v20d 流程：warmup **12 s** + settle **2 s** → 只配一组几何
   `VSIZE=960, HSIZE=STRIDE=3840, FRMPTR1=0x12000000` → **VDMA 持续运行 8 s**：
   - 每 500 ms 打印一行（共 16 行）：`SR(0x43C60034)`、`frmcnt`、`0x43CB0000`(tlast/tuser)、
     `0x43CC0000`(有效拍/反压)、`0x43CE0000`(IP tvalid/tlast/tuser 高拍)、`0x43CF0000`(tready 高拍)、
     `t=… ms since stream-on`；
   - 结束打印 `raw 0x12000000` 首 32 B + `+3840` 首 16 B；
   - 汇总行 `CAM: obs beats=… tlast=… tuser=… ip_tvalid=… ip_tready=… frmcnt=… sr=0x…`；
   - **观察期不 stop**；若 8 s 后仍无 beat，汇总行即最终判据。
3. 相机 v20 与 v19 相同（warmup 12 s + 1280×960/3840 采集 + 2×2 下采样），VDMA 启动后持续运行到结束。

#### 11.38.3 自检（PASS）
- `StartGeometry` 写序：`RESET` → 几何 `960/3840` → `RUNSTOP`；
- **日志最后一次 CR 写必须是 `RUNSTOP`，不得出现尾部 `CR=0`**；
- 观察循环只读寄存器/计数器，不写 CR；raw 抽样固定地址 `0x12000000`、`+3840`（volatile u32，偏移对齐）；
- warmup/settle 宏断言、原全部用例（CHIPID/覆盖表/VDMA/SR/2×2 抽样）保持 PASS。

#### 11.38.4 ELF（r39；sensor 时序未动、显示三件套/producer 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v20d（12s warmup + 8s 持续运行观察 + IP 侧计数器） | `b448a6d3b0748f833dce404e7cc9114868dc2d7c1162ed2664ec815a83057649` | 402,412 |
| `s5_display_app_p3r_camera.elf` | 相机 v20（正式，VDMA 持续运行） | `d2f615b001b8f59befd070ea4d87b903372947b0c437a581342fa34291557d4d` | 376,040 |

构建记录：`build/p3r_camera_record.json`（sha256 `146f99180fbf74a5493154f4ec7d20eec8e7100a0fa5d471f54359cc68512511`）。

#### 11.38.5 r39 判据（build11b + v20d，`--counter-snaps "14,20"`）
- 观察期 16 行中 `SR` 应保持 `halted=0`；
- `ip_tvalid`/`ip_tready`/`beats`/`tlast` 增量 >0、`frmcnt` 递增、raw 非零 ⇒ 采集通；
- 若 8 s 内全为 0 且 `SR` 无错误位 ⇒ 转 `video-bd` 查 IP 侧 `aclk/aresetn` 与 `tvalid` 通路（此时 VDMA 已确认在跑）。

### 11.39 v21：`0x4740` 极性扫描（HREF 极性假设）与计数器映射修正

#### 11.39.1 新假设
IP 内部可能把 `cmos_href` 的"有效/消隐"极性理解反了 ⇒ 只有极少拍被采（tvalid≈5/s、tlast/tuser=0）。
OV5640 `0x4740` 为 **Polarity Control**（bit5=0x20 为基线，bit[1:0] 为 HREF/VSYNC 极性组合；具体位名以手册
"0x4740 polarity control" 为准，本实验按 lead 给出的 4 个组合实测，报告保留位定义待手册核对）：
`0x20`（基线）、`0x22`、`0x21`、`0x23`。

#### 11.39.2 计数器映射（按 board 解析，v21 全部改正；v20d 的 ip_tv/ip_tr 地址是错的）
| 地址 | 名称 |
|---|---|
| `0x43C90000` | `cam_pclk_cnt` |
| `0x43C90008` | `cam_href_cnt` |
| `0x43CA0000` | `cam_vsync_cnt` |
| `0x43CB0000` / `+0x08` | `s2mm_tlast` / `s2mm_tuser` |
| `0x43CC0000` / `+0x08` | `s2mm_beat` / `s2mm_stall` |
| `0x43CD0000` | `cam_aresetn_ip` |
| `0x43CE0000` / `+0x08` | **`ip_tvalid` / `ip_tlast`** |
| `0x43CF0000` / `+0x08` | **`ip_tuser` / `ip_tready`** |

#### 11.39.3 实验设计（v21d）
1. 完整 302 表 + 覆盖表 + stream off（0x3008=0x42）；
2. 依次 4 个 `0x4740` 值，每个：写极性 → stream on（0x02）→ 等 1.5 s → 快照 12 个计数器 →
   再等 500 ms → 快照 → 打印各增量：
   `CAM: pol 0x4740=0x22 dIP_TVALID=… dIP_TLAST=… dIP_TUSER=… dIP_TREADY=… dPCLK=… dHREF=… dVSYNC=… dBEAT=… dTL=… dTU=…`
   → stream off；
3. 取 `dIP_TVALID` 最大的极性，再 stream on → **warmup 12 s** → 配 `VSIZE=960 / HSIZE=STRIDE=3840` →
   **VDMA 持续运行 8 s**（每 500 ms 一行，16 行，含全部计数器）→ raw 32 B + `+3840` 16 B → 汇总行。

#### 11.39.4 自检（PASS）
- 极性写序：`stream off(0x42)` → `0x4740=pol` → `stream on(0x02)`（mock 写序日志断言）；
- 计数器地址常量断言（上表 12 项）；
- `StartGeometry` 保持运行（末尾 CR=RUNSTOP，不写 0）；
- warmup/settle 宏断言、原全部用例保持 PASS。

#### 11.39.5 ELF（r40；sensor 时序寄存器未动、显示三件套/producer 未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v21d（0x4740 四极性扫描 + 最佳极性 8s 观察） | `9ec625331fbbd199bc073d6497eb45a46a4be45e2519e5629398ddbbe82a49a5` | 408,628 |
| `s5_display_app_p3r_camera.elf` | 相机 v21（正式流程不变，含极性 API） | `aa5110f7aee98b9bc1841bc6424af37b1e8f3f30f9d7015862e077ef3b6bf5c6` | 377,092 |

构建记录：`build/p3r_camera_record.json`（sha256 `2404b27e813e0a8e49f3b60e4b55798475b88316c7d9dd9c0e239a7e6ab3bf8b`）。

#### 11.39.6 判据（r40）
- 某极性下 `dIP_TVALID` 从 ~5/s 跃到 **千/s 以上**（理想 18.4M/s）⇒ 就是 HREF 极性，立即用该值继续；
- 四个极性都只有 ~5 拍/s ⇒ 极性排除，转 build11d（IP 内部探针）；
- 最佳极性下 8 s 观察若 `frmcnt` 递增且 raw 非零 ⇒ 采集通，进相机窗。

### 11.40 v22：阶段3 等价配置（今天实测可用）搬进 P3r

#### 11.40.1 阶段3 对照实验结论
- 阶段3 冻结位流 + `v10_read` ELF **今天仍能出真实彩色像素**：
  `FB=0x00114C00` head/mid 全非零、5 次采样 hash 每次变化、`nz=16384`；
- 其 `SR=0x15810` 里**同样含 `FSZ_MORE`** 却照样出图 ⇒ `FSZ_MORE` 不阻断出图；
- ⇒ 硬件/模组/IP 全正常，**责任在 P3r 集成配置**。

#### 11.40.2 阶段3 实测参数（UART 原文）
```text
OUT_W=0x0500(1280) OUT_H=0x02D0(720) VTS=0x02E4(740)
0x3035=0x21 0x3034=0x1A 0x4300=0x60 0x501F=0x01
VDMA: VSIZE=0x2D0(720) HSIZE=0xF00(3840) STRIDE=0xF00 ADDR=0x00110C00
S2MM_CR=0x00018003（RS=1 | TAIL_EN=1 | bit16）
```
我们此前用 B2：`DVPVO=480 / VTS=1480 / VSIZE=960`，且 **CR 只写 0x1（无 TAIL_EN）**。

#### 11.40.3 v22 参数（= 阶段3 等价，纯软件）
1. sensor 覆盖表改为阶段3 值：`0x3808/09=0x0500(1280)`、`0x380A/0B=0x02D0(720)`、
   `0x380E/0F=0x02E4(740)`、`0x3035=0x21`、`0x3034=0x1A`、`0x4300=0x60`、`0x501F=0x01`；
   保留 302 完整表 + stream off/on 包裹 + warmup 12 s（等待无害）。
2. VDMA：`VSIZE=720`、`HSIZE=3840`、`STRIDE=3840`、`FRMPTR1=0x12000000`（P3r DDR 1 GiB 空间）。
3. S2MM_CR 启动写 **`RS=1|TAIL_EN=1`（0x3）**（对应阶段3 的 0x03 低位）；启动前照旧 RESET→等 HALTED。
4. 显示侧 raw 几何改回 **1280×720 / stride 3840 / 1×1 直通**（与阶段3 一致，便于直接对比）。
5. 保留“VDMA 启动后持续运行 8 s + 16 行 obs + raw 抽样”。

#### 11.40.4 自检（PASS）
- 覆盖表值断言：`DVPHO=1280`、`DVPVO=720`、`VTS=740`、`0x3034=0x1A`、`0x501F=0x01`；
- `CR=0x3` 写序（Config/StartGeometry/probe 均 `RUNSTOP|TAIL_EN`）；
- raw 几何：`1280×720×3 = 2,764,800`、stride 3840、1×1 直通（抽样下标 `dst[0]←src[0]`、`dst[1]←src[1]`、行 1 用 stride 3840）；
- warmup 12 s 保留、原全部用例 PASS。

#### 11.40.5 ELF（r41；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v22d（阶段3 等价配置 + 16 行 obs + raw） | `74ec64acffd346ad0617ad1d12132116222d0e135dbedf14cfd1d33739998e09` | 408,652 |
| `s5_display_app_p3r_camera.elf` | 相机 v22（阶段3 等价，正式） | `366e1c111178995e8fcb1b7003a12cfea1c1bcab6171004103847e9aa44c5c5c` | 377,108 |

构建记录：`build/p3r_camera_record.json`（sha256 `b749e2f11b638ee9f957494ccff06a5d56cde5a9ba24b158b3ec05ec6da16a18`）。

#### 11.40.6 判据（r41，build10b2，FSYNC=2）
- 若 v22 出帧（obs 中 beat/tlast 增长、`frmcnt` 递增、raw 非零）⇒ B2 的几何/帧率/CR 位组合有问题，相机今晚即可通；
- 若 v22 仍不出帧 ⇒ P3r 的 PL 侧与阶段3 仍有差异，转 build11d 探针继续。

### 11.41 v23：r41 突破后修 obs 崩溃 + DDR 写入排查（含 0x00114C00 地址冲突结论）

#### 11.41.1 r41 突破
build10b2（FSYNC=2）+ v22（1280×720/VTS=740/CR=0x3）下 **S2MM 真的收到数据**：
- `TAP_VALID` 快照差 ≈228M / 8.27 s ≈ **27.6M beat/s**（正好 1280×720×30fps 的 27.6M beat/s）；
- `TL_TLAST` ≈ **24.6k/s**；`SR=0x14810` 与阶段3 的 `0x15810` **同型**（含 FSZ_MORE 但仍出图）；
- 停核读：`CR=0x10003 SR=0x14810 VSIZE=0x2D0 HSIZE=STRIDE=0xF00 FRMPTR=0x12000000`；
- 但 `0x12000000` 处 head/mid/last 全 0、`nonzero=1/1/2`；且 v22d 在 flow/obs 段 **ABT（PC=0x101BEC）**。

#### 11.41.2 地址冲突结论（重要，与 lead 建议的 0x00114C00 冲突）
本 ELF 的 LOAD 段（`readelf -l`）：
```text
LOAD 0x001000 0x00100000 0x00100000 0x0913c 0x0913c RWE   ← .text
LOAD 0x00b000 0x0010c000 0x0010c000 0x04010 0x242d80 RW    ← .data/.bss/heap/stack
```
⇒ **`0x00114C00` 落在本应用的 RW 段（0x0010C000 起，memsz 0x242D80）内**。
若把它做 VDMA 目标，S2MM 会覆盖程序数据/堆栈，必然崩（与 r41 的 ABT 风险方向一致）。
阶段3 的 `0x00114C00` 只在其自身内存布局下有效，**不能直接搬到 P3r**。

v23 决定：**VDMA 目标保持 `0x12000000`**，并在诊断里：
- 打印 `image_end`（用链接符号 `__data_end`）与 `0x00114C00 inside_image=?`；
- 允许时再评估低地址方案（需改应用加载地址，属重排，不在本窗做）。

#### 11.41.3 v23 obs 段加固（修 ABT）
1. 进入循环前后各打印一行：`CAM: obs enter t=… image_end=…` / `CAM: obs exit`；
2. 计数器全部用固定 `volatile u32*`（`0x43C60030/0x43C60034`，其余 `Xil_In32` 固定地址），不做指针运算；
3. flow 行改整数运算（去掉 float 除零路径），除法前判 `dt_ms==0`；
4. 读 raw 之前 `Xil_DCacheInvalidateRange(0x12000000, 4096)`（PL 经 HP 写 DDR，CPU 直读可能是陈旧缓存）；
5. 预写 `0xDEADBEEF` 8 字到 `0x12000000`，观察后读回并打印 `pattern overwritten_words`（0=未被 PL 写，>0=DDR 写入通路有效）；
6. 打印 VDMA 关键寄存器：`0x08`、MM2S `0x50/54/58/5C`、S2MM `0xA0/A4/A8/AC`、`SR`。

#### 11.41.4 自检（PASS）
- `S5_CAM_VDMA_FRMPTR==0x12000000` 且 **显式断言拒绝 0x00114C00**（与 ELF RW 段冲突）；
- obs enter/exit 存在；warmup/settle 宏断言；原全部用例 PASS。

#### 11.41.5 ELF（r42；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v23d（obs 加固 + 图案/缓存 + VDMA 寄存器 + 地址冲突提示） | `9fb0ca28ec38d7345302f772b6bae6a94892c5f54a3b5360944d58782659fadc` | 405,432 |
| `s5_display_app_p3r_camera.elf` | 相机 v23（正式，目标 0x12000000） | `fa88a5c3d70cdf657179be8524e327efd7def9b61cd8c2823040ee11a6ca0011` | 377,160 |

构建记录：`build/p3r_camera_record.json`（sha256 `2a16f5daa67b8ba7f23e4508d85a2eab188826328df24ad4acfeb94d483f3481`）。

#### 11.41.6 r42 判据
- `CAM: obs enter …` 后能走完 16 行并打印 `CAM: obs exit`（不再 ABT）；
- `pattern overwritten_words>0` ⇒ PL 确实写入了 `0x12000000`（此前全 0 是缓存/未写，需看此项）；
- 若 `pattern overwritten_words==0` 且 beats 在涨 ⇒ S2MM 收到 beat 但未落 DDR（FSIZE 不匹配丢弃/S2MM DRE/地址），结合 `0xA0/A4/A8/AC` 回读与 `SR` 继续定位；
- 若地址冲突评估需要，下一窗可讨论把应用加载地址后移或使用高位安全 DDR 区。

### 11.42 v24：S2MM 偏移确认 + 阶段3 CR/FRMSTORE 对齐 + obs 拆分 fail-safe

#### 11.42.1 驱动源码证据（确认 0xA0/A4/A8/AC）
```c
/* xaxivdma.c */
WrChannel->StartAddrBase = InstancePtr->BaseAddr + XAXIVDMA_S2MM_ADDR_OFFSET;  /* 0xA0 */
/* xaxivdma_channel.c（相对 StartAddrBase） */
XAxiVdma_WriteReg(chan->StartAddrBase, XAXIVDMA_VSIZE_OFFSET(0x00), Vsize);          /* →0xA0 */
XAxiVdma_WriteReg(chan->StartAddrBase, XAXIVDMA_HSIZE_OFFSET(0x04), HoriSize);       /* →0xA4 */
XAxiVdma_WriteReg(chan->StartAddrBase, XAXIVDMA_STRD_FRMDLY_OFFSET(0x08), Stride);   /* →0xA8 */
XAxiVdma_WriteReg(chan->StartAddrBase, XAXIVDMA_START_ADDR_OFFSET(0x0C)+i*4, addr);  /* →0xAC.. */
```
⇒ `VSIZE=0xA0 / HSIZE=0xA4 / STRIDE=0xA8 / FRMPTR1=0xAC` 正确；`0x50/0x54/0x58/0x5C` 是 MM2S 侧
（S2MM-only 读 0 正常），**不要改偏移**。`XAXIVDMA_FRMSTORE_OFFSET=0x18`（ChanBase=0x30）⇒ **FRMSTORE=0x48**。

#### 11.42.2 阶段3 的完整 VDMA 序列（原文依据）
- `dbdf\tmp\s3r06\t04_j11cmos2_elf_v10\elf_build\app\display_demo.c:655`：
  `vdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID, 1280*3, 720, 1280*3, dispCtrl.framePtr[curFrame]);`
- `...\app\vdma.c:113` `vdma_write_init()`：`XAxiVdma_LookupConfig → CfgInitialize →`
  `WriteCfg{EnableCircularBuf=1, EnableFrameCounter=0, FixedFrameStoreAddr=0, EnableSync=1, PointNum=1,`
  `VertSizeInput=720, HoriSizeInput=3840, Stride=3840} → XAxiVdma_DmaConfig(写 CR) →`
  `XAxiVdma_DmaSetBufferAddr(写 0xAC..) → vdma_write_start()（DmaStart 写 RUNSTOP）`；
- 实测 `S2MM_CR=0x18003`（RUNSTOP|TAIL_EN|GENLCK_RPT 0x8000）。

#### 11.42.3 v24 对齐/改动
1. **S2MM_CR 启动值**：`S5_CAM_S2MM_CR_START = RUNSTOP|TAIL_EN|0x8000`（对齐阶段3 的 0x18003 低位；
   我们 r41 写的是 0x10003，差 bit15 GENLCK_RPT）。
2. **FRMSTORE(0x48)=1**（对应 `C_NUM_FSTORES=1`），在配置/启动前写入。
3. **obs 段再加固**：`CAM: obs enter/exit`；VDMA 寄存器固定 `volatile` 读；计数器逐个带标记读取；
   无 float、除法前判零；pattern 预写/校验独立打印。
4. 额外打印 S2MM 状态：`0x38(CDESC) / 0x3C(IRQ_MASK) / 0x48(FRMSTORE) / 0x1C(BUFTHRES) / 0x34(SR)`。

#### 11.42.4 自检（PASS）
- `S5_CAM_S2MM_CR_START == 0x8003` 写序断言；`FRMSTORE=1`；
- S2MM 偏移断言 `0xA0/A4/A8/AC` 不变；FRMPTR 仍 `0x12000000`（拒绝 `0x00114C00`，与 ELF RW 段冲突）；
- obs enter/exit、warmup 12 s/settle；原全部用例 PASS。

#### 11.42.5 ELF（r43；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v24d（阶段3 CR/FRMSTORE + 更多 S2MM 状态 + obs 拆分） | `8bea74e8347d5404435453b455c2d88f9d225687f63d4fe86dd534f412185ee2` | 406,360 |
| `s5_display_app_p3r_camera.elf` | 相机 v24 | `737584448e74f4540bd13218ff775f83d65805689d3460a7be2c4b9a4ec145a3` | 378,088 |

构建记录：`build/p3r_camera_record.json`（sha256 `9b73b68ac03e4dd99e9fae756bc43b7ae4934468b21b41dea8b674213b17ba10`）。

#### 11.42.6 r43 判据
- `pattern overwritten_words>0` ⇒ DDR 写入成功（此前全 0 属缓存/未写）；
- 若 CR=0x8003 后 `frmcnt`/tlast 继续增长且 DDR 有数据 ⇒ 采集闭环；
- 若仍无 DDR 写入 ⇒ 对照 `FRMSTORE(0x48)` 回读、`SR`、`0xA0/A4/A8/AC` 回读，重点查 S2MM DRE/FSIZE 丢弃。

### 11.43 v25：direct 模式 VSIZE kick-off（驱动 L1004–1030）

#### 11.43.1 决定性证据（`axivdma_v6_15/src/xaxivdma_channel.c` L1004–1030）
```c
CrBits = XAxiVdma_ReadReg(Channel->ChanBase, XAXIVDMA_CR_OFFSET) | XAXIVDMA_CR_RUNSTOP_MASK;
XAxiVdma_WriteReg(Channel->ChanBase, XAXIVDMA_CR_OFFSET, CrBits);
if (XAxiVdma_ChannelIsRunning(Channel)) {
    if (Channel->HasSG) { ...TDESC... }
    else {
        /* Direct register mode: Update vsize to start the channel */
        XAxiVdma_WriteReg(Channel->StartAddrBase, XAXIVDMA_VSIZE_OFFSET, Channel->Vsize);
    }
}
```
⇒ **direct 模式必须“写完 CR.RS 之后再写一次 VSIZE(0xA0)”才真正 kick off**。
我们此前一直是“写 VSIZE → 写 CR”，**少了最后这次 VSIZE** ⇒ 收 beat（tready 高）但一帧不落 DDR、`FSZ_MORE` 常亮。

#### 11.43.2 v25 启动序列（替换旧逻辑）
```text
1) 配置（halted）：HSIZE(0xA4)=3840、STRIDE(0xA8)=3840、FRMPTR1(0xAC)=0x12000000、VSIZE(0xA0)=720
2) CR：cr = Read(0x30)；cr &= ~(TAIL_EN 0x2 | SYNC_EN 0x8 | FRMCNT_EN 0x10 | RD_PTR 0xF00)；
       cr |= RS 0x1；Write(0x30, cr)         ← 不再带 TAIL_EN / 0x8000
3) kick off：再 Write VSIZE(0xA0)=720       ← 关键新增
4) 轮询 SR.HALTED==0，打印 cr_before/cr_after/vsize_write1/vsize_write2/sr
```
- **不写 FRMSTORE(0x48)**（驱动从不写，回读 0 正常）；
- 保留 1280×720/3840 几何 + warmup 12 s；
- obs 段拆标记：`pattern write start` → `vdma kickoff start` → `pattern verify start` → `obs enter` → 16 行 → `obs exit`。

#### 11.43.3 自检（PASS）
- **kick-off 写序断言**：mock 日志中必须出现「CR 写（RS=1 且 TAIL_EN=0）」之后「VSIZE=720 写」；
- CR 清位断言（TAIL_EN/SYNC/FRMCNT/RD_PTR 清、仅 RS=1）；
- `FRMSTORE 未被写`；obs 标记存在；warmup/settle、偏移 `0xA0/A4/A8/AC`、原全部用例 PASS。

#### 11.43.4 ELF（r45；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v25d（kick-off 序列 + obs 标记） | `50e0caed2b73ce9348543ec81178e07a09f906b97a4903445e9a62c6847389b5` | 407,708 |
| `s5_display_app_p3r_camera.elf` | 相机 v25（正式） | `591b34f0eedd25034f18e4498a097fd376fb5d95ca43124ae14d08658109e818` | 379,344 |

构建记录：`build/p3r_camera_record.json`（sha256 `f7328e9f6c5012d06c3b0e027285501f71aa531a02b52f8e20fc37ea16dce345`）。

#### 11.43.5 r41–r44 现象对应
| 现象 | 解释 |
|---|---|
| TAP_VALID≈27.6M beat/s（tready 高） | CR.RS=1 让 S2MM 开始响应，但未 kick off |
| tlast≈24.6k/s | 行结束有 beat，但帧未启动 |
| `SR=0x14810`（含 FSZ_MORE） | 帧尺寸粘滞错误，因“帧”从未真正开始 |
| `0x12000000` 全 0 | 未启动 → 不写 DDR |
| CR=0x10003 / 0x18003 | 旧写法带 TAIL_EN（及 GENLCK_RPT），direct 模式应不带 |

#### 11.43.6 r45 判据
`CAM: obs enter` 后 16 行 `SR halted=0`、`frmcnt` 递增；`pattern overwritten_words>0`（DDR 被写）；
raw 非零且两次采样变化 ⇒ 采集闭环，进入相机窗。

### 11.44 v26：CR→RESET 的元凶定位 + 纯寄存器最小验证

#### 11.44.1 r45 现象与根因
- r45：kickoff 后 `CR=0x10004`（**RESET=1、RS=0**）、`rc=-4`，两次快照 `cr_running=0`；app 第 5 次 ABT（PC=0x101BEC，紧跟 `obs vdma` 行）。
- 根因：v25 的 obs 段调用 `S5CamVdma_StartGeometry()`，而该函数**开头就写 `CR.RESET=1`**
  （`src/s5_camera.c:1121`），把刚刚启动的通道置回 RESET ⇒ `CR=0x10004`、后续 poll 超时 `rc=-4`。
  这不是 VDMA 自己复位，是我们自己的诊断函数重复复位。

#### 11.44.2 app/camera 中所有写 `0x43C60030`（S2MM_CR）的位置
| 位置 | 内容 | 是否写 RESET |
|---|---|---|
| `s5_camera.c:1035` | `S5CamVdma_Config` 复位阶段写 `S5_CAM_CR_RESET` | 是（bringup 内，合法） |
| `s5_camera.c:1121` | **`S5CamVdma_StartGeometry` 开头写 RESET** | **是 ← r45 元凶** |
| `s5_camera.c:1162 / 1231` | `S5CamVdma_Probe` / `Reconfig` 写 RESET | 是（诊断用，v26 不调用） |
| `s5_camera.c:1068` | Config 启动 RMW（清控制位 + RS） | 否 |
| `s5_camera.c:1192` | Probe 启动 RMW | 否 |
| `s5_camera.c:1270` | `S5CamVdma_Start` 写 `S5_CAM_S2MM_CR_START`（=RS） | 否 |
| `s5_camera.c:1202/1211/1260/1279` | 各处停通道写 `0` | 否 |

⇒ 结论：**obs/诊断路径不能再调用 StartGeometry/Probe/Reconfig**；v26 只做寄存器读写。

#### 11.44.3 v26 纯寄存器最小验证（无 pattern/无 obs/无浮点）
```text
1) 停通道：w=Read(0x30)；Write(0x30, w & ~0x1)（只清 RS，不写 RESET）
2) 配置：Write 0xA0=720 / 0xA4=3840 / 0xA8=3840 / 0xAC=0x12000000
3) 启动：w=Read(0x30)；Write(0x30, (w & ~0x2) | 0x1)；打印 cr_write/cr_readback/sr
4) 5 ms 后 kick：Write 0xA0=720；打印 cr/sr
5) 等 1000 ms：打印 cr/sr/frmcnt + DDR 0x12000000 前 16 个 u32（读前 invalidate）
6) 不写 CR=0、不做任何其他事；任何一步 CR 含 0x4 即打印 `RESET observed at step=…`
```

#### 11.44.4 自检（PASS）
- kick-off 写序断言（CR 后必须 VSIZE）、CR 仅 RS=1 且 TAIL_EN=0、FRMSTORE 未写；
- 原有 302 表/覆盖表/warmup/2×2 抽样等用例保持 PASS。

#### 11.44.5 ELF（r46；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v26d（纯寄存器最小验证） | `241800d095916031c7008e952368c8a2d797bc658dab58fb6b9d0d83fffe5d40` | 404,332 |
| `s5_display_app_p3r_camera.elf` | 相机 v26 | `7cf085f50ab71aa819087cf69b264c078877597f0839599d8c155ffa9c7bba96` | 379,344 |

构建记录：`build/p3r_camera_record.json`（sha256 `ac51fcd120cd97000fa2342eb94188d910fde85cc3e87e28c469ad500365de2b`）。

#### 11.44.6 r46 判据
- `cr_readback` 保持 `0x1`（RS=1、无 RESET）；
- `after1s` 的 `frmcnt` 增长、`0x12000000` 前 16 字出现非零 ⇒ VDMA 启动并落 DDR 成功；
- 若 CR 再变 `0x10004` ⇒ 按上表逐点核对（v26 已不调用任何写 RESET 的诊断函数）。

### 11.45 v27：先清 RESET 再只写 RS（r46 现象修正）

#### 11.45.1 r46 现象
- 进场即 `cfg: cr=0x10004`（**RESET=1**、RS=0）；`start` 后 `0x10005`（RS=1 但 **RESET=1**）⇒ RS 被 RESET 压住，通道未真正运行；
- 说明我们此前对 CR 的写没有先清 RESET，且启动写的值把 RESET 一起带上。

#### 11.45.2 v27 流程（极简，仍无 pattern/obs/浮点）
```text
1) CAM: v27 enter
2) 清 RESET：Write(0x30, 0x0) → 等 1ms → 读回；要求 (cr&4)==0
   若仍为 1 ⇒ 打印 RESET_STUCK cr=… 并停（查时钟/复位）
3) 确认 halted：读 SR(0x34)，要求 (sr&1)==1
4) 配置：VSIZE(0xA0)=720 / HSIZE(0xA4)=3840 / STRIDE(0xA8)=3840 / FRMPTR1(0xAC)=0x12000000，全部回读打印
5) 启动：**Write(0x30, 0x1)**（只写 RS）→ 等 1ms → 读回；要求 (cr&1)==1 且 (cr&4)==0
   若 RESET 又置位 ⇒ 打印 RESET_SET_BY_START cr=… 并停
6) kick-off：Write(0xA0, 720) → 等 1ms → 打印 cr/sr
7) 等 1000ms：打印 after1s cr/sr/frmcnt
8) invalidate 后读 DDR 0x12000000 前 16 个 u32
9) CAM: v27 exit
```
- 全程**不调用** `S5CamVdma_StartGeometry` 与任何写 RESET 的函数；
- app 内对 `0x43C60030` 的写入只剩两处：步骤 2 的 `*crp=0` 与步骤 5 的 `*crp=0x1`；
- camera.c 中写 RESET 的只有 Config 复位阶段（bringup 内）、StartGeometry/Probe/Reconfig（v27 均不调用）。

#### 11.45.3 自检（PASS）
- 「RESET 清除 → RS 置位 → 无 RESET」写序与读回断言（mock 记录 CR 写：`RS=1 且 RESET=0`）；
- kick-off 写序（CR 后必须 VSIZE）、CR 仅 RS、FRMSTORE 未写；
- 原 302 表/覆盖表/warmup/2×2 用例保持 PASS。

#### 11.45.4 ELF（r47；显示三件套未改）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v27d（清 RESET → RS → kick-off → DDR 读） | `175746ad866068eebfcebcf1d5006cfa0789d6a4004899f460db5b1cf32042bc` | 404,352 |
| `s5_display_app_p3r_camera.elf` | 相机 v27 | `8eb4f3b9cb47036cfb6bf6f8b270baaf29629f50e205cbbd1337d1c0a4a8b99b` | 379,344 |

构建记录：`build/p3r_camera_record.json`（sha256 `f469fc39494a71ce21c19018878090742e5d33b41dbae7113eb9b77420ebac37`）。

#### 11.45.5 r47 判据
- `clear_reset: cr` 的 bit2==0；`start: cr` bit0==1 且 bit2==0；
- `after1s frmcnt` 增长、DDR 前 16 字非零 ⇒ **VDMA 落数据成功** ⇒ 立即接回显示、进相机窗；
- 若 `RESET_STUCK` / `RESET_SET_BY_START` ⇒ 打印相应行并停，转查 `s_axi_lite_aclk`/`m_axi` 复位与时钟。

### 11.46 v28：寄存器映射扫描（判定 S2MM 块偏移）

#### 11.46.1 r47 的矛盾
`clear_reset` 写 `CR(0x30)=0` 后仍读到 `0x10004`（RESET_STUCK），但 VDMA 仍在拉 tready
（TAP_VALID 27.6M beat/s）⇒ **通道并不在复位**，更可能是我们读写的地址不是真正的 S2MM CR 块。

#### 11.46.2 v28 扫描设计
A. **全寄存器快照**：`0x43C60000 + 0x00..0xBF` 共 48 字，4 行 × 12 列打印；
B. **写-读回映射测试**：候选 `0x00/0x04/0x30/0x34/0x50/0x54/0x58/0x5C/0xA0/0xA4/0xA8/0xAC`，
   每个地址：`old=read → write(0xA5A50000|off) → read`，打印 `addr/old/wrote/read`；
   测试前先 `Write(0x30,0)` 与 `Write(0x00,0)` 尝试清复位；
C. **CR 语义**：对 `0x30` 与 `0x00` 分别写 `0x0 / 0x1 / 0x8`，各等 1 ms 读回；
D. **恢复**：两套几何/地址都写回正确值（`0xA0..0xAC` 与 `0x50..0x5C`），打印回读；只读 DDR 8 字。

#### 11.46.3 两种假设与判定
| 假设 | CR/SR | 几何/地址 | 依据 |
|---|---|---|---|
| A（驱动源码） | `0x30 / 0x34` | `VSIZE=0xA0 / HSIZE=0xA4 / STRIDE=0xA8 / FRMPTR=0xAC` | `xaxivdma.c` StartAddrBase=BaseAddr+0xA0 |
| B（S2MM-only 沿用 0x00 起始块） | `0x00 / 0x04` | `VSIZE=0x50 / HSIZE=0x54 / STRIDE=0x58 / FRMPTR=0x5C` | 与显示 MM2S 同偏移；r42 实测 0x50–0x5C 全 0（我们从未写） |

判定：`0x00` 可写且 `0x50–0x5C` 是几何/地址 ⇒ v29 切 B 映射；`0x30` 可写且 `0xA0` 是几何 ⇒ 维持 A、
转查 aclk/aresetn；两者都写不进 ⇒ build11e 查硬件复位/时钟。

#### 11.46.4 自检（PASS）
- 两种映射假设的常量断言（A：0x30/0x34/0xA0/A4/A8/AC；B：0x00/0x04/0x50–0x5C）；
- 扫描表与恢复步骤在 mock 下可编译；原全部用例 PASS。

#### 11.46.5 ELF（r48）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v28d（映射扫描 + CR 语义 + 恢复） | `7c1ae71964325be586ced4d32002d2ff1150f18ac7a444b9bae9315524d16396` | 403,880 |
| `s5_display_app_p3r_camera.elf` | 相机 v28（逻辑暂不动，等映射结论） | `591b34f0eedd25034f18e4498a097fd376fb5d95ca43124ae14d08658109e818` | 379,344 |

构建记录：`build/p3r_camera_record.json`（sha256 `b849eaebc38c593bb1283c5f8b6f88aece640be7f25696afb816d32074bd2fe0`）。

#### 11.46.6 r48 期望输出
```text
CAM: v28 enter
regs[00-2c]: …（12 字）
regs[30-5c]: …
regs[60-8c]: …
regs[90-bc]: …
clear_try: cr30=… cr00=…
map addr=00 old=… wrote=… read=…
…（12 行）
cr_addr=30 wrote=00000000 read=…
cr_addr=30 wrote=00000001 read=…
cr_addr=30 wrote=00000008 read=…
cr_addr=00 wrote=…
cr_addr=00 wrote=…
cr_addr=00 wrote=…
restore: A0/A4/A8/AC=…/…/…/… 50/54/58/5C=…/…/…/…
ddr 0x12000000: …
CAM: v28 exit
```

### 11.47 v27e：build11e 复位验证后的主力七行诊断

#### 11.47.1 与 v27d 的差异（仅诊断增强，不改流程）
1. 保持七行：`clear_reset → halted → cfg → start(只 RS) → kick(写 VSIZE) → after1s → ddr 16 u32 → exit`；
2. **增强 a**：`clear_reset` 之前先打印简版 `regs[30-5c]: cr=… sr=…`；
3. **增强 b**：`after1s` 之后额外打印 `regs[a0-ac]: vsize/hsize/stride/frmptr`，确认几何/地址未被改动；
4. **增强 c**：`start` 后若 `cr&4` 仍为 1，打印 `RESET_SET_BY_START` 后**继续** kick/after1s，一次拿全数据；
5. 去掉 v28d 的 map 扫描；保留 `CAM: v27 enter/exit`；
6. 不调用 `S5CamVdma_StartGeometry`、不写 RESET；几何仍 1280×720/3840（与 build11e FSYNC=0 同参数）。

#### 11.47.2 期望输出
```text
CAM: v27 enter
regs[30-5c]: cr=… sr=…
clear_reset: cr=…
halted: sr=…
cfg: vsize=000002d0 hsize=00000f00 stride=00000f00 frmptr=12000000
start: cr=…（bit0=1、bit2=0 为好）
kick: cr=… sr=…
after1s: cr=… sr=… frmcnt=…
regs[a0-ac]: vsize=… hsize=… stride=… frmptr=…
ddr 0x12000000: …（16 字）
CAM: v27 exit
```

#### 11.47.3 自检（PASS）
- 写序断言：`clear_reset`（写 0）→ `start`（写 RS=1 且 RESET=0）→ `kick`（写 VSIZE）顺序在 mock 日志成立；
- `cr&4` 分支不再提前返回（代码路径保留 kick/after1s）；
- 原 302 表/覆盖表/warmup/2×2 用例保持 PASS。

#### 11.47.4 ELF（r49b）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v27e（七行 + regs 打印 + RESET 分支继续） | `8fd0ef8ee7cf77f1d97d6465ed2ae39cfc216945f4f71269bb45fbf80120af12` | 404,976 |
| `s5_display_app_p3r_camera.elf` | 相机（源码与 v27 相同；重链后 sha 见记录） | `7b6cf25cb29881cd019d3ece6570e55268628975f49e684b7747c88b0215ed26` | 379,344 |

构建记录：`build/p3r_camera_record.json`（sha256 `76e5c35c5e82f93bfc1f3d1ee472465c9428670091d78d87a1823e0745d33e70`）。
说明：相机 ELF 源码未变，重链后 sha 与上一窗不同（链接器 build-id 非确定），行为等价；若需固定 sha 可加 `--build-id=none` 重链。

#### 11.47.5 板级用法
- r49a（v28d）若确认**CR 能清**：直接跑相机窗；
- 若不能清：用 v27e 跑 r49b，按输出判断是 `RESET_STUCK`（复位/时钟）还是 `RESET_SET_BY_START`（启动语义），并一次拿到 `regs[a0-ac]` 与 DDR 数据。

### 11.48 v29：相机 VDMA 改用 XAxiVdma 驱动（阶段3 同路径）

#### 11.48.1 r50 结论（复位/时钟排除）
`0x43D40000=0x3`（rst_100/rst_all 已释放）、FCLK0=50.16 MHz、FCLK1=100.07 MHz 均在跑；
snap1 `CR=0x10001`（RS=1）⇒ **CR 写入生效**，此前 `0x10004` 是"写后立即读"的中间态/被后续代码复位。
⇒ 问题回到软件层，决定改用 Xilinx XAxiVdma 驱动（阶段3 今天实测可写 DDR 的同一路径）。

#### 11.48.2 驱动来源与编译
自阶段3 BSP `axivdma_v6_17/src` 拷入 `src/axivdma/`：
`xaxivdma.c`、`xaxivdma_channel.c`、`xaxivdma.h`、`xaxivdma_hw.h`、`xaxivdma_i.h`；
用本工程 arm-none-eabi-gcc + `-DSDT` 编译通过（`CC=0`），链接进 diag/相机 ELF。

#### 11.48.3 v29 诊断流程
```text
CAM: v29 enter
drv: CfgInitialize=%d (XST_SUCCESS=0)          ← 静态 config：S2MM-only/24bpp/DRE=1/SG=0
drv: DmaConfig=%d (VERT=720 HORI=3840 STRIDE=3840 circ=1 sync=1 PointNum=0)
drv: DmaSetBufferAddr=%d buf0=0x12000000
drv: DmaStart=%d
（等 1 s）
after1s: cr=… sr=… frmcnt=…
ddr 0x12000000: …（16 u32）
CAM: v29 exit
```
- 不再手写 CR/VSIZE/HSIZE/STRIDE/FRMPTR（由驱动内部完成，含 reset 等待与 `Update vsize to start`）；
- 保留 302 表 + 覆盖表 + stream off/on + warmup 12 s；几何 1280×720/3840（与 build11e FSYNC=0 一致）；
- 每步打印 `XST_*` 返回码，失败可定位到具体驱动调用。

#### 11.48.4 自检（PASS）
原全部用例（CHIPID/覆盖表/VDMA 写序/SR/2×2 抽样）保持 PASS；驱动源码仅参与 ARM 链接（host mock 不受影响）。

#### 11.48.5 ELF（r51）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 v29d（XAxiVdma 驱动路径 + 返回码） | `36794933695748fd74063e894d82e93ac9feecf21185e06783b35f4dfd93137c` | 464,872 |
| `s5_display_app_p3r_camera.elf` | 相机 v29（链接驱动；主流程暂保持寄存器 init，待 diag 证实后切 v30） | `ad7cd273e14c0c613381e6845bab5b649f06b22357d9247c6c146298ddfc94c1` | 385,580 |

构建记录：`build/p3r_camera_record.json`（sha256 `32b431d2b2f93a9b69aaceae750fdcefe461a97b4ba4dc6c69ed998b4b025c68`）。

#### 11.48.6 r51 判据
- `CfgInitialize=0` 且 `DmaConfig/DmaSetBufferAddr/DmaStart=0`（XST_SUCCESS）⇒ 驱动路径正常；
- `after1s frmcnt` 增长、DDR 前 16 字非零 ⇒ 驱动成功启动并落数据 ⇒ 相机 v30 把主流程切到驱动；
- 任一返回码非 0 ⇒ 按码定位（XST_FAILURE=1 / XST_INVALID_PARAM=2 等），并对照驱动源码行。

### 11.49 MVP HUD：5 类中文名 + 置信度 + latency + 交互（离线可编译）

#### 11.49.1 标签映射（权威来源，写死）
来源：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names`
sha256 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`（与阶段1 冻结记录一致）：
```text
0: fist    → 拳头
1: palm    → 布
2: one     → 数字一
3: two_up  → 数字二
4: three   → 数字三
```
代码：`s5_display_app.c` 内
`static const char *s5_hud_name_utf8[5] = {"拳头","布","数字一","数字二","数字三"};`

#### 11.49.2 HUD 内容与交互
- 视频区四边 **6 px 颜色边框**，5 类各一色（红/蓝/绿/黄/紫），无检测为灰；
- **左上大字**（3× 16×16 字形）：`手势：<中文名>`，字形表 `src/s5_hud_font.h`（离线渲染 11 个汉字，16×16 位图）；
- 其下 `conf=0.xx`（取最近一次有效检测中 score 最高者，score 为 0..100 百分数）；
- 右下 `lat=<n>ms`（info->latency_ms；0 显示 `?`）；
- 手势切换时 UART：`APP: gesture_changed from=<旧> to=<新>`；
- 每 30 帧 UART：`APP: gesture=<中文> cls=<0..4> conf=0.xx latency_ms=<n>`；
- 结果块无效时沿用既有回退（sim/测试图），HUD 显示 `gesture=none`/灰边，保证可跑。

#### 11.49.3 结果块消费（确认）
- 地址/结构不变：`0x20800000`、magic `0x53355253`、32 B 头 + `0x20` 起 16×16 B 检测项 + `0x100` 侧车；
- 显示侧 `S5Real_Parse()` 解析 → `S5FrameInfo.det[]`（cls/score）→ HUD 直接消费；**未改块布局/magic/侧车**。

#### 11.49.4 改动的文件
| 文件 | 说明 |
|---|---|
| `src/s5_display_app.c` | HUD 绘制/交互/UART；在 `S5Draw_Boxes` 后调用 `S5Display_DrawHud()` |
| `src/s5_display_app.h` | 新增 `S5Display_DrawHud()` 声明 |
| `src/s5_hud_font.h` | **新增**：11 个汉字 16×16 位图（手势：数字一二三拳头布） |
| 未动：相机链、显示三件套冻结件、producer/结果块写入端、R-16/R-17/R-02 相关 |

#### 11.49.5 主机渲染自检（PASS）
`host_render_test.exe` PASS（180 帧，RESULT 单行 265 字符），HUD 截图：
`build/hud_frame_full.png`（1280×720）、`build/hud_frame_age_over.png`。
截图内容：视频区左上 `手势：数字一`、`conf=0.92`、绿色边框（cls2=数字一）、右下 `lat=17ms`；右栏为原有信息面板。

#### 11.49.6 ELF（离线）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_ecam_diag.elf` | 诊断 + HUD | `1c64cac90d32f67e77ca81ff1dce1e93d8718e5fb924d20a7f5c29f91ae0a93e` | 476,532 |
| `s5_display_app_p3r_camera.elf` | 相机 + HUD（等 build11g/阶段3 采集通） | `6a4a252da120f7712c4e566f33cf44306ffccf639814c08b88323d256c431df7` | 393,128 |

构建记录：`build/p3r_camera_record.json`（sha256 `e2d7b1001264ee04ef2c79958e1bb4611ba5790731233c747c2d1e11744d7533`）。

#### 11.49.7 说明：当前 HUD 只能显示 sim 数据
相机链（build11g）与真实推理生产端就位前，板上 HUD 走 sim/回退数据；真实链通后无需改 HUD，仅由生产端写 `0x20800000` 即可。

### 11.50 MVP 相机修复：去 RESET 的 VDMA 启动（rc=-14 根因）

#### 11.50.1 根因
`rc=-14`：`S5Cam_Init()` 走 `S5CamVdma_Init()`（内部 `S5CamVdma_Config` 先写 `CR.RESET=1` 并期待 HALTED），
通道停在 RESET ⇒ S2MM 配置失败。诊断 v27e 已证明：**先 CR=0 清 RESET、再只写 RS、再 kick VSIZE** 可启动。

#### 11.50.2 修复（只改相机启动序列）
`S5Cam_Init()` 改用新函数 `s5_vdma_start_nors()`：
```text
1) Write CR(0x30)=0；等 1 ms；读回要求 (cr & 0x4)==0     （否则 rc=-21）
2) Write VSIZE(0xA0)=720 / HSIZE(0xA4)=3840 / STRIDE(0xA8)=3840 / FRMPTR1(0xAC)=0x12000000
3) Write CR(0x30)=1（只 RS）；等 1 ms；读回要求 RS=1 且 RESET=0 （否则 rc=-22）
4) kick：再写 VSIZE(0xA0)=720
```
- 不调用 `S5CamVdma_StartGeometry()`、不写 RESET；
- 保留 302 表 + 覆盖表 + stream off/on + warmup 12 s；
- HUD（5 类中文/置信度/latency/颜色交互）与 S5RS `0x20800000` 解析未动。

#### 11.50.3 新增细分阶段打印
`CAM: bringup rc=%d stage=%s elapsed_ms=…`（诊断）
`CAM: FAIL rc=%d stage=%s (rc map: -10 chipid/-11 sccb/-12 overlay/-13 regchk/-17 table/-18 stream_on/-19 stream_off/-20 timing/-21 clear_reset/-22 start_rs)`（正式）

#### 11.50.4 自检（PASS）
- Init 路径 **无 RESET 写入**、CR 只写 RS=1、kick 写序正确；
- halted-sticky 语义更新为"不再依赖 SR.HALTED"（无 RESET 路径容忍 sticky）；
- 原全部用例保持 PASS。

#### 11.50.5 ELF（b11h，无需重建 PL）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3r_camera.elf` | 相机修复 + HUD（正式） | `86690cc28214d2c1b695fff4a49d9a64edb1f2a32d63ab9619012ec94ee4108f` | 395,004 |
| `s5_display_app_ecam_diag.elf` | 诊断 + HUD | `516dd5343c23ad5c4922ec50ad9ebb4d085a8d08b516c1f1cb744e5b06bc464e` | 478,960 |

构建记录：`build/p3r_camera_record.json`（sha256 `c6f4c178c34366127df2824829936257b138ea19c9e2d387e3060c89afd5ed12`）。

#### 11.50.6 成功判据
- UART 不再出现 `CAM: FAILED rc=-14`（或出现 -21/-22 时按 stage 定位）；
- `S5DISP` 中 `src=real` 且 `fps_cap>0`；`0x12000000` 有非零像素 ⇒ 相机链通，HUD 显示真实手势。

### 11.51 方案 B：相机几何 1280×720 对齐 + 日志回读（MVP 终链）

#### 11.51.1 三处几何不一致（r03 板级）
| 位置 | 板级显示 | 应有一致值 |
|---|---|---|
| 应用相机日志 | `CAM: init OK … 640x480` | **1280×720**（打印误用旧宏 `S5_CAM_W/H`） |
| v31 VDMA | `VSIZE=720 / HSIZE=STRIDE=3840` | 一致（正确） |
| core1 推理 | 期望 `bytes=2764800`（1280×720） | 一致（正确） |
⇒ 每帧字节数与 HSIZE/VSIZE 不符 ⇒ `SR.FSZ_MORE(0x800)` 常亮 ⇒ datamover 中止、不落 DDR。

#### 11.51.2 方案 B 落地
- 覆盖表保持 v22/阶段3 720p 值（实测已写入）：
  `0x3808/09=0x05/0x00`、`0x380A/0B=0x02/0xD0`、`0x380E/0F=0x02/0xE4`、`0x380C/0D=0x07/0x64`、
  `0x3814/15=0x31`、`0x3035=0x21`、`0x3036=0x69`、`0x3037=0x13`、`0x3108=0x01`、`0x4300=0x60`、`0x501F=0x01`；
- `init OK` 打印改用 `S5_CAM_CAP_W/S5_CAM_VSIZE`（1280/720）；
- **新增传感器几何回读**：`CAM: geom dvpho=… dvpvo=… hts=… vts=… (expect 1280/720/1892/740)`，
  板上可直接核验覆盖表是否真正生效（0x3808/09、0x380A/0B、0x380C/0D、0x380E/0F 组合）；
- VDMA 保持 `VSIZE=720 / HSIZE=STRIDE=3840 / FRMPTR=0x12000000` + 无 RESET 启动序列；
- core1/HUD/S5RS 解析不动。

#### 11.51.3 自检（PASS）
覆盖表断言（DVPHO=1280/DVPVO=720/VTS=740/HTS=1892）、VDMA 720/3840、无 RESET 写入、kick 写序、原全部用例。

#### 11.51.4 ELF（01:30 窗口，b11h 位流不重建）

| ELF | 说明 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3r_camera.elf` | 相机几何对齐 + HUD（正式） | `6bae254b187853bebc7244a156b59b49d96ab7d0001f826e0a0df3360b0d54e9` | 395,768 |
| `s5_display_app_ecam_diag.elf` | 诊断 + HUD | `f6f967c1793259a1a8de2d8134b2c27fe00660a5d812fce9ce95e370fb395c33` | 479,616 |

构建记录：`build/p3r_camera_record.json`（sha256 `3ffa3eb759449ca8a94441804fc0c15662b58392d47e7ae4a6b0db8ea51d91c4`）。

#### 11.51.5 r03 判据
- `CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740`；
- `SR` 无 `FSZ_MORE(0x800)` 粘滞；`S5DISP` 出现 `src=real` 且 `fps_cap>0`；
- `0x12000000` 非零 ⇒ 相机链通；HUD 显示真实手势（`APP: gesture=…`）。

### 11.52 v33：VDMA SOF 相位/清错诊断（每帧前清 SR + kick 前移）

- 启动序列：CR=0 清 RESET → 配 VSIZE=720/HSIZE=STRIDE=3840/FRMPTR=0x12000000 → CR=RS → 延时 10 ms → 只读回读 CR/SR；RS 后不再写 VSIZE（kick 前移）。
- 新增 S5Cam_VdmaClearSr()：写 SR(0x34) W1C 0x7F0，打印 CAM: sr_after_clear=0x…；1 s 后打印 CAM: sr_after_1s=0x…。
  - 1 s 后又回 0x14810 ⇒ 每帧复现 FSZ_MORE（SOF 相位/硬件，转 b11j）；
  - 保持干净 ⇒ 启动瞬间一次粘滞（软件可解）。
- 每 30 帧打印 CAM: frm=… cr=… sr=… cam_gpio=… s2mm_beat=… tlast=…。
- 未改：302 表/覆盖表、几何 1280×720、HUD、S5RS 解析、core1。
- 自检 PASS：SR W1C 0x7F0 写入、RS 后无 VSIZE 写、无 RESET 写入、原全部用例。

| ELF | sha256 | 字节 |
|---|---|---|
| s5_display_app_p3r_camera.elf | 69fb99acc4385e20df9fd6dfab204a95635a724dab5c581da9ad9c8fb9f02397 | 396,688 |
| s5_display_app_ecam_diag.elf | 9a6080718aa8f5a441fb45e9c3fd6900c4a2804fabf02f0397f0ff17b711c352 | 480,484 |

构建记录：build/p3r_camera_record.json sha256 7024824abbe32ffd4e2b94276dfc7d681dffe52eafcdf8d8c575e59a7d412fdd。

### 11.53 v34：VDMA VSIZE=727 对齐传感器实际行数（r07）

- 根因：传感器每帧实际 `dvpvo=727` 行，VDMA `VSIZE=720` ⇒ 每帧多 7 行 ⇒ `FSZ_MORE` 每帧复现 ⇒ 帧中止、DDR 全 0。
- 改动（最小）：
  1. VDMA `VSIZE=727`（`0x43C600A0=0x2D7`），HSIZE/STRIDE=3840、FRMPTR=0x12000000 不变；
  2. 新增打印 `CAM: vsize=727 hsize=3840 stride=3840 frame_bytes=2791680`；
  3. 新增 DVPVO 重写回读：写 `0x380A/0x380B=0x02,0xD0` 后 1 ms / 10 ms 各读一次
     （`CAM: dvpvo_wr720_1ms=0x…` / `CAM: dvpvo_wr720_10ms=0x…`），确认能否写回 720；
  4. 保留 v33 的 `sr_after_clear` / `sr_after_1s` / `CAM: frm=…`。
- 未改：HUD、S5RS、302 表其余项、core1 ELF。
- 自检 PASS（727 写入、SR 清、无 RESET、kick 前移、原全部用例）。

| ELF | sha256 | 字节 |
|---|---|---|
| s5_display_app_p3r_camera.elf | 377937afe2533736470da86c5a14c123967289d134f2b2a998f458814546978a | 397,264 |
| s5_display_app_ecam_diag.elf | 98f46b6db5a974806608945b9bd248ed1ea05c48ce8e1acc2b780b6993661828 | 485,064 |

构建记录：build/p3r_camera_record.json sha256 68d837f607f678a2deda3124d1da740878d9317a0b3fa235c3316c64d5559161。

判据：`sr_after_1s` 不再 0x14810；`0x12000000` 非零；`S5DISP src=real`；`TUSER_TLAST=VSIZE`。

### 11.54 v35：VDMA VSIZE 统一回 720（三处全对齐，r09）

- r08 依据：`dvpvo_wr720_1ms/10ms=0x02D0`（写 720 成功）、`geom dvpvo=720`、`TUSER_TLAST=0x2D0=720`、`TLAST_BEAT=0x500=1280`。
- 改动：VDMA `VSIZE 727→720`（`0x43C600A0=0x2D0`），HSIZE/STRIDE=3840、FRMPTR=0x12000000 不变；
  保留 dvpvo 写 720 + 1 ms/10 ms 回读；保留 `sr_after_clear`/`sr_after_1s` 与每 30 帧 `CAM: frm=…`；
  打印 `CAM: vsize=720 hsize=3840 stride=3840 frame_bytes=2764800`。
- 未改：HUD、S5RS、302 表其余项、core1（720 行 / 2,764,800 B）。
- 自检 PASS（VDMA 720、frame_bytes=2764800、SR 清、无 RESET、kick 前移、原全部用例）。

| ELF | sha256 | 字节 |
|---|---|---|
| s5_display_app_p3r_camera.elf | d1ecc0d8592cec2d414dc73e2c47ee19c7e0c1eaf9ff25eefcc93465058e5743 | 397,268 |
| s5_display_app_ecam_diag.elf | 42d1c53f6508c0ffcd79908620420bdc34ca53e6350af983feb0fc2089ea3fd7 | 485,064 |

构建记录：build/p3r_camera_record.json sha256 f79df736818051a3efff81c765124ba9b5bd6609dea4be94b09ae0a21c91fe71。

判据（r09）：`sr_after_1s` 干净（0x10000）；`0x12000000` 两次快照不同且停核 head 非零；`MVP TIME raw_nz` 大幅上升；`S5DISP src=real`；`TUSER_TLAST=720`。
