# 任务卡 S5-T02：板上动态结果映射与绘制（阶段5 §7.3 缺口）

- 编号：S5-T02；开卡：2026-10-23（UTC+8）；执行方：DSH 阶段5 总控（w5）
- 依据：`CDX-20261022-014` §4.5（"从动态结果实际执行坐标映射/绘制并验证；P1预计算框只能保留为显示通路基线"）+ §7.3
- **依赖边界**：本任务**不依赖阶段4**（阶段4 未完成）。结果源使用**与阶段4 同 schema 的合成动态流**，逐处标注"合成，非阶段4输出"；阶段4 冻结结果接入后需复跑（届时另行 RunId）。

## 1. 目标
在不改 w4/dbdf/w2b/main 的前提下，把 P1 的"宿主预计算框"升级为**板上执行**：
`结果记录(detections[≤15] 的 class_id/score/xyxy) → 裁剪 → 原图归一化坐标 → 显示像素索引 → 2 px 偶数线宽居中绘制 → 标签锚点/分数文本`，
并用**冻结参考实现对拍**证明板上结果与参考一致（门槛 ≤1 px；因取整规则同源，期望逐像素相等）。

## 2. 单一来源（必须镜像，不得重写第二套）
- 参考模块：`verification/s5_display_geometry_reference.py`（`CONTRACT_ID=S5A-G0-v2`）
  - `clip_unit_box`：逐边钳到 [0,1]；上游必须正面积（`x2>x1 且 y2>y1`），零面积**不绘制**；
  - `original_norm_to_display_px`：`px = round_half_up(v·(span−1))`，`span` = 显示宽/高；**只在最后一步取整一次**，中间量 float 连续；
  - `ROUNDING_RULE = round_half_up_to_nearest_pixel_index`（`floor(v+0.5)`）；
  - 线宽：`DISPLAY_LINE_WIDTH_PX = 2`，语义"偶数线宽居中：几何线落于像素索引 p 时占 {p−1, p}，逐边钳到画布内"；
  - 标签：`框左上外侧；越界翻转到框内左上；仍越界则钳入安全区`（`SAFE_AREA_PX_1080P = 16`，按分辨率相对缩放）；
  - ≤15 框、2A 稳定顺序**不重排**、`DISPLAY_SEMANTICS = B_latest_result_overlay`。
- 因**不得**在显示代码里重写第二套逆映射：网络→原图逆式（`network_norm_to_original_norm`）**本任务不使用**；仅当阶段4 不给 `xyxy` 时才启用（`S5A-G0-v2` §4.4/§4.6，启用待阶段4 G0）。
- 参考实现哈希须写入清单；对拍脚本用**同一模块**算期望值。

## 3. 输入 / 输出 / 异常语义
- 输入：合成动态流（`S5_FRAMES_MODE` 扩展）：每帧 `frame_id` + ≤15 条 detection（`class_id`、`score`、`xyxy` 原图归一化 float）+ `stale` 标志 + 计数（warm/drop/timeout/dup/ooo）。
- 输出（UART + 板内读回）：逐帧五元组 `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`；每帧每框的**板上像素矩形**（供对拍）；HUD 13 字段。
- 异常语义：零面积 ⇒ 不绘制且计数；`age_result > 200ms` 或 `stale_flag` ⇒ `stale_effective`，不绘制、`stale_cleared+1`（**每结果只计一次**）；`state=NO_HAND` ⇒ `boxes=0`（非过期）；`TIMEOUT/ERROR` ⇒ 单独计数，不冒充零框。

## 4. 允许修改（写权范围）
`scripts/stage5_t01/p1_app/s5_overlay.c`、`scripts/stage5_t01/gen_overlay_cases.py`（或新增同目录生成器）、新增校验脚本、`report/evidence/S5-T01/<新RunId>/**`、`docs/stage5/**`。**构建目录隔离到新 RunId**（`CDX-20261022-014` §6 要求）。

## 5. 验收标准（缺一不可）
1. **对拍**：至少 6 个用例（单框/四角/15 框/零框/边缘+补边带/过期）的板上矩形与冻结参考**逐像素一致**（否则 ≤1 px 且逐条说明）；
2. `age==limit` 不过期、`limit+1` 过期且计数 +1、显式 `stale_flag` 三种边界各 1 例；
3. ≥100 帧五元组可按 `frame_id` 索引、语义唯一 B、`displayed != result` 如实记录；
4. 故障计数（warm/drop/timeout/dup/ooo/stale）不隐藏且与调度模型一致；
5. HUD 13 字段逐项核对（`capture_fps`/`inference_fps` = NA，不用 0 伪装）；
6. 显示侧连续 ≥30 分钟无死锁（可复用 `read_uart.py` 纯 UART 法）；
7. 证据：原始 UART/读回日志、对拍 JSON、真机退出码、版本哈希、限制与 NOT_RUN 清单；
8. **独立复审**（C 实现 + 校验器各一轮）后才算关闭 §7.3/§7.5。

## 6. 命令（核验后填最终值）
```
bash scripts/stage5_t01/build_p1_app.sh <新RunId 隔离目录> "<宏>"
bash <dbdf>/scripts/stage3_t05/run_t05_board_capture.sh <RUN_DIR> <ELF> <tag> <secs>
python -B scripts/stage5_t01/jtag_dump_rows.tcl 系读回 → python -B scripts/stage5_t01/decode_mrd_rows.py --log <log> --json <新报告>
python -B scripts/stage5_t01/verify_frame_stream.py --log <uart log> --json <out>
```

## 7. 未知项（先查再动）
1. P1 实际画布分辨率与显示栅格（须从构建/约束核验，不得假定 1280×720）；
2. 板上分数文本渲染方式：现为宿主预计算字形表；本任务需把**同一字形表**移入 C（或保留宿主生成 + 动态仅映射框几何，二者取其一并记录）；
3. 标签安全区在非 1080p 的缩放取整口径（沿用冻结"相对缩放"解释，需在证据中写明）；
4. 是否需要启用网络→原图兜底逆式（本任务**默认不启用**，待阶段4 G0）。