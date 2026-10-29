# P2d 地址表与数据通路（阶段5 收口，2026-10-29 r01）

位流：`58c66cdb53994d577156b4ff62eabc7187d2e88184ca965bb3395f63ec1a86a3`（P2d，50 MHz）

## 1. PS AXI 端口分配（方向 A 的核心）

| PS 端口 | 位宽 | 连接 | 用途 |
|---|---|---|---|
| `M_AXI_GP0` | 32 | `smc_ctrl`(1S/3M) | 控制面 CSR |
| `S_AXI_HP0` | 64 | **2B 推理核 `M_AXI` 直连** | 推理引擎读写 DDR（单 outstanding/单 beat，必须直连） |
| `S_AXI_HP1` | 64 | `smc_data`(2S/1M) ← preproc `M_AXI_RD` + AXI DMA `M_AXI_S2MM` | 预处理读 + 打包后 DMA 写 |

> 禁止把 2B 的 `M_AXI` 再塞回 SmartConnect：实测会让单帧 47.3 s 恶化到 >85.9 s（`s4d_p2b_infer_slowdown_20261029_r01`）。

## 2. 控制面地址（`smc_ctrl` 三个从口）

| 从设备 | 基址 | range | 说明 |
|---|---|---|---|
| 2B 推理核 CSR | `0x43C00000` | `0x00010000` | ID `0x53324250`、VER `0x00000100`；`0x008`=CMD（1=START/4=ACK）、`0x00C`=status、`0x010`=error_code、`0x028/0x02C`=core/drain timeout |
| preproc v2 CSR | `0x43C10000` | `0x00000080` | ID `0x53344450`；`0x04`=CTRL（START）、`0x08`=STATUS、`0x1C`=IRQ_CLR；busy 时写 → SLVERR |
| AXI DMA | `0x43C20000` | `0x00010000` | `0x30`=DMACR、`0x34`=DMASR、`0x48`=S2MM_DA、`0x58`=S2MM_LENGTH（23-bit 有效） |

## 3. DDR 地址（两端口共享同一块 DDR，各自 0x00000000 + 1 GiB 段）

| 区域 | 基址 | 大小 | 用途 |
|---|---|---|---|
| 张量 / arena | `0x10000000` | 32 MiB 窗口 | 2B 输入张量（519,168 B INT8 CHW）+ head13/head26 |
| 权重 | `0x10100000` | 5,903,100 B | GF8 权重（2B `weight_addr=0x00100000`） |
| raw_frame | `0x12000000` | 12 MiB + 32 KiB meta | 预处理源图（`SRC_BASE=0x12000000`） |
| head13/26 参考（M4-b 用） | `0x12000000` / `0x12002000` | 5,070 / 20,280 B | 自检参考（**head13 必须以 1268 字=5072 B 预置**） |
| 长跑记录区 | `0x11B00000` | 32 B | 探针记录（clear 后全 0） |

## 4. 时钟与复位

- FCLK0 = **50 MHz**（`PS7 PCW_FPGA0_PERIPHERAL_FREQMHZ 50`；SLCR `FCLK0_CTRL` 读回 `0x00600600`）
- 全部 PL 逻辑（preproc / 2B / packer / DMA / 互联）**同一时钟域**，无 CDC
- 复位：`proc_sys_reset`（`peripheral_aresetn`），PL 编程后需四动作：`0xF8000008=0xDF0D` → `0xF8000900=0xF` → `0xF8000240=0` → `0xF8000004=0x767B`，并读回断言 `0xF` / `0`

## 5. 数据通路（每帧）

```
raw_frame(0x12000000) --preproc(M_AXI_RD→HP1)--> engine --> M_AXIS 8bit
   --> packer(8→64, TKEEP=0xFF, TLAST 透传) --> AXI DMA S2MM(STREAM 64)
   --> M_AXI_S2MM(HP1) --> tensor(0x10000000, 519168 B)
2B 推理核(M_AXI→HP0) 读 tensor + weights --> head13/head26(0x11A46100 / 0x11AD5E80)
PS 侧只做 CSR 配置/启动/完成轮询/解码 NMS
```

## 6. 已知约束

1. **DSP 已用 158/220（71.82%）**，LUT 44.08%：加视频链（阶段6）前必须重算资源。
2. 时序余量 WNS +0.128 ns：任何改动都要重跑实现与时序，不得沿用。
3. `c_sg_length_width=23` 是硬约束：默认 14 bit 会把 519,168 B 截成 11,264 B（P2c r01 作废原因）。
4. 2B 核的 `core_timeout/drain_timeout` 运行期必须写 `0xFFFFFFFF`（50 MHz 下 85.9 s），低于单帧 47.3 s 的值会必然超时。