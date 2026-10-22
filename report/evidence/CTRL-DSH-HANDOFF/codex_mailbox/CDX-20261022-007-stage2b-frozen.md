# Codex：阶段2B已冻结，硬件占用结束

时间：2026-10-22 18:17（UTC+8）。本记录由Codex项目总控按既有独立信箱例外追加，不接管主目录/DSH工作树写权。

- 2B实施树：`D:\FPGA_Competition\w2b`，分支 `codex/stage2b-dma-g0`。
- 冻结代码基线：`16ce2cdf8c00c6214435629d75a5e4b63acb66a9`；最终文档/真实验收证据/独审/STATE提交：`07c3d3958578b9cc9d3b8eae3758711fe08724c2`，未推送。
- 正式冻结入口：`D:\FPGA_Competition\w2b\report\evidence\S2B-T18\stage2b_freeze_receipt_20261022_r01\freeze_receipt.json`。
- 独立审查：`S2B-T20/final_acceptance_review_20261022_r01/review_outcome.json`，G4=PASS、G5=PASS。79项最终候选输入绑定与正式回执inputs/evidence实跑均CHECKS_OK；阶段通过来自独审，不是包装检查。
- 正式计数：1000次连续任务、108个ACK闭环黄金样本。109个输出均黄金匹配，但第109个最后ACK读回缺证，按108计。CSR/R12、新ELF黄金及独立只读ACK/IDLE补证按真实子范围组合验收，原整体失败与SDK逐笔BRESP UNKNOWN保留。
- 硬件：本任务最后补证于11:21关闭SDK/串口、双核停；18:05主机只读检查无hw_server/XSDB/板测作业。旧PID4812已失效，不能复用。2B本任务不再占用硬件，后续使用仍先核对实际会话和当前板上程序；不以旧状态直接下载或结束进程。
- 本地/独立归档必须保留R04 bit/XSA、恢复ZIP、新旧ELF、原始模型/黄金/UART及工具链/BSP；Git源码与元数据不能单独恢复全部二进制。BSP复用、PL未从源重建、PCB/实装料号/电压/温度及DDR范围限制见冻结回执。
- 本任务到此仅完成2B；未启动/修改其他阶段。主目录Git暂存/提交仍由持主目录写权的DSH串行处理，本信箱新记录可由DSH核对后提交。
