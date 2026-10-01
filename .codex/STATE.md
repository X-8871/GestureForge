# 项目状态

更新：2026-10-02（UTC+8）。恢复时先读 `AGENTS.md`，再读本文件和当前阶段正式规格。

## 当前目标与阶段

- 目标：AX7020 摄像头五类手势检测，最终经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现作品。
- 当前阶段：阶段 2A「PL 推理仿真」。阶段一与 G0 已冻结；T02 共享 MAC 单元独立仿真及只读审查通过。Wong 已批准 8×8 空间 tile / 8 output-channel lanes；T66-A byte-lane 修复与观测回归已通过静态检查和独立审查，attempt07 完成编译并已启动 layer0 full golden XSim，结果待定、未集成描述符 backend；G1/G2/G3/G4/G5 均未通过。
- 本轮未重新训练；S2A-T02 仅执行独立 MAC RTL 单元仿真，未执行综合、Vivado 工程集成、整网仿真、板上烧录或板测。
- 归档主入口：`docs/obsidian-project/04-提交材料/阶段验收/阶段1_实施步骤与决策_最终产物_20260922.md`。

## 阶段 2A G0 冻结入口

- G0 规格：`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md`；状态 `G0_FROZEN`，主候选 `tiny416`。
- 机器清单：`report/evidence/S2A-T01/tiny416_model_manifest.json`；固定输入：`report/evidence/S2A-T01/fixed_test_samples.json`。模型清单覆盖 38 层、21 个卷积层、5 个 cfg 算子类型及共享 INT8 MAC；固定样本 109 项。
- G0 冻结模型/量化/参考源码哈希、NCHW 张量与地址、PS/PL CSR 和 memory 协议、内部 operator completion event、解码/NMS 规则、随机种子及误差口径。算子与 MAC 定向向量各 16 项，case 9 route 用于非恒等 scale 转换。
- 独立复审通过；G0 规格、生成器、测试、model manifest 和 samples manifest 的最终 SHA-256 均记在 G0 规格内。
- 下一项：sample0 当前在 `report/evidence/S2A-T68/batch109_r3` / RunId `batch109_r3` 由隐藏 pwsh 7.6.5 进程 PID 1188 运行（启动日志在 EvidenceDirectory 根目录）；`batch109_r1` 中断于 layer1/cycle30,000,000 且无仿真记录，`batch109_r2` 在 Windows PowerShell 5.1 未识别 Get-FileHash、无实际 PL 仿真；两者均保留且不纳入验收。待 r3 完成后按吞吐批跑剩余样本。

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

- 更新：2026-10-02（UTC+8）。恢复审计：`report/stage2a_execution_audit_20261001.md`，提交 `f7c5830f37f749a71fcb9639f1be58e1ca412c13`；该报告记录当时的病灶、文件哈希与恢复边界。

| T01 项 | 已通过 / 可复用版本 | 缺口 | 下一项验证 |
|---|---|---|---|
| G0 输入与接口 | T01 `G0_FROZEN`，独立审查通过；模型/样本与规则哈希见 T01 规格 | 无；冻结仅定义基线，不证明 RTL | 后续均沿用此基线 |
| 单元向量与协议 | T69 独立只读审计 PASS：T02 MAC、T17 21层卷积、T14 maxpool、T13 upsample、T15 route、T08 YOLO 随机/定向向量覆盖齐；T10–T12/T18–T21 有固定 stall、错误、取消、timeout、ACK/恢复证据；T11 CSR 回归通过非法/保留 CSR 与 BAD_RANGE/BAD_LENGTH/BAD_ARGUMENT start（595 transfers、116 directed、256 random）；T68 protocol_directed05 真实 backend+CSR code6/7→INTERNAL、pending layer0 output write 的 soft/hard reset/timeout 取消、无迟到副作用及 ACK/restart 独立审查 PASS；protocol_directed06 波形版独立复审 PASS，VCD `report/evidence/S2A-T68/protocol_directed06/backend_fault_recovery.vcd`（15,383,328 B，SHA-256 `e08b209e00c467b9571e96f723025fe59930db0721463404a18fe6459b4b1c5f`） | 无（该行通过不代表整网或阶段通过） | T68 sample0 38 层 PL golden 仿真与吞吐校准 |
| CPU oracle 与 D9 | T25 `cpu_layer_golden_index.json` 为109输入×38层整数黄金 `COMPLETE`（提交 `f669103`）；T29 D9 CPU reference 可从冻结 T25 heads 重建，109/109 canonical 比对通过；T68 D9 verifier 已提交 `e55fae0`、独立源码审查 PASS | CPU 链路不代表 PL；实际 PL heads 尚无比较 | 用整网模拟实际 head bytes 与 T29 对照，离散字段一致、score/坐标绝对误差≤1e-6 |
| PL backend 与新卷积 tile | T66 byte-lane 修复与 layer0 tile 回归已静态审查通过；另有独立 Verilator 5.050 sample0 layer0 golden 仿真 8/8 通过，1,384,448 字节、0 mismatch、26,002,719 cycles。证据目录：`report/evidence/S2A-T66/tile01/verilator_run01/` | 尚无 PL 38 层整网 golden；此前 XSim attempt07 按 Wong 指示继续自行运行，本轮未查询、读取或干预 | T67 backend 接入提交 `433b720c1006f34d191e0fd7ed07bee62d6a276c`；静态独立审查 PASS；独立 lint exit=0、143 warnings、0 errors |
| 全网 PL 与头后处理 | T68 harness commit `e55fae02554933a7af02600ffaa6300e33b9647b`；静态独立审查 PASS；protocol_directed05/06 独立审查 PASS；`verification/run_s2a_t68_batch_verilator.ps1` 独立审查及 PS7 解析 PASS，尚未运行；sample0 `batch109_r3` 在运行（PID 1188），backend SHA `3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154` | 尚无完整 sample0 全网仿真记录；109 个 PL head 导出及 D9 对照待完成 | sample0 PASS 后校准实际吞吐并批跑剩余108样本，然后执行109样本 D9 对照 |

- 截止与预算：Wong 于 2026-10-01 要求 2A 在 7 天内完成；截至 2026-10-02 尚余 6 天（目标 2026-10-08 前通过 G5），不得降低验收标准。架构仍为 8×8 tile / 8 output lanes，CSR、32-bit timeout 与 memory protocol 不变。冻结 manifest 的保守脚本估算为单帧 1,940,519,260 cycles（request stall `[0,1,2,7,3]`，4 个算术用例通过），脚本状态 `ESTIMATE_ONLY_NOT_RTL_PROOF`；109 帧按当前 8-worker layer0 吞吐线性外推约 59 小时，必须由 sample0 全网实测校准。此前约 1.16B cycles 预算仍未被 RTL 验证；不作为当前排期依据。
- 执行边界：范围为完整 Stage 2A PL 推理仿真，不含综合资源声明、板测或烧录。T61 run05 attempt05 是离线准备，不是新仿真结果；run04 DATA_ONLY 也不是全网通过。
- 保护状态：PID 8712 Vivado、22488/13156 XSim 为审计记录的受保护进程，任何运行前重新核对身份，不停止/关闭/重置/发送状态修改。MCP 当前连接健康但项目为 `s2a_t61_run04` 的 `isolated_project`、Top 为空，不是2A仿真实例。
- T63/T64/T65、进行中的 T66-A 与其他工作区差异均须保留并先核对；日志、夹具、临时文件和大型生成物留在 D 盘，默认不生成大波形。
