# 阶段3 G2 材料勘误与重固定 r02

- RunId：`t05_g2_reconciliation_20261024_r01`
- 生成时间：2026-10-24 19:43（UTC+8）
- 工作树/分支/基线：`D:\codex-worktrees\dbdf` / `codex/stage3-video` / `1d54894be4d547955034eeff8bce853dd4286fac`
- 仅离线整理证据；不修改业务 RTL、硬件或 Vivado 工程，不提交。

## 目的与状态

本 RunId 修订上一轮完整独立 G2 审查提出的四项 `CHANGES_REQUIRED`：旧计划文字与窗口后事实不一致、Stage 3 当前负责人/写权过时、跨树决策文件绑定不完整、VDMA 拆位缺少 frame-count status。旧 RunId `t05_closeout_prep_20261024_r01` 中的 README 和 `g2_material_list.json` 保持原字节；本包是当前入口与勘误，不覆盖历史。

**完整独立 G2 = `PENDING_REVIEW`。** 上轮结果仍为 `CHANGES_REQUIRED`；本修订尚无独立 Reviewer 结论。包装器 `CHECKS_OK` 只表示清单/哈希/目录封装通过，不等于 G2 PASS、G4 或 G5。

## 被审部署与已完成证据

审查对象为 2026-10-24 Stage 3 硬件窗口记录的 J11/CMOS2 无补偿实时彩色部署：bitstream SHA-256 `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`；XSA `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3`；应用 `an5642_j11cmos2_v10_read.elf` SHA-256 `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073`。这些身份限定当次被审部署；DSH-20261024-006 记载随后重新插接板卡，本包**不证明目前板上仍加载该部署**。下次硬件窗口仍须按交接要求重新核对部署身份、真彩目视和运行地址。

| 项目 | 当前结论 | 证据/边界 |
|---|---|---|
| 新模块颜色 | `PASS_VERIFIED_NEW_MODULE` | `t05_new_module_reverify_20261023_r01/`，6/6 哈希；蓝 bit7、绿 bit4 缺位签名消失；彩条满量程且顺序正确；实景 B/R≈0.85–0.99。颜色通过不替代完整 G2/G5。 |
| 实时耐久 | 完成，31 min 15 s、7 轮 | `t05_stage3_window_20261024_r01/README.md` §2.1；各轮退出码 0。仅是该次运行记录。 |
| 参考帧 | 已采集 | `t05_stage3_window_20261024_r01/reference_frame_set.md`；整帧 SHA-256 前缀 `939fce22` 与 3 行样本。 |
| 地址事实 | 已实测 | `t05_stage3_window_20261024_r01/address_facts.md`；S2MM 与 MM2S 同址 `0x00110C00`、单缓冲；运行期分配，不是静态保证。 |
| 真彩目视 | 人工通过 | 主仓记录见 `source_bindings.json`；Wong 2026-10-24 01:41：「画面可以接受，正常颜色」。仅对当时具体部署/端口/接线/显示链路有效，非仪器测量或像素对拍。 |
| task-11 静态阈值 | `PASS_STATIC_THRESHOLD_DECODE` | `task11_threshold_decode_20261024_r01/`；穷举 262,144 组、0 差异；仅 LUT4 静态组合函数。 |
| task-11 顺序等价 | `NOT_RUN` | RTL↔网表顺序等价、状态更新、复位、饱和及跨周期关系仍未验证。 |
| VDMA 状态 | `PARTIAL`，根因 OPEN | 拆位见下文；状态位义不能推断根因。 |
| 完整独立 G2 | `PENDING_REVIEW` | 修订包待 Reviewer 独立复审。 |
| 阶段3 G5 | 未通过、未冻结 | VDMA 根因、TIMING-17/36 与 I/O delay、无 ILA、task-11 顺序等价等仍未闭合。 |

## VDMA `0x00015810` 位拆解

`0x00015810` = `IRQFrameCntSts=1` (`0x00010000`) + `Err_Irq` (`0x00004000`) + `FrmCnt_Irq` (`0x00001000`) + `SOFLateErr/FSZ_MORE` (`0x00000800`) + `VDMAIntErr` (`0x00000010`)。W1C 后 `0x00011000` 仍含 frame-count status=1 与 `FrmCnt_Irq`，不表示所有状态位均为零。

现场记录为：启动时读到 `0x15810`，一次 W1C 后为 `0x11000`，后续 31 分钟 7 次回读未重现且无功能影响。AMD PG020 v6.3 将 S2MM 状态寄存器 bit 11 定义为 SOFLateErr，说明输入帧超过配置 vsize 时置位，该位本身不会使 VDMA halt，并标明 R/WC 与 flush-on-fsync 清除语义；Xilinx `xaxivdma_hw.h` 给出 `0x800` FSZ_MORE、`0x1000` FrmCnt IRQ、`0x4000` Err IRQ 与 `0x00FF0000` frame-count status mask / shift 16。此解码只解释位义，不说明触发源；故保持 `PARTIAL`，根因未定。

官方参考：[AMD PG020 v6.3 S2MM_VDMASR](https://docs.amd.com/r/en-US/pg020_axi_vdma/S2MM_VDMASR-S2MM-VDMA-Status-Register-Offset-34h)；[Xilinx embeddedsw `xaxivdma_hw.h`](https://github.com/Xilinx/embeddedsw/blob/master/XilinxProcessorIPLib/drivers/axivdma/src/xaxivdma_hw.h)。

## 文件与校验

- `g2_material_list_r02.json`：审查对象、交付证据、边界和未闭合项。
- `source_bindings.json`：dbdf task-11 四文件与两个 main 决策文件的 repo/branch/HEAD/blob OID/blob SHA-256 绑定。
- `review_errata.md` / `review_summary.md`：逐条修复与当前审查状态。
- `manifest.json`：本包清单；不在其自身 `files` 数组中。
- `SHA256SUMS`：固定负载摘要；不列自身或 manifest，避免自引用。manifest 绑定 SHA256SUMS；manifest 自身 SHA-256 在交付回执中报告。
