# short_run RunId `s5t03_offline_replay_display_20261026_r06`

> **数字口径声明**：本摘要的提交号、测试数、耗时、计数与不变量**逐项取自本包**
> `results.json` / `manifest.json` / `console/run.txt` / `console/unittest_all.txt`（机器可读权威）；
> 摘要若与之冲突，**以 JSON/日志为准**。本摘要由生成器按上述文件派生，不做模板复制。

- 生成时刻（本包 `results.json.generated_utc8`）：2026-10-26T22:48:37+08:00
- 被测代码提交（本包 `source_commit`）：`e6ac5af28333…`
- 状态标签：`PRELIMINARY`；输入范围：`synthetic_replay`
- 本包独立套件日志：`Ran 75 tests` / OK（日志 SHA `42e96f3bbc77…`）
- 命令：
  ```
  python -B scripts/stage5_t03/s5t03_replay_display.py --out report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r06 --mode mixed --frames 240 --keyframe-max 24 --stage3-binding <binding> --demo-mp4
  ```

## 1. 结果（240 帧 mixed）
- `checks = {"frames": 240, "assertions": 240, "failures": [], "passed": true}`；`recompute_matches_online = True`
- 14 项计数：`{"frames_committed": 240, "overlay_drawn_frames": 177, "boxes_drawn": 467, "warmup_frames": 0, "dropped_frames": 7, "timeouts": 14, "error_results": 7, "invalid_records": 7, "stale_cleared": 7, "duplicate_results": 8, "duplicate_frame_id_results": 0, "out_of_order_results": 8, "zero_hand_frames": 7, "zero_area_dropped": 89}`
- 关键帧 18 张；`demo.mp4` `GENERATED`（`demo_only`）
- 输入：`stage3_fixed_frame_input_only` / SHA `939fce22b7e8…`

## 3. 限制（本包自述）
- 输入为合成流；capture_time_ns 为合成单调时钟值，不是真实采集时刻。
- 真实回放接入 NOT_RUN（无可消费阶段4 冻结结果包）。
- PNG/MP4 不是验收依据；机器验收以 results.json + frame_assertions.jsonl 为准。
- 离线渲染不代表板上绘制；G0/G1/G3/G4/G5 均未通过。

## 4. NOT_RUN（本包自述）
- 真实回放接入（无阶段4 冻结回放结果包；契约 r06=DRAFT_PENDING_REVIEW / task-26 BLOCKED）
- 板上动态映射与绘制（板级 SUSPENDED_BOARD_DETACHED；本轮不接板卡）
- 真实采集路径（摄像头未到货）
- 真实集成的 30 分钟联调与 T5-10 板上回归

## 附：可复现信息与绑定口径（第 5 轮复审 O-5/O-6 补记）
- 本包套件命令（另见 `console/suite_command.txt`）：
  ```
  python -B -m unittest scripts.stage5_t03.test_s5t03_json_contract scripts.stage5_t03.test_s5t03_multi_geometry_render scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton
  ```
- **绑定口径**：`manifest.tools[]` 绑定的是**驱动/渲染/参考/参数**文件哈希（运行产物由它们决定）；
  测试文件**不在** tools 中绑定，因此套件日志用于证明"当前代码库能通过全部测试"，不构成产物溯源的一部分。
