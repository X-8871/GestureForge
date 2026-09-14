# S1-T01 开发交接与审查入口

## 可直接转交审查窗口的消息

请审查 `S1-T01 训练环境与数据准备` 的当前开发版本。任务规格沿用原项目笔记中的 S1-T01 任务卡和《B方案实施与阶段验收计划》v3.0；当前范围是官方 Darknet/CUDA 环境、五类带框数据清单、标签检查和小样本流程，不包含正式长训、INT8 量化、RTL 或板卡验证。YOLOv4-tiny 仍只是优先上板候选，完整 YOLOv4 只作 PC 对照，输入尺寸和性能未冻结。

本轮开发及复审修复新增：

- `D:\FPGA_Competition\verification\s1_t01_dataset_check.py`：UTF-8 CSV 清单、路径、PNG/BMP/PNM/JPEG 完整结构与载荷、YOLO 标签、图片/标签同 stem、五类覆盖、无手样本、人员/会话隔离、跨集合重复内容检查，并输出 JSON、抽查候选和 SVG 叠框预览。
- `D:\FPGA_Competition\verification\s1_t01_environment_probe.py`：只读检查受控 Python/NumPy/GPU/`nvcc`/CMake、可执行 Darknet 版本/帮助命令和显式 CUDA 设备冒烟程序；不安装、不下载、不切换框架、不训练。
- `D:\FPGA_Competition\verification\test_s1_t01_dataset_check.py`、`D:\FPGA_Competition\verification\test_s1_t01_environment_probe.py`：8 项定向无外部依赖回归测试；测试夹具不构成真实手势精度证据。
- `D:\FPGA_Competition\data\README.md`、`D:\FPGA_Competition\scripts\README.md`：清单接口、完整校验边界与命令说明。

初始版本已执行证据：

- 检查器回归：退出码 0，固定初始提交的独立复审实跑为 3 项通过。
- 当前空 `data/` 检查：退出码 2；`data/manifest.csv` 不存在，AC02/AC03 未通过，AC04 未执行。
- 环境探针：退出码 2；受控 Python 3.12.14、NumPy、RTX 4060 Laptop GPU、CMake 3.30.2 可查询，`nvcc` 和 Darknet 未就绪。
- JSON 原始证据：`20260913_developer_dataset_check_empty.json`、`20260913_developer_environment_probe.json`。

复审修复后已执行证据：

- S1-T01 定向回归：退出码 0，8 项通过，见 `20260913_audit_fix_test_s1_t01.json`。
- 全量 Python 回归：退出码 0，12 项通过，见 `20260913_audit_fix_full_unittest.txt`。
- Python 编译检查：退出码 0，见 `20260913_audit_fix_py_compile.txt`。
- 修复后空数据检查：退出码 2；数据仍未提供，见 `20260913_audit_fix_dataset_check_empty.json`。
- 修复后环境探针：退出码 2；GPU 查询成功但 `nvcc`、Darknet 和 CUDA 设备冒烟程序仍缺失，见 `20260913_audit_fix_environment_probe.json`。
- 问题处置与复审边界：见 `20260913_audit_fix.md`；AUD-S1-T01-004～006为“开发已修复、待独立复审确认”，不代替审查签结。

历史空数据结论（已由 2026-09-14 最新数据准备交接更新）：S1-T01 G0 仍未通过，G1/G2/G4 未执行，G3 对纯 PC 准备任务不适用；当前真实数据、标签、清单和自动检查证据已补齐，但仍没有 Darknet cfg、权重、检查点、训练日志或评估输出。不得把回归夹具或 HaGRID 公开资料指标写成真实手势精度。

请审查以下范围：

1. 检查器的清单字段、归一化 YOLO 标签约束、人员/会话隔离和跨集合重复检查是否覆盖 AC02—AC04。
2. 检查历史失败证据和 2026-09-14 最新数据证据是否准确反映“数据已提供但 Darknet/CUDA 未就绪”，以及是否错误扩大了任务边界。
3. 审查不得把 G0、环境探针失败或工具回归通过改写为阶段1或模型精度通过。

审查结果请按问题编号、文件位置、依据、关闭条件和复核版本回写；审查窗口不直接修改被审实现。

## 版本绑定

- 任务规格：原项目笔记 `03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`，2026-09-13。
- 阶段计划：原项目笔记 `02-方案设计/B方案实施与阶段验收计划.md`，v3.0，2026-09-13。
- 基础修复提交：`48cbd749721917c30346dafd631a5e11941b654c`；初始功能提交为 `6be0d6e80b8b55ca214061103ac64852a76cea75`；本轮数据准备脚本和证据随新的交付提交提交；当前代码文件 SHA-256 见下表。
- 当前工作区既有无关改动：`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr`，不属于 S1-T01，不应混入审查版本。

| 对象 | SHA-256 或状态 |
|---|---|
| `verification/s1_t01_dataset_check.py` | `3381E0A25DE5D8C2AB03211A52F2FE140D7BE2C204F81E94E92FED4CAD19ACCE` |
| `verification/s1_t01_environment_probe.py` | `6A77BC477758B4DB61F68A2F4D2A4242C52B6D9C100C11F1932DB036806928A5` |
| `verification/test_s1_t01_dataset_check.py` | `9188116CE1108C4D78A9E60D0671B84891CE6F3F8BFC180D85ACAC2B45067266` |
| `verification/test_s1_t01_environment_probe.py` | `9B3B95225AB9AF18C5A9536FF946A9986ACCB8AFA4E8B3F61B05763162B6FCDA` |
| `verification/s1_t01_prepare_hagrid.py` | `44617AAAC645DB120625E18DBFEB0B90769D6FFC98EC53BF530BF732675F1BF3` |
| `verification/s1_t01_filter_manifest.py` | `BED9A422567F0D4485A4A66FFB2FC67110564280D9581DE7E4394659251CF21D` |
| `verification/test_s1_t01_prepare_hagrid.py` | `D4687615BACDEEE564E0E53CA72AF608FC4C951E02D37B0C4009B754F31EC768` |
| `verification/test_s1_t01_filter_manifest.py` | `A80DCB4B7076877951AB9A0B47C288628B45EABC97FE0239ACAF6BF26A9CA54A` |
| `data/README.md` | `582CA4EC4896EE608636F57ACD5CC4BFFC867F74C6A08CAFD71DD7CDEB597F81` |
| `scripts/README.md` | `A66BD12921D3A0D9AF3FBF05C0E692E440071C4D3F15062A49DC696C0123A950` |
| S1-T01 主记录 | `C7DA418D22575D0D87604F816E8F3874EAC2D37ABE665D06E8B9F40D75EC776D` |
| `report/evidence/S1-T01/20260914_hagrid_prepare.json` | `884F500B775D10B17B1ED0CDB82B3D8BB708B3293384953CF431EFA50080C5C0` |
| `report/evidence/S1-T01/20260914_hagrid_filter_manifest.json` | `29B4CEC5505DFC5C67FF4C5CE0B0AFB36944B1100AAB5D8BFFE37D63A50B3EFE` |
| `report/evidence/S1-T01/20260914_hagrid_dataset_check_clean.json` | `01D658D0E76F26EEAA17984EFCDC7F6959D9488E33CD1BD66E7785A47990DC63` |
| `report/evidence/S1-T01/20260914_hagrid_extract_progress.md` | `9EE815D99B8FA96D654C20787F7BCBE5B40635CF3E4CAFD6E964AB5E731EA621` |
| `report/evidence/S1-T01/20260914_hagrid_visual_review.md` | `F7C89DE82580CB664F4D582B497A6C1BC9844B57BCAFB7256526CCD3314CEFED` |
| `report/evidence/S1-T01/20260914_hagrid_dataset_check_clean.log` | `32D06A0BA4F8D60987F61747C7F48B34601527D7D1B198E09C8D866F9A1FFCDC` |
| `report/evidence/S1-T01/20260914_hagrid_duplicate_analysis.log` | `AE1E92B8BC4E03ABF53E553EC176D5D27B2741B731A1C84425F348D79710968B` |
| `report/evidence/S1-T01/20260914_hagrid_filter_manifest_final.log` | `498F61CA1E93EE4C9B999D8AE3FB58CC9603F9FD911620575DB8716642CA9F21` |
| `report/evidence/S1-T01/20260914_hagrid_prepare_final.log` | `A349F2AE55D85012680BFD43D3F28DA44AF0F0241EA2F34B4F63F63FA6316EF9` |
| B 方案实施与阶段验收计划 v3.0 | `A94830AFE60AE6A339038C1F41656101931A2999529A1BF866AD75D8D1C9F3FD` |
| 数据清单 `D:\FPGA_Data\HaGRIDv2\manifest.csv` | `74D4A0ABEC61EA4698CAF0479FFB8FFFD0B27F308166D81E13A5C20AD06AECB4`（正式清单） |
| Darknet 提交与五类 tiny cfg | 尚未锁定，不存在，SHA-256 不适用 |
| 训练检查点 | 未生成（AC05 未执行） |
| 初始空数据检查 JSON | `41DBACB3B22531DF224859B5E919F13664E9D36077EA9E0DE2DBA6204C5F8AE6` |
| 初始环境探针 JSON | `32FDEDD9B41AC52E7CF33A597D6DD8CAC65F157E7A59ABF7EE4B1740946406E1` |
| 修复后空数据检查 JSON | `B7953D95896778F6E749D26D95B7309C1309170E730829960E95974FA5E276E9` |
| 修复后环境探针 JSON | `EE500D9264BB6DF344A6FBE7487B2708CAC88966EE461DDF718DE4B0D4F6410D` |
| 修复后定向回归 JSON | `0479DB7D0601D447A39D27E7587408A202BC4C4137403EBB9E91A6A08EDF6DAE` |
| 修复后全量回归摘要 | `851B290E20F5CFF7494B85C01C01F60472C3D77F712B6568A7AAB59340BB69C6` |
| 修复后编译摘要 | `4F00A8D9A463B7FF8646A9C2C8C78C2D11A4FC0B80B5AF5416CDF281800CADCD` |

## 未执行与下一输入

- AC01：Darknet/CUDA 不就绪，未进行框架设备运算。
- AC02—AC04：缺少真实数据根目录、来源/许可登记、清单和可视化样本。
- AC05—AC07：未训练、未保存/恢复检查点、未评估、未复跑交接。
- AUD-S1-T01-004～006：开发修复已提交并回归，等待独立复审在固定提交上复核关闭；真实环境失败不是修复回归失败。
- Wong 需按任务记录中的采集/标注操作单回传外部数据根目录、会话与人员信息、五类框统计、无手统计、来源许可和清单/数据包 SHA-256；无需进行板卡接线或烧录。

## 2026-09-14 最新数据准备交接消息

请审查当前 S1-T01 数据准备版本。Wong 已提供外部 HaGRIDv2 数据，七个下载包已逐个 CRC/内容校验、解压并清理；正式数据根目录为 `D:\FPGA_Data\HaGRIDv2`，正式清单为 `manifest.csv`，未去重备份为 `manifest_all.csv`。

本轮开发与证据交付提交：`9174c465481b153872c83cf4312679438641a6ec`；提交后 14 项 Python 回归、编译和证据 JSON 解析均退出码 0。

- 标签生成：`verification\s1_t01_prepare_hagrid.py`，逐 JSON、递归适配官方嵌套目录；目标编码 `0=fist, 1=palm, 2=one, 3=two_up, 4=three`，`no_gesture` 作为无框负样本。原始转换 158,698 行/156,536 框，缺图 0、未知目标标签 0。
- 去重：`verification\s1_t01_filter_manifest.py`，完整 SHA-256 重复分析定位 16 组/54 行跨 split 重复，按 `train > val > test` 移除 23 行（val 7、test 16），不删除原始图片或标签。正式清单 158,675 行/156,518 框，SHA-256 `74d4a0abec61ea4698caf0479ffb8fffd0b27f308166d81e13a5c20ad06aecb4`。
- 清洁清单全量回归退出码 0，`PASS_AUTOMATED_MANUAL_PENDING`：158,675/158,675 图片和标签有效，AC02/AC03 自动通过，跨 split 完全重复为 0，人员/会话交叉为空。报告：`20260914_hagrid_dataset_check_clean.json`。
- 可视化：15 张真实图片自包含 SVG 位于 `20260914_hagrid_previews_clean`；人工复核单为 `20260914_hagrid_visual_review.md`。人工观察尚未执行，AC04 保持自动通过、人工待复核，不代替审查签结论。
- 许可证：`D:\FPGA_Data\HaGRIDv2\license\en_us.pdf` SHA-256 `14f4845e9c8d3de875cbac4139491da368ab1040a7f565e02894477279134d22`。原 ZIP 按用户要求删除，未采集 ZIP SHA-256，仅保留 ZIP CRC/条目数/解压尺寸证据。
- 训练：`nvcc`、官方 Darknet/CUDA 设备环境仍缺失；小样本训练、评估、检查点、恢复和真实精度验证未执行，G0/AC01 仍未通过。不得把公开数据规模或本次自动校验当作识别精度。

审查回传应明确：人工叠框是否通过；是否接受 `session_id=hagridv2_official_split_<split>` 作为“分区键而非物理会话”的限定；以及是否关闭当前 AC04 人工观察项。审查窗口不直接修改实现代码。

## 2026-09-14 自动复核与审查接力绑定

- 当前审查锚点：`1e0641d45c95f4ca8336ef8b191efcd3f3cf9e4d`；代码修复、数据准备和文档证据均以该提交及其祖先链定位。工作区列出的 Vivado、总控、接手提示词和板卡照片改动均与本任务无关。
- 环境再核对：`20260914_environment_recheck.json`，SHA-256 `995238D2331A1910D76746AD36CF137F54777FFEA1114046BD3DCF7E9EEBE722`，实际退出码 `2`；GPU 查询成功，`nvcc`、官方 Darknet 和固定 CUDA 设备冒烟程序缺失。
- 当前全量自动回归：14 项 Python 单测退出码 `0`；显式 `py_compile` 退出码 `0`；4 份证据 JSON 解析退出码 `0`。这只证明工具和数据完整性检查，不证明训练精度或阶段通过。
- 独立复审接力文件：`20260914_review_handoff.md`，SHA-256 `8280C8DEBFF165868187FE4602032A77C7F014B13B1F71E591EB9454E428311`。该文件固定 AUD-S1-T01-004～006、007、AC04 人工抽查和 G0/AC01 环境边界的复核要求。
- 复审输入仍为正式清单 `D:\FPGA_Data\HaGRIDv2\manifest.csv`，SHA-256 `74d4a0abec61ea4698caf0479ffb8fffd0b27f308166d81e13a5c20ad06aecb4`；人工叠框观察和环境就绪仍是未完成项。没有新的任务编号和任务卡时，不启动后续任务。
