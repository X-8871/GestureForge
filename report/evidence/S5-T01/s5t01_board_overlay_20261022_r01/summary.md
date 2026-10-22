# S5-T01 P1 上板 RunId `s5t01_board_overlay_20261022_r01`（PS 合成源 + 软件叠框）

- 时间（UTC+8）：2026-10-22 15:26–15:29
- 决策依据：**Wong 2026-10-22 选择方案 B**（PS 合成视频源 + 软件叠框，零新增 PL；不依赖摄像头模块）
- 结论：**P1 应用已构建并上板运行**；六个用例循环输出正常；**送显缓冲内容已含合成画面**（数值可证）；但 **`display_fps` 本轮未测得（NOT_VERIFIED）**，且逐像素级屏上结论需按字对齐重建后再下。**未取得 HDMI 照片**（待 Wong 拍摄）。

## 1. 交付（源码与构建）

| 项 | 内容 |
|---|---|
| 用例生成器 | `scripts/stage5_t01/gen_overlay_cases.py`（框像素由**冻结参考实现** `verification/s5_display_geometry_reference.py` 计算；含笔画字体与 ASCII 自检） |
| P1 应用 | `scripts/stage5_t01/p1_app/s5_overlay.c`（只绘制预计算的矩形/笔画；**板上无逆映射逻辑**） |
| 最小补丁 | `scripts/stage5_t01/apply_p1_patch.py`（锚点唯一才插入 1 行调用；幂等） |
| 构建 | `scripts/stage5_t01/build_p1_app.sh`（复制阶段3 应用源码到本树 tmp；复用既有 BSP；`arm-none-eabi-gcc`） |
| ELF（循环版） | `s5t01_overlay_cycle.elf` SHA256 `5d5c253dfb2962f978a46f0579790c9ef0f8663edc87450f4a643f1f96ac71ac`（314,740 B，**0 警告**） |
| ELF（单用例5常显） | `s5t01_overlay_case5.elf` SHA256 `3632e9fb29f9f70d779039c18e1d50b6ecb7b4e796fc77356352859b60d055b5`（314,764 B） |
| 位流（冻结灰度） | `44e609cc…c4afb`（易失下载，未烧 QSPI） |

## 2. 板上运行（`console/uart_overlaycycle.log`）

- 下载：`FPGA_PROGRAM / PS7_INIT / DOW_ELF / RUN` 全 OK，pipeline 退出码 0。
- 应用 UART 标记：`S5_P1_BEGIN canvas=1280x720 stride=3840 frames=3 cases=6`；`S5_P1_SOURCE=PS_SYNTHETIC`；`S5_P1_SEMANTICS=B_latest_result_overlay`；`S5_P1_BUF0=00114C00 / BUF1=00703800 / BUF2=00CF2400`。
- 六个用例按表输出，计数与设计一致：`CASE 1 BOXES 1` / `CASE 2 BOXES 4` / `CASE 3 BOXES 15` / `CASE 4 BOXES 0` / `CASE 5 BOXES 2` / `CASE 6 BOXES 0 STALE`；两个完整循环（`S5_P1_CYCLE_DONE`）。
- 计时窗口正常（`window_counts≈2.298e9` ≈ 6.9 s @ 333.3 MHz），**但帧计数增量为 0**（见 §4）。

## 3. 送显缓冲数值核对（只读 JTAG，`console/read_overlay_buf.txt`）

| 探针 | 读数 | 判读 |
|---|---|---|
| `BUF0/1/2` 首字 | `FFFFFFFF` ×3 | **三块送显缓冲都含我绘制的白色四角标记** ⇒ 合成画面确已进入送显缓冲 |
| `BUF0+192`（x=64 网格线处） | `20000000` | 网格线(黑) + 下一像素灰度 0x20 → 与背景条/网格设计一致 |
| `BUF0` 行 53 x=0.. | `40FF4040` | 非背景色，分量组合符合**类色表**（B=0x40,G=0xFF,R=0x40） |
| `BUF0` 行 53 x≈77..78 | `FF4040FF` | 同上，含红色分量 |

- **不夸大**：`mrd` 按 **32 位字**读取，而像素为 **3 字节**，行内存在跨字错位 ⇒ 上述值**只能**证明“非背景、且颜色分量属于类色表”，**不能**据此逐像素断定框位。逐像素结论须按字对齐重建后再下（本轮未做，列入下一步）。
- MM2S 帧尺寸寄存器 `0x43000050=0x2D0`(720)、`0x43000054=0xF00`(3840) ⇒ 显示通道配置与本画布一致。

## 4. 显示帧率：本轮 **NOT_VERIFIED**（如实体现在此）

- `MM2S_CR(0x43000000)=0x00010001` ⇒ bit0(RS)=1，**MM2S 处于运行态**。
- `MM2S_SR(0x43000004)=0x00011000` ⇒ `IRQFrameCntSts=(SR>>16)&0xFF = 1`，**帧计数未随 6 s 窗口增长** ⇒ 我的“读 SR 帧计数”测法**未能测到显示帧率**（可能该计数仅在帧计数中断使能/特定条件下累加，或显示通道的实际帧完成事件未走该计数）。**本轮不报任何 FPS 数值**，该测量方法列入待修项。

## 5. 未执行 / 限制

- **未执行**：HDMI 屏目视与照片（**待 Wong 拍摄**；这是本轮最直接的视觉证据）；逐用例屏上验收表（T5-01/02/03/04/05/06/11/12 的机上确认）；`display_fps`（方法待修）；连续 30 分钟；G3。
- **限制**：视频源为 **PS 合成图**（`video_source=PS_SYNTHETIC`），**不是**真实采集画面，不得据此声称阶段3 采集/颜色结论；画面语义固定 B。
- **无副作用**：`0x503D` 未被改变（传感器不在位、写失败），无需恢复；未烧 QSPI；未改 dbdf/w4/w2b/主树；`hw_server` 已清理不驻留。
- 期间发现并修复的两个自身缺陷（已在本轮修正后重建）：生成头 `seg[8][4]` 装不下 'B' 的 10 笔画；`s5_text` 中字形指针 `g` 遮蔽颜色参数 `g`。构建现为 0 警告。

## 6. HDMI 照片（Wong 2026-10-22 提供）——视觉证据

- 文件：`photos/hdmi_case5_20261022.jpg`（1919×1080，493,672 B，SHA256 `110f46e3…a78f`，与提供值一致；原图为附件规范化副本，源尺寸可能不同）
- **视觉确认（照片所显内容）**：
  1. 合成背景上屏：竖直灰度条 + 条间黑线 + 中心白十字 + 四个白色角标记；
  2. **用例 5 正常显示**：左上 HUD 四行为 `CASE 5`（红）/`BOXES 2`（绿）/`SEM B`（蓝）/`FRESH`（黄），文字可读 ⇒ 笔画字体与 HUD 均工作；
  3. **左侧红色高窄框**（FIST 类色）与**顶部绿色横框**（PALM 类色）同时渲染 ⇒ 多框与类色生效；
  4. 绿框左侧有 **`PALM 0.62`** 文案，且因该框顶边贴画布上沿（y=0），文案**按契约锚点规则翻转到框内** ⇒ 与期望矩形（canvas 513..1025 × 0..66）方向一致；
  5. 红框文案 `FIST 0.66` 出现在左上区域。
- **自动定量提取：本轮未达成（如实记录）**：`scripts/stage5_t01/analyze_hdmi_photo.py` 的连通域可用，但① 四角纯白标记未达阈值；② 横向中心十字在照片中过暗（实测最长行亮像素 <40% 宽度）⇒ **不做画布↔照片映射**，只输出相对位置（`console/photo_analysis.json`，`mapping_ok=false`）。因此**不以本照片声称 1 px 级坐标门槛**。
- **照片暴露的两个待修缺陷（本轮未修，已登记）**：
  - **D-1（观感）**：背景条亮度 `(x/64)*32` 在 `u8` 上溢出（x≥512、1024 处回绕为黑带）——画面出现两条非预期黑带；
  - **D-2（布局）**：用例 5 红框标签（canvas y≈35..51）与左上 HUD 第 1/2 行重叠，文字互相压盖。

## 7. 证据文件

- `console/input_hashes.txt`、`console/download_overlaycycle.log`、`console/uart_overlaycycle.log`、`console/read_safe_overlaycycle.log`
- `console/read_overlay_buf.txt`（显示通道寄存器 + 送显缓冲取样）
- `console/build_cycle.log`、`console/s5_overlay_cases.h`（生成的用例/字形数据）
- `console/capture_overlaycycle.txt`（下载+UART+只读转储全过程）
- `run_manifest.json`（哈希绑定、命令与真实退出码、限制、未执行项）