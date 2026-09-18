# S1-T02-D3 权重标量负载代理估算 R1

- 状态：ESTIMATE_ONLY_SCALAR_PAYLOAD_PROXY。
- Git HEAD：af3c1d5922390948ac3777784100ed68073b21fd。
- 输入绑定：D1 R3 8b7239a9c3cec511b5cb5e8795f2670fe0601cbcc90592bde70c01d205a9c12d；D2 R2 14e61b90e0eac8a9a96ffcbf326ff7784e896b12fa293ef01a86892dbc7f58d6；D3 资源规格 d25ca3903d13ff2224b187c74f5795965aa20d7cba08a6cd2d6839ce4ee57226。
- 口径：从 D1 的参数计数 N 计算 FP32 bytes = N × 4 与 INT8 scalar bytes = N × 1。D1 的 N 是外部 cfg parser estimate；乘法本身为整数精确计算。D2 的 INT8 值域是 [-127,127]，zero-point 为 0。

| 模型 | 输入 | D1 参数 N | FP32 标量代理 | INT8 每参数 1 byte 代理 |
|---|---:|---:|---:|---:|
| tiny320 | 320×320 | 5,886,460 | 23,545,840 B；23.54584 MB；22.4550628662109375 MiB | 5,886,460 B；5.88646 MB；5.613765716552734375 MiB |
| tiny416 | 416×416 | 5,886,460 | 23,545,840 B；23.54584 MB；22.4550628662109375 MiB | 5,886,460 B；5.88646 MB；5.613765716552734375 MiB |
| full608（PC 对照） | 608×608 | 63,992,378 | 255,969,512 B；255.969512 MB；244.11154937744140625 MiB | 63,992,378 B；63.992378 MB；61.0278873443603515625 MiB |

full608/tiny 的参数数及上述统一标量代理比值公式为 63,992,378 / 5,886,460，约 10.871114048172。

## 边界

本报告只提供每参数标量负载代理，不是实际权重文件大小，不是总体部署存储量，也不是其上界。未计入 Darknet 权重格式额外 BN rolling statistics/header、BN-fold 与 bias 的实际编码、逐输出通道 scale、逐层 activation scale、对齐、padding、metadata、feature maps、frame buffers、PS buffers。它只属于 D3 estimate；D3 synthesis 和 board_measurement 不由本结果填充或替代。未读取权重或图片，未生成实际量化权重，未执行综合或板测。

生成环境中 Python launcher 启动失败，故使用 Windows PowerShell/.NET 完成生成和复核；失败信息记录在 JSON 的 tooling 字段。
