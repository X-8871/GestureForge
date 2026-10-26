# S5-T03 离线长跑回放 RunId `s5t03_offline_long_run_replay_20261026_r03`

> **历史记录说明（2026-10-26 补注，不修改本包历史正文数字）**：本包为**历史 RunId**，其后有修正版；
> 正文中的测试数/提交号/耗时可能早于修正（例如曾写 57 或 68 项测试、或引用 `a172dfb`/`21c11a5` 等提交）。
> **权威一律以本包 `results.json` / `manifest.json` / `console/` 为准**；本轮只回填过 `manifest.files[]` 哈希并加注记，
> **未改写**任何历史证据内容。最终版：短跑 `s5t03_offline_replay_display_20261026_r06`、
> 长跑 `s5t03_offline_long_run_replay_20261026_r04`、多几何 `s5t03_multi_geometry_render_20261026_r02`。


- 时间（UTC+8）：2026-10-26 22:24–22:27；执行方：DSH 阶段5 总控（w5 接管后）
- 范围（Wong 2026-10-26 决定 + "按默认继续"）：**阶段5 离线 replay/display 骨架**的**长跑**部分；输入＝合成流；**不接板卡**；**不宣称任何关口通过**
- 命令与退出码：
  ```
  python -B scripts/stage5_t03/s5t03_long_run_replay.py --out report/evidence/S5-T03/s5t03_offline_long_run_replay_20261026_r03 \
      --keyframe-max 16 \
      --stage3-binding D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json \
      --demo-mp4                                                     # exit 0
  python -B -m unittest scripts.stage5_t03.test_s5t03_long_run_replay \
      scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton
                                                                     # Ran 68 tests, OK, exit 0
  ```

## 1. 长跑口径（沿用已冻结参数，判据用**区间数**）
| 量 | 值 |
|---|---|
| 帧数 | **106573**（= 参数文件 `long_run_min_frames`） |
| 帧周期（离线虚拟步长） | `16 890 000 ns`（来源：板上实测 display frame period 的离线步长，**非本轮板上测量**） |
| 区间数 `period_count` | **106572**（= 帧数 − 1） |
| 虚拟时长 | **1 800 001 080 000 ns = 1800.001 s ≥ 1800 s** ✅ |
| 余量 | **1 080 000 ns（1.08 ms）**，`0 ≤ 余量 < 1 周期` ✅ |
| 处理耗时 | 152.9 s（离线计算，**不是**墙上运行时间） |

## 2. 不变量（全部为真）
| 不变量 | 结果 |
|---|---|
| 每显示帧**恰好一次** overlay 提交事件（无漏提交 ⇒ **无死锁**） | ✅ `one_commit_event_per_frame=true` |
| 提交时间戳**单调不减** | ✅ `commit_timestamps_monotonic=true` |
| 计数可由帧级事件日志**完全复算**（在线 vs 复算逐项相等） | ✅ `recompute_matches_online=true` |
| 断言覆盖全部帧（流式写入，无死锁/无丢帧） | ✅ `no_deadlock=true`（106573/106573） |
| 规范长跑（≥ 冻结最少帧数） | ✅ `canonical_long_run=true` |
| ≥1800 s 与余量口径 | ✅ `required_duration_met=true`、`margin_within_one_period=true` |

**14 项计数**（与既有骨架 `s5t03_offline_skeleton_20261024_r03` 的长跑基线**逐项相同**，无回归）：
`frames_committed=106573, overlay_drawn_frames=76603, boxes_drawn=196510, warmup_frames=0, dropped_frames=3330, timeouts=6660, error_results=3330, invalid_records=3330, stale_cleared=3330, duplicate_results=3331, duplicate_frame_id_results=0, out_of_order_results=3331, zero_hand_frames=3330, zero_area_dropped=39962`

## 3. 产物（JSON/日志为权威；PNG/MP4 仅供人工与演示）
```
s5t03_offline_long_run_replay_20261026_r03/
├─ results.json                  # 权威：口径/不变量/计数/关键帧索引/边界/限制
├─ frame_assertions.jsonl.gz     # 106573 行**紧凑**逐帧断言（1.9 MB，gzip）
├─ logs/events_mixed_106573.jsonl.gz   # 帧级事件日志（1.6 MB，gzip，可独立复算）
├─ keyframes/*.png               # 21 张：首/末 + 检查点 + 过期首帧/零框首帧/被拒首帧 + 3 张边界
├─ demo.mp4                      # demo_only（libx264，441 KB）——**非验收证据**
├─ manifest.json                 # 工具/输入/参数哈希、不变量、文件哈希、限制、NOT_RUN
└─ console/                      # stdout/run.txt/unittest_all.txt/ffmpeg_demo.txt
```
- 关键帧标签按**真实** outcome/状态打（被拒标签只在此帧确有拒绝时出现）。
- 过期边界三例（渲染路径）全部 PASS：`age==200000000` 不过期 / `+1` 过期 / 显式 `stale_flag` 过期。
- 输入帧：阶段3 `frame_full.bin` SHA `939fce22…`（实测与绑定一致），仅作**输入帧**。

## 4. 诚实边界（不冒充）
- 输入为**合成流**（`synthetic_replay` / `PRELIMINARY`）；`capture_time_ns` 是**合成单调时钟**，虚拟时间**不是**墙上时间。
- 本长跑只覆盖**显示/叠加路径**（渲染、帧关联、过期/零框/故障计数、HUD 合成）；`inference_fps=NA` ⇒ **不得**据此声称"推理 30 分钟无死锁"。
- **真实回放接入 = NOT_RUN**（无阶段4 冻结回放结果包）；**板上动态映射/绘制 = NOT_RUN**（本轮不接板卡）；摄像头真实采集路径 = NOT_RUN；T5-10 板上回归 = NOT_RUN。
- 逐帧断言为 **compact**（不含逐框像素表）；像素级细节保留在关键帧条目与事件日志中（已在限制中声明）。
- PNG/MP4 **不是**验收依据；**G0/G1/G3/G4/G5 均未通过**。

## 5. 与短跑证据的关系
- 短跑（240 帧 mixed）：`s5t03_offline_replay_display_20261026_r05`（含首轮复审修复闭环）。
- 长跑（本包）：`s5t03_offline_long_run_replay_20261026_r03`；两者共用同一管线/几何/色/字号单一来源，长跑另加"≥30 分钟 × 渲染检查点 + 全量日志"。
- 本包为新增证据，**不改写** r01–r04 历史 RunId。
## 6. 与 r01/r02 的关系（保留不删）
- `…_r01`：长跑首跑（`source_commit` 指向父提交，代码绑定以 `manifest.tools[].sha256` 为准）。
- `…_r02`：代码提交后重跑（已被本包取代）。
- **本包 `…_r03` 为最终版**：在**代码提交 `a172dfb` 之后**重跑，`source_commit` 即被测代码提交；并含复审第 2 轮非阻断观察的修复（缺 Pillow ⇒ 显式失败、测试断言加强、路径 POSIX 化）。
- 回归：`test_s5t03_long_run_replay + test_s5t03_replay_display + test_s5t03_skeleton` → **Ran 68 tests, OK, exit 0**（见 `console/unittest_all.txt`）。
