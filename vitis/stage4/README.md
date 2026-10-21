# 阶段4 S4-B：PS 解码/NMS + s2bu/1.1 风格 UART 离线骨架

范围：**纯离线**。冻结 heads 输入 → C 解码/NMS → s2bu/1.1 风格 40 B 帧打包 → 主机解帧 →
与 Python 冻结 D9 对拍。不接触 PL、板卡、UART/COM4、JTAG/hw_server、Vivado/xsim；
本目录产物不代表 G3/G4/G5 通过。

## 文件

| 文件 | 作用 |
|---|---|
| `s4_ps_decode.h/.c` | INT8 → binary64 反量化 + 2A D9 冻结语义解码/稳定 NMS（阈值含等号、类别内 greedy IoU≥0.45、≤15 框、D2 整数 resize + 左上 floor pad 逆映射、稳定 tie 顺序） |
| `s4_uart_protocol.h/.c` | s2bu/1.1 帧 pack/unpack：40 B `<4sHH8I>` 头、`<Q8I>` 响应 meta、每框 `<ii5d>` 48 B、IEEE CRC32（`0xEDB88320`）；扩展 op/TLV 位置预留但默认关闭 |
| `s4_offline_host.c` | 主机 CLI：`--selftest`、`--bundle` 模式（解码 → 打包 → 解帧回读 → S4-A 字段结果 JSON） |

驱动与测试：`scripts/stage4_s4b/run_s4b_offline_chain.py`、`verification/test_s4_ps_decode.py`。

## 编译（真实命令，退出码 0、0 error、0 warning）

```bash
d:/mingw64/bin/gcc.exe -std=c11 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow \
  -I vitis/stage4 vitis/stage4/s4_ps_decode.c vitis/stage4/s4_uart_protocol.c \
  vitis/stage4/s4_offline_host.c -o tmp/4/S4B/build/s4_offline_host.exe
```

## 运行

```bash
# 1) CRC / 帧回读 / 篡改拒绝 / 扩展门闸自检（11 项）
tmp/4/S4B/build/s4_offline_host.exe --selftest --json tmp/4/S4B/build/selftest.json

# 2) 完整离线链（冻结样本 36/56/102：多框+边界裁剪、同框两类跨类不抑制、NO_HAND）
python -B scripts/stage4_s4b/run_s4b_offline_chain.py --run-id <run_id> --sample-indices 36,56,102

# 3) unittest
python -m unittest verification.test_s4_ps_decode -v
```

证据落点：`report/evidence/S4-B/<run_id>/`（`offline_chain_summary.json` 为机器可读清单）；
临时产物：`tmp/4/S4B/<run_id>/`。

## bundle 格式（驱动生成，主机只读）

little-endian，头部 72 B：`magic "S4BUNDL1"(8)`、`version=1`、`width`、`height`、`frame_id`、
`sequence`、`head13_len=5070`、`head26_len=20280`、`score_threshold`(binary64)、
`head13_scale`(binary64)、`head26_scale`(binary64)、`blob_crc32`、`candidate_limit`、`result_seq`，
其后为 head13/head26 的 INT8 原字节。主机校验头/长度/CRC，并保证只读不写输入缓冲区。

## 口径要点（与 S4-A 契约对齐）

- `candidate_count`：**阈值筛除后、NMS 前**的候选数，与 2A T29 `raw_candidate_count_before_stable_nms`
  及 2B 冻结实现同口径，也与 UART `raw_candidate_count` 同值（可被 T29 黄金独立验证）。
- `candidate_count_pre_threshold`：可选诊断字段（= 5 × 正面积候选框数），不进 UART、不参与对拍。
- `candidate_limit`：保持 2B 冻结候选缓冲上限 12675（= tiny416 理论最大候选数）。按 2B 参考实现
  （`S2A_T62_INVALID_ARGUMENT`）候选数为**硬错误路径**：达到上限即中止，**本合同不定义“截断到候选
  上限”**；本实现只在尝试追加第 12676 个候选时置位 `candidate_overflow` 并走 `state=ERROR`、
  `error_code=BAD_ARGUMENT(1)`、`detections=[]`，tiny416 固定配置下不可达，故恒为 false，但字段与
  “未超限”事实必须显式保留。候选上限（12675）与 NMS 前 15 框截断 / NMS 后 15 框输出不得混用。
  S4-A 草案早期的 4096 已弃用，未启用。
- 时间字段：离线无 PL，`capture_time_ns/result_time_ns/inference_time_ns/end_to_end_latency_ns`
  按契约用 **0 哨兵**，并在结果元数据（非结果记录字段、不进 UART 帧）的 `measurement_scope` 中按
  `evidence_annotation.measurement_scope` 的键名标注
  `pl_timing/uart_transport/board_pl = NOT_EXECUTED_OFFLINE` 与 `unavailable_fields`；绝不冒充实测值。
- 扩展预留：`S4_UART_ENABLE_EXTENSION = 0`，保留 op 由 `s4_uart_op_is_reserved()` 拒绝；
  时间/丢帧/过期/`result_seq`/`state` 的传输扩展待 G0 决策（S4-A `uart_mapping.open_decision`）。

## 未执行 / 不适用

板上真实串口与 COM4、JTAG/hw_server/DAP、PL 加载与推理时间/期限/吞吐、Vivado/xsim/综合/仿真、
109 全量样本（S4-C 负责）、2B 实板验收。上述均不出现在本目录的任何结论中。