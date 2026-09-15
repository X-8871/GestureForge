# S1-T01 HaGRIDv2 真实标注可视化人工复核单

## 目的

复核自动生成的真实图片叠框候选，确认五类框覆盖手部、类别语义正确、无手样本没有红框。SVG 由 `verification/s1_t01_dataset_check.py` 从外部 HaGRIDv2 图片生成，不能用合成图片替代真实数据证据。

## 材料

- 正式清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`
- 自动检查报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_dataset_check_clean.json`（当前语义复核结果）
- 人工语义补充表：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_semantic_review.csv`
- 叠框候选目录：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_previews_clean`
- 候选数量：15 张（10 张带框目标、5 张非五类目标负样本；当前没有可计入 `no_hand` 的候选）。

## Wong 可执行步骤

1. 在资源管理器地址栏粘贴候选目录路径，逐张打开 15 个 `.svg`。
2. 对带框图检查：红框是否覆盖完整可辨认手部，是否明显越界/偏移，红色类别文字是否与手势一致；多手图逐个检查。
3. 对当前 11～15 号负样本检查：记录是否属于五类目标之外；它们不能因为空标签或目录名计入 `no_hand`。真正的无手样本须按单独采集单补充并逐张确认。
4. 对明显遮挡、截断或类别不确定的图片记录文件名和原因，不自行修改原始图片；回传“通过/需修订/无法判断”三态结果。
5. 若全部通过，回传“AC04 人工抽查通过”；若有问题，回传文件名、问题类别和建议动作。当前未收到人工回传前，AC04 保持“自动通过、人工待复核”。

## 回传模板

```text
AC04 人工复核：通过 / 需修订 / 无法判断
带框问题文件：无 / <文件名及原因>
无手问题文件：无 / <文件名及原因>
复核人：Wong
复核时间（UTC+8）：<YYYY-MM-DD HH:mm>
```

## Wong 人工回传（2026-09-14）

- 复核人：Wong。
- 复核时间：未提供具体时间。
- `preview_01_row2182.svg` 至 `preview_10_row99136.svg`：Wong 回传“1-10 都没有问题”，记录为带框样本人工通过（10/10）。
- `preview_11_row116536.svg` 至 `preview_15_row116540.svg`：Wong 观察为捂脸动作，“没有识别，可能不属于我们的五个手势范围内”。这说明其可能适合作为“五类目标之外”的负样本，但它们画面中存在手，不能直接等同于“确实无手”。本轮不擅自把该观察改写为无手样本通过。
- 当前 AC04 状态：带框部分人工通过；无手/非目标负样本的验收语义待独立复审确认。该记录不代替独立审查签结。

## 当前状态

- 自动图片/标签检查：基础图片/标签/跨集合检查通过；新的语义检查已改为要求人工语义补充表，不能从 `dataset/no_gesture` 目录名推断 `no_hand`。
- 跨 split 完全重复内容：清洁清单回归已通过。
- 人工可视化观察：带框 10/10 已由 Wong 回传通过；11～15 已确认属于存在手但非五类目标的负样本候选；真实无手样本仍缺 5 张。本单不是审查签结论。

## 2026-09-14 修复后候选（待 Wong 人工复核）

独立复审指出旧候选的框坐标转换和无手候选语义存在问题。本轮已修正 HaGRIDv2 `bboxes` 从归一化 COCO `[left, top, width, height]` 到归一化 YOLO `[center_x, center_y, width, height]` 的转换。此前工具曾按 `dataset/no_gesture/` 空标签行选择 5 张候选，但 Wong 后续观察确认这 5 张是捂脸/遮挡动作，因此本记录将其改列为 `non_target_gesture`，不再称为无手图。

开发侧自动核对结果：10 张带框候选的官方 21 点 landmarks 均落在生成框内（10/10）；11～15 的标签为空且来自 `dataset/no_gesture/`，但这只能支持其为空标签负样本，不能支持“确实无手”。这只是生成逻辑和来源路径的自动证据，不能替代 Wong 对真实图片的逐张观察，也不构成 AC04 或独立审查签结论。

| 序号 | 文件 | 角色 | 自动信息 | 人工状态 |
|---:|---|---|---|---|
| 01 | `preview_01_row2182.svg` | fist | `dataset/fist/fist/124f212f-ff99-4ea5-8eb1-4e6c6154b369.jpg`；官方 21 点均在框内 | 待 Wong |
| 02 | `preview_02_row1815.svg` | fist | `dataset/fist/fist/b647dcbc-ccca-446f-9266-bbdbbe85f37e.jpg`；官方 21 点均在框内 | 待 Wong |
| 03 | `preview_03_row26931.svg` | palm | `dataset/palm/palm/ec13388a-80ec-45a9-ada9-3e683a18ddf9.jpg`；官方 21 点均在框内 | 待 Wong |
| 04 | `preview_04_row39191.svg` | palm | `dataset/palm/palm/0e125bd3-5be8-46f4-a6c1-c944d1e86923.jpg`；官方 21 点均在框内 | 待 Wong |
| 05 | `preview_05_row70371.svg` | one | `dataset/one/32110431-93d1-43f9-8fe1-b94867a11564.jpg`；官方 21 点均在框内 | 待 Wong |
| 06 | `preview_06_row70407.svg` | one | `dataset/one/785e9096-bed3-4e6b-933f-8fd5be39d64d.jpg`；官方 21 点均在框内 | 待 Wong |
| 07 | `preview_07_row93230.svg` | two_up | `dataset/two_up/two_up/46efedfc-2eaa-4fc8-8f25-ef712fcd6d98.jpg`；官方 21 点均在框内 | 待 Wong |
| 08 | `preview_08_row72071.svg` | two_up | `dataset/two_up/two_up/6a7a657c-fa53-4d89-afac-4c10bee8c353.jpg`；官方 21 点均在框内 | 待 Wong |
| 09 | `preview_09_row94070.svg` | three | `dataset/three/three/f62049db-f3fa-403e-be5e-01c1c0315430.jpg`；官方 21 点均在框内 | 待 Wong |
| 10 | `preview_10_row99136.svg` | three | `dataset/three/three/58b091ae-68ca-4985-8da2-c6a32f3cdda9.jpg`；官方 21 点均在框内 | 待 Wong |
| 11 | `preview_11_row116536.svg` | `non_target_gesture` | `dataset/no_gesture/0f30b2cf-f649-4064-9706-3f921592aee6.jpg`；空标签，画面有手 | Wong 已确认非五类目标，不是 no_hand |
| 12 | `preview_12_row116537.svg` | `non_target_gesture` | `dataset/no_gesture/148ddae3-87ee-4bf8-a392-9b14b639b326.jpg`；空标签，画面有手 | Wong 已确认非五类目标，不是 no_hand |
| 13 | `preview_13_row116538.svg` | `non_target_gesture` | `dataset/no_gesture/1dd94133-9e93-4645-8092-2d2a810f0ba4.jpg`；空标签，画面有手 | Wong 已确认非五类目标，不是 no_hand |
| 14 | `preview_14_row116539.svg` | `non_target_gesture` | `dataset/no_gesture/1e52df63-42ac-4236-9207-3b88f8dc08c7.jpg`；空标签，画面有手 | Wong 已确认非五类目标，不是 no_hand |
| 15 | `preview_15_row116540.svg` | `non_target_gesture` | `dataset/no_gesture/2e0acf83-3b22-47e6-bef4-cdad47e6b000.jpg`；空标签，画面有手 | Wong 已确认非五类目标，不是 no_hand |

### Wong 回传模板（新候选）

```text
AC04 人工复核：通过 / 需修订 / 无法判断
带框问题文件：无 / <文件名及原因>
无手问题文件：无 / <文件名及原因>
复核人：Wong
复核时间（UTC+8）：<YYYY-MM-DD HH:mm>
```

## 2026-09-14 语义整改记录（待补真实无手样本）

自动报告现在通过 `20260914_hagrid_semantic_review.csv` 绑定人工语义；角色只允许 `target_gesture`、`non_target_gesture`、`no_hand` 三类。该补充表不覆盖原始 `manifest.csv`。

| 序号 | 当前预览/样本 | 角色 | Wong 人工观察 | 是否计入 no_hand |
|---:|---|---|---|---|
| 01 | `preview_01_row2182.svg` | `target_gesture` | 带框通过 | 否 |
| 02 | `preview_02_row1815.svg` | `target_gesture` | 带框通过 | 否 |
| 03 | `preview_03_row26931.svg` | `target_gesture` | 带框通过 | 否 |
| 04 | `preview_04_row39191.svg` | `target_gesture` | 带框通过 | 否 |
| 05 | `preview_05_row70371.svg` | `target_gesture` | 带框通过 | 否 |
| 06 | `preview_06_row70407.svg` | `target_gesture` | 带框通过 | 否 |
| 07 | `preview_07_row93230.svg` | `target_gesture` | 带框通过 | 否 |
| 08 | `preview_08_row72071.svg` | `target_gesture` | 带框通过 | 否 |
| 09 | `preview_09_row94070.svg` | `target_gesture` | 带框通过 | 否 |
| 10 | `preview_10_row99136.svg` | `target_gesture` | 带框通过 | 否 |
| 11 | `preview_11_row116536.svg` | `non_target_gesture` | 捂脸/遮挡；存在手但不是五类目标 | 否 |
| 12 | `preview_12_row116537.svg` | `non_target_gesture` | 捂脸/遮挡；存在手但不是五类目标 | 否 |
| 13 | `preview_13_row116538.svg` | `non_target_gesture` | 捂脸/遮挡；存在手但不是五类目标 | 否 |
| 14 | `preview_14_row116539.svg` | `non_target_gesture` | 捂脸/遮挡；存在手但不是五类目标 | 否 |
| 15 | `preview_15_row116540.svg` | `non_target_gesture` | 捂脸/遮挡；存在手但不是五类目标 | 否 |
| NH-01 | 待 Wong 提供真实图片 | `no_hand` | 尚未提供，不能自动推断 | 是，待确认 |
| NH-02 | 待 Wong 提供真实图片 | `no_hand` | 尚未提供，不能自动推断 | 是，待确认 |
| NH-03 | 待 Wong 提供真实图片 | `no_hand` | 尚未提供，不能自动推断 | 是，待确认 |
| NH-04 | 待 Wong 提供真实图片 | `no_hand` | 尚未提供，不能自动推断 | 是，待确认 |
| NH-05 | 待 Wong 提供真实图片 | `no_hand` | 尚未提供，不能自动推断 | 是，待确认 |

### AC04 当前人工结论

- 1～10：Wong 已回传“1-10 都没有问题”，带框人工通过 `10/10`。
- 11～15：Wong 观察为捂脸动作，现登记为 `non_target_gesture`；它们不是 `no_hand`，也不计入无手数量。它们可以作为五类检测器的空标签负样本，但不能满足“确实无手”的 5 张要求。
- 新增真实无手样本：当前 `0/5`，等待 Wong 按 `20260914_no_hand_collection_sheet.md` 提供并逐张确认。
- 因此 AC04 仍未完全关闭；本单不代替独立复审签结。
