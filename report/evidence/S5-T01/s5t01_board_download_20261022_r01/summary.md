# S5-T01 上板执行 RunId `s5t01_board_download_20261022_r01`（PL+PS 成功；无视频源）

- 时间（UTC+8）：2026-10-22 13:48–13:50
- 授权：Wong 显式授权上板（13:25；13:34 已上电；13:41 经 `CTRL-HW-SCAN` 证实链完整）
- 目标：下载**冻结灰度位流** + **v12 图案 ELF**（易失），验证 HDMI 出图链路与图案，为叠框 bring-up 做准备
- 结论：**PL 下载与 PS 应用运行成功**（`FPGA_PROGRAM`/`PS7_INIT`/`DOW_ELF`/`RUN` 全 OK，退出码 0）；但 **OV5640 传感器 I2C 全 0xFF（不响应）⇒ 无视频源**，`v12` 图案无法启用，帧指纹为 0。**未对传感器/寄存器造成任何改变。**

## 1. 下载与运行（`console/capture_v12bars.txt`、`tmp/.../t05_v12bars/download_v12bars.log`）

| 项 | 值 |
|---|---|
| 位流（标准亮度灰度） | `44e609cc…c4afb`（与冻结声明一致；易失下载，非 QSPI） |
| XSA | `90e1bdee…b1c4` |
| v12 ELF | `527a74fc…9845c5` |

- `T03_DL_OK=FPGA_PROGRAM / PS7_INIT_SOURCE / PS7_INIT_RUN / PS7_POST_CONFIG / DOW_ELF / RUN`，`DOWNLOAD_EXIT=0`。

## 2. 无视频源的直接证据（UART，`tmp/.../t05_v12bars/uart_v12bars.log`）

| 行 | 内容 |
|---|---|
| `S3_DIAG5_SENS=…503D=0xFF` | 传感器寄存器读取**全部 0xFF**（无 ACK） |
| `S3_DIAG10_GRAY=…5580/5583/5584=0xFF` | 同上 |
| `S3_DIAG12_BARS_SKIPPED reg=503D reason=read_failed`<br>`S3_DIAG12_BARS=503D before=0xFF after=0x80 readback=0xFF write_status=-2` | **v12 图案写失败**（读失败即跳过，符合阶段3“读失败则跳过写入”的安全原则）⇒ `0x503D` **未被改变**，无需恢复 |
| `S3_DIAG6_FP … sum=0x00000000 hash=0xD7978EEB nz=0`（t=5/10/15 三站点、三次采样） | 帧缓冲**无有效视频数据**（全零） |
| `S3_DIAG6_SR … S2MM_SR=0x00010000 S2MM_CR=0x00018003 FRMCNT=1` | S2MM 在跑但无新帧（无输入） |

## 3. 只读转储（`console/capture_v12bars.txt` 内 `read_safe` 段）

| 寄存器 | 值 | 说明 |
|---|---|---|
| `CR_S2MM`(0x43010030) | `0x00018002` | 采集通道控制 |
| `SR_S2MM`(0x43010034) | `0x00010001` | bit0=Halted=1（本转储先 halt A9 再读，属安全只读路径） |
| `VSIZE`/`HSIZE`/`STRIDE` | `0x2D0`(720)/`0xF00`(3840)/`0xF00` | 1280×720、3 B/px（RGB888 通道），与灰度位流一致 |
| `ADDR_S2MM` | `0x00114C00` | 当前采集写地址 |
| `SR_MM2S`(0x43000004) | `0x00011000` | 显示通道状态（原样记录，不作结论） |
| `DDR_FB_MID`(0x00510C00) | 全 0 | 无有效画面 |

- **注意（不夸大）**：`DDR_FB_000`(0x00110C00) 起读出 `70300C02,70400C02,…` 等结构化数值；因指纹站点全零、且该区非当前写地址，**不能**把它当作“有画面”或“图案生效”的证据——本 run 未取得任何有效视频帧。

## 4. 判定与阻塞

- **判定**：板卡、线缆、下载链路、PS 应用、VDMA 配置均正常；**唯一缺口是没有视频源**（摄像头模块不在位/不响应）。
- 这与 `DSH-20261022-008` 的“灰度先行、模块到货后再更新”一致：模块可能已被取下送修。
- 任务卡定义的视频源＝“冻结灰度位流 + v12 图案（写 0x503D）”，**该路径依赖传感器在位**；模块不在位时此视频源不可用 ⇒ 需要 Wong 决策（见给 Wong 的报告）。

## 5. 未执行 / 限制

- **NOT_RUN**：HDMI 画面目视/拍照、叠框注入、FPS 与延迟实测、T5-0x 机上用例、G3。
- **无副作用**：未烧录 QSPI；`0x503D` 未被写入（写失败）；未改 dbdf/w4/w2b/主树；探测与下载后清理本进程产生的 `hw_server`，收尾无驻留服务。
- 本 run 只证明“链路可用 + 无视频源”，**不代表**任何阶段验收。

## 6. 证据文件

- `console/input_hashes.txt`（位流/XSA/ELF 实际哈希）
- `console/capture_v12bars.txt`（下载 + UART + 只读转储全过程原始输出）
- `run_manifest.json`（命令与真实退出码、哈希绑定、限制、未执行项）
- 原始日志（本树 tmp，不入 Git）：`tmp/5/S5-T01/s5t01_board_download_20261022_r01/t05_v12bars/`