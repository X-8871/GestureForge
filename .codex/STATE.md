# 项目状态

更新：2026-10-01（UTC+8）。恢复时先读 `AGENTS.md`，再读本文件和当前阶段正式规格。

## 当前目标与阶段

- 目标：AX7020 摄像头五类手势检测，最终经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现作品。
- 当前阶段：阶段 2A「PL 推理仿真」。阶段一与 G0 已冻结；共享 INT8 MAC 原语 RTL 单元已完成独立仿真与只读审查。其他算子、控制器集成、整网逐层黄金和整体 G2 尚未完成。
- 本轮未重新训练；S2A-T02 仅执行独立 MAC RTL 单元仿真，未执行综合、Vivado 工程集成、整网仿真、板上烧录或板测。
- 归档主入口：`docs/obsidian-project/04-提交材料/阶段验收/阶段1_实施步骤与决策_最终产物_20260922.md`。

## 阶段 2A G0 冻结入口

- G0 规格：`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md`；状态 `G0_FROZEN`，主候选 `tiny416`。
- 机器清单：`report/evidence/S2A-T01/tiny416_model_manifest.json`；固定输入：`report/evidence/S2A-T01/fixed_test_samples.json`。模型清单覆盖 38 层、21 个卷积层、5 个 cfg 算子类型及共享 INT8 MAC；固定样本 109 项。
- G0 冻结模型/量化/参考源码哈希、NCHW 张量与地址、PS/PL CSR 和 memory 协议、内部 operator completion event、解码/NMS 规则、随机种子及误差口径。算子与 MAC 定向向量各 16 项，case 9 route 用于非恒等 scale 转换。
- 独立复审通过；G0 规格、生成器、测试、model manifest 和 samples manifest 的最终 SHA-256 均记在 G0 规格内。
- 下一项：先针对冻结的全网 timeout 核定可实现吞吐/存储预算，提出可审查的后端方案供 Wong 决定；不擅改 CSR/timeout，也不把未实现缓存的 8-lane 估算当 RTL 证据。

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

- 更新：2026-10-01（UTC+8）。恢复审计：`report/stage2a_execution_audit_20261001.md`，提交 `f7c5830f37f749a71fcb9639f1be58e1ca412c13`；该报告记录完整病灶与当前未提交文件哈希。

| T01 项 | 已通过 / 可复用版本 | 缺口 | 下一项验证 |
|---|---|---|---|
| G0 输入与接口 | T01 `G0_FROZEN`，独立审查通过；模型/样本与规则哈希见 T01 规格 | 无；冻结仅定义基线，不证明 RTL | 后续均沿用此基线 |
| 单元向量与协议 | 共享 MAC：T02 提交 `f547522`，单元仿真及只读审查通过；已有算子/协议证据按其具体覆盖复用 | 每 cfg 算子层 1,000 随机+16定向、MAC 1,000+16，以及固定 stall/error/reset/timeout 路径未形成完整 T01 覆盖证明 | 汇总既有证据，只补跑明确缺失项 |
| CPU oracle 与 D9 | T25 `cpu_layer_golden_index.json` 为109输入×38层整数黄金 `COMPLETE`（提交 `f669103`）；CPU decode/NMS 测试通过（`f61b8ce`） | 这是 CPU 结果，不是 PL；实际 PL heads 尚无比较 | 复用 T25 做 PL 逐层逐值比对 |
| 描述符后端尝试 | 描述符 ROM/route 改动见 `b423994`、`f7ec51b`；T64 run11 仅24 reads/1 write/109 cycles 首输出握手 | T63 XVLOG 同名日志冲突退出1、未启动 XSim；T64 无 golden；T65 sim01 曾 0ps 路径失败且修复已审，sim02 未运行，后续进程门禁未独立复审 | 核对当前差异，选单一 D 盘路径做一次短 smoke |
| 全网 PL 与头后处理 | 暂无 sample0 完整38层 PL 闭环 | 109×38 PL 零差异；两头 INT8 字节完全一致；D9 离散字段完全一致、分数/坐标绝对误差≤1e-6 | 先 sample0 全网闭环并测吞吐，再扩展109输入与头比较 |

- 架构阻断：当前标量卷积有效tap约32.509亿，无停顿周期下界约19,837,821,226，超过32-bit `TIMEOUT_CYCLES` 最大值4,294,967,295约4.62倍。缓存/并行结构、读写次数、存储与吞吐须先有具体方案并由 Wong 决定；不改冻结协议或 timeout。
- 执行边界：范围为完整 Stage 2A PL 推理仿真，不含综合资源声明、板测或烧录。T61 run05 attempt05 是离线准备，不是新仿真结果；run04 DATA_ONLY 也不是全网通过。
- 保护状态：PID 8712 Vivado、22488/13156 XSim 为审计记录的受保护进程，任何运行前重新核对身份，不停止/关闭/重置/发送状态修改。MCP 当前连接健康但项目为 `s2a_t61_run04` 的 `isolated_project`、Top 为空，不是2A仿真实例。
- 未提交 T63/T64/T65 与其他工作区差异均须保留并先核对；日志、夹具、临时文件和大型生成物留在 D 盘，默认不生成大波形。
