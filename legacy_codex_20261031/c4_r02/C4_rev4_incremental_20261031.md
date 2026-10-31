# C4/R-02 rev4 增量独立审查

审查结论：**CHANGES_REQUIRED**。rev4 修订了协议文档中的部分缺陷，并收窄了 session 主张；但当前证据仍不足以证明冻结实现及上板消费者满足修正后的要求。E6-A r04 的 PASS 记录受未完成 POR、未绑定 rev4 ELF 两项限制，不能关闭 E3 消费者取锁问题。Stage6 的旧 G4/G5 记录仍宣称冻结/通过，与同基线 6D6E 记录中的 E5 FAIL 冲突。

## 固定审查身份与输入

- 主仓指定基线：`D:\FPGA_Competition` commit `0ccbe01de180b250200fc2470401323053f33d8a`。审查时 live HEAD 已前进到 `bcee56b555b982e920b8557b7899747e36190878`（父链含固定基线），且工作树有大量其他未提交文件；本报告不把新增提交和未提交改动纳入结论。
- w4：`D:\codex-worktrees\w4`，branch `stage4-infer-prep`，固定 HEAD `07efa677d1eaa8f427ec8f3ce7216ab3ed3c431c`。阶段5 tag peeled target 为 `6b43e05baa5e67a1674f72d3acdb77e0db660954`；阶段6旧 freeze tag target 仍为 `ec43da899fd4a7329af43d9a5fbc0a9c32c9d9c4`，没有指向 rev4 或 E6-A r04。
- DSH 修订主张：`D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261031-023-c4-fixes-rev4-m3-offer2.md`，SHA-256 `07242ecc3cb3ee8c341e8cfdea06fa40d5c74bf5451fcf44ce6bfdfa34b70ad2`。
- 主仓固定版 6D 规格 blob `6b2132473b7f43faa574dadb501d33e2732786652126614ab9c1e270fe0eec9b`；6D6E 验收记录 blob `6ff84fb544b1c3feb06de041c28734d8e6adc199`；G4/G5 验收与冻结记录 blob `93ddcf35139b5f96318284281c84aa965bb8b0a7`；主 STATE blob `5ef6bcd6072c0616a40cee9d44558c1b6f29488d`。
- w4 rev4 冻结记录 `S5_PRODUCER_V2_FREEZE_rev4.md` SHA-256 `5bacbbde9d00b0e7bc50b442e1170d47e068dc208f2888aaaaf0d5134a9d5ec2`；同目录 `manifest.json` SHA-256 `78b36f64d54de5cb0c9970a33ead6ffc6cbfc0cab52ebd3071a4f16220505c72`；构建记录 SHA-256 `a75fb173a3f6cb09bf5461ef171450ac60ad4358f1819c4027bd2d4edb0d499b`。
- 主仓之前的完整 C4/R-02 报告 `C4_R02_review_20261031.md` SHA-256 `3f6efbf4567a92ceea19aeb4f7905080673ef35ad0986412352eb16998a19a43`；本报告仅更新 rev4 相关问题，task-11 判定沿用该报告。

## 原问题与各关口复核

| 项目 | 结论 | 复核事实与主张边界 |
|---|---|---|
| Stage5 tag 身份 | **PASS** | `stage5-freeze-20261030` peeled 至 `6b43e05…`；主 STATE 固定版第228行也已采用 tag target。之前把祖先 `59280d7` 写成冻结版本的问题已关闭。 |
| Stage5 G3/G4/G5 实物范围 | **PASS（仅 DDR 注入显示链）** | 旧报告及冻结记录的输入是 DDR fixture/预置框，不能称为相机接入或真实模型推理验收。G5 主机窗口约 31:43，但 UART tick 仅 t=60…1740；帧端点 240→53,940 按 30 fps 约 1,790 s（29:50）。若要求完整连续 1,800 s 样本，不能用主机窗口补足该差值。此增量审查未重跑 Stage5。
| sidecar 与 16 项检测 ABI 重叠 | **CHANGES_REQUIRED（实现绑定未闭合）** | rev4 文档 §1/§2 将可发布上限改成 14：32 B 头后 14×16 B 占 `[0x20,0x100)`，sidecar 位于 `+0x100..+0x11F`，flush 288 B 到 `+0x120`；这是与 Wong 已批准 safe14 profile 一致的无重叠布局。文档 §5/§6 声称超 14 fail-closed、自检覆盖 14/15/16，但 rev4 manifest 只列 3 个文档/JSON，无实际源码或 selftest 源；manifest 没有源码绑定键。冻结文档声称的 `s5_display_app.c` hash `bed1a9…`、`s5_publish_abi.h` hash `a8ca5c…` 无法在交付包内核验。w4 唯一旧候选 `s5_display_app.c` 实际 hash `48368f16…`，且未找到发布/sidecar/seqlock 符号；候选目录缺 `s5_publish_abi.h`。C2 r02 的 guard 测试属于独立适配器，不能替代 DSH rev4 的实现证据。故只认可 rev4 的 safe14 布局声明，不把旧冻结生产者追溯判 PASS。 |
| 写者先发布奇数 seqlock | **CHANGES_REQUIRED** | rev4 文档 §3（第41–44行）现声明：奇数锁单独 flush + DSB → 写 payload/`result_time` → flush 288 B + DSB → 偶数锁 flush + DSB。顺序在规格层已修订；但源码、构建输入和 case0f 测试文件没有随 rev4 manifest 交付，无法确认实际 ARM 实现执行了此顺序。E6-A 结果只记录发布后的样本，不能单独证明奇锁已先对消费者可见。关闭条件：绑定真实源码/目标 ELF，并以目标实现或可复核硬件日志证明各阶段顺序。
| 消费者 invalidate-first / 二次读锁 | **CHANGES_REQUIRED** | 6D 规格第73–78行和 rev4 冻结 §3 改为先 invalidate、读 s1、读 payload、DMB、再读 s2。E6-A r01/r02/r03 均为 `S6E_E3_FAIL`，`E3-11` 的 s1/s2 字段缺失；r01 的 E3-8 也失败。r04 `results.json` SHA-256 `ce5a5517b86a0a46e20013c19f8fcbc80955d7ae031fea02e9de53df3ae6311e` 报告 6 组相等偶数对 `[840,840]…[1440,1440]`，但 ELF `6260250a…` 不在 rev4 8 个 ELF 清单（该清单长跑 ELF 是 `b563453b…`），且无 manifest。`window_close.txt` 第28–31行注明 `por_precondition:not_satisfied`：R-05 异常终止后未执行 POR。按 R-15，此结果不构成有效 POR 后确认；父控最新状态也确认当前 POR/初始化未完成、M3#2 未 CLAIM/未开板。另，若读写发生在不同核/非一致性 master，单次 invalidate 后的 DMB 不保证 s2 脱离旧 cache line；需绑定并证明单核串行/非缓存一致性契约，或在复读锁前再做适当 invalidate/同步，并验证交错情形。 |
| session 跨 POR 唯一性 | **PASS（仅主张范围收窄）** | rev4 §7 明确只主张 `session_id` 会话内恒定，不主张跨 POR 唯一性，碰撞递增仅 best-effort。这个更窄主张不应外推成跨 POR 唯一保证。C2 r02 仍要求 `previous_session_valid` 来阻止跨 POR 伪唯一；与 rev4 session-only profile 的集成关系尚须显式对齐，本报告不改 C2 或扩展 R14 设计。 |
| E1 | **PASS（只读枚举）** | 只证明目标枚举/连接路径可用，不证明生产者协议或推理。
| E2 / P | **PASS（范围限定）** | 6D6E 固定版第56–62行记录 `P=16,673 µs`、`+0.04%`、`fps_dis=60`，方法是 `PARKPTR.READSTR` 六沿取五间隔平均。它是 VDMA 显示读帧周期 proxy，不是相机采集 P、HDMI 外部仪器 P 或推理延迟。
| E3 / E6-A | **CHANGES_REQUIRED** | r01–r03 的 `results.json` SHA 分别 `4ff5f5bd…`、`98bf6781…`、`65f26a43…`，均记录 `E3-11=false`、无 s1/s2；r04 的“PASS”虽有 s1/s2，但版本和 POR 前置条件不成立。四次均为 rev4文档所述模拟 producer（模拟框、`inf=cap+7 ms`），不是真实模型推理。不可把 consumer 样本通过或 E4 故障注入解释成真实推理结果。
| E4 | **PASS（固定故障模式范围）** | rev4 四个独立 ELF 的 overrun→ERROR、stale→TIMEOUT、invalid→ERROR、no_hand→NO_HAND 映射记录通过。它们是固定模式 ELF，不证明真实模型在线故障处理，也不关闭缓存一致性/原子发布源码缺口。
| E5 30 min | **FAIL（6D6E 记录正确）** | 固定版 6D6E 第78–86行将 E5 判 FAIL：`result_time` 首末 1,006,368→2,804,568 ms，业务样本跨度 **1,798,200 ms = 29:58.2**，短于30 min 1.8秒；host window 30:23 不能替代业务跨度；`vdma_err=3,695,185` 且欠载样本增长/回绕。允许表述“约30 min链路稳定性（范围限定）”，不能称 E5 30 min PASS。
| Stage6 G4/G5 最终记录 | **CHANGES_REQUIRED** | 固定版 G4/G5 blob `93dd…` 第7–36行仍称 G4 通过、G5冻结成立、E5链路PASS/显示遗留；它同一提交内与6D6E blob `6ff8…` 的严格 E5 FAIL 和生产者源码绑定缺口（第121行）冲突。主 STATE 固定版第189–190行仍称阶段6 G4/G5 通过/冻结、E5链路PASS。须由总控修订/明确 supersede G4/G5 总结，并固定新的完整证据版本；不能沿用旧 stage6 tag 的 G4/G5 PASS。 |
| `result_time` 发布完成语义 | **CHANGES_REQUIRED** | 6D 规格第80–82行定义 `result_time` 为“发布完成”GT 时间；rev4 freeze §3 第42–44行却在 payload flush 和偶数锁 flush 之前先写入它。它最多代表“最终 flush 前采样”，尚无最终 cache clean/偶锁可见时刻的测量。r04 `delta_vs_inf_ms=17.554`（路径 `hdr_inf..+2frames`）不是 flush 完成时延测量。需统一语义，或测得并纳入时间误差上界，不能继续以“发布完成时刻”解释现字段。

## 无 ILA 的后续取证建议（均为建议，非实测）

- 将真实源码、构建命令、目标 ELF 与 manifest 绑定；host 自检在第14框、sidecar 首地址和 `+0x120` 末界布置 sentinel/CRC，并记录 14 框允许、15 框拒绝且不覆盖旧数据。
- 在目标 producer/consumer 记录锁写入与读值、s1/s2、seq/sid、重试次数、状态和 GT 时间；结合 XSDB/JTAG 只读快照。UART/内存快照是辅助记录，不能单独证明 cache flush 顺序或无 torn snapshot。
- 明确同核串行、其他核/总线写者及 cache 属性。若存在非一致性并发写者，在第二次取锁前执行并验证适用的 invalidate/屏障；通过强制交错、payload CRC 和 seq 对拍覆盖窗口。
- 用 GT 在 `result_time` 采样、payload flush 完成、偶数锁 flush 完成处分别记录时间；另行记录每个 READSTR 周期与抖动。相机 P 必须单独测，不从显示刷新 proxy 推导。
- POR 相关测试仅在 R-15 前置满足后用新 RunId执行，并记录上次 session 有效标志、旧 sidecar 是否保留、当前 sid 及初始化状态；本轮未进行此测试。

## 检查记录与限制

- `git rev-parse HEAD`（主仓）退出码 0，观察到 `bcee56b…`；`git cat-file -t 0ccbe01…` 退出码 0；`git -C D:\codex-worktrees\w4 rev-parse HEAD` 退出码 0，结果 `07efa67…`；w4 两个 tag peeled 检查退出码 0。
- `git show 0ccbe:<固定路径>` 提取主 STATE、6D6E 与 G4/G5 文本并核对 blob SHA，退出码 0。
- PowerShell `Get-FileHash -Algorithm SHA256`、`Get-Content -Raw | ConvertFrom-Json`、`Select-String` 对 rev4 manifest、源码候选、E6-A r01–r04、freeze 和主记录只读核验，均退出码 0；精确固定于上文 SHA/行号。
- rev4 manifest 实际只有 `p3q_producer_A_rev4_record.json`、`S5_P3B_SW_REPORT_rev4.md`、`S5_PRODUCER_V2_FREEZE_rev4.md` 三项；实际 rev4 目录没有源码/ELF文件。主仓工作树及 w4 均未写入。
- 尝试 Git Bash 读取命令被沙箱拒绝（`E_ACCESSDENIED`，退出码 1），随后使用 PowerShell 只读命令完成相同核验。
- 未运行测试、自检、厂商工具或重型进程；未连接/启动硬件会话；未改变 Git index 或提交。上述为文档与已归档证据审查，不是新的实物测量。
- task-11 完整 SEC 的必要性与 scope-specific N/A 论证维持原报告结论；本轮未重扫 `dbdf`，未将任何 N/A 建议当成 SEC 实测或关闭。
