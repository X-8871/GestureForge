# 遗留问题与影响评估（G4 附带，2026-10-30 r01）

## 1. 阻断级：无

阶段4/5 当前范围内**没有阻断问题**：冻结回归 7/7 PASS，19 项输入 sha 未变，证据全部过统一门禁。

## 2. 遗留项（非阻断，需记录与跟踪）

| 编号 | 遗留 | 类型 | 影响 | 处置 |
|---|---|---|---|---|
| R-01 | M3 成对取样未执行 | 外部依赖 | 阶段4 少 1 项"同窗口读写一致性"证据；现有只读复检（S4-03）已通过 | 待 Codex 提供 DDR 读工具入口后单窗口补测（`DSH-20261029-007`） |
| R-02 | 2B 吞吐 47.3 s/帧（≈0.021 fps） | 指标移交 | 不满足原"5 fps"设想；Wong 已决定不追、移交 Codex | Codex 侧优化（burst/多 outstanding/超时语义）；本侧不再作为判据 |
| R-03 | P2b/P2c 拓扑已被证伪 | 已关闭 | 2B 的 `M_AXI` 经通用 SmartConnect 会串行化（≥1.82×） | 已由 P2d（方向 A）替代；P2b/P2c 仅保留为历史证据 |
| R-04 | DSP 余量 62（71.82%） | 资源风险 | 阶段6 加视频链/叠加可能超出 | 阶段6 启动前先做资源预算与（必要时）DSP 复用改造 |
| R-05 | 视频链未实现 | 范围转移 | 阶段5 原始计划含 HDMI 输出 | 归阶段6；地址/时钟裁决已定稿（VTC `0x43C20000`、dynclk `0x43C30000`、FCLK1=150） |
| R-06 | `ENABLE=1` 实时流未验证 | 未执行 | 端到端实时链路未证明 | 阶段6 联调（显示链就绪后） |
| R-07 | fixture 为生成数据，非实拍 | 数据限制 | 4-D 数值链路验证不含真实摄像头噪声/曝光 | 阶段6/7 用实拍帧补测 |
| R-08 | 工作树有 60 项旧会话/Codex 归属未提交内容 | 卫生 | 不影响本轮冻结（本轮证据均已提交） | 按单写者规则保留归属；不擅自提交 |

## 3. 本轮修掉的缺陷（已闭环，留作回归输入）

| 缺陷 | 根因 | 修复 | 证据 |
|---|---|---|---|
| 应用 ms 全部 4× 偏小 | `xtimer_config.h` 宏未加括号 + 强转 ⇒ 除数 4× | `S4D_MS_DIV` + 双读全局定时器 | `s4d_time_basis_20261029_r01`（含 `ERRATUM_ROOT_CAUSE.md`） |
| M4-b/chain 必然 `error=5` | 旧冻结 ELF `core_timeout=0x40000000`（21.47 s）< 单帧 47.3 s | 重建 ELF，超时 `0xFFFFFFFF`（85.9 s） | `s4d_elf_rebuild_timeout_20261029_r01` |
| M4-b `diff13=2` | 参考预置用 `HEAD13_BYTES//4=1267` 字（漏尾 2 字节）+ `stale=0` | 补齐 1268 字 + 输出区投毒 | `s4d_m4b_tailword_20261029_r01`、`s4d_freeze_r2_m4b_2b_20261029_r01` |
| P2c DMA 截断（11,264 B） | `c_sg_length_width=14` | 改 23 bit | `pl_v2_p2c_dma_bitstream_20261029_r02` |
| P2b 2B 慢 ≥1.82× | 单 outstanding 主端经 SmartConnect | 方向 A：2B 直连 HP0 | `s4d_p2b_infer_slowdown_20261029_r01`、`s4d_freeze_r5_m4b_p2d_20261029_r02` |
| 驱动装载 `rst -system` 清 PL | 硬编码系统复位 | `drv.load_elf_ddr` + PL 保持分支 | `bringup_longrun_probe_20261029_r03/r04/r05` |

## 4. 恢复与重建入口

1. 位流重建：`report/evidence/S4-T34/s4d_p2d_merged_bitstream_20261029_r01/bd_p2d.tcl`（Vivado 2026.1 batch，产物 `D:\tmp\lead\p2d_merged_20261029_r01\out`）
2. 应用重建：`D:\tmp\lead\rebuild_timeout_20261029_r01\build_timeout_fix.sh`（旧）与 `D:\tmp\lead\tailfix_20261029_r01\`（含诊断）
3. 板级回归：`report/evidence/S4-T34/s4d_freeze_regression_plan_20261029_r01/run_freeze_regression.py`（`--dry-run` 可先看计划）
4. 上板约定与地址表：`s4d_p2d_stage5_close_20261029_r01/README.md`、`ADDRESS_MAP.md`

## 5. 边界

`ENABLE=0`；未写 QSPI、未改线、未 push；不主张 G5；本文件不替代 Wong 的验收签署。