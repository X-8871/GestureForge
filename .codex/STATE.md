# 项目状态

更新：2026-09-14（UTC+8）。恢复先读 `AGENTS.md`；本文件只保存跨会话事实，详细实现与证据按需读取。

## 目标、阶段与基线

- 目标：AX7020 摄像头五类手势检测，经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现竞赛作品。
- 阶段0已按硬件身份、JTAG 与 XA 目标工程范围通过；当前阶段1「PC 模型与数值规格」未通过。阶段1文档收尾不代表训练或验收完成。
- 活动任务：S1-T01 训练环境与数据准备；G0/AC01 未通过，G1/G2/G4 未完成；G3 对本任务不适用。语义整改与环境探针防伪修复已独立复审通过并提交，真实数据/环境缺口仍未关闭。
- 最近工程实现基线：`073134b6ee005990ce30952f78ca005830197ce0`（环境身份绑定与哈希清单追溯修复）。本提交不推进训练、硬件验收或阶段切换。

## 已确定的架构与接口

- 实物 AX7020、XA7Z020/CLG400；JTAG IDCODE `0x23727093`；使用 `-1` 时序基线，精确速度后缀仍待原厂/供应商证明。
- YOLOv4-tiny 优先上板，完整 YOLOv4 仅 PC 对照；官方 Darknet 训练路线；比较 320/416 彩色输入后再经精度、数值、资源关口由 Wong 冻结。旧 32×32 分类方案停用。
- PL：预处理、分块 INT8 主要计算，DDR/BRAM 缓冲；PS：调度、检测头解码、阈值/NMS、显示与交互。
- 类别：`0=fist, 1=palm, 2=one, 3=two_up, 4=three`；输出框、类别、分数、帧号。PS/PL 地址、时序、布局、量化、阈值与性能尚未全部冻结，详见系统设计。
- HDMI 摄像头→板卡输入→FPGA→HDMI 输出为偏好，端口/器件/摄像头兼容性留阶段3实测；UART 连接不代表功能通过。

## 数据、环境与已完成证据

- 实际数据目录 `D:\FPGA_Data\HaGRIDv2`；最终清单 `manifest.csv`，158675 行；原始 `manifest_all.csv` 与最终清单须区分，哈希见整改证据。
- 已实现 HaGRID COCO→YOLO 转换、去重、图片/标签与分组检查、人工语义绑定，以及环境探针和 CUDA 冒烟源；CUDA 源存在不代表已编译运行。
- 最新语义全量检查有效行 158675/158675，但退出码 **2**；`no_hand=0/5`，train/val 均缺真实无手，**AC03 不通过**。目录名 `no_gesture` 和空标签不能证明真实无手。
- Wong 确认带框预览 1～10 通过，登记 `target_gesture=10`；11～15 有手但非目标，登记 `non_target_gesture=5`，不得计入 no_hand。**AC04 仍未完全关闭**。
- 最新语义证据记录 AC02 自动检查通过；不替代其他验收或独立签结。历史全量数据退出码0已被语义重查的退出码2更新。
- 最近代码回归证据：全量 `verification` 24 项测试通过，11 个 Python 文件编译检查通过；哈希清单 40 个实际文件条目逐字节一致；独立 Reviewer 对候选修复 PASS。本轮未运行约78分钟全量数据扫描。
- 环境最近证据：受控 Python 3.12.14、Pillow 12.3.0；NumPy/NVIDIA 查询/CMake 可用，`nvcc`、官方 Darknet、固定 CUDA 冒烟可执行文件未就绪；默认探针退出码2。AC05～AC07 未完成，无短训保存/恢复/评估闭环；正式长训、INT8 检测量化及整网 RTL 尚未开始。

## 下一步与边界

1. 按 `git status` 重新确认工作区归属；迁移开始前用户已有 `docs/obsidian-project/总控.md`、`docs/obsidian-project/项目接手提示词.md`、`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 修改及两张板卡 JPG，未纳入工作流提交。
2. 补真实 no_hand 至少5张并完成人工确认、来源许可及划分记录，train/val 都须覆盖；按采集单执行，不能用非目标手势替代；收到后重跑 AC03/AC04。
3. 补齐官方 Darknet/CUDA 真实设备运算并冻结代码/cfg/依赖哈希；恢复先检查既有长进程，勿重复启动约78分钟全量检查或训练。
4. 数据、环境关口通过后完成 AC04 与 AC05～AC07 短程训练/恢复/评估及复现，再验收 S1-T01。不得自行跳到正式长训、量化、烧录或下一阶段。
5. 当前采用一个阶段总控自动协调 Developer/Reviewer，最多3轮修复复审后总控重析；状态在此维护，不再依赖旧窗口或交接文件。

## 正式文档与证据入口（仓库相对路径）

- 系统架构：`docs/obsidian-project/02-方案设计/系统设计.md`；阶段计划：同目录 `B方案实施与阶段验收计划.md`。
- 接口依据：`docs/obsidian-project/02-方案设计/INT8乘加接口说明.md`（原型接口，不代表整网支持）。
- 任务标准：`docs/obsidian-project/03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`（历史状态按最新证据解释）。
- 验收：`docs/obsidian-project/04-提交材料/验收执行手册.md`；阶段1范围：同目录 `阶段验收/阶段1_PC模型与数值规格收尾记录.md`。
- 最新整改：`report/evidence/S1-T01/20260914_semantic_repair.md`；报告：同目录 `20260914_hagrid_dataset_check_semantic.json`（clean 报告为同结果副本）。
- 人工语义：`report/evidence/S1-T01/20260914_hagrid_semantic_review.csv`；待执行采集：同目录 `20260914_no_hand_collection_sheet.md`。
- 环境：`report/evidence/S1-T01/20260914_environment_recheck.json`；命令和源程序入口：`verification/README.md`、`verification/s1_t01_cuda_smoke.cu`。
