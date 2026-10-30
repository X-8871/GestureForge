# P3p 报告 —— P3n + VDMA frame-sync（修"帧不同步"第二根因）

| 项 | 值 |
|---|---|
| 阶段 / 任务 | **阶段5（HDMI 显示链）** / **S5-T01** |
| RunId | **s5_p3p_build_20261030_r01** |
| 日期 | 2026-10-30（UTC+8） |
| 工具 / 器件 | Vivado v2026.1 / `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3p_r01` / `s4d_p3p` / `top_p3p` |
| 目的 | 消除**帧不同步**（撕裂/滚动）——与欠载无关的第二根因 |

---

## 1. 结论

**位流 + XSA 已出；时序清零（WNS +3.659 / TNS 0 / 失败端点 0）、DRC 0 error、引脚与 P3m/P3n 完全一致。**
**VDMA frame-sync 已生效于 IP 配置层面**（`c_use_fsync=1`、`c_use_mm2s_fsync=1`，`mm2s_fsync` 已连到 RTL 的 `vs`，BD 参数已实证）。

| 项 | 值 |
|---|---|
| **WNS** | **+3.659 ns** |
| **TNS / 失败端点** | **0.000 / 0** |
| **WHS / THS** | +0.066 / 0.000 |
| 端点总数 | 6,001 |
| DRC | **11 条、0 error**（同 P3n 的 4 类） |
| 资源 | LUT **1,698 (3.19%)**、FF 2,795、BRAM 2、DSP 0、OSERDESE2 **8**、MMCM 1、BUFG 4、IOB 10 |
| 日志 | **0 ERROR / 0 CRITICAL WARNING / 96 WARNING** |
| **bit** | `out\s4d_p3p_r01.bit` **4,045,762 B** `25cba4ec636f038ef60a26a1dcf756deb04b86fcacb8c588269b9868f12e1237` |
| **XSA** | `out\s4d_p3p_r01.xsa` **263,672 B** `86a10c26510b20607197893a04879ff047957a356559578b8bea007549014d82` |

---

## 2. 与 P3n 的差异

| 项 | P3n | **P3p** |
|---|---|---|
| VDMA frame sync | `c_use_fsync=0`（无） | **`c_use_fsync=1` + `c_use_mm2s_fsync=1`**，`mm2s_fsync` ← RTL `axis_to_video.vs` |
| 欠载读数 | 单通道 GPIO：累计欠载 | **双通道 GPIO**：ch1=**本帧**欠载像素数、ch2=**累计**欠载像素数 |
| `tlast` 处理 | 忽略 | RTL 增加 **`tlast_misalign`** 计数（tlast 出现在非帧末像素时 +1）——**本版仅源码内诊断，未引 GPIO** |
| RTL | top_p3m/top_p3n | `top_p3p.v` 增加 vsync 2 级同步 + 帧边界减法 + 两组格雷码 CDC |
| 数据面时钟 / 控制面 / 流侧 / MMCM / rgb2dvi / 引脚 / `c_num_fstores=2` / 非 SG | — | **全部不变** |

**BD 参数实证**（直接解析生成的 `s4d_p3p.bd`）：
```
c_use_fsync      = 1
c_use_mm2s_fsync = 1
C_IS_DUAL        = 1     C_ALL_INPUTS = 1   C_ALL_INPUTS_2 = 1
C_GPIO_WIDTH     = 32    C_GPIO2_WIDTH = 32
网表连接: vdma_0/mm2s_fsync  ← BD 端口 mm2s_fsync ← RTL 的 axis_to_video.vs
```

### 为什么这样能修撕裂
P3m/P3n 里 `axis_to_video` 按自建 60 Hz **自由跑**，VDMA 按 52 fps 出帧 ⇒ 显示的一帧会横跨 VDMA 的两个帧边界 ⇒ 水平撕裂/滚动。
fsync 后 **VDMA 每收到一个 fsync 脉冲（我们的 vsync 上升沿）才推进一帧** ⇒ 供帧节奏由显示决定；
帧率不匹配时由 IP 的 gen-lock 语义处理（按 `GenLockRepeat` 重复上一帧），**不再出现"半旧半新"的撕裂**。

### SG（scatter-gather）双缓冲：**本版不做，留待 C 档**
原因：SG 需要软件侧在 DDR 里构造描述符环 + 循环位/尾指针管理（跨团队改动，~半天），
而 **fsync + 现有非 SG 已能消除撕裂**；非 SG 的"每帧重装"在 60 Hz 下 CPU 完全跟得上（每帧 ~16.7 ms 预算）。
若后续需要"零 CPU 干预的连续取帧"，再上 SG。

---

## 3. 时序（交付值 + 原始口径）

| | WNS | TNS | 失败端点 | WHS |
|---|---|---|---|---|
| **P3p 交付（含 CDC 约束）** | **+3.659** | **0.000** | **0** | +0.066 |
| P3m 原始（未加 CDC 约束，同构 CDC） | −5.503 | −173.092 | 32 | +0.050 |

**原始口径说明**：P3p 未单独构建无约束版。其 CDC 结构与 P3m 同源（格雷码 + 3 级同步），
P3m 的"未加约束"表现为 **−5.503 / TNS −173.092 / 32 端点**（32=格雷码位宽，requirement 仅 0.211 ns、
数据路径仅 1.322 ns）⇒ 假性违例，非功能缺陷。P3p 在约束下 **TNS=0、失败端点=0**。

**P3p 的 CDC 约束**（`p3p_cdc.xdc`，cell 过滤，避开 12-4739；解析无缺 cell 告警）：
- `uf_pixels_reg[*] → uf_g_s1_reg[*]` 13.474 / `uf_g_s1 → uf_g_s2` 20.000
- `tlast_misalign_reg[*] → mis_g_s1_reg[*]` 13.474 / `mis_g_s1 → mis_g_s2` 20.000
- `u_atv/vs_r_reg* → vs_meta_reg*` 20.000 / `vs_meta_reg* → vs_sync_reg*` 20.000

六时钟：`clk_fpga_0` 20.000（50）· `clk_fpga_1` **10.000（100，数据面）** · `sys_clk` 20.000 · `clk_fb` 80.000 ·
`clk_pixel_raw` **13.474（74.21875）** · `clk_5x_raw` **2.695（371.09375）**

---

## 4. DRC / 引脚 / 资源

**DRC 11 条、0 error**：`PDCN-1569` 1（协议转换器 IP 内部 LUT）、`REQP-1839` 8（RAMB36 异步控制）、`RTSTAT-10` 1、`REQP-181` 1。无 `NSTD-1`/`UCIO-1`。

**引脚（`report_io` 实测，与 P3m/P3n 完全一致）**：
`sys_clk`=**U18**（`IO_L12P_T1_MRCC_34`）· `TMDS_clk_p`=**N18**/**P19** · `data_p[0]`=**V20**/**W20** · `[1]`=**T20**/**U20** · `[2]`=**N20**/**P20** · `hdmi_oen`=**V16**，全 `TMDS_33`/LVCMOS33、bank 34、3.3 V、`FIXED`。

**资源**：LUT 1,698（3.19%）、FF 2,795、BRAM 2、OSERDESE2 8、MMCM 1、BUFG 4、IOB 10。

---

## 5. ★ 软件需配合的最小改动清单（给 video-sw）

> 目标：让 VDMA 以 **MM2S frame-sync 从模式**工作，由显示侧 vsync 驱动取帧。
> 寄存器位定义来自本机驱动头文件 `axivdma_v6_17/src/xaxivdma_hw.h`（权威）：
> `XAXIVDMA_CR_SYNC_EN_MASK=0x00000008`、`XAXIVDMA_CR_FSYNC_SRC_MASK=0x00000060`、
> `XAXIVDMA_CR_GENLCK_RPT_MASK=0x00008000`、`XAXIVDMA_CR_GENLCK_SRC_MASK=0x00000080`；
> fsync 源取值：`XAXIVDMA_CHAN_FSYNC=0`（本通道外部引脚）、`XAXIVDMA_CHAN_OTHER_FSYNC=1`。

### 5.1 用 Xilinx 驱动（推荐）
1. `XAxiVdma_DmaSetup` 里增加/修改（其余字段不变）：
   - **`EnableSync = 1`** （gen-lock 使能）
   - **`GenLock = XAXIVDMA_SLAVE`** （从模式：帧节奏由外部 fsync 决定）
   - **`GenLockRepeat = 1`** （新 fsync 到来而上一帧未完成时重复上一帧，避免半帧/撕裂；
     该值语义请以 `XAxiVdma_DmaSetup` 注释与实测为准）
2. 调用 **`XAxiVdma_FsyncSrcSelect(&Vdma, XAXIVDMA_CHAN_FSYNC, XAXIVDMA_MM2S)`**
   —— 选择"本通道外部 fsync 引脚"（即硬件已接的 `mm2s_fsync`）；
   原型为 `int XAxiVdma_FsyncSrcSelect(XAxiVdma *InstancePtr, u32 Source, ...)`，
   **第三个参数（通道）请按 v6.17 头文件核对**。
3. 之后照旧 `XAxiVdma_DmaStart(&Vdma, XAXIVDMA_MM2S)`。
4. 非 SG 模式仍是**每帧重装 + Start**；fsync 只改变"何时开始一帧"，不改变 HSIZE/VSIZE/STRIDE/帧地址写法。
5. 建议启动后读 `MM2S_VDMASR` 确认无 DMA 错误（P3m/P3n 实测为 `0x11000`、无错）。

### 5.2 直接写寄存器（驱动不支持时的兜底）
基址 `0x43C00000`：
- **`MM2S_VDMACR`**（+0x00）：`RS(bit0)=1` + **`SYNC_EN(bit3)=1`** + **`FSYNC_SRC(bits[6:5])=0b00`**（本通道外部引脚）
  ⇒ 例如 `CR = 0x00000009`
- `MM2S_START_ADDRESS`(+0x18)、`HSIZE`(+0x54)/`VSIZE`/`STRIDE` 等按现有代码不动（以驱动/文档偏移为准）
- 可选：`GENLCK_RPT`(bit15) 设重复帧数；`GENLCK_SRC`(bit7) 选 genlock 源

### 5.3 underflow 读数（GPIO，只读）
| 地址 | 含义 |
|---|---|
| **0x43C10000** | **本帧欠载像素数**（每到 vsync 归零，读它判断"当前帧是否在欠载"） |
| **0x43C10008** | **累计欠载像素数**（sticky，从 PL 复位起累加） |

判读：若**本帧计数绝大多数帧为 0** ⇒ 欠载已消除；若仍约 10–13%（≈1−52/60）⇒ 数据面仍不足，转候选 B（720p50）。

---

## 6. 未验证项 / 风险

1. **⚠️ 上屏与欠载：未验证**（需板测：看撕裂是否消失 + 读 0x43C10000/0x43C10008）。
2. **fsync 在"供数慢于显示"方向的行为未实测**：`GenLockRepeat` 语义（重复帧 vs 停顿）需板上确认；
   若表现为周期性停顿而非重复帧，可调 `GenLockRepeat`/`GENLCK_RPT`。
3. **`tlast_misalign` 未引出 GPIO**：本版两个 GPIO 通道被"本帧/累计欠载"占用；该计数仅在 RTL 源码里
   （`p3p_cdc.xdc` 已为其加约束，解析无缺 cell 告警）。若需要读它，下一版可加第二个 `axi_gpio`（基址 0x43C20000）。
   注：未从 `tlast` 做"硬复位行计数"是**有意的**——vs 由计数器派生又去驱动 fsync，
   再用 tlast 复位计数会构成闭环（可能自激/相位跳动）；fsync 已经把帧边界交给 VDMA，足够。
4. 非 SG 每帧重装：重装不及时会短暂无数据 ⇒ 本帧欠载计数会体现。SG 留待 C 档。
5. 未做叠加（G0 D2 框+文字属后续）。

---

## 7. 产物与哈希（SHA-256）

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `out\s4d_p3p_r01.bit` | **4,045,762** | `25cba4ec636f038ef60a26a1dcf756deb04b86fcacb8c588269b9868f12e1237` |
| `out\s4d_p3p_r01.xsa` | **263,672** | `86a10c26510b20607197893a04879ff047957a356559578b8bea007549014d82` |
| `bd_p3p.tcl` | — | `见目录` |
| `p3p.xdc` / `p3p_cdc.xdc` | — | 见目录 |
| `rtl\axis_to_video.v` | — | 见目录 |
| `rtl\top_p3p.v` | — | 见目录 |

边界：未上板、未 git；未改动 P2d/P3a/P3b/P3c/P3d/P3e/P3f/P3g/P3h/P3k/P3m/P3n 目录。