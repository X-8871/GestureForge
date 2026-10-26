# S5-T02（**离线部分**）板上动态结果映射 RunId `s5t02_offline_dynamic_map_20261027_r02`（复审修复版）

> 数字口径：本摘要逐项取自本包 `verify/verify_all.json`、`build/build.json`、`stream/cases_meta.json`
> 与 `console/`（机器可读权威）；冲突以 JSON/日志为准。
> **本包只覆盖 S5-T02 的「离线可做部分」**（C 实现 + 宿主隔离构建 + 用例生成 + 对拍）。
> **这不是板上验证**：`§4.5/§7.3 未关闭`，板级 B1–B10 仍 **NOT_RUN**。

- 被测代码提交（本包 `source_commit`）：`8ff43ad2271e…`（**含被审代码本身**，修复 N1 的基线口径）
- 输入：**合成动态流**（`synthetic_dynamic_stream_not_stage4_output`）；**非阶段4 输出**
- 画布 `[1280, 720]`（来源：scripts/stage5_t01/gen_overlay_cases.py:CANVAS_W, CANVAS_H（HDMI 实测模式））；契约 `S5A-G0-v2`；`stale_age_limit_ns=200000000`
- 本包独立套件日志：`Ran 130 tests` / OK（**在冻结提交上真 exit 0**）

## 1. 真实退出码
| 步骤 | 退出码 |
|---|---|
| 隔离构建（`-Wall -Wextra -Werror`） | **0** |
| 合成流生成 | **0** |
| C 执行（宿主） | **0** |
| 与冻结参考对拍 | **0**（`passed=True`，失败 0） |
| 八模块套件（本包独立运行，含 S5-T03 七模块） | **0** |

## 2. 对拍与覆盖
- 比对帧数 **137**；判定分布 **{"pixel_exact": 137}**
  ⇒ 像素矩形/边框像素数/标签锚点与 placement **全帧逐像素一致**；
- **覆盖性判据全部满足**：`{"placement 组合 +clamped_bottom": true, "placement 组合同时 clamped_bottom+clamped_x": true, "stale_reason=both": true, "zero_area_dropped>0": true, "非 OK 状态带框仍守恒（timeouts>0 且对应帧 boxes=0）": true, "NO_HAND 不计 stale": true}`
  （含 `+clamped_bottom+clamped_x` 组合、`stale_reason=both`、`zero_area_dropped>0`、非 OK 状态带框守恒、NO_HAND 非过期）；
- HUD：字段名与 **P1 权威表** 13/13 一致，**11 项值逐项核对**（`CAPTURE_FPS`/`INFERENCE_FPS` = NA，不用 0 伪装）；
- 语义唯一 `B_latest_result_overlay`；`displayed != result` **2** 帧如实记录。

## 3. 用例清单（17 例）
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
| `nonok_with_boxes_timeout` | TIMEOUT 且带 2 框 ⇒ 单独计数、不绘制 | 8 |
| `nonok_with_boxes_error` | ERROR 且带 2 框 ⇒ 单独计数、不绘制 | 9 |
| `nonok_with_boxes_duplicate` | DUPLICATE 且带 2 框 ⇒ 单独计数、不绘制 | 10 |
| `nonok_with_boxes_out_of_order` | OUT_OF_ORDER 且带 2 框 ⇒ 单独计数、不绘制 | 11 |
| `zero_area_clipped` | 越界框裁剪后零面积 ⇒ zero_area_dropped+1 且不绘制 | 12 |
| `both_stale_flag_and_age` | stale_flag 且 age_frame>limit ⇒ reason=both | 13 |
| `placement_bottom_and_x_clamped` | 右下角大标签 ⇒ +clamped_bottom+clamped_x | 14 |
| `no_hand_with_large_age` | NO_HAND 且 age_frame>limit ⇒ 仍非过期（§3 口径） | 15 |
| `edge_explicit_stale_flag` | 显式 stale_flag（age 很小）过期 | 16 |

## 4. 故障计数
```
{
  "frames_committed": 137,
  "warmup_frames": 3,
  "dropped_frames": 4,
  "timeouts": 3,
  "error_results": 2,
  "duplicate_results": 3,
  "out_of_order_results": 3,
  "stale_cleared": 6,
  "zero_area_dropped": 1,
  "boxes_drawn": 235
}
```

## 5. 本轮修复的复审阻断项（B1–B7）
| 项 | 问题 | 处置 |
|---|---|---|
| B1 | 八模块套件在冻结提交上 **exit 1**（`report/evidence/S5-T01/**` 新 RunId 被"S5-* 不得改动"判据命中；生成时未 track 才假绿） | 判据改为只对**既有文件的 M/D/R** 判违反（并用基线 blob 哈希比对既有文件内容）；本包套件在同一冻结提交上 **exit 0** |
| B2 | 宿主 CLI `frame.state` **悬挂指针** ⇒ 非 OK 状态带框时计数被隐藏、故障帧被误绘（UB） | state 存持久缓冲；新增 4 例"非 OK + 带框"用例并断言 `boxes_drawn=0` 且计数增长 |
| B3 | `both` 原因串未逐字镜像（写成 `stale_flag_and_age_frame_exceeds_limit`） | 改为冻结参考的 **`both`**；新增 both 用例（129→137 帧后已覆盖） |
| B4 | placement 组合（`+clamped_bottom(+_x)`）无覆盖 ⇒ 后缀顺序变异抓不住 | 新增贴底+靠右用例触发组合串，并加覆盖性断言 |
| B5 | HUD 只查字段数与两个 NA ⇒ 字段名/11 项值无判据 | 对拍器按 **P1 权威表**核对字段名与 11 项值 |
| B6 | `zero_area_dropped` 无覆盖 | 新增"裁剪后零面积"用例并断言计数 +1、同帧另一框照常 |
| B7 | `NO_HAND` ∩ 过期：C 与对拍器口径冲突 | 按任务卡 §3 统一为**如实报"非过期"**（flag=false、reason=none、不计 stale_cleared） |

另修非阻断项：N2（核心自己算 `border_pixels` 并由宿主自校）、N3（F 行 `nbox` 声明与实际 B 行数核验）、N6（`within_1px` 计为未达标）、N1（本包 `source_commit` 含被测代码）。

## 6. 限制与 NOT_RUN
- **宿主执行 + 离线对拍**；**不能**作为 §4.5/§7.3 关闭依据，也**不是**板上验证；
- 输入为**合成**动态流（**非阶段4 输出**）；阶段4 冻结后须复跑（另行 RunId）；
- **NOT_RUN**：板上动态映射与绘制（B1–B10）、真实回放接入（阶段4 契约未冻结）、摄像头采集路径、30 分钟板上长跑（B6）、T5-10 板上回归；**G0/G1/G3/G4/G5 均未通过**。
- 二进制**已入库**（`build/s5_dynamic_map_host.exe`）；其哈希只绑定包内这一份产物（同源重建因 PE 时间戳不同而哈希不同），可重建性由源码哈希 + 编译参数 + 构建脚本保证。
