# 阶段0–6遗留委托：当前结论及本轮精确提交入口

本函汇总018任务卡、已读取019/023/025/026/027及恢复后的离线修复。**没有全部完成，不主张阶段5/6重新冻结。** 旧板窗全部撤销；下午本轮没有启动hw_server/XSDB或连接板卡。新板窗申请见CDX-022，未收到新OFFER前不CLAIM。

## 每任务当前结论

| 任务 | 结论 | 关键结果、退出码与限制 |
|---|---|---|
| 1 / R-08 | **PASS** | 正式11字段OFFER及19项归属已落w6 STATE，DSH-020明确CLAIM，主STATE已登记关闭；本轮保留旧差异，不混入新提交。文书交接无程序判定码，当前只读Git身份核对exit0。 |
| 2 / R-03 | **BLOCKED（实采）** | state键问题已改唯一选核后调用`state`；核心43项测试、当前窗口保护42项测试均exit0，独立实现审查PASS。首个真实窗口01:20:08.792615–01:21:08.245793仅59.453s，setup读到Running后语义FAIL（进程0/语义2），未做成对采样，已一次收尾且13项输入前后一致。下午未重开窗。新程序拒绝before之后restore，包括失败半包，避免重置基准掩盖变化。 |
| 2 / 47.3s与diff0解释 | **PASS（根因分析限定范围）** | 旧失败ELF实际写400 cycles，在50MHz下为8µs；done=2/error=5跳过HEADS比较，0差异字段未计算。另3份历史done=1/error=0日志才有实际HEADS比较及47,287ms，不能与失败字段混用。historical DDR变化的硬件根因仍未由M3证明；不处理R-01吞吐。 |
| 3 / R-05 C2 | **BLOCKED（完整板验）；离线实现PASS** | 32B ABI不变，640×480、16B项、sidecar+0x100、14框安全上限、>14 ERROR，写区288B；业务状态200ms。主机单测及目标汇编检查exit0，独立离线审查PASS；尚无真实框/box_crc/age_pub/state板验。可信上一SID、真实cap GT、infer_done事件、rev4源码/ELF绑定及匹配部署包缺失；不能承诺完整板验≤1天，CDX-019已回报最小组合兜底。旧计划的decoder-return时间建议未对齐S5 DONE_SAFE前不得执行。 |
| 4 / R-09 C3 | **PASS（离线交付）** | 方法学+原CSV分析器11项+新采集核心21项均exit0，独立复审PASS。原5间隔均值复算16,673.669516µs，UART截断16,673；是VDMA读帧存代理，不能代替相机SOF。新核心GT前后包围counter读取、跨区间回退拒绝、duration按保守下界；真实测点、GT校准、板上回调NOT_RUN。 |
| 4 / R-09 C4 | **PASS（完成独立审查交付）；审查判定CHANGES_REQUIRED** | r05新审查命令exit0，已补s1/s2及POR满足标记；仍缺实际rev5源/ELF/构建记录的commit_blob绑定和执行顺序证据。r05差值26.234ms与文档17.7ms不符；稳定偶锁正样本不证明无撕裂。旧E5有效跨度29:58.2且VDMA异常，仍FAIL，新E3窗不替代长稳；G4/G5旧“全绿”表述仍须明确替代。 |
| 5 / R-02②④ | **PASS（分析交付）** | task-11为顺序等价SEC，原完整证明契约仍BLOCKED_NOT_RUN，未获豁免不能全局N/A。只对明确排除wrapper的旧DDR fixture交付可提出范围限定N/A，不能延伸至新P3r相机路径。无ILA建议为UART原始GT日志、CSR/GT计数、JTAG全区双读/多次样本、受控GPIO观测；这些有限实测不能替代完整SEC。 |

## 证据入口

- R-08：`D:\codex-worktrees\w6\.codex\STATE.md` 顶部正式OFFER；DSH-020 CLAIM及既有`legacy_codex_20261031/r08/`快照。
- M3：`D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261031_r01\INCIDENT.md`；`m4b_rootcause_20261031_r02\ROOT_CAUSE.md`；新保护源/模板/说明 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\`；最终审查 `r03\review_new\R03_m3_ordering_review_20261031.md`，SHA `03f44e12f381fa0458b99a49a93032a63bc35e0aa5686fa565565ee8f3bbaa1a`。
- C2：`D:\codex-worktrees\w6\legacy_codex_20261031\c2\`；新增准备度报告 `c2_integration\C2_REAL_APP_READINESS_20261031.md`，SHA `0dd279191cb2e235d044be5c2a9ef91538b499022ccbfa0f6b1fbf69a277d84c`。
- C3：`D:\codex-worktrees\w6\legacy_codex_20261031\c3\` 与 `c3_collect\`；最终复审 `c3_collect\review_20261031_r02.md`，SHA `238acdf5a47fea6d65f2917042ef1b64b0d7ae3a4fe6c93dfbb375c076ac533f`。失败/未达标CSV必须与采集状态摘要一同保留，不能仅据非空周期估值主张完整实测。
- C4/R02：`D:\codex-worktrees\w6\legacy_codex_20261031\c4_r02\C4_R02_review_20261031.md`、`C4_rev4_incremental_20261031.md`、`C4_r05_incremental_20261031.md`；最新SHA `4e8f62af6388bfe126645456325e53ded5ad7bb9edb8b033f045ab94a4a6a101`。旧报告及CHANGES_REQUIRED证据全部保留。

## DSH串行提交的当前唯一汇总入口

`D:\codex-worktrees\w6\report\evidence\CTRL-LEGACY\final_followup_20261031_r01\submission_inventory.json`

SHA-256：`df45f117ca36ec40ba70c1f7e22d6a647e0afa1f14a056764f84ce929fbcd790`。

该清单内 **36路径、277,838 B + 清单自身 =37精确路径**，已逐项核对字节数与SHA。它合并015的11文件、021的3文件、022的16文件，以及新C3的6文件；四份子清单一并保留。如某子批已提交，请核对相同内容后只处理余项，不回退历史、不重复改写。**017暂停的旧清单不在本批。** 排除旧硬件r02准备目录、原STATE差异、两份S6A规格、14个旧目录和其他无关改动。

按Wong已确认的安排，由DSH核验后串行git add/commit并回传实际SHA；我方未暂存/提交。此汇总`hash_basis=worktree_disk`且`delivery_eligible=false`，仅提交前附注。实际提交后按新RunId与实际Git blob另建权威清单、跑strict；不能以磁盘清单代替提交基座。

## 已提交权威身份与门禁限制

- 原86文件源提交：`25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`；此前C1提交：`892d944f6a1c04a8956fce200f9edc416edce8c6`。
- 原86项`delivery_manifest.json` SHA `cea8a6030f1cfde8fd803d7ee4f65301a35c36d2cbeadc9f567ebb7a3bf4aa10`，每项commit_blob绑定25dbc5e；strict **86 checked /0 mismatch /exit0**，执行记录及stdout在`report/evidence/CTRL-LEGACY/residuals_20261031_r01/`。
- 该strict只证明身份一致，不代表业务接口、测试或G3/G4/G5通过；当前汇总未当作stage-delivery业务验收包，不主张inputs/evidence机器关口PASS。新增37项尚无实际提交SHA，因此当前也不主张其commit_blob strict已完成。
- 当前剩余依赖：DSH新M3正式OFFER+实际就绪事实、DSH本批提交SHA、C2集成输入与匹配平台、C4所列源/ELF绑定及验收修正。`ENABLE=0`、不push、未改阶段5/6冻结物或他方工作树。
