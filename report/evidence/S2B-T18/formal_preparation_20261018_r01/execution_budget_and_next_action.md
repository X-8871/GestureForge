# T18 正式执行准备摘要

状态：`NOT_READY_NOT_FOR_EXECUTION`。本目录只保存离线准备；没有接触硬件、SDK、串口或 Vivado。基线 HEAD 为 `ce2db7437c1c067fdce826afcc8913033eea3dcf`。

## 可复用的输入

- 直接复用 `report/evidence/S2B-T18/model_assets_20261016_r02/prep/preparation.json`，原字节 SHA-256 为 `be9868e11214dd6ce64cde825e6b6dcc70690653eab9afa2de3a6d22f33d655e`。不重跑 prepare、不重算 CPU 黄金。
- 已离线重哈希该清单中的 109 个输入、109 个 reference 和 GF8 权重；均与现有清单一致。逐项映射在 `inputs_map.json`。
- T18 model scope 必须在新 epoch=0 会话先 LOAD 权重，再按索引 0–108 各跑一次，最后对 sample000 输入做 repeat=1000。全部响应需保留原 UART、两头 INT8、所有框并通过黄金比较。
- CSR scope 是独立新 RunId/config，固定次序为 sample000 seed、busy START 拒绝观察、sample000 reaccept、ABORT recovery、静止 CSR 负向矩阵。它不能代替 109/1000；当前 helper 明确保留 short_deadline、busy_start 静止矩阵和 wire_after_external_csr 的既定 BLOCKED 限制。

## 预计时间

既有 preparation 对 T18 正式 scope 的估算为：权重串口传输 513 秒（8 分 33 秒），109 输入串口传输 4,913 秒（81 分 53 秒），sample000 连续 1000 次计算约 6–24 小时；均标记 `ESTIMATE_NOT_MEASURED`，不是实测。仅串口传输与最短压力估算合计至少约 7 小时 30 分。若从 2026-10-18 19:00 开始，最短估算也到 2026-10-19 02:30 以后，尚未计入配置/复核、CSR 场景及恢复时间，因此不能预计 109+1000 和 CSR 在今日内完成。不得因此缩短指标或改超时标准。

## 当前缺口与之后动作

1. 等当前 `single_sample_qualification_20261018_r02` 有终态，再由总控核对资格结果、独立审查和真实原始证据；qualifier 的 PASS 也不能直接当 T18 109/1000 PASS。终态生成后读取：

```powershell
Get-Content -Raw -LiteralPath 'D:\FPGA_Competition\w2b\report\evidence\S2B-T19\single_sample_qualification_20261018_r02\model_qualification_result.json'
```

若文件尚未生成，停止在此等待现有运行，不重启、不另开板上任务。
2. sample000真实完整双头/框比较通过后，按 `gate_schemas_and_open_inputs.json` 生成 visibility1 proof 所需的 HP路径、PS cache/arena、同 ELF/BSP/MMU/宏、POR、UART及 DAP 证据，再由独立 Reviewer 固定 proof 原件 SHA。当前 r02 cache probe 只能作为 256 B CPU↔DAP prior observation 的一部分，不能证明 32 MiB、HP0、模型数据或冷生命周期。
3. 独立审查最终平台 manifest 与 visibility1 proof 兼容性，形成最终 review；再依据当前接口文档版本/原字节、preparation、build/ELF/XSA/bit、proof/reviews、deadline 配置生成正式 G0 receipt 和冷生命周期 receipt。二者必须分别有独立审查来源与固定原字节 SHA。
4. 当前 runner 的 G0/COLD 四个 pin 是 `None`。凭真实 receipt 固定 path+SHA 后，修改 runner pin；保持 live HEAD 未变，以改后 runner 原字节 SHA 绑定配置，之后分别用不同 RunId 运行 model、CSR scope。运行后再提交 pin 与证据，报告运行时 HEAD 基线和源码哈希，不声称运行时 HEAD 包含未提交 pin。

满足上述门禁并经总控确认后，正式 model 入口形态为：

```powershell
& 'D:\Xilinx\2026.1\Vitis\bin\vitis.bat' -s 'D:\FPGA_Competition\w2b\vitis\run_s2b_model_acceptance.py' --config 'D:\FPGA_Competition\w2b\report\evidence\S2B-T18\<model-config-run-id>\config.json' --scope model
```

CSR 必须使用另一个 config/RunId 并改为 `--scope csr`。此命令现在不可运行：配置草稿显式 NOT_READY，runner pin 仍为空，且当前 qualifier 尚无已核实终态。
