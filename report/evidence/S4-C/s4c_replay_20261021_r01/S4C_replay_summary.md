# S4-C 离线回放与对拍 RunId `s4c_replay_20261021_r01`

- 任务：S4-C（阶段4 离线准备），状态：**FAIL**
- 开始/结束：2026-10-21T21:45:15+08:00 → 2026-10-21T21:45:42+08:00（UTC+8）
- 执行环境：Python 3.12.10；纯 CPU 离线；未使用硬件/串口/Vivado/xsim
- 工作树提交：`6a666ff73e0218177f66fb17fbe1d22acd752a8a`（分支 `stage4-infer-prep`）

## 口径
- 阈值 score ≥ 0.25（含等号），NMS IoU 0.45，每图 ≤ 15 框；离散字段（框数/class_id/class_name/source_order）必须完全相同。
- score 与 xyxy 各分量绝对误差 ≤ 1e-6，相对容限 0（S2A-T01 规格第 75 行）。
- 两头 INT8 字节 SHA 必须与 T25 索引和 T29 reference 完全一致后再解码。
- 几何取 T29 `input.geometry_wh`（width,height），与 T25/T01 交叉核对。

## 结果
- 全量 109 样本：109/109 PASS，mismatch=0，字节 mismatch 样本=0，框 mismatch 样本=0，最大 score 误差=0.0，最大坐标误差=0.0，框数 104/104。
- 耗时 21.57s，tracemalloc 峰值 25.8 MiB，RSS 峰值 44.1 MiB。
- 子集（--limit 8 --seed 20261021）：8/8 PASS，seed=20261021（cli），样本：['test_fist_001', 'test_one_040', 'test_one_048', 'test_one_049', 'test_one_051', 'test_two_up_069', 'test_two_up_074', 'test_three_081']。
- --actual 正对照：PASS
- 反例（驱动侧 1 字节篡改，样本 `test_fist_000`，head13 字节 0 由 3 改为 2）：退出码 1，定位字段 ['head13.tensor_sha256']。
- 篡改自检：全部探针检出=True，退出码=0。
- unittest：33 个用例，结果 OK。

## 证据文件
- `s4c_run_manifest.json`（机器可读总清单：命令/退出码/哈希/口径/统计）
- `replay_golden_109.json`（全量 109 逐样本逐框明细）
- `replay_subset8_seed20261021.json`（种子化子集）
- `replay_actual_pristine_test_fist_000.json`（--actual 正对照）
- `replay_actual_tamper_test_fist_000.json`（--actual 反例，退出码 1）
- `selftest_tamper.json`（篡改探针自检证据）
- `manifest_head_crosscheck.json`（T01 manifest 头部常量交叉核对）
- `unittest_s4_replay_compare.txt`（回归输出）
- `console/*.txt`（每步真实 stdout/stderr 与退出码）

## 限制与未执行项
- 纯 CPU 离线对拍：无硬件、无 hw_server/JTAG/COM4、无 Vivado/xsim。
- 只对拍 2A 冻结的 CPU golden；不产生精度、时序或上板结论。
- T25 分片按需流式读取，未复制进本工作树，也不进入 Git。
- S4-A 契约为 DRAFT_NOT_FROZEN：仅对齐字段名与口径，不代表阶段4 G0 冻结。
- 不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。
- 阶段4 正式 UART/PL 实测联调未执行（待 S4-B 与实物）。
- 未执行：板上推理与实物验证（G3 不适用本任务）
- 未执行：阶段4 正式 UART 联调与 PS 侧解码实测
- 未执行：RTL 仿真/综合与 Vivado 流程

> 本摘要不替代机器可读证据，也不代表阶段4 G0/G4/G5 验收或任何实物结论。
