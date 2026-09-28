# 项目状态

更新：2026-09-23（UTC+8）。恢复时先读 `AGENTS.md`，再读本文件和当前阶段正式规格。

## 当前目标与阶段

- 目标：AX7020 摄像头五类手势检测，最终经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现作品。
- 当前阶段：阶段 2A「PL 推理仿真」。阶段一已冻结；阶段 2A G0 已冻结，RTL/G1/G2 尚未开始。
- 本轮未重新训练；G0 未执行 Vivado 综合、板上烧录或板上性能测试。
- 归档主入口：`docs/obsidian-project/04-提交材料/阶段验收/阶段1_实施步骤与决策_最终产物_20260922.md`。

## 阶段 2A G0 冻结入口

- G0 规格：`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md`；状态 `G0_FROZEN`，主候选 `tiny416`。
- 机器清单：`report/evidence/S2A-T01/tiny416_model_manifest.json`；固定输入：`report/evidence/S2A-T01/fixed_test_samples.json`。模型清单覆盖 38 层、21 个卷积层、5 个 cfg 算子类型及共享 INT8 MAC；固定样本 109 项。
- G0 冻结模型/量化/参考源码哈希、NCHW 张量与地址、PS/PL CSR 和 memory 协议、内部 operator completion event、解码/NMS 规则、随机种子及误差口径。算子与 MAC 定向向量各 16 项，case 9 route 用于非恒等 scale 转换。
- 独立复审通过；G0 规格、生成器、测试、model manifest 和 samples manifest 的最终 SHA-256 均记在 G0 规格内。
- 下一项：实现并验证共享 INT8 MAC RTL，再依冻结清单逐步实现基础算子。G0 不代表 RTL、整网黄金、综合/时序或板测通过。

## 已冻结的模型和口径

- 类别：`fist`、`palm`、`one`、`two_up`、`three`；旧 32×32 分类方案停用。
- 模型：`tiny320`、`tiny416` 为上板候选，`full608` 为 PC-only 对照。
- 固定推理：`score_threshold=0.25`、NMS IoU=`0.45`、每图最多 15 框。
- 浮点门槛：mAP@0.5≥0.90、mAP@0.5:0.95≥0.70、五类逐类 precision/recall≥0.90。
- INT8 保留门：相对浮点 mAP@0.5 和逐类 recall 下降≤5个百分点，且 D2 溢出规则满足；本轮未把整网 INT8 检测下降写成已通过。
- `no_hand` 不是第六类，也不是阶段一阻断项；官方 `no_gesture` 不改名。没有合适独立来源时只保留为可选诊断。

## 已核对的正式结果

- 官方数据来源为 HaGRID；manifest 158,680 行，SHA-256 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- tiny416 官方 test 25,484 张：mAP@0.5=`0.9774176565`，mAP@0.5:0.95=`0.7700877728`，最小 precision=`0.9479207151`，最小 recall=`0.9701880752`。
- D3 PC 本体（100 warmup+1000 valid）：tiny320 mean/P99=`17.895892/21.176 ms`；tiny416=`27.456450/31.559 ms`；full608=`43.861036/48.585 ms`；三者 timeout/drop/failure 均为 0。
- Wong 已确认三个模型通过网页/摄像头人工测试；该项是人工可用性确认，不替代正式 mAP。

## 可恢复入口

- 网页代码：`web/index.html`、`web/gestureforge_web.py`、`web/README.md`；模型注册表保留三个独立 ID、cfg/data/weights 路径和 SHA，可切换回滚。
- D2/D3/D6/D9 最终证据和清理后的保留清单见阶段一归档记录；外部模型仍在 `D:\FPGA_Data\HaGRIDv2`，本次未删除。
- 阶段冻结基础提交：`27ff12a`、`b3e82d1`；本次整理完成后以最新清理提交为准。

## 后续边界

- tiny320/tiny416 后续板上门：LUT/FF/BRAM/DSP≤85%，WNS/WHS≥0，TNS/THS=0；full608 不适用板上资源门。
- 未来若要求“无手必须拒绝输出”，需另建独立、可审计数据集和新验收门，不回写当前阶段一冻结结论。
- 阶段 2A 已开启；当前仅推进 PL 推理仿真。阶段 2B 固定输入上板须在 2A 验收完成、硬件条件核对并经 Wong 明确允许后开始。摄像头视频、HDMI、实物操作、烧录和新训练均不在当前范围。

## 阶段 2A 最新恢复点

- S2A-T56 数据级独立复核状态为 `PASS_INDEPENDENT_REVIEW_DATA_ONLY`，覆盖 tiny416 layer35 的 y=20、x=0..25、256 通道；layer35 整层、整网和阶段整体 G2/G3/G4/G5 仍待验收。提交 `7e6eac725bd9c4ed41540ca6874ae67fc03fe911`；证据：`report/evidence/S2A-T56/layer35_row20_all_channels.json`。
- 后续 Vivado 仿真等待本会话恢复 Vivado MCP 连接；当前 `check_connection` 连接 `127.0.0.1:7654` 被拒（WinError 1225），`get_project_info` 同样失败，未能确认在线实例。2026-09-28 检查无 Vivado/XSim 进程；未停止、关闭、重启其他实例。
