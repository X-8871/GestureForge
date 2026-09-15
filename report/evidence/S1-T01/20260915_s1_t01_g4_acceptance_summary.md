# S1-T01 任务级 G4 验收摘要

日期：2026-09-15（UTC+8）
被审版本：`edbc9e131584e1f219e22825a8ab1c598d137f13`

## 判定

独立 Reviewer 在隔离目录完成第 2 轮任务级复审，结论为 `PASS`：AC01–AC07、G1、G2、G4 均通过；G3 对纯 PC 环境与数据流程任务不适用。审查 JSON：

`C:\Users\22061\AppData\Local\Temp\review-s1-t01-g4-r2-20260915\review_s1_t01_g4_r2_final.json`
SHA-256：`d1192a35a292e59d5b0f7fd859b65292e455ee44fef81d57ac24b8b1832b61d4`

## 验收矩阵

| 项目 | 结果 | 证据与边界 |
|---|---|---|
| AC01 | PASS | D4 安装后环境探针、CUDA 设备冒烟、官方 Darknet CUDA 构建与独立复审；真实 GPU 训练已执行 |
| AC02 | PASS | 五类编码、来源/许可、人工语义记录；`friend_005` 明确为 Wong 提供并授权的风景/空场景负样本，不把 `no_gesture` 改写为 `no_hand` |
| AC03 | PASS | `158680/158680` 图片有效，五类框 `156518`，no_hand train/val=`3/2`，人员/会话交叉为空 |
| AC04 | PASS | 自动图片/标签/重复检查通过；10 张带框与 5 张 no_hand 有人工语义依据，5 张 no_hand 均空标签 |
| AC05 | PASS | stateless SGD（`momentum=0、decay=0、adam=0`）训练 1–12、恢复 11–12；梯度扫描 `732/122` 条，非有限数为 0，checkpoint `seen=640→768`，输入未覆盖且模型参数有限变化 |
| AC06 | PASS | 全量 valid `15195/15195`，evaluation JSON/JSONL/逐图结果完整，`friend_004` 零框路径成功；未设置 mAP 下限 |
| AC07 | PASS | 数据复检与评估复现、代码/配置/权重/清单哈希和 Darknet source commit 绑定；r2 为 r1 产物的只读版本复核，不伪造新的评估执行 |

## 限制与后续边界

- AC05 的通过路线是无持久化优化器状态的专用 stateless SGD；旧 stateful `momentum=0.9、decay=0.0005` r1 被明确拒绝，不能据此宣称其优化器状态已恢复。
- S1-T01 小样本流程通过不等于正式精度通过。尚未冻结 mAP/召回/精确率、无手误检及 INT8 相对浮点损失阈值。
- 本任务未执行正式长训、完整 YOLOv4 与 YOLOv4-tiny 320/416 对照、INT8 量化、逐层黄金结果、资源预算、RTL、烧录或板卡验证；这些属于阶段1后续任务或后续阶段。

## 提交链

- AC07 证据：`33dce790eba35abec305a4f081db5d9ecf5b7005`
- AC05 修复证据：`edbc9e131584e1f219e22825a8ab1c598d137f13`
- 评估工具修复：`de822c40771a45e2dc8be8bc6baa559bbe1933d2`

本摘要不构成阶段1 G5 或外部最终验收结论。
