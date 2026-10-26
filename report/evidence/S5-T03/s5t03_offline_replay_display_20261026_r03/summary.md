# S5-T03 离线 replay/display 骨架（渲染路径）RunId `s5t03_offline_replay_display_20261026_r03`

> **历史记录说明（2026-10-26 补注，不修改本包历史正文数字）**：本包为**历史 RunId**，其后有修正版；
> 正文中的测试数/提交号/耗时可能早于修正（例如曾写 57 或 68 项测试、或引用 `a172dfb`/`21c11a5` 等提交）。
> **权威一律以本包 `results.json` / `manifest.json` / `console/` 为准**；本轮只回填过 `manifest.files[]` 哈希并加注记，
> **未改写**任何历史证据内容。最终版：短跑 `s5t03_offline_replay_display_20261026_r06`、
> 长跑 `s5t03_offline_long_run_replay_20261026_r04`、多几何 `s5t03_multi_geometry_render_20261026_r02`。


- 时间（UTC+8）：2026-10-26 21:30–21:36；执行方：DSH 阶段5 总控（w5 接管后）
- 授权与范围（Wong 2026-10-26）：**只做阶段5 离线 replay/display 骨架**；输入用 S5-T03 合成流；**真实回放接入保持 NOT_RUN**；产物按三层（JSON 权威 / 关键帧 PNG / MP4 仅 demo）
- 命令（原文见 `console/command.txt`，真实退出码）：
  ```
  python -B scripts/stage5_t03/s5t03_replay_display.py --out report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r03 \
      --mode mixed --frames 240 --keyframe-max 24 \
      --stage3-binding D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json \
      --demo-mp4                                                 # exit 0
  python -B -m unittest scripts.stage5_t03.test_s5t03_skeleton scripts.stage5_t03.test_s5t03_replay_display
                                                                 # Ran 53 tests, OK, exit 0
  ```

## 1. 本轮补上的缺口
此前 S5-T03 骨架只有**逻辑层**（结果→关联→决策→计数/五元组/HUD）与合成流生成，**实现层渲染路径为 NOT_RUN**。本轮新增：
| 文件 | 作用 |
|---|---|
| `scripts/stage5_t03/s5t03_render.py` | 把逐帧决策**栅格化**：边框像素**只取自** `R.border_pixel_sets`（2 px 偶数线宽居中、钳到画布）；UR-3 类别色与字号；标签锚点（框外上方 → 越界翻转框内 → 钳入安全区）；HUD 13 行（`UNAVAILABLE`→`NA`） |
| `scripts/stage5_t03/s5t03_replay_display.py` | replay 驱动：合成流 → 管线 → 渲染 → **三层产物**；含阶段3 **输入帧**绑定装载（哈希不符即抛）、三例过期边界、关键帧有界选择、demo 生成 |
| `scripts/stage5_t03/test_s5t03_replay_display.py` | 13 项隔离测试（确定性、单源几何、不变量、边界、锚点、产物结构、诚实标注、输入帧哈希、无硬件依赖） |

## 2. 产物（`results.json` 为**权威**）
```
s5t03_offline_replay_display_20261026_r03/
├─ results.json            # 机器验收主证据（计数/五元组/HUD/边界/关键帧/限制）
├─ frame_assertions.jsonl  # 240 行逐帧断言（矩形/类别/分数/映射/stale/年龄/输入帧 SHA/种子/确定性参数）
├─ keyframes/*.png         # 14 张（11 关键帧 + 3 边界），不追求全量
├─ demo.mp4                # demo_only，非验收证据
├─ manifest.json           # 哈希/输入/版本/退出码/限制/NOT_RUN
└─ console/                # command.txt / stdout.txt / unittest_all.txt / ffmpeg_demo.txt
```
- `demo.mp4`：**GENERATED**（libx264，`concat` 列表法，SHA `486054…`），**一律标 `demo_only`**；r01 记录了 ffmpeg 该构建**不支持 glob** 的失败（保留不删，作为环境限制记录）。
- 每个断言行含：`displayed_frame_id / result_frame_id / result_seq / state / drawn / boxes / coordinate_mapping(px) / stale_effective+年龄 / input_frame_sha256 / png_sha256(仅关键帧) / seed / deterministic_params / checks`。

## 3. 结果与不变量（240 帧 mixed，seed=20261024，1280×720）
| 项 | 值 |
|---|---|
| checks | `frames=240, assertions=240, failures=[], passed=true` |
| 计数 | `frames_committed=240, overlay_drawn_frames=177, boxes_drawn=467, dropped=7, timeouts=14, error_results=7, invalid_records=7, stale_cleared=7, duplicate_results=8, out_of_order=8, zero_hand_frames=7, zero_area_dropped=89` |
| 复算 | `recompute_matches_online=true`（逐项等于在线计数） |
| 与既有骨架基线一致性 | 上述 12 项计数与 `s5t03_offline_skeleton_20261024_r03` 的 240 帧 mixed 计数**逐项相同**（同源、无回归） |
| HUD | 13 字段；`capture_fps/inference_fps/display_fps=NA`（不用 0 伪装） |
| 语义 | `display_semantics=B_latest_result_overlay`（唯一） |

**三例过期边界（渲染路径实测）**
| 用例 | `age_frame_ns` | `stale_effective` | PASS |
|---|---|---|---|
| `age_equals_limit_not_stale` | 200000000 | **false**（等于不算过期） | ✅ |
| `age_limit_plus_one_stale` | 200000001 | **true** | ✅ |
| `explicit_stale_flag` | 5000000（年龄很小） | **true**（由 PS 标志触发） | ✅ |

## 4. 输入帧绑定（只作**输入**，不改变"结果为合成"）
- 绑定：`D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_replay_binding_20261025_r01/replay_input_binding.json`
  （其 `delivery_manifest.json` SHA = `616da71d98ed60e59917d064848583100c14013505c6e8b7a4eda36802067b6e` ✅ 与 Wong 提供一致）
- 输入帧：`frame_full.bin`（BGR888、1280×720、stride 3840）SHA `939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0` ✅ **实测与绑定一致**，作为渲染背景；每个断言行记录该 SHA。
- **它只是输入帧**；推理结果是**合成流** ⇒ 真实回放接入仍 `NOT_RUN`。

## 5. 诚实边界与 NOT_RUN（不冒充）
- 输入为**合成流**（`synthetic_replay`，`status=PRELIMINARY`）；`capture_time_ns` 是合成单调时钟值，**不是**真实采集时刻。
- **真实回放接入 = NOT_RUN**：工作区无可消费的阶段4 冻结「回放结果包」（契约 r06 = `DRAFT_PENDING_REVIEW`，task-26 BLOCKED）。阶段3 固定帧仅作输入帧。
- **板上动态映射/绘制 = NOT_RUN**（本轮不接板卡；板级 `SUSPENDED_BOARD_DETACHED`）；离线渲染**不代表**板上绘制。
- 摄像头真实采集路径 = NOT_RUN（未到货）；真实集成 30 分钟联调与 T5-10 板上回归 = NOT_RUN。
- PNG/MP4 **不是**验收依据（JSON 才是）；`demo.mp4` 标 `demo_only`。
- **G0/G1/G3/G4/G5 均未通过**；本包只是离线骨架的渲染路径证据。

## 6. 历史 RunId（保留不删）
- `s5t03_offline_replay_display_20261026_r01`：demo 因 ffmpeg 构建不支持 `glob` 而 FAILED（记录环境限制）。
- `…_r02`：最终代码前的版本（关键帧裁剪逻辑尚未加固），保留为历史。
- 最终以 **`…_r03`** 为准（其 `manifest.json` 绑定 `s5t03_render.py`/`s5t03_replay_display.py`/管线/合成流/冻结参考/参数文件哈希）。
