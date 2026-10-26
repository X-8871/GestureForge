# S5-T02（**离线部分**）板上动态结果映射 RunId `s5t02_offline_dynamic_map_20261027_r01`

> 数字口径：本摘要逐项取自本包 `verify/verify_all.json`、`build/build.json`、`stream/cases_meta.json`
> 与 `console/`（机器可读权威）；冲突以 JSON/日志为准。
> **本包只覆盖 S5-T02 的「离线可做部分」**：把映射从宿主预计算升级为 **C 实现**，在**宿主隔离构建**并与
> 冻结参考逐像素对拍。**这不是板上验证**：`§4.5/§7.3 未关闭`，板级 B1–B10 仍 **NOT_RUN**。

- 被测代码提交（本包 `source_commit`）：`0ea7c768c892…`
- 输入：**合成动态流**（`synthetic_dynamic_stream_not_stage4_output`）；**非阶段4 输出**
- 画布：`[1280, 720]`（来源：scripts/stage5_t01/gen_overlay_cases.py:CANVAS_W, CANVAS_H（HDMI 实测模式））
- 契约：`S5A-G0-v2`；`stale_age_limit_ns = 200000000`
- 本包独立套件日志：`Ran 128 tests` / OK

## 1. 真实退出码（本包 console）
| 步骤 | 退出码 |
|---|---|
| 隔离构建（`build_dynamic_map.sh`） | **0**（gcc gcc，`-Wall -Wextra -Werror`） |
| 合成流生成 | **0** |
| C 执行（宿主） | **0** |
| 与冻结参考对拍 | **0**（`passed=True`，失败 0 项） |
| 套件（本包独立运行） | **0** |

## 2. 对拍结论（任务卡 §5.1/§5.3）
- 比对帧数 **129**（9 用例帧 + 120 长流帧）；
  判定分布 **{"pixel_exact": 129}** ⇒ 矩形/边框像素数/标签锚点与 placement **全帧一致**；
- 语义唯一 `B_latest_result_overlay`；`displayed != result` 帧 **2** 帧如实记录；
- HUD 字段数 **13**，`CAPTURE_FPS`/`INFERENCE_FPS` 强制为 `NA`（不得用 0 伪装）。

## 3. 用例清单（6 必备用例 + 3 过期边界）
| 用例 | 意图 | 帧 |
|---|---|---|
| `single_box` | 单框居中 | 0 |
| `four_corners` | 四角各一框（检验逐边钳位） | 1 |
| `boxes_15` | 15 框上限、稳定顺序不重排 | 2 |
| `zero_boxes` | 无手势 ⇒ boxes=0（**非过期**） | 3 |
| `edge_padding_band` | 贴边 + 奇数补边带（含越界裁剪） | 4 |
| `stale_case` | 显式 stale_flag ⇒ 不绘制、stale_cleared+1 | 5 |
| `edge_age_equals_limit` | age_frame==limit 不过期（严格 >） | 6 |
| `edge_age_limit_plus_one` | age_frame==limit+1 过期且计数 +1 | 7 |
| `edge_explicit_stale_flag` | 显式 stale_flag（age 很小）过期 | 8 |

## 4. 故障计数（与调度模型一致，逐项非零覆盖）
```
{
  "frames_committed": 129,
  "warmup_frames": 3,
  "dropped_frames": 4,
  "timeouts": 2,
  "error_results": 1,
  "duplicate_results": 2,
  "out_of_order_results": 2,
  "stale_cleared": 5,
  "zero_area_dropped": 0,
  "boxes_drawn": 233
}
```

## 5. 单一来源纪律
C 侧几何**镜像** `verification/s5_display_geometry_reference.py`（S5A-G0-v2）与
`scripts/stage5_t03/s5t03_render.py` 的 `label_anchor`/`safe_area_px`；对拍脚本用**同一参考模块**算期望值。
变异测试（本包套件内）证明判据有判别力：取整少一步、线宽 2→1、过期判定 `>`→`>=` **都会被对拍抓住**。

## 6. 限制与 NOT_RUN（重要）
- 输入为**合成**动态流（**非阶段4 输出**）；阶段4 冻结结果接入后须**复跑**（另行 RunId）；
- 本包是**宿主执行 + 离线对拍**：**不能**作为 §4.5/§7.3 的关闭依据，也**不是**板上验证；
- **NOT_RUN**：板上动态映射与绘制（B1–B10）、真实回放接入（阶段4 契约未冻结）、摄像头采集路径、30 分钟板上长跑（B6）、T5-10 板上回归；
- 板上真彩目视、30 分钟板上无死锁（B6）、T5-10 板上回归、UART/读回真实链路均**未做**；
- `HUD CAPTURE_FPS/INFERENCE_FPS` 在离线路径必然为 NA；`display_fps` 亦未在离线测量；
- **G0/G1/G3/G4/G5 均未通过**。
