# S1-T02-D3 存储分栏预算 R1

- 任务：`S1-T02-D3-STORAGE-BUDGET-R1`。
- 基线：`1218b029700a12c96c276b2d96059ae75033e59e`。
- 状态：`ESTIMATE_WITH_MEASURED_FP32_CHECKPOINTS_PENDING_DEPLOYMENT_STORAGE`。
- 范围：tiny320、tiny416 候选与 full608 PC 对照；未启动训练、GPU、网络、综合或板测。

## 可复核结果

| 模型 | FP32 权重标量代理 | INT8 权重标量代理 | 实际 FP32 checkpoint | 最大单层 FP32/INT8 激活 | 输入 FP32/INT8 | YOLO raw head FP32/INT8 |
|---|---:|---:|---:|---:|---:|---:|
| tiny320 | 23,545,840 B / 22.455063 MiB | 5,886,460 B / 5.613766 MiB | 23,558,276 B（实测） | 3,276,800 B / 819,200 B | 1,228,800 B / 307,200 B | 60,000 B / 15,000 B |
| tiny416 | 23,545,840 B / 22.455063 MiB | 5,886,460 B / 5.613766 MiB | 23,558,276 B（实测） | 5,537,792 B / 1,384,448 B | 2,076,672 B / 519,168 B | 101,400 B / 25,350 B |
| full608（PC） | 255,969,512 B / 244.111549 MiB | 63,992,378 B / 61.027887 MiB | pending 合规正式 checkpoint | 47,316,992 B / 11,829,248 B | 4,435,968 B / 1,108,992 B | 909,720 B / 227,430 B |

公式：权重代理 `N×4` 或 `N×1`；输入 `W×H×3×bytes_per_scalar`；raw head 为 D1 中 `type=yolo` 形状的元素和乘标量字节。十进制 MB 与二进制 MiB 在 JSON 中同时给出。

## 分栏边界

- **已实测**：tiny320 与 tiny416 的外部 FP32 Darknet checkpoint 文件长度和 SHA-256；三份 `6000/final/last` 别名各自一致。文件长度不等于 INT8 部署大小。
- **可估算**：FP32/INT8 权重标量代理、固定输入 tensor、最大单层输出 tensor、YOLO raw head payload。它们均不是整体峰值。
- **待完成**：真实 INT8 权重与 scale/metadata/对齐；full608 合规正式 FP32 checkpoint；解码后输出结构、PS 解码、NMS 工作区、帧缓存、route/tiling/ping-pong 临时缓冲、DDR 峰值/带宽。
- 不把权重、最大激活、输入和 raw head 简单相加作为 simultaneous live peak；D3 资源规范要求上述 storage 分栏，完整峰值需后续调度、综合或板上/运行时证据。

## 证据与复核

输入证据及 SHA-256 已写入 JSON 的 `source_evidence`。主要来源为 D1 R3 参数/形状、D3 scalar proxy R1、D3 最大单层激活 R1、D3 资源规范和 D8 tiny320/ D3 tiny416 checkpoint 文件证据。JSON 内 `arithmetic_validation.status=PASS`，包含输入元素数、raw head 元素数、权重乘法和 checkpoint 差值的逐项算术核对。

复现检查仅需 PowerShell/.NET 读取上述 JSON/外部 checkpoint 并执行整数公式；本轮未修改代码、STATE 或外部运行目录。该预算不产生精度、mAP、吞吐、延迟、Vivado 资源、时序、板容量或阶段1验收结论。