# S5-T03 离线 replay/display 骨架（渲染路径）RunId `s5t03_offline_replay_display_20261026_r05`

> **历史记录说明（2026-10-26 补注，不修改本包历史正文数字）**：本包为**历史 RunId**，其后有修正版；
> 正文中的测试数/提交号/耗时可能早于修正（例如曾写 57 或 68 项测试、或引用 `a172dfb`/`21c11a5` 等提交）。
> **权威一律以本包 `results.json` / `manifest.json` / `console/` 为准**；本轮只回填过 `manifest.files[]` 哈希并加注记，
> **未改写**任何历史证据内容。最终版：短跑 `s5t03_offline_replay_display_20261026_r06`、
> 长跑 `s5t03_offline_long_run_replay_20261026_r04`、多几何 `s5t03_multi_geometry_render_20261026_r02`。


- 时间（UTC+8）：2026-10-26 21:56–21:59；执行方：DSH 阶段5 总控（w5 接管后）
- 定位：**r03 的复审修复版**。独立复审（subagent `4b1f619b`）对 r03 定稿 **PASS**，并给出 8 条非阻断观察；本 RunId 关闭其中 N1/N2/N3/N4/N7，并更正 N5 表述。
- 代码提交：**`21c11a5`**（本证据在**代码提交后**重跑 ⇒ `results.json.source_commit` 即被测代码提交；代码↔证据绑定另以 `manifest.tools[].sha256` 为准）

## 1. 命令与退出码
```
python -B scripts/stage5_t03/s5t03_replay_display.py --out report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r05 \
    --mode mixed --frames 240 --keyframe-max 24 \
    --stage3-binding D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json \
    --demo-mp4                                                       # exit 0
python -B -m unittest scripts.stage5_t03.test_s5t03_skeleton scripts.stage5_t03.test_s5t03_replay_display
                                                                     # Ran 68 tests, OK, exit 0
```
（`console/command.txt` 同时记录 Windows 与 Git Bash 两种路径形式 —— 关闭 N6。）

## 2. 复审修复（逐条与其关闭证据）
| 观察 | 处置 | 判别性证据 |
|---|---|---|
| **N1** 渲染层"无第二套几何"与"字体诚实"**无判别性测试** | 新增 `test_02b`（纯色背景 + `draw_labels=False` ⇒ 非背景像素集合**恰好等于** `R.border_pixel_sets` 并集）与 `test_03b`（强制回退须 `scaled=false`/`font_size_px=None`） | 影子树变体自证：**V1 自写 1 px 线宽 → `test_02b` 失败；V5 谎报 `scaled=true` → `test_03b` 失败**；V0 基线 17/17 全绿（脚本 `tmp/5/S5-T03/adversarial_n1.py`） |
| **N2** 关键帧 `rejected_*` 误标（全局键集合导致） | 改为按**帧真实 outcome**打标（`rejects_by_index` + 事件内 `rejects_this_frame`） | `test_12` 端到端断言：文件名标签 ∈ 实际 FAIL 类型；本 RunId 实测 `reject_tags_in_filenames=['duplicate','invalid','out_of_order']` = `fail_kinds`，**无 `duplicate_frame_id` 误标** |
| **N3** `reject_reason` 空且不落事件日志 | 派生原因并标注来源（`reject_reason_source=pipeline/derived`）；落盘帧级事件日志 | `logs/events_mixed_240.jsonl`（**371 事件**）；`test_13` 断言 FAIL 提交原因非空且来源已标注 |
| **N4** `source_commit` 为父提交 | 证据在**代码提交后**重跑 | `source_commit=21c11a55…`（含被测代码） |
| **N7** 逐帧字体身份缺失 | 逐帧 `render.font` + `manifest.render.font` 记录真实字体 | `arial.ttf` / `font_sha256 5f9f2d81…` / `scaled=true` |
| **N5** 文档写"12 项计数" | 更正为 **14 项**（与 `counter_units` 一致） | 本摘要与 STATE；实测 `counters_keys=14` |

## 3. 结果（240 帧 mixed，seed=20261024，1280×720）
- `checks = {frames:240, assertions:240, failures:[], passed:true}`；`recompute_matches_online=true`
- **14 项计数**（与既有骨架 `s5t03_offline_skeleton_20261024_r03` 的 240 帧 mixed **逐项相同**）：
  `frames_committed=240, overlay_drawn_frames=177, boxes_drawn=467, warmup_frames=0, dropped_frames=7, timeouts=14, error_results=7, invalid_records=7, stale_cleared=7, duplicate_results=8, duplicate_frame_id_results=0, out_of_order_results=8, zero_hand_frames=7, zero_area_dropped=89`
- 过期边界三例 PASS：`age==200000000` 不过期 / `+1` 过期 / 显式 `stale_flag` 过期（严格 `>`）
- 关键帧 **18 张**（含 3 张边界）；`demo.mp4` **GENERATED**（`demo_only`）
- 输入帧：阶段3 `frame_full.bin` SHA `939fce22…`（实测与绑定一致），仅作**输入帧**

## 4. 诚实边界（不变）
- 输入为**合成流**：`input_scope_label=synthetic_replay`、`status=PRELIMINARY`；`capture_time_ns` 为合成单调时钟，**非真实采集时刻**。
- **真实回放接入 = NOT_RUN**（无阶段4 冻结回放结果包）；**板上动态映射/绘制 = NOT_RUN**（本轮不接板卡）；摄像头路径 = NOT_RUN；真实集成 30 分钟与 T5-10 板上回归 = NOT_RUN。
- PNG/MP4 不是验收依据（**JSON 为权威**）；**G0/G1/G3/G4/G5 均未通过**。

## 5. 历史 RunId（保留不删）
`…_r01`（ffmpeg 不支持 glob 的 demo 失败记录）、`…_r02`（最终代码前版本）、`…_r03`（复审 PASS 版）；本包为 **r04 = r03 + 复审修复**。
## 6. 与 r04 的关系与新增修复（保留不删）
- `…_r04`：关闭首轮审查 N1–N5/N7（代码提交 `21c11a5`），经**第 2 轮复审 PASS**。
- **本包 `…_r05` 为最终版**：在代码提交 **`a172dfb`** 之后重跑，`source_commit` 即被测代码提交；并关闭第 2 轮复审的**非阻断观察**：
  1. **fail-open 关闭（观察 1）**：缺 Pillow 时驱动不再报 `passed=true`，改为显式失败 `render_unavailable:…`（新增判别性用例：短跑 `test_14`、长跑 `test_10`）；
  2. 观察 2：`test_13` 改为断言 **commit 事件数 == 帧数**；
  3. 观察 3：`test_12` 改为**双向**（每种实际 FAIL 类型都必须出现在某关键帧名中）；
  4. 观察 6：参数路径改为 POSIX（`…/docs/stage5/s5t03_offline_skeleton_params_v1.json`）；
  5. N5 文档残留：`.codex/STATE.md` 的"12 项计数"更正为 **14 项**。
- 回归：三套测试 **Ran 68 tests, OK, exit 0**（见 `console/unittest_all.txt`）。
- 仍未处理（记录在案、非阻断）：观察 5（同一被拒提交两处原因串不同，来源字段已标注）、观察 7（`png_path` 与 `manifest.files[].path` 基准不同）。
