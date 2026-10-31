Hello Wong.

# C4/R-02 E6-A r05 增量独立复审

审查日期：2026-10-31（UTC+8）  
结论：**CHANGES_REQUIRED**

## 审查范围与固定身份

本次只复核 C4 rev4 报告之后新增的 POR 后 E6-A r05、对应生产者 rev4/rev5 绑定材料，以及当前 6D/6D6E/G4G5 文档对既有问题的处理；不重跑 Stage5，也不复审 session 跨 POR 唯一性。Stage5 S5-T01 G3/G4/G5 结论沿用既有报告：**仅 DDR 注入显示链范围 PASS**，不是相机/真实推理验收；G5 30 分钟采样跨度仍须按旧报告限定。

| 输入 | 固定身份 / SHA-256 |
|---|---|
| 主仓 D:\FPGA_Competition | HEAD 35c45778d2473faea41f16da014ba33e8e031bda；AGENTS 38746412608f5a7ccd82303495f672d898d8c57cfe90c3af2f607521af72e15a；STATE 311c89a75ac6e6671cd1e9c816435d568c6e3b82d2be2f5d612d5a3551a34675 |
| w6 | HEAD 25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3；既有原报告 C4_R02_review_20261031.md SHA-256 3f6efbf4567a92ceea19aeb4f7905080673ef35ad0986412352eb16998a19a43；rev4 增量报告 SHA-256 e36a4e092ddcf8b163b8e615e5f9394bcb2d2c38102bc6184e64c796e78effcd |
| w4 | HEAD e22fccf8cc8bbd0ccc8b20c4289c3244b0508c2a；本次引用的相关证据目录在该树中无未提交改动 |
| 当前 6D / 6D6E / G4G5 文档 | 6D 口径 SHA-256 6b2132473b7f43faa574dadb501d33e2732786652126614ab9c1e270fe0eec9b；6D6E 记录 b5bedad0ec94d306cd19b29ec28b2e084f8f2b68412bd8226b11497222125ffb；G4G5 记录 dbd1722db1d6a8682c609d8b6d48ff6c6b209e05492bc288b40874f9e95e4f08 |
| E6-A r05 | manifest.json SHA-256 49f316dd02fe77c77f8b0efa38cd59a0e7eac91a06e12cfbd0b77f60758d3de7；results.json 4e3dfb040f2e39c145db8b3715cf2c8814d16d494d9cabcd377fcd5ebf4be2ea；W3_judgement.json e99e9ea4c6f1ddaa1a76bf20e675c16ba8bfcf5fffc6107bfe99f82a5ec3ba9f；UART 872c4f285d584888420711d71c6bbc0324f54453b18efcc2024e4ac4644f5dd2 |
| producer rev4 归档 | manifest SHA-256 78b36f64d54de5cb0c9970a33ead6ffc6cbfc0cab52ebd3071a4f16220505c72；freeze SHA-256 5bacbbde9d00b0e7bc50b442e1170d47e068dc208f2888aaaaf0d5134a9d5ec2；build record a75fb173a3f6cb09bf5461ef171450ac60ad4358f1819c4027bd2d4edb0d499b |

旧报告保留原样。本报告不改主仓、w4、冻结物或 Git index。

## 逐项复核

### 1. r05 POR 窗口与来源/ELF/冻结清单绑定：**未关闭**

E6-A r05 比 r04 多了消费者 s1/s2 字段，并把窗口标为 POR 前置满足：report/evidence/S6-T01/s6e_e6_age_r05_20261031_r01/window_close.txt 第 3–10 行；运行结果 results.json 第 4–13 行将本次标为 mode=e3，记录位流/XSA 与 ELF SHA-256 6260250a4a9707657c354016f951122743fa502a8f4b8356ef772aea3f7047a5。S6_load_app_output.txt 写明实际 dow 路径为 D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_p3q_producer_longrun.elf。对此路径执行 Get-FileHash -LiteralPath ... -Algorithm SHA256 退出码 0，磁盘 ELF 的 SHA-256 与 r05 记录一致。

但该 ELF 不属于归档的 rev4 冻结清单：producer rev4 manifest.json 第 8–18 行的 longrun ELF 是 b563453b70624cb95ea23e1da7655582237b153345efcd36a30dab8c1fadee17；其 items 第 24–39 行只绑定构建记录和两份文档，没有源码或 ELF 文件。r05 manifest 第 4 行虽声明 hash_basis=commit_blob，其 items 绑定的是本次窗口的结果、UART、探测和快照文件，没有纳入 rev5 build record、rev5 ELF 或源文件。

在窗口外的临时构建目录找到 D:\tmp\lead\p3b_display_sw_20261030_r01\build\p3q_producer_A_rev5_record.json（磁盘 SHA-256 807f427b79ef66e93ab7e0225f5b9d9c5a157dbe4264c23b7bdff676c274cef9）。该文件宣称 rev5 longrun ELF 为 626025…，与运行 ELF 一致，并列出源哈希；这是有用的交叉线索，但它不在 r05 manifest 或 producer rev4 归档中，也没有随本次 E6 提供的 rev5 冻结 manifest。记录没有 hash_basis/source commit。记录声称 src/s5_display_app.c 为 cd2b093a…；相同临时目录当前该路径的磁盘 SHA-256 是 beead486…，最后写入时间 10:36，晚于构建与 r05 窗口。因没有被审 ELF 对应的不可变源码快照，无法独立复算记录中的编译源版本。这里判定的是证据链未封闭，不据此断言当时构建错误。

关闭条件：将 rev5 build record、实际 ELF、全部编译源码/脚本哈希和构建命令/退出码纳入新证据包，并用有 hash_basis=commit_blob 的 manifest 与 r05 的 ELF SHA 绑定；或提供等价的不可变冻结包。当前不能把 rev4 freeze 或 r05 wrapper/judgement 的 PASS 代替此绑定。

POR 状态方面，E1 r06 的 results_e1.json 第 63–67 行记录 por_precondition_before=not_satisfied、por_cleared=true，E6 r05 window_close.txt 第 7 行标为 satisfied；因此 r04 的“不满足 POR”限制没有被直接复用到 r05。物理断电本身未见于 r05/E1 manifest 清单，DSH-026（SHA-256 d83340f39dcab8cae9ba680e43808b9c8c80aa122263ed022d0897df2609e93b）第 10–11 行是对 Wong 断电及 board_state 的文字回报，不是独立的电源事件记录。本审查只把 POR 视为任务给定且运行记录标记满足的前置，不从该回报单独推出 G4/G5 PASS。

### 2. 写者奇数锁先 flush/DSB：**协议文字已改，目标实现未证**

现行 6D 口径第 67–71 行与 producer rev4 freeze 第 40–44 行要求：先置奇、单独 flush 锁行并 DSB；再写 payload/result_time、flush 288 B 并 DSB；最后置偶、flush 锁行并 DSB。rev5 build record 声称同一顺序，rev4 freeze 第 75 行还宣称 case0f 离线顺序断言通过。

这些是规格/构建记录层的声明。r05 manifest 未绑定目标 ELF 所属的 rev5 源文件或 case0f 源码/输出；r05 UART 和 memory dump 只显示发布后的稳定状态，没有记录写者奇锁、flush 调用或 DSB 的执行序列。故不能据此确认上板目标实现确实先使奇锁可见再写 payload。**此项仍 CHANGES_REQUIRED。**

### 3. 消费者在 s1 前 invalidate：**观测字段补齐，代码顺序未证**

现行 6D 口径第 73–78 行、rev4 freeze 第 46–53 行均规定先 invalidate，再读 s1、复制 payload、DMB、复读 s2。r05 的 W3_judgement.json 第 147–185 行现在包含 s1/s2、偶数判断、retries 与 timeout 汇总；这关闭了 r04 缺少 s1/s2 可观测字段的问题。

这些汇总没有记录 invalidate 操作发生在 s1 之前，也没有绑定本次 ELF 对应的消费者源码。日志结果只证明解析到的读锁值符合判据，不能证明执行顺序。**消费者顺序问题仍 CHANGES_REQUIRED。**

### 4. result_time 与“最终发布可见”口径：**未关闭，且文档值与 r05 结果不一致**

当前 6D 口径第 80–82 行把 result_time 冻结为“发布完成且可被消费”的 GT 时刻；同一文档第 69–71 行及 producer freeze 第 41–44 行却把 result_time 写在 payload flush 之前，随后才 flush payload、DSB、发布偶数锁并再 flush/DSB。因此 r05 的 sidecar 值只能证明保存/读出的时间字段自洽，不能证明它测到最后一次 flush 和偶数锁可见完成的时刻。

r05 W3_judgement.json 第 211–223 行给出的 delta_vs_inf_ms 是 **26.234 ms**（sidecar result_time_ticks=33113219965 与 header inf_ticks=33104475185），不是文档及 DSH-026 所述 **17.7 ms**；同一字段校验路径是 hdr_inf..+2frames，并非最终 flush 完成时间测量。当前 6D6E 文档第 125–134 行仍将“17.7 ms”写入 E6 总结。应统一 result_time 的可实现语义、记录阶段时间，或给出最终发布时刻测量及误差上界。**此项仍 CHANGES_REQUIRED。**

### 5. E5 FAIL 与新版 G4/G5：**FAIL 已在增补中披露，但未被有效替代/关闭**

当前 6D6E 文档第 78–86 行继续把 E5 严格判为 FAIL：有效业务跨度 29:58.2，小于 30 分钟，并有 vdma_err/欠载问题。r05 results.json 第 4 行是 mode=e3，window_close.txt 第 4 行窗口仅 02:10:37–02:12:03；它不是 E5 长稳复测，不能改变旧 E5 的退出码或结果。

新版 G4/G5 文档确实在第 70 行补写“E5 改 FAIL”，第 75–78 行称 E5 FAIL 保留；但同一文件第 17、28 行仍写“E5 链路 PASS”，第 34–36 行仍称“E3/E4/E5 链路全绿”。增补没有明确声明这些旧段落被哪一条新结论取代，且仍把未满足的 E5 判据作为 G5 冻结的“记录性局限”。因此它没有形成无歧义的 G4/G5 结论，也没有新证据替换 E5 FAIL。按工程规则中 G5 的“阻断问题清零”要求，不能只把未满足的 E5 标为局限后继续宣称阶段冻结完成。

结论：E5 FAIL 应继续保留；G4/G5 文件需明确标记旧 PASS/全绿段落为历史并由新判定取代，并依据既有验收标准处理未通过项。若拟更改 E5/G5 验收范围，需按项目决策规则另行批准，不能由本次 E3 窗口推定。

### 6. 相同偶锁正样本是否足以证明原子协议：**不足**

r05 W3_judgement.json 第 147–185 行记录 6 组 s1/s2 相等偶数对（2880–3480）、retries_dist={"0":29}、无 timeout；这支持“所采样读取均成功且未观察到重试/超时”。它没有观察到奇数锁写入阶段，没有强制读写交错，也不显示 invalidate/flush/DSB 的实际调用序列。稳定的正样本不能证明所有发布交错下无 torn snapshot，不能证明写者先 flush 奇锁或消费者先 invalidate。故 6D6E 第 129 行和 G4/G5 第 68 行把这些样本称为“原子协议板上验证通过”的范围过宽；最多保留为 E3 采样结果。

### 7. E6 的数据是实际推理还是模拟：**模拟结果**

r05 是真实板上运行/采集（例如 E6 S7_uart_output.txt 第 8 行记录测试图样，第 14 行起有 S5PROD 输出），但 producer rev4 freeze 第 83–87 行明确该版的 n_dets/class/score/坐标由模拟框供给，inf=cap+7 ms；rev5 构建记录仅列协议顺序与源码版本变化，没有声明已接入真实推理写端。故 E6 可支持限定范围的板上结果块生产/消费观察，不能表述为真实模型输出或推理链验收。

## 对前两份 CHANGES_REQUIRED 的关闭状态

| 原问题 | r05 后状态 |
|---|---|
| r04 POR 前置不满足 | **对本次窗口的运行标记已补齐**：E1 r06 记录 por_cleared，r05 close 标 satisfied；缺少物理电源事件的独立归档，不外推为其他窗口证据。 |
| r04 无 s1/s2 消费者字段 | **观测缺口关闭**：r05 有 s1/s2/retries 字段；并未关闭 invalidate-first 实现顺序证明。 |
| r04 ELF 与 rev4 冻结 ELF 不同 | **仍未关闭**：r05 ELF 与本地 rev5 record 相符，但该 record/source/ELF 未纳入 r05 的 commit_blob manifest，也无 rev5 不可变冻结包。 |
| 写者奇锁可见顺序 | **未关闭**：只有规格/构建记录声称，没有本次目标实现绑定与顺序证据。 |
| 消费者 invalidate-first | **未关闭**：读值相等不能证明调用先后。 |
| result_time = 最终发布可见时刻 | **未关闭**：字段早于最终 flush/偶锁发布，且 6D6E 的 17.7 ms 与 r05 实际 26.234 ms 不符。 |
| E5/G4/G5 | **未关闭**：E5 仍 FAIL；新版 G4/G5 同文保留旧 PASS/全绿语句并仍称 G5 冻结成立。 |
| 原子协议由正样本证明 | **不成立**：样本支持观测值，但不证明发布/读取顺序或覆盖并发交错。 |
| 真实推理输出 | **未提供**：E6 是模拟框/测试图样 producer。 |

## 核查命令与限制

- git rev-parse HEAD（主仓、w4、w6）及限定路径 git status --short：退出码 0；固定 HEAD 分别为上表所列身份。主仓存在与本审查无关的预存工作区改动，本次未触碰。
- 对两份旧报告、当前 6D/6D6E/G4G5、r05/E1 关键文件、producer freeze/manifest/build record 执行 sha256sum 或 PowerShell Get-FileHash -Algorithm SHA256：退出码 0；哈希见上表或对应条目。
- 对固定 E6、producer、文档、mailbox 目录执行有限 rg --files、rg -n -C 和逐文件读取：命中目标；用于本报告的检索退出码 0。
- 对 r05 实际 ELF 精确路径执行 Get-FileHash -LiteralPath ... -Algorithm SHA256：退出码 0，值为 6260250a…，与 r05 记录及本地 rev5 build record 声明一致。
- 未运行构建、测试、自检、manifest wrapper、Vivado、XSDB、硬件操作或 socket；未写主仓/w4/冻结物，未改 Git index，未提交。唯一写入是本独立审查报告。
