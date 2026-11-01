# 既有 DDR 前置探测独立核查

- 判定：**限定范围 PASS**
- 对象：`report/evidence/S2B-T19/cache_probe_execution_20261017_r02/`
- 范围：旧 visibility0 平台上，PS CPU 与 JTAG DAP 在 `0x10000000` 处双向交换各 256 B；不扩展到 HP0、整片 DDR、PCB 器件身份或当前 R04 ELF。
- 方法：只读检查原始结果、调用记录、UART/JTAG 回执、输入绑定、执行源和构建清单；未运行测试，未连接硬件，未更改源文件、STATE 或 HEAD。

## 结论依据

阶段计划 [plan_b_execution_and_acceptance.md](../../../plan_b_execution_and_acceptance.md) 要求使用 DDR 的方案用明确地址范围做写读比对，并记录模式、次数与错误数。本次独立核查确认 2026-10-17 的 R02 确有早于后续模型压力运行的有限 CPU↔DAP 检查：

- R02 `visibility_probe_result.json` SHA-256：`85f7c52f9444ed1e62f490a85a1c632d837c043b53f0b625a12b4e8b99bde03d`。其 `cache_probe.status` 为 `CROSS_MASTER_256_BYTES_MATCHED`，地址 `0x10000000`，两个不同 seed：`722665479`、`722665480`；phase0/phase1 各有256字节真实UART回执，均为 `epoch=0`、`phys_status=0x400`、`error_code=0`、`response_code=0`。
- `jtag_result.json` SHA-256：`f28685606a00d374b092793a10dbadc62722a44113a0c80e1ea076014e25814f`；`jtag_calls.jsonl` SHA-256：`82256782e3dd1b06089892f1800e0a32bd813fa7275d8a4f97646b4a0f48c102`。JTAG调用记录中地址 `0x10000000` 的64-word DAP读、64-word `--bypass_cache_synq` 写、随后64-word读均返回；独立按冻结模式公式比对，phase0 CPU回执与DAP读值相符，DAP写值与phase1 CPU回执及DAP读值相符，四组均为64/64 word、零不匹配。
- 被执行的历史 `s2b_inference_app.c` 源 SHA-256 为 `9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39`，与构建清单及当前同路径源文件 SHA 相符。该版本 phase0 对 `arena` 写64 words 后调用 `Xil_DCacheFlushRange(..., 256)`；phase1 调用 `Xil_DCacheInvalidateRange(..., 256)` 再逐word核对DAP写入值。固定的 JTAG controller 源也在历史运行记录内绑定，`cache_probe` 的检查不匹配会抛错并使本次运行失败。
- `input_config.json` SHA-256：`2d7d4828121ed7f5e0c8b4877caf617a0d66bebd9220dd61c9753d872d5e67ef`。配置中的四项绑定均与实盘字节一致：历史 `init.elf`=`26824eb5…faaadc`、`infer.elf`=`a7fbbab2…02ce82`、编译 no-bit XSA=`0607120b…f04252`、bit=`cec64cd0…0145a`。实际 JTAG 调用记录含 `cpu0.dow.init` 和 `cpu0.dow.app`，目标路径与配置绑定吻合；历史构建的 implemented XSA=`d3f1f147…6ca938` 也与结果内绑定一致。结果 `saved_files` 所列哈希与实际JTAG日志和原始UART收发文件SHA相符。
- 前置检查发生于 `2026-10-17 02:12:15–02:13:33`（UTC+8）。成功的 `formal_stress1000_then109_20261018_r02` 模型运行从 `2026-10-18 23:45:16` 开始，晚于此探测。旧运行真实状态仍是 `API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`、`cold_lifecycle_proven=false`、`owned_hw_server_released=false`、`uart_failed=false`、`cleanup_errors=[]`、native exit code `0`；本判定不提升原运行状态。
- `current_probe_independent_20261017_r02/reviewer_outcome.json` 的 PASS scope 明确为 `visibility0_cache_probe_only_server_release_attachment`，只审查 owned hw_server 释放证据，不是DDR接受审查。本报告独立核验DDR证据本身。

## 当前 R04 边界

历史检查绑定的是 visibility0/T15-R03 构建；它不代表当前 R04 平台的DDR/cache结果。当前 R04 在线模型配置 R10 的实际绑定为：`init.elf=237dd959…79e7b1`、`infer.elf=a5149989…e090bf8`、visibility1 XSA=`ea52da1b…f5cb0eb6`、bit=`555a70c2…1047ef7`。这些都不同于历史运行所用的 init ELF、app ELF、XSA 与 bit。后续对重建 ELF 执行的 R04 双模式探测应独立记录；本报告不替代该项。

本 PASS 仅支持：在该次历史 visibility0 实物运行中，对 `0x10000000` 起始的256 B进行了CPU flush→DAP读，以及DAP写→CPU invalidate/读两种方向，观测为零不匹配。它不证明整片/32 MiB DDR、HP0事务或缓存可见性，不证明真实POR冷生命周期，不证明板卡料号或PCB接线，也不代表109/1000模型验收或G3/G4/G5通过。
