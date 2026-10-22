# S5-C 阶段4 数值链路回归勾连 · s5c_regression_20261021_r03

- 生成时刻（UTC+8）：2026-10-21T23:13:31+08:00
- 总体状态：**PASS**（退出码 0 = 无 FAIL；1 = 存在 FAIL；2 = 输入/环境错误）
- 契约：S5A-G0-v2（STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED）
- 冻结参考实现：`D:\codex-worktrees\w5\verification\s5_display_geometry_reference.py` SHA256 `556f78c53bba8a75db5746b2cf94f5cfbb5c0f004400acafb5dfec809a05e4be`
- 样本选择：full_all_samples，样本 109/109，框 104，种子 None（not_used_full_selection）

## 逐项结果

| 检查 | 状态 | 关键量 |
|---|---|---|
| C1 字段级一致（109 样本逐框） | PASS | 字段值比较 1159，mismatch 0，最大 score 误差 0.000e+00，最大坐标误差 0.000e+00 |
| C2 不引入第二套语义 | PASS | 常量一致=True，accepted≡阶段4=True，禁用 token=[] |
| C3 几何同源交叉核对 | PASS | S4-B 3/3，样本集内 21 种几何三方一致，非对称补边 5 种 |
| C4 显示像素层往返 | PASS | 最大往返误差 0.499058 px（门槛 1.0），零面积探针 4/4 |
| C5 D9 参考追溯 | PASS | PS 记录 3 条，SKIP 0，mismatch 0 |
| C6 反例（篡改探针） | PASS | 必检探针 4/4 检出（真实退出码 1），正对照退出码 0 |
| C7 用词与契约 | PASS | 扫描 11 文件，禁用用词 48 处（无依据 0） |

## 用例覆盖（S5-A 契约 test_cases 与本任务的对应）

| 用例 | 状态 | 覆盖检查 | 说明 |
|---|---|---|---|
| T5-10 | OFFLINE_CHAIN_ASSERTED | C1,C2,C4,C5 | 回归阶段4 数值链路：沿用 2A 容限、离散字段全等、可追溯到阶段4 整数结果与 D9 参考 |
| T5-06 | OFFLINE_TEXT_SCANNED_AND_FIELD_CHECKED | C7 | 分数/置信度用词：字段名为 score、无依据时不出现禁用用词 |
| T5-05 | PARTIAL_OFFLINE | C1 | 本任务逐样本核对 109 条 frame_id 与阶段4 记录一致；五元组日志/年龄口径属 S5-B 与阶段5 正式运行 |
| T5-01/T5-02/T5-03/T5-04/T5-07 | PARTIAL_OFFLINE | C3,C4 | 几何与像素索引级断言在本任务内完成（C3/C4）；出图渲染与过期清除 HUD 属 S5-B |
| T5-08/T5-09/T5-11/T5-12 | NOT_RUN | — | 需实板/完整链路或属 S5-B 序列用例 |

## 统计口径

- 样本数：109（通过 109，失败 0）
- 框数：104（零框样本 8）
- 参与比较的字段值数：1159（每样本 frame_id/detection_count/框数 + 每框 class_id/class_name/source_order/score/xyxy×4）
- 最大 score 绝对误差：0.000e+00（Gate A 容差 1e-06）
- 最大坐标绝对误差：0.000e+00（Gate A 容差 1e-06）
- 位型（逐字节）违规数：0（Gate D）；别名引用违规数：0
- 最大像素往返误差：0.499058 px（Gate B 门槛 1.0）
- 最大接受框数：2（上限 15）；接受框最小分数：0.31230869634401914

## 反例与对照（C6）

- `box_count`：检出=True，命中门槛=['discrete']，真实退出码=1，证据 `tamper/tamper_box_count_before_after.json`
- `frame_id`：检出=True，命中门槛=['discrete']，真实退出码=1，证据 `tamper/tamper_frame_id_before_after.json`
- `identity_rebuild`：检出=True，命中门槛=['identity_invariant']，真实退出码=1，证据 `tamper/tamper_identity_rebuild_before_after.json`
- `score_tol`：检出=True，命中门槛=['A', 'D']，真实退出码=1，证据 `tamper/tamper_score_tol_before_after.json`
- `score_ulp`：检出=True，命中门槛=['D']，真实退出码=1，证据 `tamper/tamper_score_ulp_before_after.json`
- `source_order`：检出=True，命中门槛=['discrete']，真实退出码=1，证据 `tamper/tamper_source_order_before_after.json`
- `xyxy_tol`：检出=True，命中门槛=['A', 'D']，真实退出码=1，证据 `tamper/tamper_xyxy_tol_before_after.json`
- `xyxy_ulp`：检出=True，命中门槛=['D']，真实退出码=1，证据 `tamper/tamper_xyxy_ulp_before_after.json`
- 未篡改正对照：真实退出码 0

## SKIP / NOT_RUN（如实标注）

- NOT_RUN `U5-05` 真实 HDMI/摄像头联调、上板、30 分钟运行、截图/视频：阶段3 颜色验收受阻（硬件）+ 阶段4 未联调 + 2B 未让出硬件；本轮为纯离线
- NOT_RUN `T5-09` 连续 30 分钟无死锁：需要实板与完整链路
- NOT_RUN `T5-08` FPS/延迟真实统计：离线无 PS 单调时基与帧级事件日志
- NOT_RUN `G3` 实物验证：本轮无板卡/HDMI/摄像头操作
- NOT_APPLICABLE_THIS_TASK `T5-01/T5-02/T5-03/T5-04/T5-07` 离线渲染用例（PNG/叠框/零面积绘制/非方形画布/过期清除）：属 S5-B 交付范围（scripts/stage5_s5b/**、report/evidence/S5-B/**）；本任务只做数值链路勾连与像素索引级往返，不重复渲染出图

## 限制

- 纯离线：无 Vivado / xsim / JTAG / 硬件 / HDMI / 摄像头；所有板上与真实时延项 NOT_RUN
- S4-A 契约状态 DRAFT_NOT_FROZEN；本检查只核对字段名与语义一致性，不构成阶段4 G0
- S4-C 样本不含显式 state 字段，state 由 detections_expected 长度派生并已在报告中标注
- xyxy_px 派生字段未参与对拍；显示层不使用该字段（G0 规定只用 xyxy）
- 1 ULP 级篡改在 Gate A（1e-6）内、只能由 Gate D（逐字节一致）捕获；两项门槛分别报告
- 抽样运行（--limit）的 C6 为 NOT_APPLICABLE_THIS_RUN：篡改探针与终态汇总只在主运行目录完成
