# S3-T05 VDMA 启动边界诊断 ELF 构建记录

- RunId：`t05_vdma_start_trace_20261026_r03`
- 结果：**make-only 构建通过；未进行板上运行验证**。
- 基线：阶段三工作树 `D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，提交 `d0697672ddd106e948be3670f59e91a28f4d8860`。
- 目的：在既有 v12 诊断应用上叠加 v13 只读插桩，记录 VDMA API 调用边界的 S2MM CR/SR、VSIZE、HSIZE、STRIDE、帧地址及 API 返回码。

## 可复核文件

- [交付核验清单](delivery_manifest.json)：仓库标准 `inputs` / `evidence` 只读检查入口。
- [机器可读构建记录](build_record.json)：输入、命令、工具、输出哈希及限制。
- [make-only 构建脚本](build_make_only.ps1)：先复制全新应用与既有 BSP，再依次应用 v12 和 v13 补丁；目标已存在时会停止，不清理旧目录。
- [make 构建日志](make_only_build.log)：包含实际编译/链接命令与 `BUILD_RC=0`。
- [ELF 头核验](readelf_header.txt)：确认 ELF32 / ARM / EABI5 hard-float，退出码 0。
- 补丁：[s3_t04_app_diag_v13_vdma_start_trace.patch](../../../../board/stage3/software/sensor/s3_t04_app_diag_v13_vdma_start_trace.patch)，SHA-256 `019ea44bf299f27d8a6bdefb91d2bf978c7e952fa2aceb440dcd18e93a060884`。
- ELF：`D:\codex-worktrees\dbdf\tmp\s3r06\t05_vdma_start_trace_20261026_r03\app\an5642_j11cmos2_v13_vdma_start_trace.elf`，SHA-256 `84bddf04f482baee08aaf6a2df84cdec9d514b508e2a0fb08b351b5266cadedb`，310,404 字节。

## 判读边界

参数寄存器回读由绑定 BSP `xparameters.h` 的 `XPAR_AXI_VDMA_1_ENABLE_VIDPRMTR_READS=1` 支持。快照均为 MMIO 读取，不清除状态位、不写寄存器。v13 记录的是软件观察到的 API 边界，不能定位 `XAxiVdma_DmaStart` 内部的精确置位时刻，也不能观测 AXI-Stream 每拍握手。

每个边界样本执行 6 次 MMIO 读，可能轻微改变相邻启动 API 的调用间隔；本次没有测量采样耗时，诊断 ELF 不应视为无扰动时序基线。

本次只编译 ELF，没有运行 Vivado、下载、烧录或操作硬件。板上采集、VDMA 首置位根因关闭以及阶段 G3/G5 仍未完成；本构建不构成阶段冻结。

r01、r02 是编译前的隔离设置失败，失败说明各自保存在对应 RunId；未复用或覆盖这两个目录。
