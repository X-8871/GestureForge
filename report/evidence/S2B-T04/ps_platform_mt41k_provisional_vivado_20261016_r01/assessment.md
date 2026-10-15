# S2B-T04：MT41K 暂定 PS7 离线读回

日期：2026-10-16（UTC+8）。状态：`OFFLINE_CANDIDATE_READBACK_PASS_WITH_LIMITATIONS`。RunId：`ps_platform_mt41k_provisional_vivado_20261016_r01`。

## 执行范围

- 源码基线：`502ed0aa703d823ef8522db9f2bb065509080f19`；候选脚本为 `vivado/s2b_ps_platform.tcl`，版本 `1.0.2`。
- Vivado 2026.1，ROSS 会话 `vivado-20261016-013522-818e3111`，Tcl 模式，执行 `::s2b_ps_platform::run`，Vivado 返回码 0，历时 72.224 秒。
- 项目目标 `xc7z020clg400-2`；实际调用 `validate_bd_design`、生成 PS7 Block Design 输出并导出 XSA。XSA SHA-256：`c6f8f89181fca4a020a3391a60df8ab26967315c02765a51c88b7524d2507985`；BD SHA-256：`84068e94fb3b41ba079870e4a21c6c7f03da0085b747d59b1e6cf269439e4977`。
- 该流程没有连接 PL AXI、没有综合/实现或生成位流，也没有打开硬件管理器、编程器件、初始化或读写 DDR。XSA 内含 `ps7_init` C/H/Tcl 等 PS 初始化描述文件，但本次没有执行这些文件。Vivado 属性读回见 `readback.tsv` 和 `readback.tcldict`；完整原生日志见 `vivado_native.log`。

## 配置与读回

PS7 实际读回与本次暂定请求一致：DDR part number `MT41K256M16TW-107`、DDR 3 配置枚举、32-bit 总线、16-bit 器件宽度、4096 Mbits 单器件容量、row/column/bank 为 15/10/3、请求频率 533.333333 MHz；Vivado 读回实际 DDR 时钟 `533.333374 MHz`。块设计器件属性为 `xc7z020clg400-2`，UART1/MIO48..49 也与请求一致。

Vivado 基于该候选输入另外派生并读回 CL=7、CWL=5、speed-bin=`DDR3_1066F`、tFAW=25、tRAS(min)=34.0、tRC=48.91、tRCD=7、tRP=7，以及封装/时钟延时属性。这些是工具当前候选配置的读回值，不是针对当前实物颗粒、PCB 版次、电压或走线的时序资格结论。配置文件没有显式请求 CL/CWL、DDR 时序或板级延时。

## Vivado 诊断

- warning 计数存在未解释差异：`validate.tcldict` 的消息列表和截取输出各记录 2 条普通 warning（BD 5-700、BD 5-699），但同一结果记录 `native_counts_after WARNING=9` 和 `unprinted_warning_count=7`。当前保留的 `validate.tcldict.native.log` 只包含前述 2 条文本；其余 7 条 warning 的内容、来源、所属命令及影响均无法由本 Run 的现存证据确认。因此不能将这 2 条视作本次 Vivado 会话的完整 warning 清单，也不能推断未打印项无关或无影响。`validate_bd_design` 的 Tcl 返回码为 0，包装器观察到 0 critical warning、0 error；这只证明命令成功返回，不关闭上述诊断完整性缺口。

- `validate_bd_design -force` 返回成功，无 error 或 critical warning；产生两条普通警告：`BD 5-700` 没有匹配 PS7 Data 地址空间、`BD 5-699` 没有匹配地址段。该 PS-only BD 未连接 PL AXI，警告原文保留在 `validate.tcldict` 与原生日志中。
- 首次 `products` capture 因生成前后普通 WARNING 计数历史重排而记录 `FAIL`，Tcl 命令本身返回码为 0、没有 error/critical warning。脚本仅按既定的精确条件执行一次 `products_recheck`；复查返回 `OK` 后才继续导出。首次失败与复查收据均保留，不能把首次结果改写成成功。
- XSA 导出返回成功。XSA 包含 PS7 平台描述，不含 PL bitstream。

## 限制与验收边界

- `MT41K256M16TW-107` 仍是 Wong 暂定采用的手册料号；照片上的 `D9PSK` 尚未解码，厂家对实装料号的确认仍待回传。当前实物与料号、PCB 修订、电源轨和 PCB 延时的对应关系未确认。
- 尚无覆盖本板候选频率且绑定准确裸料号的可核验厂家时序输入；工具派生时序值不得据此用于板上 DDR 初始化或任务运行。收到厂家准确料号后必须重核配置与时序，并重新运行受影响检查。
- 本记录只证明 Vivado 对离线请求的属性读回、BD 验证、产品生成和 XSA 导出。XSA 与其中的 PS 初始化描述不得在准确实装 DDR 料号及板级资格确认前用于板卡初始化。它不证明实板 DDR 初始化/训练、PS 启动、UART、PL/HP0、32 MiB arena/cache 可见性、模型推理、100 样本黄金比较、1000 次连续任务、异常恢复或阶段 2B G0/G3/G4/G5。
