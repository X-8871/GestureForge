# S5-B 离线渲染/叠框自测证据 — RunId `s5b_20261021_r07_b`

- 任务：S5-B（阶段5 离线准备；不接硬件、不跑 Vivado/xsim）
- 状态：**PASS**
- 退出码（写 summary 时计算）：**0**（0=全部断言 PASS / 1=断言失败 / 2=环境或输入错误）；写后复核见 `console/wording_scan.txt`、`console/hash_recheck.txt` 与 `console/final_verdict.json`
- 源码 HEAD：`acd2df6774ead5c8085fa2417882c8315c18eecd`（分支 `stage5-display-prep`）
- 种子：20261021；种子化随机框 N=64/几何；五元组 129 条
- 断言：583/583 PASS，FAIL 0，ERROR 0

## 一键命令 / 恢复命令

```bash
# 本证据包的实际一键命令（RunId 基名 s5b_20261021_r07，产出 <out>/s5b_20261021_r07_a 与 _b）
python scripts/stage5_s5b/run_s5b_evidence.py --out report/evidence/S5-B --run-id s5b_20261021_r07 --seed 20261021

# 全新 RunId 重跑（不覆盖已有 RunId）
python scripts/stage5_s5b/run_s5b_evidence.py --out report/evidence/S5-B \
       --run-id <新的 RunId> --seed 20261021

# 恢复：单 pass 重出（新 RunId，不覆盖他人 RunId）
python scripts/stage5_s5b/render_s5b_overlay.py --out report/evidence/S5-B \
       --run-id <新 RunId>_recover --seed 20261021

# 恢复：库内自检 / 子集用例
python scripts/stage5_s5b/render_s5b_overlay.py --selfcheck
python scripts/stage5_s5b/render_s5b_overlay.py --out tmp/5/S5-B \
       --run-id probe_t5_04 --cases T5-04

# 单元测试
python -m unittest discover -s scripts/stage5_s5b -p "test_s5b_overlay.py" -v

# 只读输入恢复参数（契约声明路径不可用时）
python scripts/stage5_s5b/render_s5b_overlay.py --run-id <id> \
       --s4b-dir <S4-B 目录> --s4c-golden <replay_golden_109.json>
```

## 用例逐项结果

| 用例 | 组 | 状态 | 断言(通过/总) | 框(结果/绘制) | PNG | 五元组 / 台账 |
|---|---|---|---|---|---|---|
| `t5_01_landscape_1280x720` | T5-01 | PASS | 26/26 | 2/2 | cases/t5_01_landscape_1280x720.png | `[5001, 5000, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_01_portrait_720x1280` | T5-01 | PASS | 21/21 | 1/1 | cases/t5_01_portrait_720x1280.png | `[5011, 5010, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_01_oddw_683x384` | T5-01 | PASS | 32/32 | 2/2 | cases/t5_01_oddw_683x384.png | `[5021, 5020, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_01_square_640x640_no_pad` | T5-01 | PASS | 24/24 | 2/2 | cases/t5_01_square_640x640_no_pad.png | `[5031, 5030, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_01_canvas_683x384_k2_1920x1080` | T5-01 | PASS | 29/29 | 1/1 | cases/t5_01_canvas_683x384_k2_1920x1080.png | `[5041, 5040, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_01_canvas_1280x720_k1_1920x1080` | T5-01 | PASS | 28/28 | 1/1 | cases/t5_01_canvas_1280x720_k1_1920x1080.png | `[5051, 5050, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_edge_flush` | T5-02 | PASS | 24/24 | 2/2 | cases/t5_02_edge_flush.png | `[5061, 5060, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_corners` | T5-02 | PASS | 31/31 | 4/4 | cases/t5_02_corners.png | `[5071, 5070, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_letterbox_padding_zero_area` | T5-02 | PASS | 23/23 | 3/1 | cases/t5_02_letterbox_padding_zero_area.png | `[5081, 5080, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_partial_out_of_bounds` | T5-02 | PASS | 23/23 | 2/2 | cases/t5_02_partial_out_of_bounds.png | `[5091, 5090, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_clip_zero_area` | T5-02 | PASS | 20/20 | 2/1 | cases/t5_02_clip_zero_area.png | `[5101, 5100, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_02_degenerate_new_w_1` | T5-02 | PASS | 19/19 | 1/0 | cases/t5_02_degenerate_new_w_1.png | `[5111, 5110, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_03_multi_15` | T5-03 | PASS | 63/63 | 15/15 | cases/t5_03_multi_15.png | `[5121, 5120, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_03_no_hand_zero` | T5-03 | PASS | 17/17 | 0/0 | cases/t5_03_no_hand_zero.png | `[5131, 5130, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_03_no_hand_s4b_640x963` | T5-03 | PASS | 19/19 | 0/0 | cases/t5_03_no_hand_s4b_640x963.png | `[103, 102, 7000000, 17000000, 'B_latest_result_overlay']` |
| `t5_04_age_equal_limit` | T5-04 | PASS | 21/21 | 1/1 | cases/t5_04_age_equal_limit.png | `[5151, 5150, 180000000, 200000000, 'B_latest_result_overlay']` |
| `t5_04_age_limit_plus_1` | T5-04 | PASS | 19/19 | 1/0 | cases/t5_04_age_limit_plus_1.png | `[5161, 5160, 180000001, 200000001, 'B_latest_result_overlay']` |
| `t5_04_stale_flag_small_age` | T5-04 | PASS | 19/19 | 1/0 | cases/t5_04_stale_flag_small_age.png | `[5171, 5170, 5000000, 15000000, 'B_latest_result_overlay']` |
| `t5_04_stale_both` | T5-04 | PASS | 19/19 | 1/0 | cases/t5_04_stale_both.png | `[5181, 5180, 180000001, 200000001, 'B_latest_result_overlay']` |
| `t5_01_s4b_palm_1440x1920` | T5-01 | PASS | 26/26 | 2/2 | cases/t5_01_s4b_palm_1440x1920.png | `[37, 36, 6000000, 16000000, 'B_latest_result_overlay']` |
| `t5_05_s4c_golden109_frame_ledger` | T5-05 | PASS | 55/55 | 104/104 | 台账子集 5 张（用例日志见 logs/） | `[1, 0, 5000000, 15000000, 'B_latest_result_overlay'] … 共 109 帧` |

## 数值断言摘要

| 手算样例 | 算式 | 手算值 | 参考值 | 误差 | 容限 |
|---|---|---|---|---|---|
| HS1_683x384_odd_padding | `x1=(0.25*416-0)/(416-1); y1=(0.50*416-91)/(233-1); x2=(0.75*416-0)/(416-1); y2=(0.75*416-91)/(233-1)` | ['0.25060240963855424', '0.5043103448275862', '0.7518072289156627', '0.9525862068965517'] | ['0.25060240963855424', '0.5043103448275862', '0.7518072289156628', '0.9525862068965518'] | 1.110e-16 | 1e-09 |
| HS2_1280x720_network_boundary | `x1=(0.0*416-0)/(416-1); y1=(0.25*416-91)/(234-1); x2=(1.0*416-0)/(416-1); y2=(0.75*416-91)/(234-1)` | ['0.0', '0.055793991416309016', '1.002409638554217', '0.9484978540772532'] | ['0.0', '0.05579399141630901', '1.0024096385542167', '0.9484978540772533'] | 2.220e-16 | 1e-09 |
| HS3_1440x1920_non_integer | `x1=(0.50*416-52)/(312-1); y1=(0.10*416-0)/(416-1); x2=(0.60*416-52)/(312-1); y2=(0.20*416-0)/(416-1)` | ['0.5016077170418006', '0.1002409638554217', '0.6353697749196141', '0.2004819277108434'] | ['0.5016077170418006', '0.1002409638554217', '0.6353697749196141', '0.2004819277108434'] | 0.000e+00 | 1e-09 |

- 冻结 `border_pixel_sets` 独立手算对拍：框 [1, 1, 4, 3] 线宽 2 ⇒ 19 像素，逐值一致
- 原图→网络→原图 round-trip：逐用例最大误差 2.220e-16，容限 1e-12；每几何 N=64（种子 20261021）
- S4-C 台账：109 帧 / 21 种几何；台账内种子化随机框样本 1344 条，最大误差 2.220e-16
- 显示像素层 vs float64 连续参考：逐框逐边 ≤1 px（实际落在取整半像素内）
- 683×384：上侧补边 91 / 下侧补边 92，非对称补边保留，未被对称化

## 语义断言摘要

- display_semantics 唯一取值：`['B_latest_result_overlay']`
- 五元组 129 条，全部满足 displayed_frame_id != result_frame_id（最新结果叠加；未出现画面与结果来自同一帧号的伪称）
- 过期清除事件 3 条：每结果只计一次，记录 frame_id / age_frame_ns / cleared_at_ns / reason；边界为严格大于（age==limit 不过期）
- 零框（NO_HAND）被判过期的用例：无

## 用词与伪称扫描

- 扫描 47 个产物（用例 JSON、PNG 字节），命中 0 次
- 禁用 token 身份（拆分存储以避免自触发）：['W1:U+0063 U+006F U+006E U+0066 U+0069 U+0064 U+0065 U+006E U+0063 U+0065', 'W2:U+0070 U+0072 U+006F U+0062 U+0061 U+0062 U+0069 U+006C U+0069 U+0074 U+0079', 'W3:U+7F6E U+4FE1 U+5EA6', 'W4:U+53EF U+4FE1 U+5EA6', 'W5:U+51C6 U+786E U+7387', 'W6:U+540C U+5E27']
- 字段名统一使用 `score`；阈值/NMS/上限/类别顺序取自冻结契约，未引入第二套

## 契约 test_cases 覆盖对照（逐项如实标注）

| 契约用例 | 本任务状态 | 说明 | 覆盖用例 |
|---|---|---|---|
| T5-01 | PASS | 非方形/竖屏/奇数宽/方形无补边/画布整数倍不拉伸：逐值断言 + 出图 | `t5_01_landscape_1280x720`, `t5_01_portrait_720x1280`, `t5_01_oddw_683x384`, `t5_01_square_640x640_no_pad`, `t5_01_canvas_683x384_k2_1920x1080`, `t5_01_canvas_1280x720_k1_1920x1080`, `t5_01_s4b_palm_1440x1920` |
| T5-02 | PASS | 贴边/四角/部分越界/裁剪零面积/补边带零面积/退化几何兜底：逐边裁剪断言 + 出图 | `t5_02_edge_flush`, `t5_02_corners`, `t5_02_partial_out_of_bounds`, `t5_02_clip_zero_area`, `t5_02_letterbox_padding_zero_area`, `t5_02_degenerate_new_w_1` |
| T5-03 | PASS | 15 框上限与零框 NO_HAND：契约校验 + 出图 | `t5_03_multi_15`, `t5_03_no_hand_zero`, `t5_03_no_hand_s4b_640x963` |
| T5-04 | PASS | 过期边界/原因/每结果只计一次：age==limit 不过期、limit+1 过期、flag/both | `t5_04_age_equal_limit`, `t5_04_age_limit_plus_1`, `t5_04_stale_flag_small_age`, `t5_04_stale_both` |
| T5-05 | PASS | 结果—帧号对应：S4-C 只读台账 109 帧，五元组可按 frame_id 索引、语义唯一 | `t5_05_s4c_golden109_frame_ledger` |
| T5-06 | PASS | 分数用词扫描：产物 0 命中；字段名统一 score | - |
| T5-07 | PASS | 奇数补边半像素：683×384 上 91/下 92 保留；D2 端点对齐 scale 同源 | `t5_01_oddw_683x384` |
| T5-08 | PARTIAL | FPS/延迟口径：13 个 HUD 字段与本工具两个年龄可由合成台账复算；真实采集/推理/显示 FPS 与实测延迟 NOT_RUN（需硬件） | - |
| T5-09 | NOT_RUN | 30 分钟无死锁：需实板与摄像头，本任务不执行（无硬件） | - |
| T5-10 | PARTIAL | S5-B 侧：显示消费的框可直接追溯到 S4-C 台账与 S4-B 记录（只读重放、不重跑 NMS）；与阶段4 整数结果的完整回归属 S5-C 任务 | - |
| T5-11 | PARTIAL | 预热/丢帧/超时字段在 HUD 与逐用例 JSON 中单列；取值为离线占位（非实测） | - |
| T5-12 | PASS | 显示语义一致性：全部产物 display_semantics 唯一且与五元组一致 | - |

## 确定性

- 确定性状态：NOT_RUN_SINGLE_PASS（双 pass 比对口径见 `determinism.note` 与 `console/determinism_compare.txt`）
- 主 pass A 的 PNG 集合摘要：`556adb5265613d49c113c826ef421becfe8a8a199be54fe2c76b7e66c8fed45f`
- 主 pass A 的 JSON 统计摘要：`52097557f549d91ad62889810ff1f16f696ce080896ee5ac3953e5c495ad0692`
- 双 pass 比对结果见 `run_s5b_evidence.py` 写入的 `determinism` 段

## HUD 字段

- 逐用例 JSON 的 `hud` 字段：['capture_fps', 'inference_fps', 'display_fps', 'inference_time_ns', 'age_result_ns', 'age_frame_ns', 'frame_id', 'boxes', 'stale_cleared', 'dropped_frames', 'timeouts', 'warmup_state', 'display_semantics']
- 数值均为离线合成占位量（非实测）；逐字段口径见 `hud_provenance`

## 限制与未执行项

- 限制：几何/口径全部导入冻结参考模块；本工具不复制 letterbox/逆映射公式
- 限制：合成帧与合成时间台账为离线占位，非真实摄像头/HDMI 数据
- 限制：S4-B 时间字段为 0 哨兵：改用离线合成台账时间，不声称实测
- 限制：G0 未固定非 1080p 的布局相对缩放规则：本工具仅对安全区按画布高度等比缩放，线宽统一用 1080p 参考值 2
- 限制：画布缩放仅用整数倍块复制（无插值）；文本叠加为可选 ASCII 层
- NOT_RUN：实板 HDMI 输出与截图
- NOT_RUN：摄像头采集与 30 分钟无死锁运行
- NOT_RUN：PL/UART 时序与真实 FPS 实测
- NOT_RUN：阶段6 状态机联动实测
- NOT_RUN：CJK 字体渲染（本工具仅 ASCII 标签）

- 环境错误：无
