# long_run RunId `s5t03_offline_long_run_replay_20261026_r04`

> **数字口径声明**：本摘要的提交号、测试数、耗时、计数与不变量**逐项取自本包**
> `results.json` / `manifest.json` / `console/run.txt` / `console/unittest_all.txt`（机器可读权威）；
> 摘要若与之冲突，**以 JSON/日志为准**。本摘要由生成器按上述文件派生，不做模板复制。

- 生成时刻（本包 `results.json.generated_utc8`）：2026-10-26T22:45:10+08:00
- 被测代码提交（本包 `source_commit`）：`e6ac5af28333…`
- 状态标签：`PRELIMINARY`；输入范围：`synthetic_replay`
- 本包独立套件日志：`Ran 75 tests` / OK（日志 SHA `d6c99402e27e…`）
- 命令：
  ```
  python -B scripts/stage5_t03/s5t03_long_run_replay.py --out report/evidence/S5-T03/s5t03_offline_long_run_replay_20261026_r04 --keyframe-max 16 --stage3-binding <binding> --demo-mp4
  ```

## 1. 长跑口径（判据用区间数）
- 帧数 **106573**；帧周期（离线虚拟步长）`16890000 ns`
- 区间数 `period_count=106572`；虚拟时长 **1800001080000 ns = 1800.001 s**（要求 ≥ 1800000000000 ns）；余量 `1080000 ns`
- 规范长跑：`canonical_long_run=True`（最少帧数 106573）
- 处理耗时（离线计算，非墙上运行时间）：**137.551 s**

## 2. 不变量
- 每显示帧恰好一次提交事件：`True`（死锁判据：`one_commit_event_per_frame（每显示帧恰好一次 overlay 提交事件）`）
- 时间戳单调：`True`；计数可复算：`True`；断言覆盖全帧：`True`
- ≥1800 s / 余量：`True` / `True`

- 14 项计数：`{"frames_committed": 106573, "overlay_drawn_frames": 76603, "boxes_drawn": 196510, "warmup_frames": 0, "dropped_frames": 3330, "timeouts": 6660, "error_results": 3330, "invalid_records": 3330, "stale_cleared": 3330, "duplicate_results": 3331, "duplicate_frame_id_results": 0, "out_of_order_results": 3331, "zero_hand_frames": 3330, "zero_area_dropped": 39962}`
- 关键帧 21 张；`demo.mp4` `GENERATED`（`demo_only`）；断言行 106573

## 3. 限制（本包自述）
- 输入为合成流；虚拟时间不是墙上时间，capture_time_ns 是合成单调时钟值。
- 本长跑只覆盖**显示/叠加路径**；inference_fps=NA，不得据此声称推理 30 分钟无死锁。
- 真实回放接入 / 板上绘制 / 摄像头路径 NOT_RUN。
- 逐帧断言为 compact（不含逐框像素表）；像素级细节在关键帧条目与事件日志中。
- PNG/MP4 不是验收依据（JSON/日志为权威）；G0/G1/G3/G4/G5 均未通过。

## 4. NOT_RUN（本包自述）
- 真实回放接入（无阶段4 冻结回放结果包）
- 板上动态映射与绘制（本轮不接板卡）
- 摄像头真实采集路径
- 真实推理 30 分钟联调（本长跑只覆盖显示/叠加路径；inference_fps=NA）
- T5-10 板上回归

## 附：可复现信息与绑定口径（第 5 轮复审 O-5/O-6 补记）
- 本包套件命令（另见 `console/suite_command.txt`）：
  ```
  python -B -m unittest scripts.stage5_t03.test_s5t03_json_contract scripts.stage5_t03.test_s5t03_multi_geometry_render scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton
  ```
- **绑定口径**：`manifest.tools[]` 绑定的是**驱动/渲染/参考/参数**文件哈希（运行产物由它们决定）；
  测试文件**不在** tools 中绑定，因此套件日志用于证明"当前代码库能通过全部测试"，不构成产物溯源的一部分。
