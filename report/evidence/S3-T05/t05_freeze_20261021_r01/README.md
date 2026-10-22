# S3-T05 阶段三 暂定冻结记录（2026-10-21 23:3x UTC+8）

## 0. 决定与依据

Wong 2026-10-21 23:2x 决定：黑白画面可接受，颜色项待**更换模块到货后**再复测 ⇒ **暂定冻结**（frozen-provisional），不宣称阶段完全通过。

## 1. 冻结配置（可复现）

| 项 | 值 |
|---|---|
| 工作树/分支 | `D:\codex-worktrees\dbdf` / `codex/stage3-video` |
| 硬件 | AX7020 + AN5642 模块插 **J11（CMOS2 通道）** |
| 位流（灰度，2026-10-21 冻结候选） | `tmp/s3r06/t04_gray_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` = `2f72aaa42936225eb7215bd8f138f68e52c27c3ab31ab236c8a3c15f7669af4f` |
| XSA | `tmp/s3r06/t04_gray_20261021_r01/design_1_wrapper.xsa` = `bb71c3f6e15b6f22fd0709373c3910f3dc4682214fb0cd6a9f69330a13eaaa12` |
| **部署位流（2026-10-22 12:4x Wong 决定按灰度继续后续工作）** | **标准亮度灰度** `tmp/s3r06/t04_stdluma_20261022_r01/.../design_1_wrapper.bit` = `44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb`，XSA = `90e1bdee1f5baaf9e772edcddc800aab6927d2099b54a45bc020025d82ccb1c4`；亮度式 `Y=(77R8+150G8+29B8)>>8`（**训练集转灰度须用同一整数权重**）；板上实测 `\|R−B\|=0.0`、`\|R−G\|≈\|G−B\|≈2/255` |
| 备选（仅留档） | 纯绿灰度 bit `2f72aaa4…`；补偿彩色 bit `30db09ba…`（`t04_dualmsb_20261021_r01`，**暂不使用**） |
| 应用 | `an5642_j11cmos2_v10_read.elf` = `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073`（TRY=0：只回读、不改寄存器） |
| 灰度补丁 | `board/stage3/software/sensor/alinx_ov5640_gray_luma.patch`（2601 B） |
| 启动器 | `scripts/stage3_t04/run_t04_camera_j11cmos2_gray_build.sh` |
| 构建 | `write_bitstream Complete!`、Vivado exit 0；WNS **0.422210** / TNS 0 / WHS **0.040176** / THS 0；DRC **0 Error**（8 Warning 同基线） |

## 2. 冻结时的板上实测（2026-10-21 23:2x）

- 帧地址核实：`S3_DIAG5_CFG ... ADDR=0x00110C00`，安全转储（halt→mrd→resume）3 行各 3840 B 成功 ✓
- **中性度**：`|R−G| = 2.0 / 1.9 / 2.0`、`|G−B| = 2.0 / 1.9 / 2.0`（y=100/400/600）⇒ **真灰**（残差为 5/6/5 位宽映射的 1 LSB）
- 传感器寄存器已由 init 表恢复：`0x5580=0x06`、`0x5583=0x40`、`0x5584=0x10`（回读一致）⇒ 先前失败的 sat0 改动已消除
- Wong 目视确认：画面为黑白 ✓

## 3. 灰度实现与边界（必须随冻结一起说明）

- 取**绿通道**为亮度：`G' = {G5,G4,G3, maj3(G3), G1, G0}`，新字 `{G'[5:1], G'[5:0], G'[5:1]}` ⇒ R=B=G'[5:1]、G=G'。
- **蓝通道被完全弃用**（它正是 MSB 坏掉的那一路）；**这是灰度补偿，不是修复**，不得用于颜色验收。
- 根因（模块侧 DVP 字节 MSB 线 `cmos_d[9]` 无信号）仍然存在，真实修复需硬件返修/更换。
- 补丁已由阶段总控**人工逐行审阅**（只改 FIFO `din` 前的灰度构造；tlast/tuser/tkeep/tvalid/tready/时钟未动）。

## 4. 未关闭项（冻结不清零）

1. **颜色验收**：待更换模块到货后复测（见 §5）；当前判"受阻/待硬件"。
2. **task-11 的网表交叉核对未完成**：dev-ila 在写证据/网表核对阶段失败；其 `build_report.json` 自标 `status=failed`。已用"人工审阅补丁 + 实机中性度指标"替代验证，但**不作为独立网表核对**。
3. **实时性已在本灰度位流上验证**：v10_read 运行中指纹 t=5/15/25 = `6BDB38A6` / `BC9D07B5` / `9159752F`（互不相同）⇒ 冻结配置实时 ✓（证据 `report/evidence/S3-T05/t05_gray_board_20261021_r01/uart_gray.log`）。
4. VDMA 粘滞错误 `0x00015810`、方法学 TIMING-17/36 critical 与 I/O delay 缺口、J10 "半屏黑"未定性、无 ILA 波形、未做 ≥30 分钟耐久。

## 5. 模块到货后的颜色复测步骤（可直接执行）

```bash
# ① 刷回无补偿基线（SOF 修复位流 7cb33068…8710）+ v9_read（只读）
bash scripts/stage3_t05/run_t05_board_capture.sh D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01 \
  D:/codex-worktrees/dbdf/tmp/s3r06/t04_j11cmos2_elf_v9/elf_build/app/an5642_j11cmos2_v9_read.elf retest 90
# ② 安全转储 3 行（手动新建空目录），再跑签名脚本：**修好则应"不符合签名"**
python scripts/stage3_t05/analyze_missing_msb_signature.py "<新目录>/row*.bin"
# ③ 彩条判读（0x503D=0x80）：色相与顺序正确；④ 白纸不再发黄 ⇒ 颜色项解除受阻
```

## 6. 证据入口

- 灰度构建：`report/evidence/S3-T05/t05_gray_20261021_r01/`（补丁、构建报告[含 `status=failed` 自标]、网表 trace 日志、时序/DRC 报告）
- 本冻结记录与板上实测：`report/evidence/S3-T05/t05_freeze_20261021_r01/`
- 根因判定：`report/evidence/S3-T05/t05_msb_line_diagnosis_20261021_r01/`、`t05_v9_board_20261021_r01/`
- 彩色补偿备选（未采用）：`t05_dualmsb_20261021_r01/`（bit `30db09ba…`）
- 交接与路线：`report/evidence/S3-CTRL/S3-T05/S3CTRL-20261021-003-handoff-to-dsh-stage3.md`