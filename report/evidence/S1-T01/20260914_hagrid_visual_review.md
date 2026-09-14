# S1-T01 HaGRIDv2 真实标注可视化人工复核单

## 目的

复核自动生成的真实图片叠框候选，确认五类框覆盖手部、类别语义正确、无手样本没有红框。SVG 由 `verification/s1_t01_dataset_check.py` 从外部 HaGRIDv2 图片生成，不能用合成图片替代真实数据证据。

## 材料

- 正式清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`
- 自动检查报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_dataset_check_clean.json`
- 叠框候选目录：`D:\FPGA_Competition\report\evidence\S1-T01\20260914_hagrid_previews_clean`
- 候选数量：15 张（每类最多 2 张带框图、最多 5 张无手图；由工具按确定性顺序选择）。

## Wong 可执行步骤

1. 在资源管理器地址栏粘贴候选目录路径，逐张打开 15 个 `.svg`。
2. 对带框图检查：红框是否覆盖完整可辨认手部，是否明显越界/偏移，红色类别文字是否与手势一致；多手图逐个检查。
3. 对无手图检查：画面中没有应纳入五类的手，且图中不应出现红框。
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

## 当前状态

- 自动图片/标签检查：通过。
- 跨 split 完全重复内容：清洁清单回归已通过。
- 人工可视化观察：未执行，等待 Wong 回传；本单不是审查签结论。

## 2026-09-14 修复后候选（待 Wong 人工复核）

独立复审指出旧候选的框坐标转换和无手候选选择存在问题。本轮已修正 HaGRIDv2 `bboxes` 从归一化 COCO `[left, top, width, height]` 到归一化 YOLO `[center_x, center_y, width, height]` 的转换，并仅从 `dataset/no_gesture/` 的空标签行选择无手候选。旧候选文件不再作为当前候选；目录中当前仅保留下面 15 张新候选。

开发侧自动核对结果：10 张带框候选的官方 21 点 landmarks 均落在生成框内（10/10）；5 张无手候选均来自 `dataset/no_gesture/` 且标签为空（5/5）。这只是生成逻辑和来源路径的自动证据，不能替代 Wong 对真实图片的逐张观察，也不构成 AC04 或独立审查签结论。

| 序号 | 文件 | 角色 | 自动信息 | 人工状态 |
|---:|---|---|---|---|
| 01 | `preview_01_row2182.svg` | fist | `dataset/fist/fist/124f212f-ff99-4ea5-8eb1-4e6c6154b369.jpg`；官方 21 点均在框内 | 待 Wong |
| 02 | `preview_02_row1815.svg` | fist | `dataset/fist/fist/b647dcbc-ccca-446f-9266-bbdbbe85f37e.jpg`；官方 21 点均在框内 | 待 Wong |
| 03 | `preview_03_row26931.svg` | palm | `dataset/palm/palm/ec13388a-80ec-45a9-ada9-3e683a18ddf9.jpg`；官方 21 点均在框内 | 待 Wong |
| 04 | `preview_04_row39191.svg` | palm | `dataset/palm/palm/0e125bd3-5be8-46f4-a6c1-c944d1e86923.jpg`；官方 21 点均在框内 | 待 Wong |
| 05 | `preview_05_row70371.svg` | one | `dataset/one/32110431-93d1-43f9-8fe1-b94867a11564.jpg`；官方 21 点均在框内 | 待 Wong |
| 06 | `preview_06_row70407.svg` | one | `dataset/one/785e9096-bed3-4e6b-933f-8fd5be39d64d.jpg`；官方 21 点均在框内 | 待 Wong |
| 07 | `preview_07_row93230.svg` | two_up | `dataset/two_up/46efedfc-2eaa-4fc8-8f25-ef712fcd6d98.jpg`；官方 21 点均在框内 | 待 Wong |
| 08 | `preview_08_row72071.svg` | two_up | `dataset/two_up/6a7a657c-fa53-4d89-afac-4c10bee8c353.jpg`；官方 21 点均在框内 | 待 Wong |
| 09 | `preview_09_row94070.svg` | three | `dataset/three/f62049db-f3fa-403e-be5e-01c1c0315430.jpg`；官方 21 点均在框内 | 待 Wong |
| 10 | `preview_10_row99136.svg` | three | `dataset/three/58b091ae-68ca-4985-8da2-c6a32f3cdda9.jpg`；官方 21 点均在框内 | 待 Wong |
| 11 | `preview_11_row116536.svg` | no_gesture | `dataset/no_gesture/0f30b2cf-f649-4064-9706-3f921592aee6.jpg`；空标签 | 待 Wong |
| 12 | `preview_12_row116537.svg` | no_gesture | `dataset/no_gesture/148ddae3-87ee-4bf8-a392-9b14b639b326.jpg`；空标签 | 待 Wong |
| 13 | `preview_13_row116538.svg` | no_gesture | `dataset/no_gesture/1dd94133-9e93-4645-8092-2d2a810f0ba4.jpg`；空标签 | 待 Wong |
| 14 | `preview_14_row116539.svg` | no_gesture | `dataset/no_gesture/1e52df63-42ac-4236-9207-3b88f8dc08c7.jpg`；空标签 | 待 Wong |
| 15 | `preview_15_row116540.svg` | no_gesture | `dataset/no_gesture/2e0acf83-3b22-47e6-bef4-cdad47e6b000.jpg`；空标签 | 待 Wong |

### Wong 回传模板（新候选）

```text
AC04 人工复核：通过 / 需修订 / 无法判断
带框问题文件：无 / <文件名及原因>
无手问题文件：无 / <文件名及原因>
复核人：Wong
复核时间（UTC+8）：<YYYY-MM-DD HH:mm>
```
