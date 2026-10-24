# Reviewer `CHANGES_REQUIRED` 勘误处理

被修订对象为 `t05_closeout_prep_20261024_r01`。本轮不改写该旧 RunId 的文件。

| Reviewer 问题 | 修正 | 证据/状态 |
|---|---|---|
| 旧 G2 清单及 README §3/§4 在窗口前写目视、耐久等未做，与后续证据冲突。 | 原文件字节保留；新 `g2_material_list_r02.json` 记录实际窗口结果和证据入口，旧计划标为历史。 | 原 README SHA-256 `d6046dfccc051adaa3dbc9e2ee20394e1aca9ab4d41ff9eb01a82c3bb16385b7`；原清单 SHA-256 `d777a976da1a9c34cddc6d58e989b5cb8c8e8d55b2c79c4fbf5c9bd33f6aa1a9`。修订待复审。 |
| STATE 仍称 DSH 当前唯一写者/DSH 评审运行，并称 task-11 阈值未核。 | 按 DSH-20261024-006 的正式交接更新当前负责人、写权与当前复审状态；记录静态 LUT4 `PASS_STATIC_THRESHOLD_DECODE`，RTL↔网表顺序等价 `NOT_RUN`。历史 DSH 作者/运行事实保留为历史。 | 同树 `.codex/STATE.md`；交接全文 `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261024-006-handover-main-write-right-to-codex.md`。 |
| 主仓决策记录缺 repo、HEAD、Git blob 和内容绑定。 | 对 C2/I/O delay 决策及人工目视记录绑定 repo、branch、HEAD、精确路径、Git blob OID、blob 字节数与 SHA-256。 | `source_bindings.json#main_repo_decision_records`；两文件均在该 HEAD 下可解析。 |
| `0x15810` 拆位遗漏 `IRQFrameCntSts`；清后 `0x11000` 未解释。 | 补 `IRQFrameCntSts=1` (`0x10000`) 及所有置位；说明 `0x11000` 仍含 count=1 + `FrmCnt_Irq`。保持 VDMA `PARTIAL`/根因 OPEN。 | `README.md` § VDMA；`g2_material_list_r02.json#vdma_sticky`；来源为 AMD PG020 v6.3 和 Xilinx 官方头文件。 |

旧 README 的板级项目表、旧清单的 reviewer scope 和待办是窗口执行前的计划。后续确已产生耐久和人工目视证据，因此旧文件不再是当前结果索引，但仍保留当时状态的历史记录。本次未执行硬件、Vivado、RTL 仿真或顺序等价检查；修订材料不等于 Reviewer 复审通过。
