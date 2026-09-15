# S1-T01-D2 无手样本摄入收尾证据

核验日期：2026-09-15（UTC+8）

## 用户确认

Wong 已确认五张 PNG 为 `user_no_hand` 样本，五个对应标签为空标签；manifest.csv 与 `20260914_hagrid_semantic_review.csv` 已各追加五行；追加前备份已存在。本文仅记录核验结果，不修改 semantic CSV。

## 五张图与标签核验

“源 SHA”取自 semantic review 五行的 `image_sha256`；“目标 SHA”是本次对 `D:\FPGA_Data\HaGRIDv2\user_no_hand` 目标文件计算的 SHA-256。五项逐一一致。

| 样本 | 源 SHA-256 | 目标 SHA-256 | 尺寸 | 格式/模式 | 标签字节 |
|---|---|---|---|---|---:|
| 001 | `10f1f104343cae97abf817316de3a75bacb646da6c686a2204eedcc2611f34f4` | `10f1f104343cae97abf817316de3a75bacb646da6c686a2204eedcc2611f34f4` | 640×963 | PNG / RGB | 0 |
| 002 | `80e63a26ab3e4ff42b60ee442f6a8e7028e0327bb4c20fbc1995a4e345574dfb` | `80e63a26ab3e4ff42b60ee442f6a8e7028e0327bb4c20fbc1995a4e345574dfb` | 559×800 | PNG / RGB | 0 |
| 003 | `2b267c7dd6ee3a2bbb65064d1f760528f3b0dc81b281929be3dde742924f7360` | `2b267c7dd6ee3a2bbb65064d1f760528f3b0dc81b281929be3dde742924f7360` | 1080×2400 | PNG / RGB | 0 |
| 004 | `8d79dc6c3cd4bb5e2134dedf4f9f8232586c15d84f2f8106c9dc8e73a781806c` | `8d79dc6c3cd4bb5e2134dedf4f9f8232586c15d84f2f8106c9dc8e73a781806c` | 720×827 | PNG / RGB | 0 |
| 005 | `5d207a8c919f5e6be254b35249cd857cdcf9f1c288ac2a00991dcfa86c5c2522` | `5d207a8c919f5e6be254b35249cd857cdcf9f1c288ac2a00991dcfa86c5c2522` | 2551×1384 | PNG / RGB | 0 |

对应标签目录：`D:\FPGA_Data\HaGRIDv2\labels\user_no_hand\20260915_friend_001..005.txt`；五个文件均为 0 字节。

## 清单与划分

- `D:\FPGA_Data\HaGRIDv2\manifest.csv`：158680 条数据行（含表头共 158681 行）。
- `report/evidence/S1-T01/20260914_hagrid_semantic_review.csv`：20 条数据行（含表头共 21 行）。
- 本次五行：`train=3`（001–003），`val=2`（004–005）。
- train/val 人员集合无交集；train/val 会话集合无交集。
- 五行均为 `sample_role=no_hand`、`manual_result=confirmed_no_hand`、`reviewer=Wong`。

## 追加前备份

- `D:\FPGA_Data\HaGRIDv2\backup\20260915_before_no_hand_ingest_manifest.csv`：SHA-256 `74d4a0abec61ea4698caf0479ffb8fffd0b27f308166d81e13a5c20ad06aecb4`。
- `D:\FPGA_Data\HaGRIDv2\backup\20260915_before_no_hand_ingest_semantic_review.csv`：SHA-256 `a32cb29c0520b405cde0854b1e00860cbdc467416794aaa300a532bbda1c3fee`。

## 快速核验命令与结果

使用 Python 标准库 `csv`、`hashlib`、`pathlib` 与 Pillow，对五个指定 PNG、五个指定标签及两个 CSV 进行摄入时点的定点核验；该快速核验未替代后续全量扫描。

命令：PowerShell here-string 通过 `python -` 执行快速核验脚本，检查五项源/目标 SHA 一致、PNG 解码及格式、标签 0 字节、CSV 行数、train/val 数量和人员/会话集合无交集。

结果：`PASS: 5 PNG/labels, source SHA == target SHA, manifest=158680, semantic=20, train=3, val=2, person/session disjoint`；退出码 `0`。

## 全量扫描收尾

在五行追加和标签/图片完成后，使用项目 checker 对当前 `D:\FPGA_Data\HaGRIDv2\manifest.csv` 的 158680 条记录执行全量图片载荷、标签、来源、重复内容及人员/会话隔离检查：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py --data-root 'D:\FPGA_Data\HaGRIDv2' --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' --semantic-review report\evidence\S1-T01\20260914_hagrid_semantic_review.csv --report report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json --preview-dir report\evidence\S1-T01\20260915_after_no_hand_previews
```

退出码：`0`。报告 SHA-256：`9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`；状态：`PASS_AUTOMATED_MANUAL_PENDING`；AC02、AC03 自动通过，AC04 自动检查无错误但保留人工复核状态。结果为有效图片/清单 `158680/158680`、五类框 `156518`、no_hand `train=3、val=2、test=0`、人员/会话交叉为空。15 张预览含 10 张带框候选和新增 5 张 no_hand，人工结论与批准记录见同目录的 `20260915_hagrid_visual_review_after_no_hand.md` 和 `20260915_hagrid_dataset_approval.json`。

## 仓库写入边界

证据创建前只读检查显示，仓库已有用户改动为两份 docs、Vivado 工程、两张 JPG，以及本任务相关的 semantic CSV 五行追加；本任务未修改代码、STATE、用户 docs、Vivado、JPG，也未提交 Git。本文为目标 evidence 的新建文件。
