# S2B-T20 独立 G2 审查：阶段3现场恢复2B

- 最终结论：`PASS`（静态审查；未运行恢复脚本或操作硬件）
- 最终审查对象：`D:\FPGA_Competition\w2b\tmp\2B\restore_2b_after_stage3_20261021.py`
- 最终 SHA-256：`84BD9AD81E818F0A450706E3CDF7FB6FC5E4C8DB5288FCB0E03321D167EF5E79`
- 首轮 SHA-256：`F500A632B9FD1AE50E11D6BB7478E3BB20B162CA4A11A248054DDC68A06A9136`
- 审查范围：恢复入口、绑定的2B控制器与CSR映射helper、本机 XSDB `target.py`、当前阶段3状态、阶段3 XSA HWH、AXI VDMA 官方头文件。未修改被审源文件。

## 首轮问题及关闭情况

首轮发现脚本将helper结果保存在独立 `hr`，但没有把实际SDK CSR映射范围、类型、flags 和清理结果写进最终 `restore_result.json`，故首轮为 `CHANGES_REQUIRED`。

最终版在第51行将 `hr` 引用放入最终 `record`；第115行把 helper 的 cleanup errors 归并到顶层 `record.cleanup_errors`，第116–118行保存结果并据顶层清理状态决定退出码。JSON 序列化发生在helper注册和清理之后，因此会包含实际映射及清理信息。首轮问题已关闭。

## 核查结果

- 阶段3门禁读取精确 `.codex/STATE.md` 最后一行，要求当前状态为 `OFFERED / DSH 阶段三总控`，并记录该状态文件SHA和最后一行；交接文档路径也经过精确路径检查。
- 脚本重新读取当前 Git HEAD，并对精确 runner 文件计算SHA，更新本次配置绑定；控制器对其所有绑定文件执行SHA核验。
- 阶段3 ELF有固定SHA；脚本通过CPU0 PC/CPSR及实读指令要求PC处16字节与该ELF唯一可执行段完全一致，随后才触及VDMA。
- 阶段3 XSA HWH显示 `0x43000000–0x4300FFFF` 与 `0x43010000–0x4301FFFF` 是两个 VDMA 寄存器窗口。脚本只读两窗口各自CR/SR两个字，并只清CR的RUNSTOP bit0、轮询SR的HALTED bit0。本机 Vitis 2026.1 `xaxivdma_hw.h` 的CR/SR偏移与位定义一致。
- 本机 Vitis 2026.1 `xsdb/target.py` 的 `mrd` 支持 `address_space="AP0"`。CSR helper校验唯一 `0x43C00000–0x43C0FFFF` 寄存器窗口及实际SDK映射 flags=3；最终版会将这些helper结果及清理状态保存。
- 异常路径在CPU0被触碰后尝试停止CPU0；`finally` 分别尝试关闭本控制器、清理本次映射、断开本入口创建的XSDB session、释放本入口XSDB对象。没有结束外部 `hw_server` 的动作。检查到的板上访问限定于目标核状态/寄存器、VDMA及2B控制器已用的复位/配置/CSR地址，未发现阶段3其它外设访问。

## 限制

本机 Python 3.12 进程启动被环境拒绝，未能运行 `ast.parse`。没有执行脚本、连接硬件、读取实板或复现本地权限检查。因此本结论是对最终SHA的静态G2审查，不构成恢复成功、板测验收或G3/G4证据。
