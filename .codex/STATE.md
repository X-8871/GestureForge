# 阶段4 状态（摄像头推理 · 离线修复与 G2 补齐）

更新：2026-10-23 02:00（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：Codex 阶段4接续总控受 Codex 项目总控委派独占，IN_PROGRESS。** 认领基线 `af85d5a8495598262395165492df5e4d0bfb723c`；DSH 于 00:35 OFFERED 并停止写入，00:42 现场复核 `handoff_check --claim` 得到 9 PASS / 0 FAIL / 0 SKIP，随后 CLAIMED→IN_PROGRESS。
**本树只推进阶段4离线交付；完整阶段4未验收。** 4-D 板测与真实摄像头回归仍需正式硬件授权、会话交接及阶段3依赖。

## 继承的交付与版本

- DSH 主体提交 `e247b49`：4-A G0 r06、共享契约 `s4-shared-io/1.1.0` r02、主机 mock DDR/cache 单帧注入；审查限制 `bb5d9ab`；OFFERED 声明 `821b05a`；末次交接提交 `af85d5a`，认领时工作树干净。
- 4-A 自检 18/18、变异 9/9、包装核验通过；24条上游绑定包含23文件及109分片目录。R1 只读独立复算全部匹配（109片 / 390,700,998 B）。
- Codex接管后新自检：`report/evidence/S4-A/s4a_g0_20261023_r03/`，18/18、23文件及109分片SHA匹配，exit 0；首轮R02日志编码环境失败原样保留。
- 最终修复S4-B r08：严格GCC 0警告、host42/42、C API检查30/30、unit10/10、小图CRC2/2；30项含两个64位平台不适用提示，不代表32位覆盖。32位两个编译单元通过，链接缺i686 CRT/libgcc退出1，行为NOT_RUN。S4-CTRL r05：23项通过、契约变异5/5及运行书反序变异1/1拒绝；最终两包CHECKS_OK。
- 4-B 历史离线证据：gcc 严格编译0警告、23用例、8条 unittest；这些证据未覆盖本轮独审缺陷，不能据此判 G2。
- 契约与地址图仍 `DRAFT_PENDING_REVIEW`；200 ms stale 门槛仍 `DRAFT_PENDING_APPROVAL`。不得提前作为正式验收阈值。
- 提交前源码/STATE空白检查通过；全量暂存检查退出2仅因原始证据CRCRLF/历史探针末尾空行，保留原字节，例外及实际退出码见最终 `lead_validation.json`。

## 本轮离线修复与独立审查

- Codex 独立 Reviewer R1/R2 已对 `bb5d9ab` 源码补审，均 `CHANGES_REQUIRED`（源文件在交接提交中未变）。
- R1：共享契约 session_id string 与 S4-A u32 不一致；各连接键角色未对齐；synthetic 时间可用性/词表不完整；地址图草案被称冻结、S4-A 镜像旧哈希未标历史。T3显示语义/T4 HUD 13键符合；旧 r01 T1–T4 原始报告未找到，类别摘要不能代替原关闭条件。
- R2：写前未拒绝在途区间重叠；在途帧序号回退；空payload绕过完整性；采集时间哨兵/CLI解析；stride/帧长溢出；缓存顺序与mock可见性；CHW平面统计；timeout后安全释放及回调生命周期。
- 两轮修复后R1-03/R2-03独立复审均PASS，本轮主机离线实现/规格G2通过；最终19文件快照及原始探针在 `report/evidence/S4-CTRL/s4_g2_closure_20261023_r02/`。闭合运行书顺序、通用SIZE_MAX范围及初始化失败重试；先前失败复审与所有RunId保留。此结论不等于32位行为、真实PS/BSP、PL、G3/G4或阶段G5通过。
- 保护旧已冻结离线链：`s4_ps_decode.*`、`s4_uart_protocol.*`、`s4_offline_host.c`、`run_s4b_offline_chain.py`、`build_s4b_manifest.py`、`test_s4_ps_decode.py` 与全部旧RunId不改写。

## 必须保持的接口与边界

- 2B 正式冻结 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`：1000连续任务、108 ACK闭环样本；109黄金不等于109 ACK闭环。
- UART方案B：`s2bu/1.1`正文不变、扩展关闭，时间/丢帧/过期/状态只记PS侧；结果与旁路日志按会话/帧/结果序号明确关联。
- 候选上限12675可行，尝试追加12676为硬错误；4096禁用；候选数与最终≤15框不同。
- 注入须位于被验收预处理前；capture_time_available=false，capture_time_ns为0哨兵并注解，计时起点用injection_start_ns。灰度不能对旧彩色golden。
- 当前仅主机离线实现；实际预处理接入、PS/BSP缓存与屏障、PL启动/完成及板上驱动尚未交付可执行闭环。
- 阶段5仍绑定S4-A r05；请求 `S4CTRL-20261022-003` 由阶段5所有者改绑r06并确认共享契约，不写w5。
- 摄像头待购；无真实摄像头回归不能声明完整阶段4 G5。不得操作板卡/JTAG/COM4或结束他人进程。

## 证据与恢复入口

- 认领：`report/evidence/S4-CTRL/S4-C05/s4_codex_claim_20261023_r01/claim.json`；DSH原让出：`report/evidence/CTRL-DSH-HANDOFF/handoff_20261023_r01/`（原记录不改）。
- 既有：`report/evidence/S4-A/s4a_g0_20261022_r01/`、`report/evidence/S4-B/s4b_injection_20261022_r01/`、`report/evidence/S4-CTRL/S4-C02|S4-C03|S4-C04/`。
- 通用清单规范包：`report/evidence/S4-CTRL/s4_codex_takeover_20261023_r01/`，认领及审查摘要包装CHECKS_OK；初版清单结构失败与原始C05记录保留。
- 上游冻结 SHA 仍以 `docs/stage4/s4a_stage4_g0_fields.json` 及原证据清单为权威；不复制另一套业务规格。

## 交接行（11字段）

任务=`S4-CTRL 阶段4离线缺陷修复与G2补齐` | 负责人=`Codex 阶段4接续总控（受Codex项目总控委派）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`af85d5a8495598262395165492df5e4d0bfb723c` | 允许修改范围=`本树docs/、verification/、scripts/、vitis/、report/evidence/、tmp/4/、.codex/STATE.md；保护旧冻结离线链与既有RunId` | 未提交改动归属=`认领时无；此后本轮STATE、认领证据及修复均归Codex阶段4接续总控` | 让出声明=`未让出；本树写权由Codex阶段4接续总控独占` | 心跳(UTC+8)=`2026-10-23 02:00` | 证据入口=`report/evidence/S4-CTRL/s4_g2_closure_20261023_r02/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock` | 状态/下一接手方=`IN_PROGRESS / 当前Codex阶段4接续总控`
