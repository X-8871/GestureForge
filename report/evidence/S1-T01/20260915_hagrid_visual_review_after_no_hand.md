# S1-T01 全量数据与新增无手样本人工复核记录

## 复核范围

- 清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`，数据行 158680。
- 自动报告：`20260915_hagrid_dataset_check_semantic_after_no_hand.json`，SHA-256 `9B2E4336E30AB49DFD4DFCFA4C9363BE8AB82EC13F9FE80C55D8A3412B3277BE`。
- 预览目录：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_after_no_hand_previews`，由同一报告生成 15 张 SVG。
- 语义补充表：`20260914_hagrid_semantic_review.csv`，本轮新增 5 行真实无手样本。

预览边界声明：`20260915_after_no_hand_previews/*.svg` 是由 checker 从外部真实图片生成并内嵌 `data:image` 的派生预览，预览包含真实朋友图片；该目录及其中预览不属于 Git 交付物，不应提交。原始图片、`labels` 和大清单均位于 `D:\FPGA_Data` 外部目录。

## 自动结果

全量命令使用受控 Python 3.12.14、Pillow 12.3.0，从外部数据根读取当前清单并完成图片像素载荷、标签格式、来源字段、跨集合重复及人员/会话隔离检查；退出码 `0`。

| 项目 | 实际结果 |
|---|---:|
| 有效图片/清单行 | 158680 / 158680 |
| 五类框总数 | 156518 |
| train / val / test | 118001 / 15195 / 25484 |
| no_hand train / val / test | 3 / 2 / 0 |
| no_hand 总数 | 5 |
| non_target_gesture | 5 |
| 人员/会话跨集合交叉 | 0 |
| 自动错误 | 0 |

自动报告状态为 `PASS_AUTOMATED_MANUAL_PENDING`；这表示 AC02/AC03 自动通过，AC04 的自动部分通过，仍需保留人工复核语义，不把该状态误写成全阶段通过。

## 人工语义结论

1. 原有带框预览 1—10：沿用 Wong 2026-09-14 的回传“1-10 都没有问题”，10/10 通过；对应五类框覆盖与类别语义记录见 `20260914_hagrid_visual_review.md`。
2. 原有预览 11—15：沿用 Wong 观察为捂脸/遮挡动作，属于五类之外的负样本；画面有手，继续登记为 `non_target_gesture`，不计入 `no_hand`。
3. 本轮新增 5 张：Wong 明确要求加入 `no_hand`，并确认五张均为朋友提供的真实照片、已同意用于 GestureForge 项目；图像中没有可见手，标签均为空。按 Wong 指定划分，前三张为 train，后两张为 val，人员和会话两侧不重复。

| manifest 行 | 图片 | split | person_id | session_id | 结果 |
|---:|---|---|---|---|---|
| 158677 | `user_no_hand/20260915_friend_001.png` | train | `friend_001` | `session_friend_001` | confirmed_no_hand |
| 158678 | `user_no_hand/20260915_friend_002.png` | train | `friend_002` | `session_friend_002` | confirmed_no_hand |
| 158679 | `user_no_hand/20260915_friend_003.png` | train | `friend_003` | `session_friend_003` | confirmed_no_hand |
| 158680 | `user_no_hand/20260915_friend_004.png` | val | `friend_004` | `session_friend_004` | confirmed_no_hand |
| 158681 | `user_no_hand/20260915_friend_005.png` | val | `background_scene_001` | `session_background_001` | confirmed_no_hand |

复核人：Wong。语义确认时间：2026-09-15 13:06:32（UTC+8）。

## 结论

AC03 的自动条件已满足；AC04 的 10 张带框样本和 5 张 no_hand 语义均有人工依据，5 张 no_hand 已绑定清单 val/train 行。该记录只证明本轮数据与人工语义输入，不代表 CUDA/Darknet、小样本训练、恢复、评估或阶段1最终验收已通过。
