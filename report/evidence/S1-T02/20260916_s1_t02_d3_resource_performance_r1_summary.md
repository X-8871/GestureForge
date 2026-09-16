# S1-T02-D3 资源、性能与阶段验收门槛

状态：`NOT_EXECUTED_PENDING`。本任务只冻结资源/性能测量口径和自动检查语义；没有伪造 Vivado 综合、真实板上测量或最终 FPS/延迟结果。

## 已编码门槛

- 硬件基线：AX7Z020 / XA7Z020 CLG400，`-1` 时序基线；LUT、FF、BRAM、DSP 分别不超过 85%；WNS/WHS 不小于 0，TNS/THS 必须为 0。
- tiny320、tiny416 分别作为板上候选预算；完整 YOLOv4 仅 PC 对照，板上资源验收为不适用，但保留 PC 计算/存储预算字段。
- 权重、feature map、frame buffer、PS buffer、DDR peak 分栏；DDR 带宽字段覆盖视频输入、模型传输、PS 解码/NMS、缓存竞争及总峰值。
- 每个固定配置要求 100 次 warmup、至少 10000 次有效推理，不筛快样本；分别记录 preprocess、PL/model、PS decode/NMS、display、end-to-end 的 mean/P50/P95/P99，并单列 timeout/drop/failure。
- `final_threshold_status=pending_until_wong_decision`；旧 20 FPS、100 ms、3–5 倍不作为现行门槛。

## 当前证据

- `estimate`、`synthesis`、`board_measurement` 严格分栏；当前缺少综合与板测，自动状态为 `NOT_EXECUTED_PENDING`，不是 PASS。
- 机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d3_resource_performance_r1.json`。
- 校验错误数：`0`；待执行/待决数：`168`。
- 当前未执行训练、CUDA 长测、Vivado 综合、上板烧录、板上性能测量和最终精度/性能判定。

## 关口状态语义

- G0：本规格和输入输出口径待总控/Wong确认；本报告不宣称正式 G0 通过。
- G1：检查器、测试和证据结构已实现；不等于资源或性能实测。
- G2：须由独立 Reviewer 核对版本、字段、边界和证据来源。
- G3：tiny 需要目标板综合/实现及板上实测；full 对板上资源不适用。
- G4：必须同时具备精度、数值、资源和性能适用证据，并经 Wong 决策冻结最终候选。

## 复现命令

```powershell
py verification\s1_t02_d3_resource_performance.py --input "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d3_resource_performance_r1_spec.json" --report "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d3_resource_performance_r1.json" --summary "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d3_resource_performance_r1_summary.md"
```

该命令只读输入并刷新机器报告/摘要，不启动训练、CUDA、Vivado 或硬件；非法百分比、时序、地址重叠、样本不足和错误证据来源返回非零退出码。
