# S1-T02-D3 tiny416 FP32 checkpoint 文件大小核验 R1

状态：MEASURED_EXISTING_FP32_DARKNET_CHECKPOINT_FILE_SIZE。HEAD：70f55a1c0321152151a6653b2d8a9b147e4154ea。

训练执行报告 SHA-256：6ebc69807fd6e08f8c33dab7204c193a9fc98646de9c329fd02c455c6c1fac0e；状态 EXECUTED_REVIEW_REQUIRED，退出码 0。Reviewer R2 审查证据 SHA-256：a177e1d60e53ec58f829f370370e50ed85dc7f14c1cdd1c08dcb4b7d85a84ca4，结果 PASS，共 29 项检查。

D3 scalar proxy JSON SHA-256：9da748b290cdefdaecd88d2c4b0bcd0fbfeadf1dae90f7deec659a16237be2ac。tiny416 FP32 scalar proxy 为 23,545,840 B。

| 文件 | 实测长度 | SHA-256 |
|---|---:|---|
| gesture_yolov4_tiny_416_d8_formal_6000.weights | 23,558,276 B | 3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a |
| gesture_yolov4_tiny_416_d8_formal_final.weights | 23,558,276 B | 3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a |
| gesture_yolov4_tiny_416_d8_formal_last.weights | 23,558,276 B | 3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a |

当前 checkpoint 与 final/last 别名的哈希和字节数一致。实测文件长度减去 D3 FP32 scalar proxy：23,558,276 - 23,545,840 = 12,436 B。这里仅记录差值，不推测其原因。

## 边界

这是对训练报告绑定的现存 FP32 Darknet checkpoint 文件做长度和哈希核验。不是 INT8 文件大小，不是参数标量代理，不是封装部署体积、整体 storage、上界或板上容量。未读取或解析权重张量内容；未运行 GPU、训练、推理、联网、综合或板测。
