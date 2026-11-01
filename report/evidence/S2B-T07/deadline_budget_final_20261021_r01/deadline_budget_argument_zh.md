# S2B-T07 最终期限预算候选论证（2026-10-21）

## 结论

CORE 正常推理的两次实测 START→安全终态 wall 区间，在绑定 XSA/HWH 配置的 50 MHz 假设下均满足 25% 余量算术：R11 为 2,370,089,810 个名义周期，R12 为 2,370,291,540 个名义周期；较大者乘 1.25 并向上取整为 2,962,864,425，低于 32-bit 上限 4,294,967,295。

这说明本次观察到的完整推理 wall 区间有余量，不能据此宣称已量得精确 PL 周期、逐笔 HP 延迟、HP 等待累计值或未来最坏情况。§202 要求的部署期限论证只形成部分证据；DRAIN 最终候选仍为最大值，但 R12 的实板短测使用 `DRAIN_TIMEOUT_CYCLES=1`，因此没有测得最终 `0xFFFFFFFF` 配置的安全返回区间。当前记录为 `CANDIDATE_BUDGET_BLOCKED_PENDING_REVIEW_AND_ADDITIONAL_EVIDENCE`，不改变正式验收标准。

## 工作量与计算依据

沿用 `deadline_budget_20261019_r02` 的冻结模型口径：tiny416 输入为 416×416，38 层共有 84,753,811 个逻辑读请求和 11,382,150 个逻辑写请求，合计 96,135,961 个单字节逻辑请求；卷积计算状态共 424,506,368 次迭代。仅按每请求两拍的最低请求状态估算，得到 192,271,922 拍；加上计算迭代，下界为 616,778,290 拍，即 50 MHz 下约 12.3355658 秒。

这个下界不含初始化、扫描、重定量、输出、HP 等待/背压、控制流程和主机观察开销，不能当作完整推理预测。旧预算绑定的 12 个 RTL/软件源文件哈希与当前文件逐项匹配，机器记录为 `MATCH_ALL_12_FILES_AGAINST_20261019_R02_BUDGET`。上游预算状态仍是离线请求/计算计数，不是 HP 延迟测量。

## 正常 START 实测包络与余量

R11 的正常 START 测量为 47,401,796,200 ns；R12 为 47,405,830,800 ns。转换计算使用 `ceil(elapsed_ns × 50,000,000 / 1,000,000,000)`，没有将其标记为实测 FCLK 或精确 PL 周期。较大的 R12 数值换算为 2,370,291,540 个名义周期；乘以 1.25 为 2,962,864,425 个周期，剩余 1,332,102,870 个周期，即配置频率下名义 26.6420574 秒。

这两个 wall 区间是在实际完整推理与本次 HP 行为同时发生时，从 START 测量起点到读到 DONE_SAFE 的整段时间。因此它们是该两次运行的 **HP-inclusive 整体运行包络**，其中同时包含模型计算、HP 响应与可能的背压、控制与主机轮询开销。证据没有单独计时 HP 的 AR/R/AW/W/B 延迟，也没有把可能重叠的等待拆成可相加的 HP-only 总时长；不能把整段 wall 时间冒称成一笔事务延迟或逐笔等待总和。实际 FCLK 频率也未在板上测量，50 MHz 来自绑定 XSA/HWH 的生成配置。

两次样本只证明这些运行的观测值。不能据此推断所有 DDR 状态、长期背压、109 样本语料或 1000 次连续任务的最坏边界。R11 整体结果仍是 FAILED/native exit 2，原因是稍后保存重复的不可变 `deadline_epoch_causality.json` 失败；本预算保留该失败，不将正常单次场景的 PASS 改写为 R11 整体 PASS。R12 的总结果只声明 `PASS_CSR_DEADLINE_SCOPE_ONLY`。

## DRAIN 测量、候选最大值与隔离语义

最终候选 `DRAIN_TIMEOUT_CYCLES=0xFFFFFFFF` 在配置的 50 MHz 下名义为 85.8993459 秒，是有限 32-bit 值；它不是“85.9 秒内一定排空”的保证。接口规定 DRAIN 期限超限进入 `FAULT_ISOLATED`，但仍继续接收 B/R 响应。若事务永不完成，有限计数器本身不能保证有限安全返回时间；若晚响应最终合法完成且其他可见性条件满足，才可走向安全终态。

R12 的短期限实测使用 CORE=10,000、DRAIN=1。记录显示 `FAULT_DETAIL.bit3`、错误码 5、安全终态、ledger=0，并在匹配 ACK 后回到 IDLE。START CSR 写调用时间到首次 CSR 快照读到安全终态调用时间的主机观察括区间为 42.262 ms。该值包含 DAP 调用和轮询间隔，不能视为硬件准确转换延迟；本次没有观察到 `FAULT_ISOLATED` 阶段，也没有声称发生或采到 pending 晚响应。因此该运行只支持 DRAIN=1 的短期限/安全 ACK 场景，不能定量证明最终最大 DRAIN 配置的观察期限依据或安全返回时间。

据此，最终 DRAIN 部署观察期限的量化依据仍开放。保留正式接口中“期限有限、过期隔离但继续接收响应”的语义，不把“仍在 drain”解释为已经可 ACK/复用。

## R12 范围边界

R12 deadline scope 真实完成了正常 START 测量、CORE 短期限错误码 5 安全返回与 ACK、DRAIN bit3 短期限安全返回与 ACK、真实 DIAG mode0 epoch 对账以及 sample000 黄金恢复。它没有执行 109 样本语料、1000 次连续任务、busy/pending reset，也没有声称 pending 晚响应。

独立 T20 static matrix 仍有多个 `BLOCKED_BRESP_UNRESOLVED` 场景和 `busy_start=BLOCKED`，状态为 `SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE`。不要将 T18 deadline-only 结果描述为完整阶段验收。R12 scope 及静态矩阵的原始证据均以 JSON 的路径、SHA-256 和字节数绑定。

## 证据与复核

机器量化和逐项证据绑定见同目录 `deadline_budget_final.json`。上游 R02 预算及 R11/R12 原始结果保持只读；本文件是候选论证，不改写接口规范、阶段状态或历史 RunId。复核时应特别检查：

- 50 MHz 是 XSA/HWH 配置值，非实测板上频率；周期换算仅是 wall-time 名义上界。
- R11 的整体 FAILED 及其原因仍然保留。
- R12 的 PASS 仅为 deadline scope；静态矩阵、109/1000、pending 晚响应和 busy/pending reset 等结论不得扩展。
- DRAIN=1 的 42.262 ms 主机括区间不可替代 DRAIN=`0xFFFFFFFF` 的实测依据。
- “正常总运行包络有 25% 算术余量”不等于精确 HP 延迟或未来最坏情况证明。
