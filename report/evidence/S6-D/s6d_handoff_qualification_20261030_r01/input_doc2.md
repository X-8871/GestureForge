# 阶段5（HDMI 显示链）G3 实物验证记录 · 2026-10-30

- 记录方：DSH 项目总控；验收人：Wong（目视）
- 阶段：**阶段5 HDMI 显示链**；任务号 **S5-T01**
- 时间：2026-10-30（UTC+8），上板窗口 12:04–18:2x
- 结论：**G3 通过（S6-A/B/C/D/E/F 六项全部达成）**，候选基线 = **P3n** 位流 + `P3n` 显示软件

## 1. 交付身份

| 项 | 值 |
|---|---|
| 位流 | `s4d_p3n_r01.bit`，4,045,762 B，sha256 `80b88f1750698e15a1961a2b1ee3081fc9d2c8f5744035e9f119ac82fc9cfcb0` |
| XSA | `s4d_p3n_r01.xsa`，263,571 B，sha256 `a9953d04c5d9d89a5f9cc2adbd0693619d7c1cb053156651839b6a891ef45133` |
| 有界 ELF | `s5_display_app.elf`，281,624 B，sha256 `49070390f8f08784fd9139af447b370d9eeb610c159a81590006bd2c25aa96c0` |
| 长跑 ELF | `s5_display_app_longrun.elf`，284,812 B，sha256 `388a0a07101a16e3b3fb43a51b6b987f63bff9200821c3f9ddca1e896fe0752a` |
| 时序 | WNS **+4.252 ns** / WHS +0.056 / TNS=THS=0 / 失败端点 0（5,606 端点，含 CDC 约束） |
| 资源 | LUT 1,637（3.08%）、FF 2,503、BRAM 2、OSERDESE2 8、MMCM 1、BUFG 4、IOB 10 |
| DRC | 11 条、**0 error**（全在协议转换器/BRAM 内部） |
| TMDS 引脚 | `clk_p=N18`(n=P19)、`data_p[0]=V20`(n=W20)、`[1]=T20`(n=U20)、`[2]=N20`(n=P20)，全 `TMDS_33`/bank34/3.3 V |
| 板卡 | AX7020（`xc7z020clg400-2`），HDMI OUT J19，AOC 显示器 |

## 2. 架构（P3n）

```
U18 50 MHz → MMCME2_ADV → clk_pixel 74.21875 MHz / clk_5x 371.09375 MHz / locked → rgb2dvi.aRst_n
VDMA(MM2S, 非SG, 2 帧存, MM 侧 100 MHz) ─AXIS─▶ axis_to_video（自产 720p60 时序）
                                              └─▶ rgb2dvi ─▶ TMDS N18/V20/T20/N20
```
- **删除**了 BD 的 `v_tc` 与 `v_axi4s_vid_out`（P3g/P3h 证明其不出 HS/VS/DE）
- VDMA AXI-Lite `0x43C00000`；欠载计数 GPIO `0x43C10000`；帧存 `0x20000000`/`0x20384000`（1280×720×32bpp、stride 5120、帧 3,686,400 B）

## 3. G3 五项（S6-A..F）逐项

| 项 | 要求 | 结果 | 证据 RunId |
|---|---|---|---|
| **S6-A 上屏** | 720p60 稳定出图，无撕裂/花屏 | ✅ `fps_dis=60`、运行期欠载 **0**、Wong 目视确认画面干净（真实手图 + 3 框 + 面板） | `s5_g3_a_p3n_20261030_r02`、`s5_g3_n_realimage_hold_20261030_r01`（照片） |
| **S6-B 时序/DRC** | WNS/WHS ≥0、TNS/THS=0、DRC 0 error | ✅ +4.252/+0.056、0 失败端点、DRC 0 error | `s5_p3n_hw_20261030_r01` |
| **S6-C 帧数据一致** | 应用与 JTAG 读帧存一致 | ✅ JTAG 整帧 CRC-32 `0xFE1A71E6` == 应用 `fb_crc` | `s5_g3_c_fbcrc_p3n_20261030_r01` |
| **S6-D 叠加坐标** | 已知框 → 期望 CRC/坐标 | ✅ `box_crc=0x2D949C0C`、`nbox=3`、`src=real`、hex 逐项一致 | `s5_g3_b_box_p3n_20261030_r01` |
| **S6-E 回归** | P2d 冻结回归在新区位流上不退化 | ✅ 见 §5 | `s5_g3_d_*_p3b_20261030_r01`（P3b 上）+ 见 §5 |
| **S6-F 长稳** | ≥30 min 无死锁、`vdma_err=0` | ✅ 30.4 min、tick 29 条、**最大间隔 60.2 s**、`vdma_err=0` 全程、`fps_dis=60`、帧号 60→53,940 | `s5_g3_e_longrun_p3n_20261030_r01` |

## 4. 上屏证据（Wong 拍照）

1. `report/evidence/S5-T01/s5_g3_n_realimage_hold_20261030_r01/photos/real_image_boxes_panel_20261030.jpg`
   —— 左侧 960×720 真实手部图像（HaGRID fixture）+ 3 个检测框（`@100,80 120×200`、`@500,300 100×100`、满幅边框），右侧 320×720 面板（`SRC REAL`、`FPS D 60.0`、`FPS U 29.9`、`VDMA RUN`、`DET 03`、三框坐标、类别图例、`P3B-SW r06`）。肤色自然 ⇒ 红蓝未互换；无撕裂/黑带。
2. `report/evidence/S5-T01/s5_g3_n_static_hold_20261030_r02/photos/panel_ok_video_noise_20261030.jpg`
   —— 面板完美渲染；视频区噪点源于 `0x12000000` 断电后垃圾字节（非显示缺陷）。

## 5. 回归（S6-E）

P3b 位流上（含显示链的合并体）重跑阶段4 冻结回归 3 项，全部与 P2d 一致：
- M4-b 收口 `pass=1`、`diff13=0/diff26=0`、**47,287 ms**（`s5_g3_d_m4b_p3b_20261030_r01`）
- chain-lite A `pass=1`、`decode_rc=0`、47,287 ms（`s5_g3_d_chaina_p3b_20261030_r01`）
- preproc→DMA 张量 CRC `0x5B183B50` 一致（`s5_g3_d_crc_p3b_20261030_r01`）

> 说明：P3n 与 P3b 的差别是"显示链实现"（VTC/vid_out → axis_to_video + 数据面 100 MHz），计算/链路侧 BD 未变；如需在 **P3n** 上补跑同一回归，待阶段4 硬件窗口（与 M3 遗留项一起排）。

## 6. 长稳（S6-F）

**PASS**。窗口 2026-10-30 17:49:14–18:19:41（30.4 min），P3n 位流 + P3n 长跑 ELF：
- tick **t=60 … 1740（29 条）**，**最大间隔 60.2 s**（远小于 130 s 判据）⇒ 无死锁；
- **`vdma_err=0` 全程**、`fps_dis=60`、帧号 60 → **53,940**（约 1,798 帧/min 的稳定推进）；
- 证据 `report/evidence/S5-T01/s5_g3_e_longrun_p3n_20261030_r01/`。

## 7. 本轮定位并修复的四个根因（供后续阶段参考）

| # | 根因 | 修复 |
|---|---|---|
| 1 | TMDS 引脚抄自 `course_s1/02_hdmi_out_test` 工程（U13/W14/Y18/Y16），与本板不符 | 改 `N18/V20/T20/N20`（ALINX demo XDC，10-22 亮屏基线实证） |
| 2 | BD 的 `v_tc` + `v_axi4s_vid_out` 不出 HS/VS/DE（屏判"无信号"） | 删除，改自写 `axis_to_video` |
| 3 | VDMA 带宽 190 MB/s < 需求 221 MB/s（13.1% 欠载，`1−52/60`） | VDMA 数据面 100 MHz ⇒ 欠载 0、`fps_dis=60` |
| 4 | A/B 两帧存内容不同 ⇒ 30 Hz 交替闪烁 | 两帧存画同一内容 |

另有两条关键方法结论：
- **不用厂商另一工程的约束替代本板事实**（引脚错就是由此产生）
- **必须先做阳性对照再下因果结论**（10-22 基线亮屏否定了"板卡通路坏"的早期判断）

## 8. 遗留与未验证

1. **P3n 上的计算回归**未跑（P3b 上已跑，S6-E 以 P3b 结果为据）；建议与阶段4 遗留 M3 一起排板级窗口补跑。
2. 有界 ELF 结束后 VDMA 会被软件停止（画面停/黑属预期）；需要长时间亮屏用"停核 + VDMA 继续读"的静态挂屏方式。
3. `hdmi_oen`(V16) 与 HDMI **无电气连接**（走 J20.21 扩展排针，Codex 图纸实证）⇒ 该信号在任何后续位流中都不应作为 HDMI 使能。
4. **VDMA 飞带宽**：P3n 数据面 100 MHz 已验证可支撑 720p60；若后续叠加更多 PL 负载需复测欠载。
5. `axis_to_video` 的 `tlast_misalign` 计数未引出 GPIO；P3p（fsync 版，`25cba4ec…`）已构建但**未采用**（P3n 目视无撕裂）。
6. SG（描述符环）双缓冲未做，软件当前用"非 SG + 每帧只写非在读 buffer"。

## 9. 复现命令（安全入口）

1. 起 `hw_server`（3121）、枚举 A9#0/#1；
2. `loadhw`（P3n XSA）登记地址；
3. `rst -processor -stop` 两核；
4. SLCR `0xA`（`0xF8000008=0xDF0D`、`0xF8000900=0x0A`、`0xF8000240=0`、`0xF8000004=0x767B`）；
5. `xsdb fpga -file s4d_p3n_r01.bit`；
6. P3n XSA 的 `ps7_init` + `ps7_post_config`；SLCR `0xF8000900=0x0F`；
7. （可选）写 raw 图像到 `0x12000000`，回读校验；
8. `dow -force s5_display_app_longrun.elf` → `con`；
9. 观察 UART：`fps_dis`、`TEST PATTERN DRAWN`/`src=real nbox=3`、`vdma_err=0`；
10. 收窗：`rst -processor -stop` → 杀 `hw_server` → **禁止 `rst -system`**（会清 fabric 导致 CSR 读挂死）。

## 10. 边界

- 未写 QSPI/Flash；未改线；未 push；
- 未主张 G4/G5（G4 需剩余遗留项与记录签字）；
- 本记录只覆盖阶段5 的显示链，不覆盖阶段4 的 M3 遗留项（R-01）。