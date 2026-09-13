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

当前结论：S1-T01 G0 未通过，G1/G2/G4 未执行，G3 对纯 PC 准备任务不适用；没有图片、标签、Darknet cfg、数据哈希、权重、检查点、训练日志或评估输出。不得把回归夹具或 HaGRID 公开资料指标写成真实手势精度。

请审查以下范围：

1. 检查器的清单字段、归一化 YOLO 标签约束、人员/会话隔离和跨集合重复检查是否覆盖 AC02—AC04。
2. 检查当前失败证据是否准确反映“数据和 Darknet 未提供”，以及是否错误扩大了任务边界。
3. 审查不得把 G0、环境探针失败或工具回归通过改写为阶段1或模型精度通过。

审查结果请按问题编号、文件位置、依据、关闭条件和复核版本回写；审查窗口不直接修改被审实现。

## 版本绑定

- 任务规格：原项目笔记 `03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`，2026-09-13。
- 阶段计划：原项目笔记 `02-方案设计/B方案实施与阶段验收计划.md`，v3.0，2026-09-13。
- 当前代码提交：`48cbd749721917c30346dafd631a5e11941b654c`；初始功能提交为 `6be0d6e80b8b55ca214061103ac64852a76cea75`；当前代码文件 SHA-256 见下表。
- 当前工作区既有无关改动：`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr`，不属于 S1-T01，不应混入审查版本。

| 对象 | SHA-256 或状态 |
|---|---|
| `verification/s1_t01_dataset_check.py` | `3381E0A25DE5D8C2AB03211A52F2FE140D7BE2C204F81E94E92FED4CAD19ACCE` |
| `verification/s1_t01_environment_probe.py` | `6A77BC477758B4DB61F68A2F4D2A4242C52B6D9C100C11F1932DB036806928A5` |
| `verification/test_s1_t01_dataset_check.py` | `9188116CE1108C4D78A9E60D0671B84891CE6F3F8BFC180D85ACAC2B45067266` |
| `verification/test_s1_t01_environment_probe.py` | `9B3B95225AB9AF18C5A9536FF946A9986ACCB8AFA4E8B3F61B05763162B6FCDA` |
| `data/README.md` | `464475DE605C832A0E7C451E77BEA5F9527E36444A6B1FAF2D076335AA80620D` |
| `scripts/README.md` | `EF44B684049560F82D7721A4DFA372731F395EC957132FABBB6BFEEA12933468` |
| S1-T01 主记录 | `54AC9E3D6FD45B3E59501542D1641E2D32BDC456978A8CEE603E34265A678E17` |
| B 方案实施与阶段验收计划 v3.0 | `A94830AFE60AE6A339038C1F41656101931A2999529A1BF866AD75D8D1C9F3FD` |
| 数据清单 `data/manifest.csv` | 未提供，不存在，SHA-256 不适用 |
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
