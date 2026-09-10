# AX7Z020 Gesture Engineering Workspace

本目录保存 Vivado、Vitis、日常验证和构建产物；`docs/obsidian-project/` 保存指定 Obsidian 项目笔记的 Git 快照，原笔记仍在知识库维护。

仓库：https://github.com/X-8871/GestureForge 。同步范围与操作见 [仓库同步说明](docs/仓库同步说明.md)。

工程根目录：`D:\FPGA_Competition\`

## 目录

- `vivado/`：正式 Vivado 工程。
- `vitis/`：PS 侧软件工程。
- `verification/`：临时验证工程、仿真输出和综合报告。
- `build/`：bitstream、xsa、bin 等正式构建产物。
- `scripts/`：工程重建、数据转换和批处理脚本。
- `src/`：提交包统一入口，汇总 RTL、HLS 和 PS 侧源码。
- `sim/`：提交包统一入口，汇总仿真脚本和结果。
- `board/`：板卡资料、测试数据和参考结果。
- `data/`：输入样例、标签和数据集说明。
- `skill/`：可复用技能包，必须包含 README.md。
- `report/`：设计报告和 AI 协作记录。

提交包按 AMD 选题指南的推荐结构组织；开发阶段的 `vivado/`、`vitis/`、`verification/` 与最终提交目录保持对照关系。

工程名称、源文件名称和工程目录使用英文、数字和下划线。
