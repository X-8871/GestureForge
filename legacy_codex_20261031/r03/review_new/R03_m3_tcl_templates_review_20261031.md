# R-03 独立审查：M3 r02 Tcl 模板与 capture/compare 边界（2026-10-31）

## 结论

**CHANGES_REQUIRED。** 四份 Tcl 的单步硬件动作在限定模板范围内符合已批准流程；capture/compare 固定范围和双读校验也正确。唯一阻断是恢复步骤仅靠注释要求在 `before` 前执行，代码和捕获比较链没有阻止 `before` 后再次恢复，因此可能掩盖事件期间的变化。

## 冻结核验

以下内容只读读取并计算 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `setup/setup.tcl` | `061b6d77e7a787f0dc3f7031bb732696ce484f7afe4b7bb25c2c4d57f600ca3b` |
| `restore/restore.tcl` | `528f03907ff808540e2e1f03ed6f2f530d4241f3b1360f8db476915aa8271762` |
| `event/event.tcl` | `ddeed7b75b450d7683ef0cf560ca4ed8f2121a8678f358919da28422901617dc` |
| `close/close.tcl` | `00f308d5267d3dc68359dc0d152edff16c6b5d61e645ce024e5d975d18caad91` |
| `port.txt` | `bfe360dbd8328aee017eb49fd726e7af05062339c08ffa7d934aa500a48b618e` |
| `r03/m3_pair.py` | `475805761decab570d7b5da8b5d2fd762496adc8a0beb2b63625c387b94f61c2` |

指定的新报告路径创建前验证为不存在。当前 `port.txt` 内容是 `3121` 加 LF；它只是允许端口的配置，不证明该端口空闲或已获本轮使用授权。

## Tcl 与采样实现

- `setup.tcl`（第 2–8、36–39 行）按唯一目标数及预期 A9/xc7z020 名称选择目标；`loadhw` 后重新选核并核验状态。每核初态若为 Running，字典只允许一次 `stop`，随后读回状态；其他状态失败关闭。PS 配置顺序为 0xA、固定 2B bit、0xF；随后检查 CSR ID `0x53324250` 与 status mask `0x3107` 为 idle。仅 `dow` 固定 chainA ELF，没有 `con`。文件中没有执行 `init` 或 `reset` 命令，脚本结尾会把主体或 disconnect 错误转为 exit 2。
- `restore.tcl`（第 18–25 行）要求两核已停并通过 CSR idle 后，将固定旧快照写到 `0x12000000`，计数 3,153,920 words。按工具固定区间 `[0x12000000, 0x12C08000)` 计算，该 count 正好是全区字数（12,615,680 bytes / 4）；没有建立新基准或写其他地址。
- `event.tcl` 只读两核 state、CSR ID/status 与 Global Timer，三次采样之间等待 200ms；没有 `mwr`、stop、reset、init、dow 或 fpga 操作。`close.tcl` 每核至多执行一次必要 `stop`，必须读回 Stopped/Suspended；主体失败或 disconnect 失败均以 exit 2 结束。
- 四个脚本均从本 RunId 上级 `port.txt` 读取端口，仅接受 3121/3122，使用 `connect -url` 参数而非拼接 Tcl 命令；所有 Tcl 路径和目标选择均固定。仅 `setup` 含获准的部署与 PS 配置写入；restore 仅写旧快照；event 只读；close 只停止目标核。
- `m3_pair.py` 常量固定采样区 `[0x12000000,0x12C08000)`；capture Tcl 先确认双核 Stopped/Suspended，再连续两次 `mrd -bin` 各读全区。程序检查两个文件字节数均为 12,615,680 且同阶段 SHA-256 相同。verify 阶段再核相位、范围、长度、A/B 哈希、日志 marker/error 与 manifest/原始输出绑定。
- compare 要求 before/after 目录不同、相同 window/event/lifecycle/context 身份、after 时间晚于 before、before SHA 等于固定 baseline `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf`，再逐字节比较全区。v2 会校验固定官方 xsdb.bat、同一 bat 哈希、真实 Job/日志/cleanup 元数据。v1 仍允许作历史离线比较，输出明确 `hardware_launcher_v2_bound=false`/legacy 范围；不得把它计作本轮板证据。`masters_quiesced=true` 是已哈希 context 中的外部事实声明，capture Tcl 本身只现场核双核状态，不独立枚举所有 DMA master。

## CHANGES_REQUIRED

**恢复顺序目前没有程序门禁。** `restore.tcl` 注释（第 10 行）写明只在 before 之前使用，但脚本不检查 `capture_before`、guard 或任何步骤状态。被审的 capture/compare 边界也不要求成功 restore 记录，且只要求 `after` 晚于 `before`。因此运行者可以先取得 before，再调用 restore，最后取得 after；若恢复成功，compare 可能看到原 baseline 并返回 `PAIR_UNCHANGED`，掩盖 restore 前的内存变化。

影响是可能把错误顺序造成的数据恢复误报为本次事件期间未变化。关闭条件：在新 R03+ RunId 的执行门禁中实现单调步骤状态；before capture 必须要求已成功且时间早于 before 的 restore receipt；任何 before capture/guard 已存在时拒绝 restore。加入两个隔离 mock 负控：缺 restore receipt 时拒绝 before、已有 before 后拒绝 restore。保持四份 frozen Tcl 原文不变。

## 时限与安全边界

前次已审的 lease/job/client 包装器把租约限制为至多 540 秒、Job 执行预算至多 520 秒并为收尾预留 10 秒；单步上限 setup/restore/event/close 为 90/130/20/20 秒，两次 capture 各最多 120 秒并扣收尾余量，合计最高 500 秒，客户端核验与 capture 均受同一 Job/lease 预算限制。此处只确认 Tcl 模板的单步边界，没有重跑该 wrapper 测试或实物验证。

## 只读验证与边界

- 对上述 6 个精确文件执行 `Get-FileHash -Algorithm SHA256`：exit 0；Tcl、m3_pair 相关片段与调用序列只读检查：exit 0。
- 未执行 Tcl，未调用真实 socket、XSDB/Vivado/hw_server 或硬件；未修改/暂存/提交源文件。
- 本 PASS/CHANGES_REQUIRED 判断只涉及模板实现范围。当前没有新 OFFER；本审查不构成启动授权或 ready 声明。