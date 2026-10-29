# S5 P3b-sw：HDMI 显示链 PS 侧显示软件报告

- 任务：阶段5 HDMI 显示链 · PS 侧显示软件（P3b-sw）
- 日期：2026-10-30（UTC+8）　版本：**r02**（r01 → r02：布局裁决落地、补 VTC 生成器初始化、帧存改 2）
- 边界：**离线编写 + 编译通过 + 主机端自检（渲染 PNG / 假寄存器堆跑寄存器序列）**。未接触板卡 / JTAG / COM4 / hw_server，未运行 Vivado，未修改 `w4` 仓库文件（只读引用），未 git 提交。
- 工作目录：`D:\tmp\lead\p3b_display_sw_20261030_r01\`

---

## 0. 结论摘要

| 项目 | 结果 |
|---|---|
| ARM 编译/链接 | **exit 0**（compile 0 / link 0 / size 0 / nm 0） |
| ELF | `build/s5_display_app.elf`，**sha256 `9fdec1d909054b1a08fdcd9a6b048fc8e0381327dc07e711e9c85d8de8790b38`**（重建可复现，同 sha） |
| ELF 大小 | **268,184 B**；text 40,021 / data 72 / bss 2,353,184（berkeley） |
| VTC 生成器 | **已实现**（VTC 6.2，720p60）：12/12 寄存器回读校验 OK，负例可检出 MISMATCH（§2.4） |
| VDMA | **2 帧存**（与 BD `c_num_fstores=2` 一致），A/B 双缓冲，只写 0x5C/0x60 两个地址（§2.2） |
| 布局 | **已裁决：无重叠方案**（视频 `x=0..959` + 信息栏 `x=960..1279`），字面 160 黑边方案仅作实验分支（§3.2） |
| 主机渲染自检 | **PASS**，同一份绘图源码渲染出 10 张 1280×720 PNG（两套布局 ×5） |
| 寄存器序列自检 | **PASS**（假寄存器堆跑 `vtc_ctrl.c` + `vdma_ctrl.c`：VTC 校验、负例、双缓冲 6 帧决策，§8.2） |
| VDMA 寄存器用法 | **有把握**：逐条来自本机 Vitis 2026.1 的 `axivdma_v6_17` 驱动源码（`xaxivdma_hw.h` + `xaxivdma_channel.c`），非 SG 写序列与驱动实现一一对应；题面里两处猜测已被纠正（§2.3） |
| 未验证 | 全部上板行为：VDMA 实际搬数、VTC 实际时序输出、rgb2dvi/TMDS、DDR 带宽、撕裂/闪烁、真实延迟数值 |

---

## 1. 交付物

| 文件 | 作用 | sha256 |
|---|---|---|
| `src/s5_display_app.c` | 绘图核心（纯函数，可主机编译）+ 模拟数据源 + 裸机 `main()`（VTC→测试图→VDMA→乒乓） | `6ac01dc1b80d0734956c6833ce2a60ab365b55438e2dffd636343586fe85e498` |
| `src/s5_display_app.h` | 布局/颜色/数据结构/API，G0 口径集中定义（含布局裁决宏） | `fcedcdc3ad95b0157b468676908786e909a3462a8978effd8ab6b42b335de52d` |
| `src/vdma_ctrl.c` | axi_vdma 6.3 MM2S 非 SG 寄存器级初始化/启动/状态 | `b9792bce1eff5a7e5e049853b9f1d10388686684b967d371c73d078d7241b6b0` |
| `src/vdma_ctrl.h` | 寄存器偏移表 + 依据注释 + API | `1f23ef28a9df13afda8279577a11bf9c7583a529ba9b30b71f73e6cee5d76199` |
| `src/vtc_ctrl.c` | v_tc 6.2 生成器初始化（720p60）+ 回读校验 + 文本摘要 | `8ba7d212b4f5d5ec2781bc84b9041cbe218dd935596644acd72de5bf532b6fa6` |
| `src/vtc_ctrl.h` | VTC 寄存器偏移/位域/结构 + 依据注释 | `68d1555cd3a78aff5d206a90229c1184cdd096b3c00f09b441ecb42c24162458` |
| `src/s5_timebase.h/.c` | 全局定时器 64 位读取、宏括号坑的编译期断言 | `3a2e9c8e3da8b4f6c2ea72755d5b428d241788d5da18d15e4b688072d469d64a` / `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/s5_font8x16.h` | 自带 8×16 ASCII 点阵字库（95 字符 ×16 B，自动生成） | `2f26b78b1098b974c60ee2a1d173107c5b44ef8f8f19dbdc4b599ef93a2d50d3` |
| `tools/gen_font8x16.py` | 字库生成器（DejaVu Sans Mono 11 px 栅格化，可复现） | `b9c5a583435d7120f76ae36b17df4a761f347cd1983866fefc66a0b2e3c04b87` |
| `tools/host_render_test.c` | 主机端离线渲染自检（同一份绘图源码） | `aef11ef370ffd2e4000020eb7ef1b47e63d87536d4756240d7c99f1fde5fc00e` |
| `tools/vtc_vdma_selftest.c` | 假寄存器堆离线自检：VTC 校验 + 负例 + VDMA 双缓冲决策 | `3b5c7c1fdeac00d4c1b5c91bde7d29faf5551bf9a22aff72dc1372b3e2e412b7` |
| `tools/host_xil_shim/xil_io.h` | 主机自检用 `Xil_In32/Xil_Out32` 替身声明（不进 ARM 构建） | `1844e41d2b61f00af0a278d7d7147bdaca605318e24bf7e65155cc40f566e263` |
| `build_s5_display_app.py` | 一键构建 + 三方自检 + 证据记录 | `e446e267e8c690feb0c7da5c20676fa83551f03586f184291a32bb157ce4258f` |
| `build/` | ELF、map、build_record.json、构建日志、`selftest_vtc_vdma.txt`、10 张 PNG | — |

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

---

## 3. 帧缓冲与画布布局

### 3.1 冻结地址与尺寸

| 项 | 值 | 计算 |
|---|---|---|
| 画布 | 1280×720，32-bit/像素，`0x00RRGGBB` | — |
| 单帧字节 | **3,686,400 B = 0x384000** | 1280×720×4 |
| 缓冲 A | `0x13000000` | 冻结 |
| 缓冲 B | `0x13384000` | A + 0x384000 |
| B 结束 | `0x13708000` | — |
| 链接脚本内存区 | `0x00100000..0x01100000`（app）、`0x10000000..0x12000000`（r13 tensor） | 帧缓冲在两区之外，用绝对地址访问，链接器不分配 |

实测 ELF 内存布局（`arm-none-eabi-nm`）：`__bss_start=0x0010C010`、`__bss_end=0x00239030`、`_heap_end=0x00339030`、`_stack=0x00349030`、`end=0x0034A830` —— 全部低于 `0x01100000`（链接脚本 `ASSERT(app budget)` 通过），与 `0x13000000` 帧缓冲无重叠。

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

## 6. 未验证项与风险

### 6.1 高风险（阻断上板联调）

1. **帧存个数已按 2 对齐，但 BD 侧改动未由本卡核验**：lead 2026-10-30 已把 BD 的 `c_num_fstores` 改为 2，本 SW 只编程 A/B 两个地址（`0x5C/0x60`），与 BD 一致。若实际硬件仍是 3（BD 未重新生成/未综合），第 3 个帧存会读地址寄存器复位值（0）→ 周期性花屏。
   - 本 SW 的防护：init 读回 `0x18`，不等于 2（且非 0）时打印 `WARN FRMSTORE readback != 2`；`0x18` 本身是否可读取决于 IP 调试参数，读回 0 时只记录、不据此决策。
   - 上板第一步：确认 `c_num_fstores=2` 的新 BD 已生效（读回 / 看综合报告参数），再观察帧序列。
2. **未上板**：VDMA 实际搬数、`vid_out` 的 `tready` 反压、VTC 实际时序输出、rgb2dvi/TMDS、DDR 带宽全部未验证。本 ELF 只证明“能编译链接 + 寄存器序列逻辑正确（假寄存器堆自检）+ 图形逻辑正确”。
3. **VTC 已实现但只验证到寄存器层**：`vtc_ctrl.c` 按 720p60 写生成器并在写后逐寄存器回读（12/12 OK，负例可检出 MISMATCH）。**未验证**：真实 VTC 输出时序（HS/VS/DE/极性）、`v_axi4s_vid_out` 是否 `locked`、`rgb2dvi`/TMDS 是否出图。若上板无图，排查顺序：`vid_out` locked 位 → VTC 极性 → VDMA 是否在跑（SR/CR）→ 帧缓冲内容（JTAG 看 0x13000000）。
4. **缓存一致性**：帧缓冲 3.7 MB ≫ 32 KB D-cache。`main()` 每帧调用 `Xil_DCacheFlushRange()`（`S5_DCACHE_FLUSH=1`）。若 bring-up 时 D-cache 关闭，可置 0；若开启，必须保证 0x13000000 区按 write-back 正常维护，且 flush 的耗时（~115k cache line）计入帧预算。

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
| 编译 app / vdma / vtc / timebase | 0 / 0 / 0 / 0 |
| 链接 | **0** |
| size / nm | 0 / 0 |
| 主机渲染自检（两套布局） | 0 / 0（PASS，各 5 张 PNG） |
| VTC/VDMA 寄存器序列自检 | **0**（PASS，见 §8.2） |

产物：`build/s5_display_app.elf`（**268,184 B，sha256 `9fdec1d9...` 见 §0**）、`build/s5_display_app.map`、`build/build_record.json`（输入/输出哈希、命令、退出码、限制项、自检结果）、`build/selftest_vtc_vdma.txt`、`build/host_render_test*.exe`、`build/*.png`。

### 7.3 符号检查（防止“链接成功但内容被 gc 掉”）

断言 ELF 中存在：`main`、`S5Draw_Text`、`S5Draw_CameraLetterbox`、`S5Vdma_Init`、`S5Vdma_Start`、`S5Vdma_WaitNotReading`、`S5Vtc_Init`、`S5Ticks_Now` —— **missing = []**。
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
VDMA: CR=0x00000003 SR=0x00000002 HSIZE=5120 VSIZE=720 STRIDE=5120
VDMA: store0=0x13000000 store1=0x13384000
frame 0: VDMA reads B(0x13384000) -> draw into A(0x13000000) wait=ok PASS
frame 1: VDMA reads A(0x13000000) -> draw into B(0x13384000) wait=ok PASS
frame 2: VDMA reads B(0x13384000) -> draw into A(0x13000000) wait=ok PASS
frame 3: VDMA reads A(0x13000000) -> draw into B(0x13384000) wait=ok PASS
frame 4: VDMA reads B(0x13384000) -> draw into A(0x13000000) wait=ok PASS
frame 5: VDMA reads A(0x13000000) -> draw into B(0x13384000) wait=ok PASS
==== selftest: PASS ====
```
解读：`CR=0x3` = RUNSTOP|TAIL_EN；`SR=0x2` = IDLE（已启动、无错误位）；
每帧都选“当前不被读”的缓冲写入并 `wait=ok`，6/6 帧无冲突 → 乒乓逻辑正确。
**注意**：这是假硬件的逻辑验证，`READSTR` 的真实行为仍是联调第一优先（§6.2-5）。

---

## 9. 接真实推理结果的接线点（替换清单）

全部替换集中在 `src/s5_display_app.c` 的 `S5Sim_NextFrame()`，**绘图侧一行都不用改**：

| `S5FrameInfo` 字段 | 现模拟源 | 真实来源 |
|---|---|---|
| `frame_id` | 自增 | PL 采集帧计数（与 VDMA/CSR 同一帧号） |
| `fps_cap_x10` | 模型值 29.7~30.0 | 采集中断里计数，1 s 滑动窗口 ×10 |
| `fps_inf_x10` | 模型值 27.5~28.0 | 推理完成计数，1 s 窗口 ×10 |
| `fps_dis_x10` | 模型值 59.8~60.0 | 显示帧提交计数（或 VTC 帧率） |
| `latency_ms` | 17 ms + 抖动 | `S5Ticks_ToMs(t_display_start − t_infer_done)` |
| `age_ms` | 30 ms + 抖动（每 47 帧注入 41 ms） | `S5Ticks_ToMs(t_display_start − t_capture_end)` |
| `det[]` | 1~3 个移动框 | 解码/NMS 输出，**保持摄像头 640×480 原始坐标**（框映射在 `S5Draw_Boxes` 里做） |
| `status` | `CAM_OK|INF_OK|AGE_OVER` | 各子系统状态位（`S5_ST_*`） |

三个时间戳都用同一时间基座（`S5Ticks_Now()`，0xF8F00200，~3 ns 分辨率），测量口径与 G0 一致。

---

## 10. 待办（按优先级）

1. ~~裁决 §3.2 布局~~ —— **已完成**：默认 L0（无黑边、无重叠），L1 仅作实验分支。
2. ~~补 VTC 编程~~ —— **已完成（离线）**：`vtc_ctrl.c` 720p60 + 回读校验 + 负例；上板仍需验证实际时序输出。
3. ~~确认 `c_num_fstores`~~ —— **已按 2 实现**（与 BD 对齐）；上板读回 0x18 复核一次。
4. **上板联调（最高优先）**：①`PARKPTR.READSTR` 在 circular 模式是否随帧更新（决定写侧同步是否可用）；②`vid_out` locked；③VDMA 启动/状态与 SR 错误位；④撕裂观察；⑤DDR 带宽与帧耗时（GT 打点）；⑥rgb2dvi/TMDS 出图。
5. 接真实推理输出，替换 `S5Sim_NextFrame`；把延迟/年龄换成真实时间戳（口径不变）。
6. 性能优化（如需 60 fps）：面板局部重绘、按行 flush、必要时把画布改成 RGB565 减半带宽（会改冻结格式，需批准）。
7. 类别名/颜色表（`s5_class_name`/`s5_class_color`）等阶段5 类别定义冻结后替换。
6. 性能优化（如需 60 fps）：面板局部重绘、按行 flush、必要时把画布改成 RGB565 减半带宽（会改冻结格式，需批准）。