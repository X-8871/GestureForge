# S1-T02-D3 最大单层激活张量估算 R1

状态：ESTIMATE_ONLY_LARGEST_SINGLE_TENSOR。HEAD：4bdde64102228d6186f13baa01be20c459e299d1。

形状输入为 D1 R3 JSON，SHA-256：8b7239a9c3cec511b5cb5e8795f2670fe0601cbcc90592bde70c01d205a9c12d。INT8 语义输入为 D2 R2 JSON，SHA-256：14e61b90e0eac8a9a96ffcbf326ff7784e896b12fa293ef01a86892dbc7f58d6。D3 资源规格 SHA-256：d25ca3903d13ff2224b187c74f5795965aa20d7cba08a6cd2d6839ce4ee57226。

对每份 D1 output_shapes 数据，跳过 type=input，逐项按 N = width × height × channels 计算元素数，再选出最大值；并列项全部列出，按 layer 升序。D1 形状来自外部 cfg parser estimate。完整 full-map materialized 仅是单层张量的计算假设。

| 模型 | 检查的非 input 形状数 | 最大张量（layer、type、shape） | 元素 N | FP32 标量字节 | INT8 激活标量字节 |
|---|---:|---|---:|---:|---:|
| tiny320 | 38 | L0 convolutional 160×160×32；L8 route 80×80×128 | 819,200 | 3,276,800 B；3.2768 MB；3.125 MiB | 819,200 B；0.8192 MB；0.78125 MiB |
| tiny416 | 38 | L0 convolutional 208×208×32；L8 route 104×104×128 | 1,384,448 | 5,537,792 B；5.537792 MB；5.28125 MiB | 1,384,448 B；1.384448 MB；1.3203125 MiB |
| full608（PC 对照） | 162 | L0 convolutional 608×608×32；L9 route 304×304×128 | 11,829,248 | 47,316,992 B；47.316992 MB；45.125 MiB | 11,829,248 B；11.829248 MB；11.28125 MiB |

公式：FP32 bytes = N × 4；INT8 activation bytes = N × 1；十进制 MB = bytes / 1,000,000；二进制 MiB = bytes / 1,048,576。D2 激活语义是 per-layer/per-tensor symmetric INT8，值域 [-127,127]，zero-point 0；此处只计算激活标量字节，不含 scale 元数据。

## 边界

这只是最大单张非 input 层输出张量的 estimate，不是多个张量同时存活时的峰值，也不推断并发存活关系或整体缓冲规模。结果不覆盖多张 tensor 并存、branch/route retention、tiling、ping-pong、alignment/padding、DDR 或 buffers。它只属于 D3 estimate，不代表 synthesis 或 board measurement。本证据未改写 D3 规格中的存储字段；未使用 GPU，未训练，未读实际权重或图片。