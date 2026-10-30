# 阶段5 显示 ABI 与帧缓冲布局（2026-10-30 r01）

- 目的：把 **阶段5（HDMI 显示链）** 的显示接口契约（ABI）固化到可被 PS 软件、BD、验收三方共同引用的一份文档：帧缓冲布局、VTC/VDMA 寄存器表、坐标映射、地址总表增补、待核对项。
- 编号澄清：**HDMI 显示链 = 阶段5**；P2d 合并计算体属**阶段3/4 集成**（不是阶段5）。本文所有措辞按此。
- 性质：**离线文档**。未碰板卡/JTAG/COM4/hw_server，未运行 Vivado/Vitis 编译，未改 `w4` 源码或历史证据目录，未 git。
- 边界：本文不构成 G3/G4/G5，不构成"显示链已通过"；所有"上板行为"一律标未验证。
- 唯一写区：本文件（`D:\FPGA_Competition\docs\obsidian-project\02-方案设计\`）+ 证据目录 `D:\codex-worktrees\w4\report\evidence\S5-T01\s5_abi_layout_20261030_r01\`。

---

## 0. 证据基线（每条结论都挂来源）

| 编号 | 来源 | 用途 |
|---|---|---|
| B1 | `docs/obsidian-project/02-方案设计/阶段5_HDMI显示链G0方案_20261030.md`（G0，2026-10-30 冻结） | 范围/地址/时钟/端口/测量口径的**冻结依据** |
| B2 | `w4/report/evidence/S5-T01/s5_p3a_video_bd_20261030_r01/P3A_BD_REPORT.md` + `bd_p3a.tcl` + `bd_p3a.bd` | 视频通路 BD 的**实测参数与地址**（validate 0 ERROR） |
| B3 | `w4/report/evidence/S5-T01/s5_p3b_sw_20261030_r01/S5_P3B_SW_REPORT.md` | PS 侧显示软件实现事实（ELF 构建、寄存器序列自检、布局裁决） |
| B4 | `D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_8\src\xvtc_hw.h` / `xvtc.c` | **VTC 寄存器偏移/位域/写序列的权威依据**（本机 Vitis 2026.1） |
| B5 | `D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\xaxivdma_hw.h` / `xaxivdma.c` / `xaxivdma_channel.c` | **VDMA 寄存器偏移/位域的权威依据**（本机 Vitis 2026.1） |
| B6 | `w4/docs/stage4/S4B_stage4_address_map.json` | 既有地址图（用于**一致性核对**，不作为本阶段写权对象） |
| B7 | `report/evidence/CTRL-DSH-HANDOFF/decisions/stage4_raw_address_d1_optionA_20261027_r01.md` | DDR 尾部禁区 `[0x12C08000,0x20000000)` 的裁决来源 |
| B8 | `w4/report/evidence/S4-T34/s4d_p2d_stage5_close_20261029_r01/ADDRESS_MAP.md` | P2d（阶段3/4 集成）地址与数据通路事实（**历史目录，只读不改**） |

> 本机**没有** PG020（AXI VDMA）与 PG016（VTC）PDF。凡只能由 IP 手册而不能由驱动源码确定的点，一律写 **"待核对 pgxxx 表 x"**，不猜。见 §9。

---

## 1. 显示 ABI 总览

### 1.1 角色与数据流

```
PS 应用（Cortex-A9）
  │ ① 渲染整帧到 DDR 帧缓冲（32-bit/像素，0x00RRGGBB）
  │ ② Xil_DCacheFlushRange(帧缓冲整帧)
  │ ③ 乒乓选择：写"VDMA 当前不在读"的那一块
  ▼
DDR: FB_A 0x13000000 / FB_B 0x13384000（各 3,686,400 B）
  │ ④ VDMA MM2S（非 SG，circular，2 帧存）按像素时钟连续读
  ▼
AXI VDMA ──AXI4-Stream 32-bit──> v_axi4s_vid_out(4.0, RGBA 格式) ──vid_data[23:0]──> rgb2dvi ──TMDS──> HDMI
  ▲
  └── VTC(6.2) 720p60 提供 HS/VS/DE 时序（vidout 为 slave，vg_ce 由 VTC 给）
```

### 1.2 ABI 三要素（本文件冻结的接口面）

| 要素 | 契约 | 章节 |
|---|---|---|
| 帧缓冲布局 | `0x13000000` 起、A/B 双缓冲、stride 5120 B、帧 3,686,400 B、32-bit/像素 | §2 |
| 控制面寄存器 | VTC `0x43C30000`、VDMA `0x43C40000` 的偏移/位域/写序列 | §3、§4 |
| 坐标/排版 | 640×480 → 960×720 映射、取整规则、信息栏排版、颜色与线宽 | §5 |

### 1.3 关键几何与时钟（冻结值 + 算术核对）

| 项 | 值 | 核对 |
|---|---|---|
| 分辨率/刷新 | 1280×720p60 | G0 §10 决策 D1 |
| 像素时钟 | **74.21875 MHz** | VCO = 100 ÷ 8 × 59.375 = 742.1875 MHz；÷10 = 74.21875（B2 §2.2；B2 `bd_p3a.tcl:144-146`） |
| 串行时钟（预留） | 371.09375 MHz = 5 × 74.21875 | B2 §2.2 |
| 行频 | 74,218,750 ÷ 1650 = **44,981.06 Hz** | 算术 |
| 场频 | 74,218,750 ÷ (1650×750) = **59.9747 Hz** | 算术；相对 60 Hz 偏差 −0.042% |
| FCLK0 | 50 MHz（控制面 + P2d 全部逻辑 + VDMA 的 lite/mm 时钟） | B2 §2.1 |
| FCLK1 | 100 MHz（仅作 clk_wiz 参考） | B2 §2.1 |
| 像素字格式 | 32-bit 小端 `0x00RRGGBB`；AXIS 字节序 B/G/R/A；`vid_data[23:0]={R,G,B}`，alpha 丢弃 | B2 §5.3；B3 §3.1 |

---

## 2. 显示帧缓冲规范

### 2.1 地址与尺寸

| 项 | 值 | 说明 |
|---|---|---|
| 画布 | 1280 × 720，32-bit/像素 | G0 §10 D1/D4 |
| 单帧字节 | **3,686,400 B = 0x384000** | 1280×720×4 |
| stride（行字节） | **5,120 B = 0x1400** | 1280×4；= 80 × 64 B ⇒ 64 B 对齐 |
| 缓冲 A | **`0x13000000`** | 1 MiB 对齐 |
| 缓冲 B | **`0x13384000`** | = A + 0x384000 |
| B 结束（开区间上界） | `0x13708000` | 双缓冲总 7,372,800 B = 0x708000 |
| 缓冲数量 | **2**（乒乓） | 任务冻结；**硬件侧见 T-01** |

**对齐结论（可复算）**：帧长 0x384000 = 3,686,400 = **900 × 4096** ⇒ 4 KiB 页对齐；stride 5120 = **80 × 64** ⇒ 64 B（cache line）对齐；基址 0x13000000 与 0x13384000 均 4 KiB 对齐。⇒ 任意帧首均落在 4 KiB 边界，任意行首均落在 64 B 边界，**不产生跨 cache line 的部分行写**。

### 2.2 所有权与乒乓规则（写入方 = PS，读取方 = VDMA）

| 规则 | 内容 | 依据 |
|---|---|---|
| R1 | 同一时刻**只有一块**被 VDMA 读；PS 必须写另一块 | B3 §3.2/§8.2 乒乓决策 |
| R2 | 切换判据：读 `PARKPTR(0x28).READSTR`（bit[20:16]），写入 `READSTR` 指向之外的缓冲 | B3 §2.2；见 **T-02** |
| R3 | 读指针不由 PS 主动切换（不写 `CR.RD_PTR`）；VDMA 在 circular 模式自行轮转 | B2 `bd_p3a.tcl:184-191`（`c_use_fsync=0`、非 SG）；B3 §6.3-10（未实现 RD_PTR 切换） |
| R4 | 若 100 ms 内未取得安全窗口：置 `S5_ST_TEAR` 状态位并在信息栏显示，**不静默写** | B3 §6.2-5 |
| R5 | 帧缓冲**不参与链接器分配**：用绝对地址访问，链接脚本不声明该区 | B3 §3.1 |
| R6 | 帧缓冲不得与 app / tensor / raw 区重叠 | §7 一致性核对 |

> **ABI 语义**：VDMA 是"自由跑"（无 fsync、无 SG）的连续读者。因此 ABI 的正确性完全依赖 R2/R4；R2 的硬件行为是本阶段**第一优先待核对项**（T-02）。在 T-02 关闭前，本 ABI 的乒乓语义只能算"设计意图"，不算"已验证契约"。

### 2.3 写入方式：D-cache write-back + `Xil_DCacheFlushRange`（选用），非"非缓存映射"

**选择**：帧缓冲按 **cacheable（write-back）** 映射，PS 渲染完成后对**整帧范围**调用 `Xil_DCacheFlushRange((UINTPTR)fb, 3,686,400)` 再交给 VDMA。

**理由**：
1. **性能**：整帧 3.7 MB ≫ 32 KB D-cache。渲染是逐像素写（约 92 万次写/帧）。若非缓存映射，每次写都是总线事务，Cortex-A9 上会慢一个数量级；cacheable + 一次 flush 把 ~92 万次写合并成约 11.5 万条 cache line 回写（3,686,400 ÷ 32 = **115,200 条**）。
2. **一致性正确性**：VDMA 经 PS 的 HP 口读 DDR，**不经 CPU cache**；只有 flush 后 VDMA 才看得到新内容。
3. **可维护性**：非缓存映射需要改 MMU 页表/`Xil_SetTlbAttributes` 对 3.7 MB 区间逐段设置，出错面更大，且与阶段4 既有的 cache 维护惯例（flush/invalidate 周边）不一致。

**风险与约束（必须写进实现）**：
| # | 风险 | 约束/缓解 |
|---|---|---|
| C1 | flush 时机错 ⇒ VDMA 读到旧帧（撕裂/滞后一帧） | flush 必须在"渲染完成"与"该缓冲被允许读"之间完成，且顺序不能与 R2 选择颠反 |
| C2 | flush 耗时未测 | 115,200 条 line；B3 §6.1-4 已标注"未测"，需上板用 GT 打点，**计入帧预算** |
| C3 | D-cache 若被关闭，flush 变成空操作 | 目标 BSP 的 SCTLR.C 必须显式断言；见 **T-05** |
| C4 | flush 粒度为 32 B，帧长是 32 的整数倍（3,686,400/32 = 115,200）⇒ 无尾部部分行 | 算术已核 |
| C5 | 只 flush 脏行属后续优化 | 优化会改变本 ABI 的"整帧 flush"语义 ⇒ 属 ABI 变更，需重新评审（B3 §10-6） |

### 2.4 VDMA 读侧假设（ABI 的另一半）

| # | 假设 | 依据/状态 |
|---|---|---|
| A1 | VDMA `HSIZE = 5120`（字节/行）、`STRIDE = 5120`、`VSIZE = 720` | B3 §2.2；单位见 **T-03** |
| A2 | 帧存 0 = A、帧存 1 = B，只编程 `0x5C`/`0x60` 两个地址 | B3 §2.2；数量见 **T-01** |
| A3 | MM 侧 64-bit @50 MHz，流侧 32-bit @74.21875 MHz ⇒ IP 自动 ASYNC 模式 | B2 §5.2 |
| A4 | 带宽：读需求 74.21875 Mpx/s × 4 B = **296.875 MB/s**；HP2 峰值 64 bit × 50 MHz = **400 MB/s** ⇒ 占用 **74.2%** | B2 §9-4；余量偏小，underflow 风险见 **T-08** |
| A5 | VDMA 不改写 DDR（只读） | 只开 MM2S（B2 `bd_p3a.tcl:185-186`） |
| A6 | 帧缓冲内**无 padding/无 tile**，纯行优先线性布局 | A1 的 stride == HSIZE 即隐含此假设 |

---

## 3. VTC 寄存器表（`v_tc` 6.2 @ `0x43C30000`）

### 3.1 偏移表（依据 B4 `xvtc_hw.h`，逐行标注）

| 偏移 | 名称 | 访问 | 依据（文件:行） |
|---|---|---|---|
| `0x000` | `CTL` | RW | `xvtc_hw.h:150` |
| `0x004` | `ISR` | RW1C | `xvtc_hw.h:151` |
| `0x00C` | `IER` | RW | `xvtc_hw.h:154` |
| `0x010` | `VER` | RO | `xvtc_hw.h:156` |
| `0x060` | `GASIZE` | RW | `xvtc_hw.h:186` |
| `0x068` | `GFENC` | RW | `xvtc_hw.h:188` |
| `0x06C` | `GPOL` | RW | `xvtc_hw.h:189` |
| `0x070` | `GHSIZE` | RW | `xvtc_hw.h:190` |
| `0x074` | `GVSIZE` | RW | `xvtc_hw.h:192` |
| `0x078` | `GHSYNC` | RW | `xvtc_hw.h:194` |
| `0x07C` | `GVBHOFF` | RW | `xvtc_hw.h:197` |
| `0x080` | `GVSYNC` | RW | `xvtc_hw.h:199` |
| `0x084` | `GVSHOFF` | RW | `xvtc_hw.h:201` |
| `0x08C` | `GVSYNC_F1` | RW | `xvtc_hw.h:206` |
| `0x094` | `GASIZE_F1` | RW | `xvtc_hw.h:210` |

位域（依据 B4 `xvtc_hw.h`）：

| 位域 | 掩码/位移 | 依据（文件:行） |
|---|---|---|
| `CTL.SW`（核使能） | `0x00000001` | `xvtc_hw.h:308` |
| `CTL.RU`（寄存器更新） | `0x00000002` | `xvtc_hw.h:307` |
| `CTL.GE`（生成器使能） | `0x00000004` | `xvtc_hw.h:306` |
| `CTL.RESET`（写 1 复位，自清） | `0x80000000` | `xvtc_hw.h:253` |
| `GFENC.ENC_PROG`（0=逐行） | `0x00000040` | `xvtc_hw.h:449`（shift 6 @451） |
| `GASIZE.ASIZE_VERT` 位移 | `<<16` | `xvtc_hw.h:420` |
| `GVSIZE.VSIZE_F1` 位移 | `<<16` | `xvtc_hw.h:485` |
| sync/blank 字段编码 | `SB_START=0x3FFF` / `SB_END=0x3FFF0000` | `xvtc_hw.h:500` / `:495` |
| 极性命：HSP/VSP/AVP/HBP/VBP | `0x08/0x04/0x10/0x02/0x01`；全正 `0x7F` | `xvtc_hw.h:466/468/464/470/472/474` |

### 3.2 720p60 生成参数（几何 ↔ 寄存器编码）

几何（G0 冻结；B2 §5.1 核对一致）：

| 方向 | active | front porch | sync | back porch | total |
|---|---|---|---|---|---|
| 水平 | 1280（0..1279） | 110（1280..1389） | **40**（1390..1429） | 220（1430..1649） | **1650** |
| 垂直 | 720（0..719） | 5 | **5** | 20 | **750** |

寄存器值（B2 `bd_p3a.tcl:161-176` 的 IP 参数 + B3 §2.4 实测回读，两者一致）：

| 寄存器 | 偏移 | 值 | 依据 |
|---|---|---|---|
| `GHSIZE` = 1650 | `0x070` | `0x00000672` | `bd_p3a.tcl:162`；B3 §2.4 |
| `GVSIZE` = {750,750} | `0x074` | `0x02EE02EE` | `bd_p3a.tcl:166,169` |
| `GASIZE` = {720,1280} | `0x060` | `0x02D00500` | `bd_p3a.tcl:161,165` |
| `GASIZE_F1` = {0,720} | `0x094` | `0x02D00000` | `bd_p3a.tcl:165`（F1 vactive 同 720） |
| `GHSYNC` = {1430,1390} | `0x078` | `0x0596056E` | `bd_p3a.tcl:163-164` |
| `GVSYNC` = {729,724} | `0x080` | `0x02D902D4` | `bd_p3a.tcl:167-168` |
| `GVSYNC_F1` = {729,724} | `0x08C` | `0x02D902D4` | `bd_p3a.tcl:170-171` |
| `GVBHOFF` = {1280,1280} | `0x07C` | `0x05000500` | `bd_p3a.tcl:175`（HBlank 极性 High）+ B3 §2.4 |
| `GVSHOFF` = {1390,1390} | `0x084` | `0x056E056E` | 同上 |
| `GPOL` = 全正 | `0x06C` | `0x0000003F` | `bd_p3a.tcl:172-176` |
| `GFENC` = 逐行/RGB | `0x068` | `0x00000000` | `bd_p3a.tcl:158-160` |
| `CTL` = SW\|GE | `0x000` | `0x00000005` | B3 §2.4 |

**同步寄存器编码公式（有据，不是笔误）**：B4 `xvtc.c:1358` 水平 `GHSYNC = HSyncStart + HActive`；B4 `xvtc.c:1366` 垂直 `GVSYNC = V0SyncStart + VActive − 1`。
⇒ 几何的 "725..730" 在**本 IP 的寄存器编码**里就是 **724..729**（与 P3a BD 预设一致）。若上板实测场同步差 1 行，回退写 725..730（B3 §2.4 备注的 `S5_VTC_VSYNC_USE_IP_PRESET=0` 分支）。

### 3.3 初始化写序列（依据 B4 `xvtc.c` 的 `XVtc_SetGenerator` / `XVtc_Reset` / `XVtc_Enable*`）

`读 VER 判活 → CTL.RESET=1 并轮询自清（10 ms 超时）→ 写 GHSIZE/GVSIZE/GASIZE/GASIZE_F1/GHSYNC/GVSYNC/GVSYNC_F1/GFENC/GPOL/GVBHOFF/GVSHOFF（11 个）→ CTL |= SW|GE → 逐寄存器回读校验`

- 回读校验失败必须**返回错误并打印**（B3 §2.4：返回码 −3），不得静默继续。
- `HAS_INTC_IF=false`（B2 `bd_p3a.tcl:155`）⇒ 本阶段**不用 VTC 中断**，帧事件只能靠软件轮询/VDMA 中断。

---

## 4. VDMA MM2S 寄存器表（`axi_vdma` 6.3 @ `0x43C40000`）

### 4.1 频道基址与偏移（依据 B5，逐行标注）

B5 `xaxivdma_hw.h:109-110`：`TX_OFFSET = 0x00`（MM2S/读通道）、`RX_OFFSET = 0x30`（S2MM/写通道）。
本次**只开 MM2S**（B2 `bd_p3a.tcl:185-186`：`c_include_mm2s=1`、`c_include_s2mm=0`）。⇒ **任务卡里"MM2S_VDMACR 在 0x00"正确；0x30/0x34 属 S2MM，本设计不存在**。

| 绝对偏移 | 名称 | 依据（文件:行） | 备注 |
|---|---|---|---|
| `0x00` | `MM2S_VDMACR` | `xaxivdma_hw.h:118`（`CR_OFFSET`）+ `:109`（TX base） | 见 §4.2 位域 |
| `0x04` | `MM2S_VDMASR` | `xaxivdma_hw.h:119` | 见 §4.2 |
| `0x08` | `MM2S_CURDESC` | `xaxivdma_hw.h:120` | **SG 专用，本设计不写** |
| `0x10` | `MM2S_TAILDESC` | `xaxivdma_hw.h:121` | **SG 专用，本设计不写** |
| `0x14` | `HI_FRMBUF`（32 帧存选择） | `xaxivdma_hw.h:122` | 2 帧存用不到 |
| `0x18` | `MM2S_FRMSTORE` | `xaxivdma_hw.h:123` | **只读回记录，不写**（调试参数门控，见 T-04） |
| `0x1C` | `BUFTHRES`（行缓冲阈值） | `xaxivdma_hw.h:124` | 本设计用默认 |
| `0x28` | `PARKPTR` | `xaxivdma_hw.h:111` | `READSTR` mask `0x001F0000`（`:231`） |
| `0x2C` | `VERSION` | `xaxivdma_hw.h:112` | 判活；读回 `0x60300000`（B3 §8.2） |
| **`0x50`** | **`MM2S_VSIZE`** | `MM2S_ADDR_OFFSET=0x50`（`:125`）+ `VSIZE_OFFSET=0x00`（`:141`） | **写它 = 启动**（见 §4.3） |
| **`0x54`** | **`MM2S_HSIZE`** | `:125` + `HSIZE_OFFSET=0x04`（`:142`） | 每行字节数（单位见 T-03） |
| **`0x58`** | **`MM2S_STRD_FRMDLY`** | `:125` + `STRD_FRMDLY_OFFSET=0x08`（`:143`） | `(FRMDLY<<24)|STRIDE` |
| **`0x5C + 4i`** | **`MM2S_START_ADDR[i]`** | `:125` + `START_ADDR_OFFSET=0x0C`（`:144`）+ `START_ADDR_LEN=4`（`:145`） | i = 0,1（2 帧存）⇒ `0x5C`/`0x60` |

**"0x50 起"的推导链（可复核，避免把 TX base 与 addr-array base 混淆）**：
`xaxivdma.c:166-167` 定义 `RdChannel->StartAddrBase = BaseAddr + XAXIVDMA_MM2S_ADDR_OFFSET(0x50)`；
`xaxivdma_channel.c:828-829` 写 `HSIZE` 于 `StartAddrBase + 0x04`；`:831-834` 写 `STRD_FRMDLY` 于 `+0x08`；`:1018-1019` 写 `VSIZE` 于 `+0x00`；`:925-928` 写帧存地址于 `StartAddrBase + 0x0C + 4i`。
⇒ 绝对地址 `0x50/0x54/0x58/0x5C…` 与 B3 §2.2 的表**逐项一致**。

### 4.2 位域

| 位域 | 值 | 依据（文件:行） |
|---|---|---|
| `CR.RUNSTOP` | `0x00000001` | `xaxivdma_hw.h:153` |
| `CR.TAIL_EN`（直连模式下使能 circular） | `0x00000002` | `xaxivdma_hw.h:154` |
| `CR.RESET`（写 1 复位，自清） | `0x00000004` | `xaxivdma_hw.h:155` |
| `CR.FRMCNT_EN` | `0x00000010` | `xaxivdma_hw.h:157` |
| `CR.RD_PTR`（读指针选择） | mask `0x00000F00`，shift 8 | `xaxivdma_hw.h:160` / `:164` |
| `SR.HALTED` | `0x00000001` | `xaxivdma_hw.h:172` |
| `SR.IDLE` | `0x00000002` | `xaxivdma_hw.h:173` |
| `VSIZE` mask | `0x00001FFF` | `xaxivdma_hw.h:276` |
| `HSIZE` mask | `0x0000FFFF` | `xaxivdma_hw.h:277` |
| `STRIDE` mask | `0x0000FFFF` | `xaxivdma_hw.h:278` |
| `FRMDLY` mask / shift | `0x0F000000` / `<<24` | `xaxivdma_hw.h:279` / `:281` |

### 4.3 初始化与启动序列（ABI 规定，依据 B5 源码）

```
① 读 VERSION(0x2C) 判活（期望 0x60300000，major.minor.rev）
② CR(0x00).RESET=1 → 轮询自清（5 ms 超时）
③ 写 START_ADDR0(0x5C)=FB_A=0x13000000、START_ADDR1(0x60)=FB_B=0x13384000
④ 写 HSIZE(0x54)=5120、STRD_FRMDLY(0x58)=0x00001400（FRMDLY=0, STRIDE=5120）
⑤ 读回 0x18 FRMSTORE 仅记录（不据此决策）
⑥ CR = RUNSTOP | TAIL_EN = 0x00000003
⑦ 写 VSIZE(0x50) = 720  ← **直连模式下的启动动作**
⑧ 轮询 SR.HALTED(0x04 bit0) 清零
```

依据：B5 `xaxivdma_channel.c:1014-1019` 源码注释原文 *"Direct register mode: Update vsize to start the channel"*；`XAxiVdma_ChannelSetBufferAddr`（`:862-935`）；`XAxiVdma_SetFrmStore` 的调试位门控（B3 §2.1-2）。
⇒ **ABI 硬约束：`VSIZE` 不是"配置寄存器"而是"启动触发"**。任何"先写 VSIZE 再改地址/STRIDE"的实现都是错的。

### 4.4 生效值（P3b 实测自检；假寄存器堆为离线证据，非上板）

`CR=0x00000003`、`SR=0x00000002`（IDLE）、`HSIZE=5120`、`VSIZE=720`、`STRIDE=5120`、`store0=0x13000000`、`store1=0x13384000`（B3 §8.2）。**这是逻辑验证，不证明硬件行为**（B3 §8.2 结尾已声明）。

---

## 5. 坐标映射与信息栏排版规范

### 5.1 画布分区（G0 后续裁决：**无黑边**）

| 区 | 范围 | 内容 |
|---|---|---|
| 视频区 | `x = 0..959`（960 宽）、`y = 0..719` | 640×480 放大 3/2 后的完整画面 |
| 信息栏 | `x = 960..1279`（320 宽）、`y = 0..719` | 帧号/FPS/延迟/年龄/状态/逐框明细 |
| 分割线 | `x = 960..961`（2 px） | 面板左侧高亮分隔线 |

**不变形理由（算术）**：640×480 = 4:3；960×720 = 4:3；两轴缩放比同为 **3/2 = 1.5** ⇒ 无各向异性畸变。
**与 G0 原文的冲突**：G0 §10.1（B1 L131）仍写"960×720 居中、左右各 160 px 黑边"。2026-10-30 后续裁决（B3 §3.2）以"160+960+320=1440 > 1280 不可能同时成立"为由改为**无黑边**。本 ABI 取**无黑边**；G0 文档未回写（本卡不改），见 T-07。

### 5.2 检测框映射（640×480 原图 → 960×720 显示坐标）

**输入**：解码/NMS 输出的框 `(x, y, w, h)`，**保持摄像头 640×480 原始坐标**，不在上游预缩放（B3 §9）。
**输出**：视频区局部坐标 → 画布坐标（视频区起点 x=0，故局部即画布 x）。

**规则（边界映射，不是"起点+宽度"）**：

```
X0 = (x   * 3) / 2        Y0 = (y   * 3) / 2          # 整除，向下取整
X1 = ((x + w) * 3) / 2    Y1 = ((y + h) * 3) / 2      # 整除，向下取整
框宽 = max(1, X1 - X0)    框高 = max(1, Y1 - Y0)
```

**为什么必须这样写**：若先算 `X0` 与 `w' = (w*3)/2` 再相加，右边界会分别截断两次，误差可累积到 2 px，违反"≤1 px"判据。按两个**真实边界**各截断一次时，`|X0 − y·1.5| < 1`、`|X1 − (x+w)·1.5| < 1`，故**每条边的绝对误差 < 1 px**，宽度误差 < 1 px（取整同向时严格 ≤1 px）。

**绘制**：线宽 `2 px`（上/下边各 2 行、左/右边各 2 列；B3 §4.3）；矩形裁剪在像素写函数内完成（越界不写）。
**标签**：`"<类别> <整数分数>"`，黑底彩字，画在框上方；顶部空间不足时改画框内（B3 §4.3）。
**分数语义**：按**整数分数**显示，**不得称"置信度"**（G0 §10.1 明令）。
**类别**：`C0..C4` 与类别色为**占位**，等类别定义冻结后只改两张表（B3 §4.3/§6.2-8）⇒ ABI 层面只承诺"5 类 + 颜色 5 元组"，不承诺具体名字。

### 5.3 信息栏排版

| 项 | 值 | 依据 |
|---|---|---|
| 面板底 | `0x00101820`（深色） | B3 §4.4 |
| 字形 | 8 × 16 点阵 ASCII（0x20..0x7E，95 字符，自带表 `s5_font8x16[95][16]`） | B3 §4.1 |
| 列宽 | **8 px**（字宽 8，墨迹 ≤7 列，右留 1 列防粘连） | B3 §4.1 |
| 行高 | **16 px**（字形高度） | B3 §4.1 |
| 行距 | **20 px**（8×16 字 + 4 px 间隙） | B3 §4.4 |
| 面板左边距 | `x = 960 + 2`（避开 2 px 分隔线）+ 16 px 文本边距 | B3 §4.4 |
| 位序 | `bit7 = 最左列`（经典 VGA 8×16） | B3 §4.1 |
| 字段顺序 | 标题 / FRAME / FPS C·I·D / LAT / AGE / LIM / VDMA / ST / DET / 逐框明细（≤5）/ CLASS 图例 / 版式脚注 | B3 §4.4 |

> 任务卡写"行高 16 px"：本文按**字形高 16 px、行距 20 px**精确化，二者不矛盾。若后续实现改用 16 px 行距，字形会上下相贴，属实现选择变更，需同步改本节。

### 5.4 颜色

| 用途 | 值 | 依据 |
|---|---|---|
| 黑 | `0x000000` | B3 §4.2 |
| 白（文字） | `0xFFFFFF` | B3 §4.4 |
| 面板底 | `0x00101820` | B3 §4.4 |
| AGE 超限 | 转红（告警） | B3 §4.4 |
| VDMA 状态 | 绿 RUN / 黄 OFF / 红 ERR | B3 §4.4 |
| 类别色 | 红/绿/蓝/黄/紫 5 元组（占位） | B3 §4.3 |

---

## 6. 测量口径（G0 冻结）

| 项 | 定义 | 依据 |
|---|---|---|
| `t_capture_end` | 采集帧写入 DDR 完成 | G0 §10.1 |
| `t_infer_done` | 2B 推理完成（`DONE_SAFE`） | G0 §10.1 |
| `t_display_start` | 该结果首次被写入显示缓冲（render 调用点） | G0 §10.1；B3 §5.2 |
| 显示延迟 | `t_display_start − t_infer_done` | G0 §10.1 |
| 结果年龄 | `t_display_start − t_capture_end` | G0 §10.1 |
| 年龄上限 | **≤ 1 帧（47.3 s）+ 1 屏刷新（16.7 ms）= 47,316.7 ms** | G0 §10.1 |
| 坐标误差 | **≤ 1 px**（在 720p 显示坐标系） | G0 §10.1；§5.2 已证 |
| 分数 | 整数分数，**不称置信度** | G0 §10.1 |
| 三口径 FPS | 采集 / 推理 / 显示（×10 定点） | B3 §5.2 |

> **时间基座**：Zynq 全局定时器 `0xF8F00200/0x204`，`hi-lo-hi` 双读；`S5_GT_HZ = 333,333,343`（= 666,666,687/2），不用 BSP 的 `COUNTS_PER_SECOND`（无括号宏，会把 ms 压小 4 倍；B3 §5.1）。
> **重要不一致**：B3 实现里 `S5_ST_AGE_OVER` 的判据是 **> 33 ms**（B3 §4.4 面板 `LIM 33 ms (1f+16.7)`、§6.2），与本 ABI 的 **47,316.7 ms** 差约 1400 倍。本 ABI 以 G0 为准；该不一致列入 **T-06**（需裁决），ABI 层面不改判据。

---

## 7. 地址总表增补（阶段5 显示链）

### 7.1 PL MMIO（`0x40000000–0x7FFFFFFF`）新增行

| 基址 | 范围 | 归属 | 从端 | 相对 P2d | 依据 |
|---|---|---|---|---|---|
| `0x43C00000` | 64 KB | 2B 推理核 CSR | `smc_ctrl/M01` → `infer_0/S_AXI` | 不变（**2B 冻结**） | B2 §3.1；B8 §2 |
| `0x43C10000` | 128 B | preproc v2 CSR | `smc_ctrl/M00` → `s4d_0/S_AXI` | 不变 | B2 §3.1；B8 §2 |
| `0x43C20000` | 64 KB | AXI DMA（打包后写 tensor） | `smc_ctrl/M02` → `axi_dma_0/S_AXI_LITE` | 不变 | B2 §3.1；B8 §2 |
| **`0x43C30000`** | **64 KB** | **VTC（720p60 时序发生器）** | **`smc_ctrl/M03` → `vtc_0/ctrl`** | **新增（阶段5）** | B2 §3.1；B2 `bd_p3a.tcl:349` |
| **`0x43C40000`** | **64 KB** | **AXI VDMA（MM2S 显示读）** | **`smc_ctrl/M04` → `vdma_0/S_AXI_LITE`** | **新增（阶段5）** | B2 §3.1；B2 `bd_p3a.tcl:350` |

**重叠结论**：五段首尾相接（`0x43C00000–0x43C4FFFF`），互不重叠；`smc_ctrl` 由 P2d 的 1S/3M 扩为 **1S/5M**。机器证据：`validate_bd_design` **0 ERROR**（B2 §1；地址重叠会被 validate 直接判 ERROR）。

### 7.2 DDR 新增行（显示帧缓冲）

| 区域 | 基址 | 结束（开区间） | 大小 | 状态 | 依据 |
|---|---|---|---|---|---|
| `display_buffer_a` | `0x13000000` | `0x13384000` | 3,686,400 B | **STAGE5_G0_FROZEN**（待 gap 处理，见 §7.3） | 任务冻结；B3 §3.1 |
| `display_buffer_b` | `0x13384000` | `0x13708000` | 3,686,400 B | 同上 | 同上 |

主端：`vdma_0/M_AXI_MM2S` → `smc_vid`(1S/1M) → **`ps7_0/S_AXI_HP2`**（64-bit，孔径 `0x0`/1 GB）（B2 §3.2/§5.4）。

### 7.3 与既有地址图的一致性核对（**结论：region 无重叠，但有 3 处声明层面的不一致**）

**与 region 的重叠检查（逐对）**：

| 比对对象 | 区间 | 与 `0x13000000–0x13708000` | 结论 |
|---|---|---|---|
| `raw_meta` | `0x12C00000–0x12C08000` | 不相交 | ✅ |
| DDR 尾部禁区（gap） | `0x12C08000–0x20000000` | **被包含** | ❌ 声明冲突（见下 I-1） |
| `feature_envelope` | `0x11000000–0x11ADADB8` | 不相交 | ✅ |
| `network_input_tensor` / `gf8` / `injection_frame_rgb` | ≤ `0x10B00000` | 不相交 | ✅ |
| `ps_app_arena`（阶段4 口径） | `0x00100000–0x01100000` | 不相交 | ✅ |
| app 实际 ELF 载入跨度 | `0x00100000–0x0130AD40` | 不相交 | ✅（相差 0x11CF52C0） |

| # | 不一致 | 事实 | 需要的处置 |
|---|---|---|---|
| **I-1** | 帧缓冲落在**既有禁区**内 | B6 `gaps[]` 有 `[0x12C08000,0x20000000)`，rule="不得访问：专属窗口之外 DDR"（`S4B_stage4_address_map.json` 第 599–610 行）；B7 的 D1 裁决只把 raw_frame/raw_meta 从该禁区中减去 | 按 D1 的**同一先例**（`shrink_note`/`gap_exception` 机制）把该 gap 缩减为 **`[0x12C08000,0x13000000)` + `[0x13708000,0x20000000)`**，并留"缩减量 7,372,800 B"的裁决记录。**该缩减须由 lead/裁决方出具，本文只提出**（算术：原 gap 222,265,344 B − 7,372,800 B = **214,892,544 B**） |
| **I-2** | `display_buffer` 在阶段4 地址图里是"未决" | B6 `unresolved_regions[]` 有 `display_buffer`：`status=UNRESOLVED_DO_NOT_GUESS`、`reason` 明确要求"阶段5 G0 冻结显示语义与缓冲深度"（第 527–544 行） | 阶段5 G0 已冻结（地址/深度/格式/口径）⇒ 该未决项在**本文档层面已可关闭**；B6 的 JSON 属 w4 写权，**本卡不改**，需 w4 写入方按流程把该条目更新为已解析 |
| **I-3** | 阶段4 地址图的 PL MMIO gap 也已过期 | B6 `gaps[]` 的 pl_mmio 段仍是 `[0x43C10000,0x80000000)`（第 621–622 行），而 P2d 的 AXI DMA `0x43C20000` 与阶段5 的 VTC/VDMA 都落在其中 | 一并按 §7.1 更新；属**跨阶段登记补记**，不改变任何地址 |

> **重要**：I-1/I-2/I-3 都**不是**"地址写错"，而是"新阶段占用了旧阶段声明为不可用/未决的区间，需要一次显式登记"。本文把三处都摆出来，不用"看起来不重叠"糊过去。

### 7.4 完整阶段5 PL/DDR 归属速查（一页版）

```
DDR (512 MiB @0x00000000)
  0x00100000–0x01100000   ps_app_arena（阶段4 口径）        [既有]
  0x10000000–0x1007EC00   network_input_tensor（2B 冻结）   [FROZEN]
  0x10100000–0x106A12FC   gf8_weight_package（2B 冻结）     [FROZEN]
  0x10700000–0x10B00000   injection_frame_rgb               [阶段4]
  0x11000000–0x11ADADB8   feature_envelope（2B 冻结）       [FROZEN]
  0x12000000–0x12C00000   raw_frame                          [D1=A]
  0x12C00000–0x12C08000   raw_meta                           [D1=A]
  0x13000000–0x13384000   display_buffer_a  ← 阶段5 新增
  0x13384000–0x13708000   display_buffer_b  ← 阶段5 新增
  0x12C08000–0x20000000   禁区（待 I-1 缩减为两段）

PL MMIO (GP0)
  0x43C00000 2B CSR 64K | 0x43C10000 preproc CSR 128B | 0x43C20000 AXI DMA 64K
  0x43C30000 VTC 64K    | 0x43C40000 VDMA 64K          ← 阶段5 新增

HP 端口
  HP0 → 2B 推理核 M_AXI（直连，禁止并 SmartConnect）
  HP1 → smc_data → preproc M_AXI_RD + AXI DMA M_AXI_S2MM
  HP2 → smc_vid  → VDMA M_AXI_MM2S        ← 阶段5 新增
```

---

## 8. 与既有制品的一致性核对汇总

| # | 比对 | 结论 |
|---|---|---|
| K1 | 地址 VTC/VDMA vs G0 §3（B1 L41-43/L124） | **一致**（`0x43C30000` / `0x43C40000`） |
| K2 | 地址 VTC/VDMA vs P3a BD 实测（B2 §3.1） | **一致**（含 `M03`/`M04` 映射与 validate 0 ERROR） |
| K3 | 像素时钟 vs G0 §1 L18（74.25 请求）/B2（74.21875 实际） | **一致且有据**：偏差 −0.042%，G0 §8 容差 ±0.5% |
| K4 | FCLK0/FCLK1 vs G0 §3 L44 | **一致**（50 / 100） |
| K5 | 帧缓冲地址/尺寸 vs B3 §3.1 | **一致**（`0x13000000` / `0x13384000` / `0x384000`） |
| K6 | 布局 vs G0 §10.1 L131 | **不一致**：G0 写"左右各 160 黑边"，后续裁决为无黑边 → **以无黑边为准**（T-07） |
| K7 | 年龄门槛 vs B3 实现（33 ms） | **不一致**：G0 为 47.3 s + 16.7 ms → **以 G0 为准**（T-06） |
| K8 | 帧存数量 vs B2 `bd_p3a.tcl` | **不一致**：脚本未设 `c_num_fstores`，ABI 要求 2 → **T-01** |
| K9 | VDMA 频段 vs B2 §5.2/§9-4 | 一致：MM 50 MHz / 流 74.21875 MHz，带宽占用 74.2%，有 underflow 风险（T-08） |
| K10 | 寄存器偏移 vs B3 §2.2/§2.4 | **一致**，且本文补上了驱动源码的**逐行依据**（B4/B5） |

---

## 9. 待核对项（12 项，均需关闭后才能称"ABI 已验证"）

| # | 项 | 现状 | 需要什么 | 影响 |
|---|---|---|---|---|
| **T-01** | VDMA **帧存数量** | ABI 要求 2；P3a BD 脚本 `bd_p3a.tcl:183-191` **未设 `c_num_fstores`**，`bd_p3a.bd` 中亦检索不到该参数 | lead 确认"硬件侧已定=2"落在哪一版 BD；若是重生成，需给出新 BD/validate 证据 | 若硬件仍 >2，未编程的帧存地址寄存器为 0 ⇒ 周期性花屏（B3 §6.1-1） |
| **T-02** | `PARKPTR(0x28).READSTR` 在 **circular 模式**是否随帧更新 | 驱动只在 park 分支读它；B3 §6.2-5 已列为联调第一优先 | 上板读 0x28 两帧对比；`待核对 pg020 表 2-x（PARKPTR）` | 乒乓写窗口的判据是否成立 |
| **T-03** | `HSIZE` 单位（字节 vs 像素） | 驱动注释仅"Hori size"，`XAxiVdma_DmaSetup` 只做上界检查；本 ABI 取 **5120 字节/行** | `待核对 pg020 表 2-1（MM2S_HSIZE）` | 单位错 ⇒ 每行只搬 20 字节（5120 px 视角）或越界 |
| **T-04** | `0x18 FRMSTORE` 可读性 | 依赖 IP 调试参数 `Mm2SFrmStoreRegEn`；P3a BD 未开 | `待核对 pg020 FRMSTORE` + 上板读回 | 不可作为帧存数量判据 |
| **T-05** | cache 口径 | 本文选 write-back + 整帧 flush；目标 BSP 的 SCTLR.C 与 flush 耗时均未确认/未测 | 目标 BSP 只读核对 + 上板 GT 计时 | 漏 flush ⇒ VDMA 读旧帧；flush 过慢 ⇒ 掉帧 |
| **T-06** | **结果年龄门槛口径冲突** | G0：47.3 s + 16.7 ms；B3 实现：33 ms | **需裁决**：以 G0 为准（则 SW 的 `S5_ST_AGE_OVER` 判据必须改），或修正 G0 | 面板 AGE 颜色与验收判据不一致 |
| **T-07** | **布局黑边冲突** | G0 §10.1（L131）仍写左右各 160 px 黑边；后续裁决为无黑边 | 需在 G0 文档回写/加勘误（本卡不改 G0） | 版式验收口径 |
| **T-08** | VDMA MM 50 MHz < 流 74.21875 MHz | IP 报 `axi_vdma 6.3-166`（B2 §1 第 4 条）；带宽占用 74.2% | 上板观察 underflow / 掉帧；必要时 G0 变更（提高 FCLK0 会牵动 P2d） | 显示稳定性 |
| **T-09** | 像素时钟与 TMDS 实链 | 74.21875 MHz 是 IP 参数/报告值，**非实测**；rgb2dvi/TMDS 在本阶段尚未接入（B2 §9-1） | P3b 上板：`clk_wiz` locked、`vid_out` locked、TMDS 出图 | 显示链是否成立 |
| **T-10** | `FRMDLY=0` 与 circular 的交互 | STRD_FRMDLY 高 4 位帧延迟固定 0 | `待核对 pg020（FRMDLY 语义）` | 帧延迟语义 |
| **T-11** | 帧缓冲 vs 既有禁区 | §7.3 I-1 | **需裁决**：按 D1 先例缩减 gap 并留记录 | 地址准入 |
| **T-12** | 像素字高 8 位（alpha） | ABI 要求写 0；P3a 用 RGBA 格式 + `xlslice[23:0]` 丢弃 alpha（B2 §5.3） | 实现约定即可，但不得依赖"alpha 被使用" | 颜色正确性 |

**另需登记（非待核对，属流程）**：§7.3 的 I-2/I-3 需要 w4 写入方更新 `S4B_stage4_address_map.json`（本卡无 w4 源码写权，且明确不 git）。

---

## 10. 边界与不做

1. 本文**不**主张显示链已通过任何关口；`validate 0 ERROR` 只证明 BD 拓扑合法（B2），不证明时序/资源/上板行为。
2. 本文**不**修改任何既有制品：G0 文档、P3a/P3b 证据、`S4B_stage4_address_map.json`、P2d 历史目录一律只读；差异以 §8/§9 的条目形式提出。
3. 本文**不**含任何上板结论；B3 的寄存器序列自检是**假寄存器堆**的离线自检（B3 §8.2 已声明）。
4. 本文的寄存器表以**本机 Vitis 2026.1 驱动源码**为依据（B4/B5）；凡驱动不能决定的语义，均已标 `待核对 pg020/pg016`。
5. 帧缓冲的 47.3 s 量级来自 2B 单帧推理耗时（G0 §10.1 与 B8 §6-4）；显示必然是"延迟显示"，画面必须显式标注结果年龄，**不得伪称同帧**。

---

## 11. 复现与校验命令（只读）

```powershell
# VTC 偏移（B4）
Select-String -LiteralPath 'D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_8\src\xvtc_hw.h' -Pattern 'XVTC_(CTL|VER|GASIZE|GHSIZE|GVSIZE|GHSYNC|GVSYNC)_OFFSET'
# VTC 同步编码公式（B4）
Select-String -LiteralPath 'D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_8\src\xvtc.c' -Pattern 'V0SyncStart \+ r_vactive|HSyncStart \+ r_hactive'
# VDMA 偏移与位域（B5）
Select-String -LiteralPath 'D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\xaxivdma_hw.h' -Pattern 'XAXIVDMA_(MM2S_ADDR|VSIZE|HSIZE|STRD_FRMDLY|START_ADDR|PARKPTR|CR_|SR_)'
# "写 VSIZE 即启动"的源码注释（B5）
Select-String -LiteralPath 'D:\Xilinx\2026.1\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\xaxivdma_channel.c' -Pattern 'Update vsize to start the channel'
# BD 参数与地址（B2）
Select-String -LiteralPath 'D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3a_video_bd_20261030_r01\bd_p3a.tcl' -Pattern 'GEN_|c_num|c_use_fsync|assign_bd_address|MMCM'
```

---

## 12. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| r01 | 2026-10-30 | 首版：显示 ABI、帧缓冲布局、VTC/VDMA 寄存器表（含驱动源码逐行依据）、坐标映射与排版、地址总表增补、12 项待核对。**离线**，未上板。 |

## 附：lead 裁决（2026-10-30，针对本文件不一致项）

| 编号 | 裁决 |
|---|---|
| I-1 / 帧缓冲地址 | **采纳**「落在阶段4 禁区」的判断 ⇒ 帧缓冲改为 **A=`0x20000000`、B=`0x20384000`**（每帧 3,686,400 B，终点 `0x20708000`）；不修改阶段4 禁区，需 Wong 批准才能动禁区定义 |
| I-2 | `unresolved_regions.display_buffer` **可关闭**（地址已确定） |
| I-3 | 阶段4 pl_mmio gap 未含 VTC/VDMA/AXI DMA —— 记为**已知缺口**，在阶段5 收口时统一更新，不单独改阶段4 冻结表 |
| T-01 | **已消解**：P3b BD `bd_p3b.tcl` 已设 `CONFIG.c_num_fstores {2}`（P3a 未设是因为用不到；P3b 以 2 为准） |
| T-06 | **口径区分**：G0 的 ≤47.3167 s 是**真实推理源**门槛；P3b 冒烟用模拟源（33 ms 级）只验证显示链路，**不得**当作真实延迟指标，证据里须注明「模拟源」 |
| T-07 | **已回写**：G0 §10.1 布局改为无黑边（960+320），「160 黑边」写法废止 |

## 附二：结果块 ABI（lead 裁定，2026-10-30）

- 基址：**`0x20800000`**（FB 末端 `0x20708000` 之后，8 MiB 空间）
- 头（32 B）：`0x00 magic=0x53355253("S5RS")`、`0x04 frame_id`、`0x08 n_dets(≤16)`、`0x0C cap_lo`、`0x10 cap_hi`、`0x14 inf_lo`、`0x18 inf_hi`、`0x1C status`（bit0 valid/bit1 overrun/bit2 stale）
- 检测项：`0x20` 起，**步进 16 B**（裁定，非 12 B）：
  - `+0 u16 x`、`+2 u16 y`、`+4 u16 w`、`+6 u16 h`（原图 640×480 坐标）
  - `+8 u8 cls`、`+9 u8 score_q8`
  - `+10..+15` 保留（生产端写 0；读端忽略）
- 语义：读端先读 `magic`+`status`；magic 不符或 `valid=0` ⇒ 回退模拟源并在 RESULT 里给 `reason`；`status.bit2` ⇒ 面板显示 `STALE`
- 写端（生产端）尚未实现：属推理/解码应用集成项，联调第一步核对步进与字节序

## 附三：P3n 架构（2026-10-30 15:xx 起为当前候选，替代 VTC/vid_out 方案）

> 背景：P3g/P3h 证明 BD 的 `v_tc` + `v_axi4s_vid_out` 组合在本设计里不出 HS/VS/DE（屏判"无信号"）；P3k（纯 PL 彩条）证明 rgb2dvi/时钟/复位/引脚全部正常。因此改用**自写时序发生器**并删除 VTC 与 vid_out。

### 硬件结构
```
U18 50 MHz ──▶ MMCME2_ADV 原语 ──▶ clk_pixel 74.21875 MHz
                              └──▶ clk_5x   371.09375 MHz
                              └──▶ locked ──▶ rgb2dvi.aRst_n
VDMA(MM2S, 非SG, 2 帧存) ──AXIS(32b, pixel_clk 域)──▶ axis_to_video ──▶ rgb2dvi ──▶ TMDS
                                                        └─▶ HS/VS/DE 自产（720p60: H 1650 / V 750，全正极性）
```
- **TMDS 引脚（本板实测正确值）**：`TMDS_clk_p=N18`（n=P19）、`data_p[0]=V20`（n=W20）、`[1]=T20`（n=U20）、`[2]=N20`（n=P20）；`hdmi_oen=V16`（与 HDMI 无电气连接，仅占位）
- **VDMA 数据面 100 MHz**（`m_axi_mm2s_aclk`/`S_AXI_HP2_ACLK`/协议转换器），**AXI-Lite 控制面 50 MHz**（与 `smc_ctrl` 同域）
- VDMA 进 ASYNC 模式：MM 侧 100 MHz、流侧 = pixel_clk 74.21875，跨域由 IP 内部异步行缓冲完成
- **欠载语义**：`axis_to_video` 在 `de=1 且 tvalid=0` 时输出纯黑 `0x000000`（不残留上一像素），并计数

### 地址与寄存器（P3n / P3p）
| 项 | 地址 | 说明 |
|---|---|---|
| VDMA AXI-Lite | **`0x43C00000`** | MM2S CR=+0x00、SR=+0x04 |
| underflow 计数（GPIO） | **`0x43C10000`** | P3n：累计欠载像素；P3p：本帧欠载像素（每 vsync 归零） |
| （P3p 追加）累计欠载 | **`0x43C10008`** | 仅 P3p 有 |
| 帧存 A / B | `0x20000000` / `0x20384000` | 1280×720×32bpp、**stride 5120 B/行**、帧 3,686,400 B |
| 结果块 | `0x20800000` | magic `S5RS`，检测项 16 B 步进（附二的裁定） |
| raw frame | `0x12000000` | 640×480 BGR888 |
| **VTC** | **不存在（P3n/P3p）** | **禁止访问 `0x43C30000`**（总线挂死风险） |

### 像素格式
软件写 `0x00RRGGBB`（`S5_RGB(r,g,b)=(r<<16)|(g<<8)|b`），ARM 小端内存字节序 `[B][G][R][00]`；硬件取 `tdata[23:0]` 解释为 `{R,G,B}`。若上屏红蓝互换，属硬件端字节序取值问题，不是软件字格式。

### 帧同步（P3p，可选）
`c_use_fsync=1`，`mm2s_fsync ← axis_to_video.vs`；软件 `EnableSync=1`、`GenLock=XAXIVDMA_SLAVE`、`GenLockRepeat=1` + `XAxiVdma_FsyncSrcSelect(MM2S)`（兜底：`CR=0x00000009`）。用于消除"CPU 边写帧存 + VDMA 边读"造成的撕裂。

### 已验证事实（2026-10-30 15:xx，P3n）
- `fps_dis=60`（VDMA 读周期 16,674 µs）、**运行期欠载 0.0%**（25 点采样差值 0）、`vdma_err=0`、frame 单调 +60
- 双帧存**必须画同一内容**：A 棋盘 / B 彩条会使屏幕以 30 Hz 交替 ⇒ 花屏闪烁（已定位并修正）

### 未验证/待办
- P3p fsync 在"供数不足"时的行为（重复帧 vs 停顿）待板上确认
- SG 双缓冲（描述符环）留待后续；`tlast_misalign` 未引出

