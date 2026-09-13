# S1-T01 开发交接与审查入口

## 可直接转交审查窗口的消息

请审查 `S1-T01 训练环境与数据准备` 的当前开发版本。任务规格沿用原项目笔记中的 S1-T01 任务卡和《B方案实施与阶段验收计划》v3.0；当前范围是官方 Darknet/CUDA 环境、五类带框数据清单、标签检查和小样本流程，不包含正式长训、INT8 量化、RTL 或板卡验证。YOLOv4-tiny 仍只是优先上板候选，完整 YOLOv4 只作 PC 对照，输入尺寸和性能未冻结。

本轮开发新增：

- `D:\FPGA_Competition\verification\s1_t01_dataset_check.py`：UTF-8 CSV 清单、路径、图片头部、YOLO 标签、五类覆盖、无手样本、人员/会话隔离、跨集合重复内容检查，并输出 JSON、抽查候选和 SVG 叠框预览。
- `D:\FPGA_Competition\verification\s1_t01_environment_probe.py`：只读检查受控 Python/NumPy/GPU/`nvcc`/CMake/明确指定 Darknet，不安装、不下载、不切换框架、不训练。
- `D:\FPGA_Competition\verification\test_s1_t01_dataset_check.py`：2 项无外部依赖回归测试；测试夹具不构成真实手势精度证据。
- `D:\FPGA_Competition\data\README.md`、`D:\FPGA_Competition\scripts\README.md`：清单接口与命令说明。

已执行证据：

- 检查器回归：退出码 0，2 项通过。
- 当前空 `data/` 检查：退出码 2；`data/manifest.csv` 不存在，AC02/AC03 未通过，AC04 未执行。
- 环境探针：退出码 2；受控 Python 3.12.14、NumPy、RTX 4060 Laptop GPU、CMake 3.30.2 可查询，`nvcc` 和 Darknet 未就绪。
- JSON 原始证据：`20260913_developer_dataset_check_empty.json`、`20260913_developer_environment_probe.json`。

当前结论：S1-T01 G0 未通过，G1/G2/G4 未执行，G3 对纯 PC 准备任务不适用；没有图片、标签、Darknet cfg、数据哈希、权重、检查点、训练日志或评估输出。不得把回归夹具或 HaGRID 公开资料指标写成真实手势精度。

请审查以下范围：

1. 检查器的清单字段、归一化 YOLO 标签约束、人员/会话隔离和跨集合重复检查是否覆盖 AC02—AC04。
2. 检查当前失败证据是否准确反映“数据和 Darknet 未提供”，以及是否错误扩大了任务边界。
3. 审查不得把 G0、环境探针失败或工具回归通过改写为阶段1或模型精度通过。

审查结果请按问题编号、文件位置、依据、关闭条件和复核版本回写；审查窗口不直接修改被审实现。

## 版本绑定

- 任务规格：原项目笔记 `03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`，2026-09-13。
- 阶段计划：原项目笔记 `02-方案设计/B方案实施与阶段验收计划.md`，v3.0，2026-09-13。
- 当前代码提交：待本轮提交后填写完整提交哈希；代码文件 SHA-256 见下表。
- 当前工作区既有无关改动：`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr`，不属于 S1-T01，不应混入审查版本。

| 对象 | SHA-256 或状态 |
|---|---|
| `verification/s1_t01_dataset_check.py` | `B65C0E4767B8D69DF8F893B5C0106CD95B02800E097EB2F115D10C5BD447BD5C` |
| `verification/s1_t01_environment_probe.py` | `3345BCDD7682672AA0480059E4E9EB1F3D7F87AB622C13D409A926E0F970125A` |
| `verification/test_s1_t01_dataset_check.py` | `45D3912FD8F293D6E2DA31D9A204045538F0B8DEF1AF929C1CF19D8A0231442B` |
| `data/README.md` | `32516D1D2BD9A8C5E38946A2F009385108042E7CA13BD24371A6F9B188B4E532` |
| `scripts/README.md` | `9892B45ACA6D5940400C7E6498AD2456EA7BAE78239DB99165E4530D1CA63B1A` |
| S1-T01 主记录 | `C30AAC3BB9810A39C67459C0A730EEC4995F21F61FEAF22FC209D8926EC87F33` |
| B 方案实施与阶段验收计划 v3.0 | `A94830AFE60AE6A339038C1F41656101931A2999529A1BF866AD75D8D1C9F3FD` |
| 数据清单 `data/manifest.csv` | 未提供，不存在，SHA-256 不适用 |
| Darknet 提交与五类 tiny cfg | 尚未锁定，不存在，SHA-256 不适用 |
| 训练检查点 | 未生成（AC05 未执行） |
| 当前空数据检查 JSON | `41DBACB3B22531DF224859B5E919F13664E9D36077EA9E0DE2DBA6204C5F8AE6` |
| 环境探针 JSON | `32FDEDD9B41AC52E7CF33A597D6DD8CAC65F157E7A59ABF7EE4B1740946406E1` |

## 未执行与下一输入

- AC01：Darknet/CUDA 不就绪，未进行框架设备运算。
- AC02—AC04：缺少真实数据根目录、来源/许可登记、清单和可视化样本。
- AC05—AC07：未训练、未保存/恢复检查点、未评估、未复跑交接。
- Wong 需按任务记录中的采集/标注操作单回传外部数据根目录、会话与人员信息、五类框统计、无手统计、来源许可和清单/数据包 SHA-256；无需进行板卡接线或烧录。
