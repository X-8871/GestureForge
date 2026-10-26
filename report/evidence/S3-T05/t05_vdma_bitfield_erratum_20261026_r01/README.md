# 阶段3 VDMA 状态位勘误与根因边界

- 任务：`S3-T05`；RunId：`t05_vdma_bitfield_erratum_20261026_r01`。
- 分析基线：阶段3 HEAD `389acaf564cf268e96b564a4911fc75dab3f42fe`。
- 性质：只读离线核验；未访问或操作硬件，未改写旧 RunId 下的原始记录。

## 勘误

旧记录 `report/evidence/S3-T05/t05_stage3_window_20261024_r01/vdma_sticky_result.md` 第 11、20 行把 `0x00001000` 笼统称为“帧计数类状态位”。本材料保留旧文件原字节，精确解释如下：

- S2MM_VDMASR bit 11 / `0x00000800`：`SOFLateErr`；官方 PG020 v6.3 将它描述为 incoming frame size 大于 programmed VSIZE 时的 Start of Frame Late Error，并注明 VDMA 不停机。它是粘滞状态，不能仅凭寄存器快照反推出具体内部触发分支。
- S2MM_VDMASR bit 12 / `0x00001000`：`FrmCnt_Irq`，帧计数中断状态标志；**不是计数值本身**。
- S2MM_VDMASR bits 23:16 / mask `0x00FF0000`：`IRQFrameCntSts`，当前 interrupt frame-count status 值。

现有值 `phase=0: 0x00014810` 到 `t=5s: 0x00015810` 的 XOR 增量是 `0x00001000`，对应 bit 12 新置位。W1C 后 `0x00011000` 中 `0x00001000` 仍是 bit 12 状态标志，而高字节 `0x00010000` 是 bits 23:16 的计数状态值 1。不要把 `0x1000` 写成 frame-count 数值，也不要将 `0x11000` 整体解释成单一状态位。

## 根因仍开放

V11 诊断补丁在 `vdma_write_init()` 返回后才做 `phase=0` 寄存器采样；现有 5 秒间隔采样没有记录 reset、HSIZE/STRIDE、帧地址、CR.RS、VSIZE 启动与首帧边界之间的首次置位时刻。Vivado 2026.1 本地 VDMA v6.3 元数据/HDL和 v6.17 驱动支持上述位定义；官方 PG020 v6.3 在线页也核对一致。HDL 的 bit11 锁存逻辑关联帧尺寸比较和 SOF 时序状态，单个粘滞位不能唯一识别触发路径。

现有证据只证明 W1C 后 31 分钟 15 秒稳态期间没有再次观察到对应错误位，不能解释初始 bit11 来源，也不能证明 bit11 根因已经关闭。最小后续硬件证据必须将首次 bit11 置位沿与 VDMA 配置/启动（含 HSIZE、STRIDE、VSIZE）以及输入 AXI-Stream 的 TVALID/TUSER/TLAST/TREADY 对齐。BASIC 许可下无 ILA；若没有可用的既有采集路径，需要先准备并独立审查可行诊断手段及新硬件窗口。

## 来源与绑定

本地 AMD/Xilinx 元数据、HDL、驱动、V11 补丁、参考初始化源码和旧窗口记录的逐字节 SHA-256、精确路径与核验范围见同目录 `source_provenance.json`。本机未找到 PG020 PDF；官方文档页面为 [AMD AXI VDMA v6.3 PG020：S2MM_VDMASR](https://docs.amd.com/r/en-US/pg020_axi_vdma/S2MM_VDMASR-S2MM-VDMA-Status-Register-Offset-34h)，页面版本 6.3 English，发布日期 2022-06-08。

该勘误只关闭 `0x1000` 的术语歧义及本地位定义核对，不关闭 VDMA 粘滞 bit11 的触发根因，不提升实物验证状态，也不使阶段3 G5 通过。
