# 阶段3 VDMA 粘滞状态离线核对

- RunId：`t05_vdma_root_cause_offline_20261025_r01`
- 生成时间：2026-10-25（UTC+8）
- 源基线：`25629e507acb5b59486589481b4713a77a60e5d1`，分支 `codex/stage3-video`
- 范围：只读复核已提交的串口日志、VDMA IP 元数据/HDL 摘录、应用补丁与既有分析；未改代码、未运行 Vivado/仿真、未操作硬件。
- 结论：**`PARTIAL`，实际触发源仍未确定，阶段3 G5 不因此关闭。**

主要新事实：首次 `phase=0` 采样的 `S2MM_SR=0x00014810` 已有 bit11；到 `t=5` 的 `0x00015810` 相比仅新增 bit12。已提交的 IP 元数据将 bit11 标为 `SOFLateErr`，而 HDL 状态组装片段将它接到 `s2mm_fsize_more_or_sof_late_bit`；寄存器位不足以区分帧尺寸超过 `VSIZE` 与 SOF 迟到的具体触发过程。详见 [vdma_offline_root_cause_supplement.md](vdma_offline_root_cause_supplement.md)。

本包只补充新一轮离线分析，不重写先前窗口记录或 `vdma_fsz_more_analysis.md`。机器清单中的哈希检查仅证明当前绑定文件与本清单一致，不代表根因通过、硬件验收通过或阶段冻结。
