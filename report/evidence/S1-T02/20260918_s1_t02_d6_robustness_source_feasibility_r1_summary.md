# S1-T02-D6 robustness 来源可行性盘点 R1

状态：**BLOCKED_NO_ELIGIBLE_INDEPENDENT_LOCAL_ROBUSTNESS_SOURCE_IN_SCOPED_INPUTS**。只评估指定 manifest、候选标签和已审 R2 目录快照；不是 G0/G4 验收，没有模型预测或精度指标。

盘点时间（本地）：`2026-09-18T22:15:27.9947913+08:00`。基线 HEAD：`bb560cea1e84bc9515a98492e2e18f644ead8d8c`。

## 输入和批准口径

- 批准 manifest：`D:/FPGA_Data/HaGRIDv2/manifest.csv`；SHA-256 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`；158,680 行、158,680 唯一路径，train 118,001 / val 15,195 / official test 25,484。
- `manifest_all.csv`：SHA-256 `c0f93b494cd6649fdbf14d5bae0448ed7f9f77ca340a82f6e16b98657cb0c07e`；158,698 行，均属 train/val/test。R2 目录 inventory JSON/summary SHA-256 `44c8a7c36f94401762cea3e4b93ae6364b407609feb01a22031e6d91818fe99f` / `473e8bc4ca85d84cf414501320641cc9af8c4848a9c7ea6cf8a0c720e269f85a`。
- 获批最低数：test 25,484；五目标类各≥100；no_hand、non-target、多手、遮挡、小目标各≥100张唯一图；person/session 必须与现有 train/val/test 隔离。小目标边界未冻结。

## 差分与隔离结果

按 `image` 精确集合比较：交集 158,675；current-only 5（均为已批准 no_hand，train 3 / val 2）；manifest_all-only 23（旧清单 split 为 val 7 / test 16）。候选类别计数：fist 3、palm 4、one 4、two_up 5、three 2、no_gesture 5。

候选有 13 个 distinct person 值、2 个 distinct session 值。person 对 current train/val/test 的交集基数 `{"test": 5, "train": 0, "val": 0}`；session 交集基数 `{"test": 1, "train": 0, "val": 1}`。候选与 test 有人员重叠，并与 val/test 有 session 重叠；不能成为独立集。当前批准 manifest 的 train/val/test 两两 person/session 交集均为0。

## 标签与已审 R2 目录快照

23个 manifest_all-only 候选标签文件均存在、严格 UTF-8 解码和格式解析通过：18个目标类样本每张一框，5个 no_gesture 文件均为空。18个框归一化面积最小值 `0.007596558588101999`；≤0.01 有 1 框，≤0.0025 有 0 框。这些仅为几何预筛示例，不是已冻结的小目标口径。

已审 R2 快照：dataset 子树 158,705 唯一路径、30条未与批准 manifest 精确匹配（目标类18、no_gesture 7、user_no_hand 5）；path+size 总 SHA-256 `46642ac0b7343b8a726276dabc850b3221c624a19a3840466496b35866aca16e`，未匹配子集 SHA-256 `b1e848f9f8b1a38da1450daf452b8a3968c93489f609dcd38e851a700e8501e4`。路径大小/时间戳不能证明内容唯一；R2 未绑定足够的 condition/person/session 证据。

## 可证范围与缺口

标签文本支持类别、标注框行数和归一化几何。空标签或 `no_gesture` 不能证明 no_hand；多行标签不能证明可见手数或标注完整；manifest/候选标签没有遮挡或 no_hand 条件字段。occlusion、no_hand、non-target 语义、真实多手与样本内容唯一性须人工图像审计及来源绑定；小目标阈值须先冻结。

**结论：这些指定本地输入中没有满足样本数与person/session隔离的独立robustness候选集。**此范围不排除HaGRIDv2根外或未指定目录的其他数据源；不声称穷尽所有来源。未读图像或annotation JSON，未访问网络/Vault，未作许可证判断。

## 复核命令和计数口径

- 生成器：`bundled-python.exe -B <system TEMP>/d6_robust_source_feasibility_r1_tmp.py`，exit 0。读取两个清单的原始SHA；精确按image路径做集合差分；按split与label父目录聚合；身份值只用于集合运算，仅输出数量；只解析差集行指向的标签文本。
- 候选行绑定 SHA-256（image/label/split/person_id/session_id，TAB分隔，Ordinal排序，UTF-8/LF）：`16b8f3779d58d76b74f9953714c940d90c50d96a105ca93aa5bbcd69407946c6`。
- 候选标签内容多重集 SHA-256（类别 + 标签文件原始SHA，不含路径）：`31a96aaf62b9a6a7057e4578e640dc7f02bcd6c2181d5a4fe52f36e3ec7df45c`。
- JSON：`20260918_s1_t02_d6_robustness_source_feasibility_r1.json`。

## 验证结果

- JSON与摘要均无BOM并通过严格UTF-8解码；JSON解析、聚合断言、摘要一致性和原始标识模式扫描均通过。
- 批准manifest、manifest_all、R2 JSON及R2摘要复读SHA均与报告输入绑定一致。
- `git diff --check` exit 0。Git仅对既有工作副本发出LF/CRLF提示，没有空白错误。两个新建未跟踪输出分别通过 `git -c core.autocrlf=false diff --no-index --check`；命令exit 1代表与空文件存在预期差异，均无空白诊断。
- 未暂存、未提交。
