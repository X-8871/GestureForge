# 项目状态入口

更新：2026-10-14（UTC+8）。按根目录 AGENTS.md 恢复；先核对Git和实际证据，不将历史源码基线写作当前HEAD。

## 当前目标与器件基本事实

- 本窗口是阶段2B总控：持续完成固定模型部署、至少100个黄金样本、1000次连续任务与异常恢复，直至2B G5；不自动进入阶段3或推送。
- AX7020实物器件为 XC7Z020-2CLG400I，Vivado part为 xc7z020clg400-2，时序按 -2。Wong于2026-10-14明确确认此前照片中的同一块板也是该型号；旧XA解读不再作为身份冲突或部署阻断。
- 本轮实际Vivado查询唯一匹配XC7Z020/CLG400/-2，主XPR项目、综合、实现三个字段及visibility=1会话均匹配。当前事实入口为 board/README.md；厂商原件目录 D:\FPGA\AX7Z020\AX7Z020 保持只读。
- 分支 codex/stage2b-t01-board-audit；本轮文档修订起点提交 5b4b140d9540759a6940b339e93278371c06987e。恢复时以 git rev-parse HEAD 为准。
- Wong已授权本阶段必要的易失PL/PS下载、DDR模型装载与板上验证；不含QSPI等非易失烧写。板卡目前可保持断电，离线包与运行条件就绪后再通知接电源/JTAG/UART，保持JTAG模式。

## 已完成与证据

- 阶段2A已通过G4/G5并冻结：tiny416、8×8空间tile、8路输出通道并行、双检测头与PS解码/NMS。验收基线 671f9cf494b92ce182b3f1542fefd0cfd4b209f5，入口 report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md。
- 当前2A候选109/109整网仿真及D9对比通过，最大score/xyxy误差0；原始Run为 candidate8x8_109_20261006_130252、恢复Run为 candidate8x8_109_resume_20261007_023531。它们是离线逻辑证据，不是2B实板109样本结果，不重复运行。
- T19当前visibility=1平台以RTL源码基线 f92823f0bd577a49db543868f44c4f63b670d8e0 在XC/-2、50 MHz完成布局布线、bit与含bit XSA。WNS +0.229 ns/TNS 0/失败端点0，WHS +0.095 ns/THS 0，WPWS +8.870 ns；入口 report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/。
- 当前XSA SHA 90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065；bit SHA a3e87d076ac102a4927a20ffa1e80699c2a29b5bc1ad3eacd1d7623f9ccf43da，XSA内bit与独立bit一致。XA/-1补充分析仅针对其他器件条件，不作为本板时序失败依据。
- T15同XSA Vitis 2026.1离线构建通过：CPU0 BSP 102/102、infer.elf和OCM init.elf生成，独立复审PASS；入口 report/evidence/S2B-T15/visibility1_xsa_20261014_r01/。应用ELF SHA a7ca427ab06f5f81a650bcb0d2bda3ed0adb716c3c2cb226c34519e695d47869；硬件执行NOT_RUN。
- T19顶层恢复仿真R02/R04及独审通过，覆盖公开CSR超时停止、迟到响应排空、错误安全ACK重启与协议故障持续隔离；入口 report/evidence/S2B-T19/top_recovery_verilator_20261014_r02/、top_recovery_verilator_20261014_r04/。保留177/179条warning，不能继承为硬件通过。
- GP0 HWH静态审计已独审并提交 5b4b140：AXI3→AXI4-Lite、mode0，LEN连线仅静态；入口 report/evidence/S2B-T01/gp0_translation_mode_audit_20261014_r01/。当前补齐实际ELF的32位Device标量访问依据。
- 2026-10-09 PS初始化、UART与1 MiB DDR smoke有实板功能通过记录。后续旧平台CPU/DAP缓存预探针只覆盖起始256字节，不经过PL/HP0；不能作为当前平台32 MiB arena或整网可见性证明。
- 许可证问题已解决：有效Basic许可完成bitgen。历史许可证隔离与兼容审查入口 report/evidence/S2B-T17/basic_license_isolation_20261013_r01/、implemented_export_independent_20261013_r01/。

## 当前阻碍与在制事项

- PS/PL s2b-physical-candidate/0.1.1、UART s2bu-candidate/1.1 尚未整体冻结；器件身份已由最新实物确认关闭，不能继续列为阻断。
- 仍需收敛HP0非Bufferable完整路径依据、统一冷启动/排空恢复、32 MiB arena的实际BSP/cache访问与运行绑定；实际总线、延迟、可见性及恢复结果必须在受控实板测试留证。
- 整网core/drain部署期限尚未实测。32位全局core计数在50 MHz最多85.8993459秒；正在按实际tile复用/权重重读修正请求预算，静态估算不等于真实HP0延迟或上界证明。
- 平台检查器受限祖先目录枚举问题已实现修复：路径11项测试中10通过、1项因WinError1314跳过，静态preflight通过；计数文案修正后待最终独审与提交。入口 report/evidence/S2B-T19/platform_path_preflight_20261014_r01/。
- 当前完整平台尚未完成JTAG/PS/UART/DDR/cache联调、完整模型首次实板推理、100样本/1000连续任务及异常恢复；2B G0/G3/G4/G5尚未通过。

## 下一步与恢复限制

- 完成并提交路径工具修复、GP0软件输入契约及当前请求预算的独立审查；明确限定探针准入与G3动态验证边界，保留正式100/1000及恢复标准。
- 核对同一bit/XSA/ELF/BSP和冷JTAG生命周期，先执行受控CSR/cache先验与单样本整网，再执行正式黄金样本、连续任务和恢复矩阵；需要接板时再通知Wong。
- 历史板级调试失败、TCF memory map及目标枚举修复、unloadhw无进度原件见 report/evidence/S2B-T19/cache_probe_execution_20261013_r01/至_r04/、board_failure_packaging_20261013_r01/、server_starter_fix_review_20261014_r01/。不把启动器退出0当实际运行通过；SDK卸载根因仍UNKNOWN。
- 当前16 GB机器只运行一个重型任务。新增综合最多三次的历史追加预算已使用1/3；仅豁免4.5 GiB启动门槛，其他既有运行停止条件仍有效。轻量读报告/静态检查不算重跑综合。
- 仿真、独审、包装CHECKS_OK与实板分别判断；不改原始失败/冻结证据，不覆盖RunId，不降低指标。阶段冻结须绑定版本、完成适用验收、独审和精确Git提交。
