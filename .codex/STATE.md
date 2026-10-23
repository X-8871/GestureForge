# 阶段4 状态（真实PS张量诊断接入准备）

更新：2026-10-23 15:35（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：Codex 阶段4接续总控受 Codex 项目总控委派独占，IN_PROGRESS。** 认领基线 `af85d5a8495598262395165492df5e4d0bfb723c`；DSH 于 00:35 OFFERED 并停止写入，00:42 现场复核 `handoff_check --claim` 得到 9 PASS / 0 FAIL / 0 SKIP，随后 CLAIMED→IN_PROGRESS。
**Wong 要求持续推进至4-D结束；完整阶段4未验收。** 当前先闭合4-B真实PS诊断、原始帧PL预处理G0及板测操作入口；硬件执行前须完成正式授权记录、会话交接及适用G0，4-D不以张量诊断代替完整预处理路径。12:46在额度中断后由同一总控恢复，无写权转移。

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
- S4-B-REAL-01/02A已提交 `0d3ad04be26efeb366ecf20487848a613a0a63fe`：离线源码/操作计划G2闭合，R1来源计划PASS、R2终态PASS；37单测及34独立CRC快照探针exit0，17文件原字节Git快照核对一致。闭合包 `report/evidence/S4-CTRL/s4_ps_tensor_closure_20261023_r02/`；evidence exit0、inputs exit2保留草案/硬件/RGB门禁。ARM相关源码未变，限定复用r12实际构建，不冒称旧全包匹配当前doc。5份ELF及5份map原位保留并绑定SHA，不入源码Git；不等于完整4-B/G3/G4。
- S4-B-REAL-02B首轮R1/R2均CHANGES_REQUIRED：来源身份可换r04 ELF/map或伪init后自证通过；另有ZIP多成员/字面路径/未来心跳与归属、错误repo根和package导入问题；正常ACK后CSR为IDLE，与旧导出终态矛盾；缺本次trace/UART逐条对账。旧2源原字节冻结在 `report/evidence/S4-B/s4b_ps_adapter_g2_20261023_r01/`。Developer修复轮1进行中，未提交；初版12测试与r11 prepare/validate通过不能关闭这些反例，硬件NOT_RUN。
- 原始RGB入口尚未接通；合法202×329→416半量化反例已独立复算（D2=100，精确有理数=101），不能自行改容限。`docs/stage4/S4B_pl_preprocess_g0_readiness.md` 的独立PS/JTAG描述符、HP0串行owner与PS跳过tensor拷贝候选已获“待决策材料”PASS；路线批准已异步提请Wong，仍DRAFT_NOT_APPROVED/G0_NOT_READY。数值证据包包装CHECKS_OK；新增资源/时序未知。实际装载、串口、板测仍NOT_RUN。
- 阶段5仍绑定S4-A r05；请求 `S4CTRL-20261022-003` 由阶段5所有者改绑r06并确认共享契约，不写w5。
- 真实摄像头回归尚未完成，不能声明完整阶段4 G5；模块到货/阶段3复测以其持有方现场证据为准。4-D文件注入候选不合并视频XSA。硬件门禁未闭合前不操作板卡/JTAG/COM4，不结束他人进程；阶段5已明确释放板卡，仍须核对当前注册表及正式接管条件。

- G0材料增补已独审PASS、两个evidence清单exit0：109帧中97帧>4MiB，最大packed RGB888=11,059,200B，4MiB草案只能容12帧。按默认109完整覆盖预算，不自行减样本/扩地址。D2旧/新SHA仅LF/CRLF差；34合成桥接一致，未重生成/逐值核验109帧或PL。证据 `S4-B/s4b_pl_g0_input_scope_20261023_r01/`、`s4b_pl_g0_reference_bridge_20261023_r01/`、`S4-CTRL/s4_pl_g0_materials_20261023_r01/`；6份桥接文件误落主tmp已保全并清理自有副本/3空目录，恢复记录保留。材料PASS不是路线批准，Wong答复仍待。

- 历史S4-C `s4c_replay_20261021_r05` 的109/109 PASS、0数值差异已独立核对，可精确复用CPU golden heads→D9→T29范围；本轮未重跑109样本/重哈希390MB分片，未覆盖D2/r06新字段或板卡。复用证据 `report/evidence/S4-C/s4c_evidence_reuse_20261023_r01/` 包装CHECKS_OK；此前“109全量NOT_RUN”不能解释为历史离线回放未做。

## 证据与恢复入口

- 认领：`report/evidence/S4-CTRL/S4-C05/s4_codex_claim_20261023_r01/claim.json`；DSH原让出：`report/evidence/CTRL-DSH-HANDOFF/handoff_20261023_r01/`（原记录不改）。
- 既有：`report/evidence/S4-A/s4a_g0_20261022_r01/`、`report/evidence/S4-B/s4b_injection_20261022_r01/`、`report/evidence/S4-CTRL/S4-C02|S4-C03|S4-C04/`。
- 通用清单规范包：`report/evidence/S4-CTRL/s4_codex_takeover_20261023_r01/`，认领及审查摘要包装CHECKS_OK；初版清单结构失败与原始C05记录保留。
- 上游冻结 SHA 仍以 `docs/stage4/s4a_stage4_g0_fields.json` 及原证据清单为权威；不复制另一套业务规格。

## 交接行（11字段）

任务=`持续推进至4-D：02B修复轮1、G0材料收尾与路线待决策` | 负责人=`Codex 阶段4接续总控（受Codex项目总控委派）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`af85d5a8495598262395165492df5e4d0bfb723c` | 允许修改范围=`本树docs/、verification/、scripts/、vitis/、report/evidence/、tmp/4/、.codex/STATE.md；保护旧冻结离线链与既有RunId` | 未提交改动归属=`02A已提交0d3ad04；STATE、G0增补与02B待审新文件归本总控；5ELF/5map本机恢复依赖不入源码提交` | 让出声明=`未让出；本树写权由Codex阶段4接续总控独占` | 心跳(UTC+8)=`2026-10-23 15:35` | 证据入口=`report/evidence/S4-B/s4b_ps_adapter_g2_20261023_r01/；已闭合PS诊断见S4-CTRL/s4_ps_tensor_closure_20261023_r02/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock` | 状态/下一接手方=`IN_PROGRESS / 当前Codex阶段4接续总控`
