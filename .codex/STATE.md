# 项目状态

更新：2026-09-15（UTC+8）。恢复先读 `AGENTS.md`；本文件只保存跨会话事实，详细实现与证据按需读取。

## 目标、阶段与基线

- 目标：AX7020 摄像头五类手势检测，经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现竞赛作品。
- 阶段0已按硬件身份、JTAG 与 XA 目标工程范围通过；当前阶段1「PC 模型与数值规格」未通过。阶段1文档收尾不代表训练或验收完成。
- 活动任务：S1-T01 训练环境与数据准备；D4 环境子任务、D5A 配置/权重/dry-run 子任务和 D5B-1 短训/恢复子任务已完成 G1/G2，D5A 证据提交为 `29e43a0`、D5B-1 代码/证据提交为 `5645a17`；D5B-2 全量评估/复现尚未完成，整体 AC06/AC07 与 G4 仍未完成；G3 对本任务不适用。S1-T01-D1 official Darknet 工作流入口已完成 G1/G2 并提交 `94fe7da2689f5556d49418e089858aa8001cc736`；D5B2 单进程 stdin 评估工具改进已提交 `de822c4`，全量评估证据已提交 `0619905`，不等于整体任务或阶段通过。
- 最近工程实现基线：`4c82535dba330a85187adba53e42f4e41c365981`（D4 CUDA smoke、官方 Darknet CUDA 构建、环境 probe 与身份绑定）。本提交不推进训练、硬件验收或阶段切换。

## 已确定的架构与接口

- 实物 AX7020、XA7Z020/CLG400；JTAG IDCODE `0x23727093`；使用 `-1` 时序基线，精确速度后缀仍待原厂/供应商证明。
- YOLOv4-tiny 优先上板，完整 YOLOv4 仅 PC 对照；官方 Darknet 训练路线；比较 320/416 彩色输入后再经精度、数值、资源关口由 Wong 冻结。旧 32×32 分类方案停用。
- PL：预处理、分块 INT8 主要计算，DDR/BRAM 缓冲；PS：调度、检测头解码、阈值/NMS、显示与交互。
- 类别：`0=fist, 1=palm, 2=one, 3=two_up, 4=three`；输出框、类别、分数、帧号。PS/PL 地址、时序、布局、量化、阈值与性能尚未全部冻结，详见系统设计。
- HDMI 摄像头→板卡输入→FPGA→HDMI 输出为偏好，端口/器件/摄像头兼容性留阶段3实测；UART 连接不代表功能通过。

## 数据、环境与已完成证据

- 实际数据目录 `D:\FPGA_Data\HaGRIDv2`；最终清单 `manifest.csv`，158680 行；原始 `manifest_all.csv` 与最终清单须区分，当前 manifest SHA-256 为 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- 已实现 HaGRID COCO→YOLO 转换、去重、图片/标签与分组检查、人工语义绑定，以及环境探针和 CUDA 冒烟源；CUDA 源存在不代表已编译运行。
- 2026-09-15 追加 Wong 确认的 5 张真实 no_hand（朋友照片且同意内部项目使用）：前三张 train、后两张 val，人员/会话两侧不交叉，空标签；语义表与外部 manifest 均精确追加 5 行。
- 新语义全量检查报告退出码 **0**，有效行/图片 `158680/158680`，`no_hand=train 3、val 2、test 0`，人员/会话交叉为空，AC02/AC03 自动通过；报告状态仍按工具约定为 `PASS_AUTOMATED_MANUAL_PENDING`，AC04 的 10 张带框、5 张 no_hand 与 5 张非目标手势人工语义现已分别有记录和批准 JSON，任务总体验收仍保留人工证据核对。
- 已完成 D3 官方 Darknet 输入绑定独立复审：158680/158680 sidecar 内容匹配，train/valid 清单与 manifest 集合/顺序一致，五类 names/data 可解析，Reviewer PASS；外部产物与哈希见 `20260915_darknet_input_binding.md`。不等于 Darknet/CUDA 已构建或训练通过。
- 最新语义证据记录 AC02 自动检查通过；不替代其他验收或独立签结。历史全量数据退出码0已被语义重查的退出码2更新。
- 最近代码回归证据：S1-T01-D1 定向 24 项、全量 `verification` 48 项测试通过，14 个 Python 文件编译检查通过，独立 Reviewer 对第3轮候选 PASS；真实预检退出码2、`BLOCKED_PREFLIGHT`、Darknet 命令数0。工作流和三轮阻断证据入口见 `report/evidence/S1-T01/`，代码提交为 `94fe7da2689f5556d49418e089858aa8001cc736`。本轮全量数据扫描运行约 78 分钟后退出码0，报告为 `20260915_hagrid_dataset_check_semantic_after_no_hand.json`。
- 环境 D4 已通过：VS Build Tools 17.14.40/MSVC 19.44、CUDA Toolkit 13.4.59、CMake 3.30.2、RTX 4060 Laptop/驱动 610.88；固定 smoke `sm_89` 真实运行通过，官方 Darknet commit `59596d7880f6504768df41d6daa586f5cb2b932f` 以 CMake CUDA ON/CUDNN OFF/OpenCV OFF 构建成功。安装后 probe status=PASS、退出码0；Darknet SHA-256 `358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`，smoke SHA-256 `4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c`。D5A 已固定 416 cfg（SHA-256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`）和官方 `yolov4-tiny.conv.29`（19,789,716 bytes，SHA-256 `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`），r2 dry-run 为 `PLANNED_NO_EXECUTION`/exit 0，独立 Reviewer PASS；D5B-1 已真实训练 1～20 步并恢复 11～20 步，train/resume 报告均 `EXECUTED_REVIEW_REQUIRED`、顶层 exit 0、独立 Reviewer PASS；D5B-2 全量评估/复现尚未完成，正式长训、INT8 检测量化及整网 RTL 尚未开始。

## 下一步与边界

1. 按 `git status` 重新确认工作区归属；迁移开始前用户已有 `docs/obsidian-project/总控.md`、`docs/obsidian-project/项目接手提示词.md`、`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 修改及两张板卡 JPG，未纳入工作流提交。
- 2. 数据/无手输入已完成自动检查、人工语义记录、批准 JSON 和 Darknet sidecar/list 绑定；AC04 工具状态仍保留人工待复核语义，后续训练前复核预览入口和批准记录哈希，不用非目标手势代替 no_hand。
- 3. D4 环境关口、D5A 配置/权重/dry-run 和 D5B-1 短训/恢复关口已通过；D5B-2 工具提交 `de822c4` 与全量输出已独立复审 PASS，AC06 流程闭环完成但不含 mAP/精度结论；AC07 复跑、正式精度阈值和 S1-T01 G4 仍待完成。勿把当前 200 步诊断权重冻结为最终模型。
4. 在固定配置与权重后完成 AC04 总体核对及 AC05～AC07 短程训练/恢复/评估/复现，再验收 S1-T01。不得自行跳到正式长训、量化、烧录或下一阶段。
5. 当前采用一个阶段总控自动协调 Developer/Reviewer，最多3轮修复复审后总控重析；状态在此维护，不再依赖旧窗口或交接文件。

## 正式文档与证据入口（仓库相对路径）

- 系统架构：`docs/obsidian-project/02-方案设计/系统设计.md`；阶段计划：同目录 `B方案实施与阶段验收计划.md`。
- 接口依据：`docs/obsidian-project/02-方案设计/INT8乘加接口说明.md`（原型接口，不代表整网支持）。
- 任务标准：`docs/obsidian-project/03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`（历史状态按最新证据解释）。
- 验收：`docs/obsidian-project/04-提交材料/验收执行手册.md`；阶段1范围：同目录 `阶段验收/阶段1_PC模型与数值规格收尾记录.md`。
- 最新整改：`report/evidence/S1-T01/20260914_semantic_repair.md`；报告：同目录 `20260914_hagrid_dataset_check_semantic.json`（clean 报告为同结果副本）。
- 人工语义：`report/evidence/S1-T01/20260914_hagrid_semantic_review.csv`；本轮收尾：`20260915_no_hand_ingest.md`、`20260915_hagrid_visual_review_after_no_hand.md`、`20260915_hagrid_dataset_approval.json`。
- 环境：`report/evidence/S1-T01/20260914_environment_recheck.json`；命令和源程序入口：`verification/README.md`、`verification/s1_t01_cuda_smoke.cu`。
- D4 安装后环境：`report/evidence/S1-T01/20260915_s1_t01_d4_round3_summary.md`、`20260915_environment_probe_after_install_v3.json`、`20260915_darknet_cmake_build_release.md`、`20260915_cudnn_check_after_install.md`；独立 Reviewer 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d4-round3-20260915\review_s1_t01_d4_round3_final.json`。
- D5A 配置/权重/dry-run：`report/evidence/S1-T01/20260915_s1_t01_d5a_preflight_r2.json`、`20260915_s1_t01_d5a_preflight_r2_summary.md`、`20260915_s1_t01_d5a_short_train_preflight_blocked.md`；独立 Reviewer PASS 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5a-r2-final-20260915-180935\review_s1_t01_d5a_r2_final.json`。外部 cfg/weight 不在 Git，使用上述固定路径与哈希。
- D5B-1 短训/恢复：`report/evidence/S1-T01/20260915_s1_t01_d5b1_r1_summary.md`、`20260915_s1_t01_d5b1_train_r1.json`、`20260915_s1_t01_d5b1_resume_r1.json`；训练报告 SHA-256 `e46a433d5bccd209fc1f117280affce06e6f47a1166bd2024aaa3d776da3b45b`，恢复报告 SHA-256 `24cbecaccb37cde0e4755499a771b3291948714a813ebad7cdee4d7222d8111a`，workflow 修复提交 `5645a17`；独立 Reviewer PASS 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b1-fix-20260915-191045\review_s1_t01_d5b1_fix_r1_final.json`。外部训练/恢复 checkpoint 和日志位于 `D:\FPGA_Data\HaGRIDv2\darknet_inputs`，未纳入 Git。
- D5B-2 工具改进：提交 `de822c4`；独立复审 PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b2-r3-20260915-r2\independent_r3_final_check.json`；r2 中止与 r3 smoke 分别见 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r2\abort_status.json`、`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r3_smoke_final\smoke_result.json`，均为外部运行证据，未纳入 Git。
- D5B-2 全量评估：报告与失败/中止摘要已提交 `0619905`，主报告 `20260915_s1_t01_d5b2_eval_r4_full_200.json` SHA-256 `843ed924af2b6799b75eed57fe799c8dba232409b2188bea07a11e1ee04d12e8`；valid 15195/15195、逐图 15195、11,212 框、friend_004 零框；独立 Reviewer 31/31 PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b2-full-r1-20260915\review_s1_t01_d5b2_full_r1_final.json`，SHA-256 `deb1cf23d15abce5304dda30951dcfccc2720ba5a31119099e83e209c83f48bd`。外部 run-dir 未纳入 Git。
