# R-04 冷启动 VDMA 显示流：A/B 对照报告

- 生成：2026-10-31T01:45:36+08:00（UTC+8）
- A 冷启动：`r04_coldstart_vdma_20261031_r01`
- B 热机对照：`r04_hot_control_20261031_r01`

## A/B 现象差异表

| 项目 | A 冷启动 | B 热机 |
|---|---|---|
| RunId | r04_coldstart_vdma_20261031_r01 | r04_hot_control_20261031_r01 |
| 结论 verdict | R04_COLD_UNEXPECTED | R04_HOT_OK |
| fps_dis | 60 | 60 |
| read period (µs) | 16673 | 16673 |
| VDMA: init OK | 有 | 有 |
| UART WARN/vdma_err 行 | TEST PATTERN HOLD done, vdma_err=0 | TEST PATTERN HOLD done, vdma_err=0 |
| S5DISP 帧行数 | 24 | 24 |
| CR | 0x00010003 | 0x00010003 |
| SR | 0x00011000 | 0x00011000 |
| PARKPTR | 0x00010000 | 0x00010000 |
| VER | 0x62000050 | 0x62000050 |
| HSIZE | 0x00001400 | 0x00001400 |
| STRIDE | 0x00001400 | 0x00001400 |
| UF_FRAME | 0x00000000 | 0x00000000 |
| UF_TOTAL | 0x0D593000 | 0x0D20F000 |
| CSR2B | 0x53324250 | 0x53324250 |
| CR.RS(bit0) | 1 | 1 |
| SR.Halted(bit0) | 0 | 0 |
| SR.Idle(bit1) | 0 | 0 |

## 判据对照（VDMA 是否启动 / 读流是否在跑）

- A：CR.RS=1、SR.Halted=0、SR.Idle=0；fps_dis=60、period=16673 µs
- B：CR.RS=1、SR.Halted=0、SR.Idle=0；fps_dis=60、period=16673 µs

## 结论口径
- 若 A 满足 fps_dis=0 且 SR.Halted=0、B 满足 fps_dis=60/period≈16,667 µs ⇒ **冷启动特有 VDMA 读流不启动**，热机可恢复；
- 若 A 出现 CR.RS=0 ⇒ 软件未启动 VDMA；若 CR.RS=1 但无帧 ⇒ 启动了但读不到（帧存/带宽/PL 路径问题），需查 PARKPTR/STRIDE/HSIZE 与 HP 端口；
- 若 A、B 都异常 ⇒ 非冷启动特有，转到 PL/软件配置问题。
