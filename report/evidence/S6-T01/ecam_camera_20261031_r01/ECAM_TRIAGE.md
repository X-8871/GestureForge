# E-cam 窗失败分诊（rc=-11）

- RunId：`ecam_camera_20261031_r01`；时间 2026-10-31 10:25:12–10:26:39（UTC+8）
- 身份：P3r **build3**（bit `648f3156…` 4,045,762 B；XSA `1284f637…` 418,950 B）；ELF 相机版 `9ffc68e6…`（315,308 B）
- 结果：`ECAM_CAMERA_FAIL`（exit 1）；R7-1..R7-6 全 FAIL，根因单一：**相机初始化失败 rc=-11**

## UART 关键行
```
CAM: FAILED rc=-11（I2C/覆盖表/回读/S2MM 配置阶段失败）→ 继续显示测试图
VDMA: init OK, version=62000050 ...
VDMA: read period = 5557897 ticks (16673 us) -> fps_dis=60 (display refresh)
S5DISP RESULT={... "fps_dis":60,"vdma_err":0,"src":"real_nobox","reason":"result_magic_mismatch"}
```

## 判据对照
| 判据 | 结果 | 事实 |
|---|---|---|
| R7-1 `CAM: init OK chip=0x5640…` | FAIL | 未出现，仅 `CAM: FAILED rc=-11` |
| R7-2 `CAM: sr=` 帧递增≥10 | FAIL | `CAM: sr=` 行 0 条（未进入视频流阶段） |
| R7-3 RESULT src=real/fps_dis=60/vdma_err=0 | FAIL | fps_dis=60、vdma_err=0 达成，但 `src=real_nobox`（无相机源） |
| R7-4 UF 增量 0 | FAIL | `uf_total` mid→end 增 2,232,840,570（显示侧因无相机源而欠载） |
| R7-5 raw 非全 0 且两次采样有变化 | FAIL | 非全 0=true，changed=false（raw 区未被相机写入） |
| R7-6 无 `CAM: FAIL` | FAIL | rc=-11 |
| 目视（Wong） | 待确认 | 预期屏幕为**测试图 bars8+border+cross**（非实时画面） |

## 停核后寄存器快照（只读）
| 寄存器 | 地址 | 值 |
|---|---|---|
| camera VDMA CR | 0x43C60000 | `0x00000000` |
| camera VDMA SR | 0x43C60004 | `0x00000000` |
| camera VDMA PARKPTR | 0x43C60028 | `0x00000000` |
| camera GPIO | 0x43C70000 | `0x00000000` |
| camera RST | 0x41200000 | `0x00000000` |
| display VDMA CR | 0x43C40000 | `0x00010002` |
| display VDMA SR | 0x43C40004 | `0x00011001`（已停核） |
| UF frame / total | 0x43C50000/08 | `0x00096A00` / `0xCB31C00A` |
| 2B CSR | 0x43C00000 | `0x53324250` |

**前置探测（dow 前）**：CSR2B=0x53324250 ✓、DISP_VER=0x62000050 ✓、CAM_CR/SR 可读（=0）、CAM_GPIO/RST 可读（=0）
⇒ AXI-Lite 通路正常；**camera 侧寄存器全程 0**，说明应用在 SCCB 阶段即中止，尚未进入 S2MM/VDMA 配置。

## 分诊（结合 lead 返回码表）
- **`-11` = SCCB 写失败**（video-sw 的 "I2C/覆盖表/回读/S2MM" 合并文案需拆分；建议下一步打印具体 SCCB reg/addr/ack）
- 优先检查（硬件侧）：
  1. **SDA=F16 / SCL=F19 上拉是否在位**（模块板上拉/主板上拉，2.2–4.7 k）
  2. **I2C 分频/时钟**：SCCB 需 100–400 kHz；XCLK（24 MHz?）是否起振
  3. **相机模组供电**：3.3 V/1.8 V 是否到 J11；PWDN/RESET 电平（本窗 CAM_GPIO=0、CAM_RST=0）
  4. **J11 排线/连接器**接触
- 软件侧建议：`video-sw` 拆分 rc=-11 子码并打印 SCCB 目标寄存器与读回值；确认 P3r 的 SCCB 走 PS I2C0 还是 PL GPIO bit-bang（地址映射影响 0x41200000/0x43C70000 的用法）

## 结论
- **P3r build3 的显示链路正常**（VDMA VER/read period/fps_dis/vdma_err 全绿），可继续用于显示/交互证据
- **相机链路未通过**：卡在 SCCB 写失败，camera VDMA/GPIO/RST 未被应用配置；与 PL 时序无关（WNS +0.342），属 I2C/供电/连接或应用 I2C 实现问题
- 本窗正常收窗（teardown PASS、零残留、board_state clean）