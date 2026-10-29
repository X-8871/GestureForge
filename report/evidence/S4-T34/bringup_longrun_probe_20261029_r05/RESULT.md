# 长跑 r05 结果（判据常量修正后）

- 探针 ELF：`4ef402c7…efffee`（时间基座 + MIN_ITERS 修正版）
- **应用自身 RESULT**：exit=`0` iterations=`40` failures=`0` wall_ms=`1844812`（真实 30.7 min）within_judgement=`1`
- 每轮：elapsed_ms 恒 `47287`/`47287`；epoch 1..39；tensor_crc32 恒 `0x5B183B50`
- 主机/应用比值：`1.000`（时间基座修复生效）

## 结论

**A 项（长跑停住定位）按真实口径通过**：连续 40 轮 / 30.7 min 真实时间，零失败、零停住、每轮耗时稳定、epoch 单调、张量 CRC 恒定。

## 一处更正（诚实记录）

- 执行器 r03 的 `parse_result` 用 `json.loads` 解析 RESULT 行，但应用把 `box_*` 打印为裸十六进制（`"box_score_hi":3FDFA8EE`）⇒ 非法 JSON ⇒ 解析失败 ⇒ 被误判为 `FAIL`。
- 本节数据由 lead 用宽松正则重新解析 `W2_uart.log` 原始行得到；`results_diag_probe.json` 已加 `classification_correction` 字段，未删除原始 FAIL 记录。
- 已修正 r03 解析器（`parse_result` 改为宽松 kv 解析）供后续窗口使用。

## 边界

- 2B 平台位流 + SW 预处理 + fixture 非实拍；`ENABLE=0`；未写 QSPI/未改线/未 push。
- 不主张 G3/G4/G5；M2/M3 未闭合（M3 依赖 Codex DDR 工具）；本窗口只证明长跑不挂死与判据可达。
