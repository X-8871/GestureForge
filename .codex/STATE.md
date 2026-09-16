# 项目状态

更新：2026-09-16（UTC+8）。恢复先读 `AGENTS.md`；本文件只保存跨会话事实，详细实现与证据按需读取。

## 目标、阶段与基线

- 目标：AX7020 摄像头五类手势检测，经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现竞赛作品。
- 阶段0已按硬件身份、JTAG 与 XA 目标工程范围通过；当前阶段1「PC 模型与数值规格」未通过。阶段1文档收尾不代表训练或验收完成。
- 活动任务：S1-T01 训练环境与数据准备已完成任务级 G4；AC01–AC07、G1、G2、G4 均由独立 Reviewer 第2轮通过，G3 对纯 PC 环境/数据流程任务不适用。AC07 证据提交为 `33dce790eba35abec305a4f081db5d9ecf5b7005`，AC05 修复证据提交为 `edbc9e131584e1f219e22825a8ab1c598d137f13`；S1-T01 通过不等于阶段1通过。S1-T01-D1 official Darknet 工作流入口已完成 G1/G2 并提交 `94fe7da2689f5556d49418e089858aa8001cc736`；D5B2 工具改进已提交 `de822c40771a45e2dc8be8bc6baa559bbe1933d2`，全量评估证据已提交 `0619905`。S1-T02-D1 浮点 setup 已完成 G1/G2/G4，独立 Reviewer 最终 PASS；仅建立 tiny 320/416 与完整 YOLOv4 五类配置、拓扑/参数/BFLOPs 和 provenance 证据，不代表正式训练、mAP 或最终模型验收。
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
- 新语义全量检查报告退出码 **0**，有效行/图片 `158680/158680`，`no_hand=train 3、val 2、test 0`，人员/会话交叉为空，AC02/AC03 自动通过；报告状态仍按工具约定为 `PASS_AUTOMATED_MANUAL_PENDING`，但 AC04 的 10 张带框、5 张 no_hand 与 5 张非目标手势人工语义已有记录、批准 JSON 和独立 G4 核对。`friend_005` 明确为 Wong 提供并授权的真实风景/空场景负样本，不是人物肖像，也不把 `no_gesture` 解释为 `no_hand`。
- 已完成 D3 官方 Darknet 输入绑定独立复审：158680/158680 sidecar 内容匹配，train/valid 清单与 manifest 集合/顺序一致，五类 names/data 可解析，Reviewer PASS；外部产物与哈希见 `20260915_darknet_input_binding.md`。不等于 Darknet/CUDA 已构建或训练通过。
- 最新语义证据记录 AC02 自动检查通过；不替代其他验收或独立签结。历史全量数据退出码0已被语义重查的退出码2更新。
- 最近代码回归证据：S1-T01-D1 定向 24 项、全量 `verification` 48 项测试通过，14 个 Python 文件编译检查通过，独立 Reviewer 对第3轮候选 PASS；真实预检退出码2、`BLOCKED_PREFLIGHT`、Darknet 命令数0。工作流和三轮阻断证据入口见 `report/evidence/S1-T01/`，代码提交为 `94fe7da2689f5556d49418e089858aa8001cc736`。本轮全量数据扫描运行约 78 分钟后退出码0，报告为 `20260915_hagrid_dataset_check_semantic_after_no_hand.json`。
- 环境 D4 已通过：VS Build Tools 17.14.40/MSVC 19.44、CUDA Toolkit 13.4.59、CMake 3.30.2、RTX 4060 Laptop/驱动 610.88；固定 smoke `sm_89` 真实运行通过，官方 Darknet commit `59596d7880f6504768df41d6daa586f5cb2b932f` 以 CMake CUDA ON/CUDNN OFF/OpenCV OFF 构建成功。安装后 probe status=PASS、退出码0；Darknet SHA-256 `358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`，smoke SHA-256 `4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c`。D5A 已固定 416 cfg（SHA-256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`）和官方 `yolov4-tiny.conv.29`（19,789,716 bytes，SHA-256 `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`），r2 dry-run 为 `PLANNED_NO_EXECUTION`/exit 0，独立 Reviewer PASS；D5B-1 已真实训练 1～20 步并恢复 11～20 步，train/resume 报告均 `EXECUTED_REVIEW_REQUIRED`、顶层 exit 0、独立 Reviewer PASS；D5B-2 全量评估/复现尚未完成，正式长训、INT8 检测量化及整网 RTL 尚未开始。

## S1-T02-D1 浮点 setup 证据

- R3 JSON SHA-256 `8b7239a9c3cec511b5cb5e8795f2670fe0601cbcc90592bde70c01d205a9c12d`；R3 summary SHA-256 `ae76dcc6e11add7079f4b46a48dfce103b8f4b5ac41e3ec3f8921b69e5ed6768`；setup 脚本 SHA-256 `936cc77b527498a78dc532a2842b6a3098bdb19c28018c7eef0b6aef556a8295`。tiny416=`5,886,460` params/`6.793486` BFLOPs，tiny320=`5,886,460`/`4.019814`，与既有官方日志按三位小数交叉核对；完整 YOLOv4 五类=`63,992,378` params/`123.248005` BFLOPs 仅为 parser estimate，无五类权重或 official runtime pilot。R1/R2/R3 文件在 `report/evidence/S1-T02/`；Nietzsche 最终独立 PASS 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t02-d1-r3-final-20260916\final_pass_review_s1_t02_d1_r3.json`，SHA-256 `DBFDE14BBA0D0AE1B723B46402C947341A8AF6E37F6AB528D2687921DF0D28B2`。D1 未执行正式训练、mAP、INT8、完整模型 pilot 或 pilot 重跑。

## S1-T02-D2 固定预处理与 INT8 数值规格

- 2026-09-16：Wong 接受第4项预设并完成任务级 G1/G2/G4；独立 Reviewer 最终确认 PASS。固定 RGB→letterbox→CHW/255→INT8，INT8 `[-127,127]`、zero-point=0、输入 scale=`1/127`、权重逐输出通道/激活逐层对称量化、INT32 累加和 INT64 溢出检查、半数远离零、PS 浮点检测头后处理。
- R2 证据：spec `14e61b90e0eac8a9a96ffcbf326ff7784e896b12fa293ef01a86892dbc7f58d6`，summary `0153db5b5dd93ac80f8551d2098fd33d107b2d33583062dfb669d36801347d7b`，golden `7f469d8274a3ce2ca1f89727b847961f93b8d322407dc89b17a4e7ed1ca802e1`，calibration `ffe3596ff8ae265ab8489c051878588833d80266028448c37c8b890e0c35059f`，list `d637a2feb671429741c8b6703caaa9cdf995abf49dfa4b72e41f62dfbea1a35c`。
- Reviewer 最终确认 JSON 位于 `C:\Users\22061\AppData\Local\Temp\review-s1-t02-d2-submit-20260916\review_s1_t02_d2_submit_final.json`，SHA-256 `1D9083EAD70F0DCE0E21F602D00FC6FB7C8AE2AF3D50B910900463740D5AC9BD`。D2 测试16/16、全量71/71；仅完成输入绑定和数值参考，未执行正式训练、mAP、INT8 整网、资源、RTL 或板上验证。

## Wong 已确认的 S1-T02 G0 决策

- 2026-09-16：同意“官方 test 作为主要最终测试集，并另建独立鲁棒性测试集”的数据口径。当前官方 test 保留为最终基准；no_hand、non-target、多手、遮挡和小目标等鲁棒性指标使用独立、固定且不与 train/val/test 人员或 session 重叠的集合。已提供的 5 张 no_hand 继续保持 train 3 张、val 2 张，不移入 test；它们不单独代表正式 no_hand 泛化率。
- 该决定冻结的是数据集组织方案；官方 test 是否全量使用、鲁棒性集合的最低样本数量和各类覆盖仍需在后续 G0 决策中写成数值。
- 2026-09-16：接受评估口径预设：报告 mAP@0.5、mAP@0.5:0.95（IoU 0.50:0.05:0.95、101-point AP、五类宏平均）、各类 precision/recall；同类别一对一匹配、按 score 降序；no_hand 误检率≤5%，non-target 误检率≤10% 为辅助门槛。score threshold 仅在 val 的 0.25–0.50 范围内选择后固定，NMS 为类别内 greedy、IoU=0.45；每图最大输出框数由 20 调整为 15。test 和鲁棒性测试均不得重新调参；该项已确认，但不等于 S1-T02 整体 G0 通过。
- 2026-09-16：接受模型/训练/恢复预设：PC 对照包含完整 YOLOv4 608×608，候选包含 YOLOv4-tiny 320×320 与 416×416；tiny 使用官方 `yolov4-tiny.conv.29`，完整模型使用官方 `yolov4.conv.137`，正式训练不使用 20/200 步诊断权重。训练参数预设为 batch=64、tiny subdivisions=16、完整模型 subdivisions=32、SGD momentum=0.9、decay=0.0005、tiny learning_rate=0.00261、完整模型 learning_rate=0.0013、max_batches=6000、steps=4800/5400、burn_in=1000；固定输入训练、保存 checkpoint/last/final。正式训练需补充固定 seed 支持并绑定源码/可执行文件哈希；恢复只保证权重与 seen 计数恢复，因 Darknet 不保存 momentum 缓冲区不宣称 bit-exact。当前无板上模型运行；完整 YOLOv4 仅 PC 对照，板上默认候选为 tiny、优先评估 tiny416，但最终模型仍待精度/数值/资源三关和 Wong 确认。

## S1-T02-D3 资源、性能与阶段验收门槛

- 2026-09-16：Wong 批准第5项冻结口径；D3 任务级 G1/G2/G4 通过（仅冻结规范、检查器和 pending 证据结构，不代表 G3、资源/性能实测或阶段通过）。独立 Reviewer 第3轮 PASS；证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t02-d3-r3-20260916\review-s1-t02-d3_r3.json` 与同目录 summary，SHA-256 分别为 `6bb9cdae85dcdd87d13caff6572441e0944d53075dca95c5fddcd6bd4d3e75bb`、`1a911f79731c2da8ab5d1773115e187e35186acea6cca264df7c8b46ae7fbebd`。
- 固定 AX7Z020/XA7Z020 CLG400、-1 基线；LUT/FF/BRAM/DSP 各≤85%，WNS/WHS≥0、TNS/THS=0；存储、地址半开区间和 DDR 视频/模型/PS/NMS/缓存带宽分栏；tiny320/tiny416 分开，full 仅 PC 对照。
- 固定性能测量方法：固定模型/输入/权重/预处理/阈值/NMS，warmup=100、有效推理≥10000，五阶段 mean/P50/P95/P99，timeout/drop/failure 单列；最终 FPS、端到端 P99、ARM 对照仍为 `pending_until_wong_decision`，不继承旧20 FPS/100 ms。
- D3 实现与证据：`verification/s1_t02_d3_resource_performance.py`、对应测试、规范、`report/evidence/S1-T02/20260916_s1_t02_d3_resource_performance_r1_spec.json`、r1 report/summary；checker SHA `79621c530c8463b391f449000cc1ca882b1c7a0c9168cc8e01f4bcafc388866a`，spec SHA `d25ca3903d13ff2224b187c74f5795965aa20d7cba08a6cd2d6839ce4ee57226`，report SHA `0f7812c1dfd6c6b33795bd322c21f6a368b76af8c275e243c1774bddd3b84b20`。
- 当前 D3 report 为 `NOT_EXECUTED_PENDING`，errors=0、pending=168；未执行正式权重训练/评估、CUDA 长测、Vivado 综合、烧录、板测、最终精度或性能。输入 spec 与 report 输出分离，同路径被拒绝；D3 不关闭 S1-T02 G0。

## 下一步与边界

1. 按 `git status` 重新确认工作区归属；迁移开始前用户已有 `docs/obsidian-project/总控.md`、`docs/obsidian-project/项目接手提示词.md`、`vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 修改及两张板卡 JPG，未纳入工作流提交。
- 2. 数据/无手输入已完成自动检查、人工语义记录、批准 JSON 和 Darknet sidecar/list 绑定；AC04 已由人工记录与独立 G4 核对闭合，不用非目标手势代替 no_hand。
- 3. S1-T01 G4 已通过；AC05 采用专用 stateless SGD 证据，旧 stateful r1 优化器状态不宣称恢复。AC06/AC07 仍不代表正式精度，勿把当前 200 步诊断权重冻结为最终模型。
4. S1-T02-D1 setup、D2 固定预处理/INT8 参考与 D3 资源性能门槛已完成任务级验收；S1-T02 G0 尚未通过。下一步为正式浮点模型基线与完整 YOLOv4 / YOLOv4-tiny 320/416 对照、真实 Darknet 训练/恢复/评估和 INT8 对照。正式测试前仍须冻结测试样本、随机种子、mAP@0.5、mAP@0.5:0.95、各类召回/精确率、无手误检、INT8 相对浮点损失和性能统计口径；最终上板模型/尺寸/性能仍由 Wong 决策。
5. 当前采用一个阶段总控自动协调 Developer/Reviewer，最多3轮修复复审后总控重析；状态在此维护，不再依赖旧窗口或交接文件。

## 正式文档与证据入口（仓库相对路径）

- 系统架构：`docs/obsidian-project/02-方案设计/系统设计.md`；阶段计划：同目录 `B方案实施与阶段验收计划.md`。
- 接口依据：`docs/obsidian-project/02-方案设计/INT8乘加接口说明.md`（原型接口，不代表整网支持）。
- 任务标准：`docs/obsidian-project/03-实验记录/任务记录/S1-T01_训练环境与数据准备.md`（历史状态按最新证据解释）。
- 验收：`docs/obsidian-project/04-提交材料/验收执行手册.md`；阶段1范围：同目录 `阶段验收/阶段1_PC模型与数值规格收尾记录.md`。
- D2 规范：`docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md`；R2 机器证据：`report/evidence/S1-T02/20260916_s1_t02_d2_numeric_spec_r2.json`。
- 最新整改：`report/evidence/S1-T01/20260914_semantic_repair.md`；报告：同目录 `20260914_hagrid_dataset_check_semantic.json`（clean 报告为同结果副本）。
- 人工语义：`report/evidence/S1-T01/20260914_hagrid_semantic_review.csv`；本轮收尾：`20260915_no_hand_ingest.md`、`20260915_hagrid_visual_review_after_no_hand.md`、`20260915_hagrid_dataset_approval.json`。
- 环境：`report/evidence/S1-T01/20260914_environment_recheck.json`；命令和源程序入口：`verification/README.md`、`verification/s1_t01_cuda_smoke.cu`。
- D4 安装后环境：`report/evidence/S1-T01/20260915_s1_t01_d4_round3_summary.md`、`20260915_environment_probe_after_install_v3.json`、`20260915_darknet_cmake_build_release.md`、`20260915_cudnn_check_after_install.md`；独立 Reviewer 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d4-round3-20260915\review_s1_t01_d4_round3_final.json`。
- D5A 配置/权重/dry-run：`report/evidence/S1-T01/20260915_s1_t01_d5a_preflight_r2.json`、`20260915_s1_t01_d5a_preflight_r2_summary.md`、`20260915_s1_t01_d5a_short_train_preflight_blocked.md`；独立 Reviewer PASS 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5a-r2-final-20260915-180935\review_s1_t01_d5a_r2_final.json`。外部 cfg/weight 不在 Git，使用上述固定路径与哈希。
- D5B-1 短训/恢复：`report/evidence/S1-T01/20260915_s1_t01_d5b1_r1_summary.md`、`20260915_s1_t01_d5b1_train_r1.json`、`20260915_s1_t01_d5b1_resume_r1.json`；训练报告 SHA-256 `e46a433d5bccd209fc1f117280affce06e6f47a1166bd2024aaa3d776da3b45b`，恢复报告 SHA-256 `24cbecaccb37cde0e4755499a771b3291948714a813ebad7cdee4d7222d8111a`，workflow 修复提交 `5645a17`；独立 Reviewer PASS 证据在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b1-fix-20260915-191045\review_s1_t01_d5b1_fix_r1_final.json`。外部训练/恢复 checkpoint 和日志位于 `D:\FPGA_Data\HaGRIDv2\darknet_inputs`，未纳入 Git。
- D5B-2 工具改进：提交 `de822c4`；独立复审 PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b2-r3-20260915-r2\independent_r3_final_check.json`；r2 中止与 r3 smoke 分别见 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r2\abort_status.json`、`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r3_smoke_final\smoke_result.json`，均为外部运行证据，未纳入 Git。
- D5B-2 全量评估：报告与失败/中止摘要已提交 `0619905`，主报告 `20260915_s1_t01_d5b2_eval_r4_full_200.json` SHA-256 `843ed924af2b6799b75eed57fe799c8dba232409b2188bea07a11e1ee04d12e8`；valid 15195/15195、逐图 15195、11,212 框、friend_004 零框；独立 Reviewer 31/31 PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5b2-full-r1-20260915\review_s1_t01_d5b2_full_r1_final.json`，SHA-256 `deb1cf23d15abce5304dda30951dcfccc2720ba5a31119099e83e209c83f48bd`。外部 run-dir 未纳入 Git。
- AC05 修复与语义澄清：`edbc9e131584e1f219e22825a8ab1c598d137f13`；主报告 `20260915_s1_t01_d5b1_ac05_repair_r1.json` SHA-256 `cbecaed68b65a1f3b1ff42565b7b45ab1b6a6c5888e3e5a8f669ffabaaeb17e5`；独立 Reviewer PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-ac05-repair-r1-20260915\review_s1_t01_ac05_repair_r1_final.json`，SHA-256 `8edd0ac519066da7db0572c2aeec94f1f3e81b9d7451ced779b38e701164368c`。stateless SGD 的机器梯度证据在外部 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\ac05_repair_r1\runs\ac05_gradient_finite_evidence.json`，SHA-256 `164a69a18dc7f332520f134ecba632a08a1b68debefbe6094addf62a2e50d2fc`。
- AC07 复现与绑定：`33dce790eba35abec305a4f081db5d9ecf5b7005`；数据复检报告 SHA-256 `ec9be81db33a36830c9dbc3f50a6127a5cc949c20862ae59941bdea97d852082`，r1 全量报告 SHA-256 `0394d2125e9597f01e9d5c0cca2ce5e81483505f63bb7b3a7611ce5a4dd6cf6f`，r2 绑定报告 SHA-256 `8ada6e3572577464639aba3248ceb1e38056977b36df3c7a013917de8ff1eb06`；独立 Reviewer r2 PASS，证据 SHA-256 `67d709bc5b8875766d4fbc540bb54a8a673063f4b34d2e86c65ff9fa2ec4002c`。
- S1-T01 G4 任务验收：摘要 `report/evidence/S1-T01/20260915_s1_t01_g4_acceptance_summary.md`；独立 Reviewer 第2轮 PASS 在 `C:\Users\22061\AppData\Local\Temp\review-s1-t01-g4-r2-20260915\review_s1_t01_g4_r2_final.json`，SHA-256 `d1192a35a292e59d5b0f7fd859b65292e455ee44fef81d57ac24b8b1832b61d4`。S1-T01 已通过 G4，但不构成阶段1 G5 或外部最终验收。
- 当前活动任务为 S1-T02 G0 准备：D1 setup 已完成任务级 G4，正式测试阈值、对照模型与数据口径仍待冻结；最终上板模型、输入尺寸和性能仍由 Wong 决策。不得将 S1-T01 小样本或 200 步诊断权重写成正式精度结论。
