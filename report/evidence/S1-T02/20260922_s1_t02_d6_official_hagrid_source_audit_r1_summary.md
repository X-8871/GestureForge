# S1-T02-D6：官方 HaGRID 来源与独立鲁棒性候选审计

## 结论

当前只有 `hukenovs/hagrid` 也足够作为正式来源入口，不需要另找“主仓库”。本轮只读审计确认：

- 本机 `D:\FPGA_Data\HaGRIDv2` 已基本覆盖 HaGRIDv2 五个目标类；按 `user_id` 与现有正式清单做差集后，每类只剩 1、1、1、1、2 条 person-disjoint 标注记录，不能满足独立 robustness 的每类至少 100 张要求。
- 官方 `no_gesture` 的 2,164 条标注记录全部有非空 `bboxes`，不能改名或解释为 `no_hand`。
- 同一官方仓库的 `Hagrid_v1` 分支提供 `subsample` 和 `ann_subsample`，README 标明每个手势 100 张、图像压缩包约 2.5 GB、标注约 1.2 MB；这是当前最小的同源独立目标候选，但本轮未下载，尚未完成实际字节、人员隔离、重复和人工条件审查。
- v2 的 `like、ok、stop、peace` 等非目标类在标注上有足够的 person-disjoint 候选，但仍需获取图像并进行视觉审核；标注统计本身不能证明遮挡、可见手数量或 no_hand 语义。

## 建议的最小方案

先取得官方 `Hagrid_v1` 的 `subsample.zip` 和 `ann_subsample.zip`，只做候选鲁棒性集，不下载 716 GB/723 GB 全量数据。解压后严格核对五类各至少 100 张、人员/会话不与当前 train/val/test 交叉、图像可读、无重复，并人工标出多手、遮挡、小目标和背景/距离/光照条件。`no_hand` 单独补充真实无手图片；`no_gesture` 只能作为非目标手势/自然手姿候选，不能代替无手。

本轮不改变 D6 阈值，不更新正式 manifest，不启动训练，不进入阶段2；D6、G4、G5 仍保持未就绪。

## 证据绑定

- 机器可读详情：`20260922_s1_t02_d6_official_hagrid_source_audit_r1.json`
- 当前正式清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`，SHA-256 `FD60E7A67161F242276A1B97B09AD07C0D7F41D30067266BB99620ABE6D7ED74`
- 选定官方 v2 标注文件清单聚合 SHA-256：`2AB3195FBDaf6B78D780850BD576F087B5EC3BD390A4513D6992FD12499985E9`
- 官方代码只读提交：v2 `080e18917376ec935e453cd0e599c23478c7e98f`；v1 `116ee6b548f5611d543768ad9991f33f140f979d`

状态词义：`CANDIDATE` 不是 G0/G4/G5 通过；实际下载和人工语义审核完成前，不把候选写入正式评估集。
