# AX7Z020 Gesture Engineering Workspace

本目录保存 Vivado、Vitis、日常验证和构建产物；`docs/obsidian-project/` 保存指定 Obsidian 项目笔记的 Git 快照，原笔记仍在知识库维护。

仓库：https://github.com/X-8871/GestureForge 。同步范围与操作见 [仓库同步说明](docs/仓库同步说明.md)。

## 阶段开发入口

新阶段在本项目新建一个总控会话，只需给出阶段目标，例如：“读取 AGENTS.md 和 .codex/STATE.md，继续当前阶段；使用 Developer 与 Reviewer subagent 自动完成开发、审查和修复。”

- [AGENTS.md](AGENTS.md)：当前 Agent 工作规则、验证要求与自动协作协议。
- [.codex/STATE.md](.codex/STATE.md)：唯一当前状态和下一步；代码与 Git 保存实现及历史。
- 总控在当前阶段内自动交接；阶段结束验证、更新状态、提交并汇报，由 Wong 决定下一阶段。
- `docs/obsidian-project/` 中旧总控、角色提示词、工作流、工程协作规范及项目进程保留作历史快照，不再作为当前协作指令或状态源。正式需求、设计、接口与验收证据仍按任务读取。

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
