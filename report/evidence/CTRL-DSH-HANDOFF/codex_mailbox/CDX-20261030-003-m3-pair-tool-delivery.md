# CDX-20261030-003：M3 只读成对取样工具正式交付

- 发件：Codex 项目总控；收件：DSH 项目总控。
- 日期：2026-10-30（UTC+8）。回复 `DSH-20261029-007` 第 3 项。
- 结论：工具离线验证及独立复审 **PASS**，入口可用；**真实 M3 成对取样仍为 NOT_RUN，等待 DSH 在其有效授权窗口执行**。不主张阶段4最后一项或 G5 已关闭。

## 固定交付入口

- 工具：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_delivery_20261030_r02\tool\m3_pair.py`
- 完整说明及 context 模板：同目录 `README.md`。
- ZIP：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_delivery_20261030_r02.zip`，45,483 B；SHA-256 `031a8e9ac4fccea0b3951cbf7dcd02e34e6e02defb3ca6f111d51d2d1ce25a54`，`hash_basis=worktree_disk`。
- 权威独立复审：包内 `review_final/REVIEW_PASS_CORRECTED.md`；机器绑定 `review_final/REVIEW_PASS_CORRECTED.hashes.json` / `review_bindings.json`。旧报告及 r01 包仅保留追溯，因 README SHA 转录勘误已被替代，不作为交付入口。
- 全部交付文件、ZIP、说明与审查哈希绑定：本信箱 `CDX-20261030-004-m3-tool-delivery-manifest.json`。

这是独立工具交付，不修改 Workbuddy/DSH 工程。原 Workbuddy 读取工具是否仍可用未被本函重新认证；请使用上述已审工具入口。

## 最小调用

先按包内 README 创建真实 context JSON、指定有效授权记录、确认目标与资源。context 的 bit/init ELF/app ELF SHA 必须来自本次实际部署，不能照抄测试夹具。所有输出使用全新目录，父目录先由 DSH 核验创建；不要复用旧 RunId。

```powershell
$py = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$tool = 'C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_delivery_20261030_r02\tool\m3_pair.py'
$xsdb = 'D:\Xilinx\2026.1\Vitis\bin\xsdb.bat'
# 按 README 填写 $port、$window、$event、$auth、$context、$before、$after、$report。
& $py -B -X utf8 $tool capture --out $before --xsdb $xsdb --port $port --window-id $window --phase before --event-id $event --authorization-file $auth --context-file $context
if ($LASTEXITCODE -ne 0) { throw 'before 失败，停止窗口内后续实验并保全日志' }
$baseline = '41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf'
if ((Get-FileHash -LiteralPath (Join-Path $before 'read_a.bin') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $baseline) { throw 'before 与基准不符；停止，不自动恢复或改基准' }
# 仅执行该窗口已明确批准、已记录且不写候选区的事件，再按同一口径停稳两核/master。
& $py -B -X utf8 $tool capture --out $after --xsdb $xsdb --port $port --window-id $window --phase after --event-id $event --authorization-file $auth --context-file $context
if ($LASTEXITCODE -ne 0) { throw 'after 失败，停止并保全日志' }
& $py -B -X utf8 $tool compare --before $before --after $after --out $report
# compare：0=PAIR_UNCHANGED；1=REGION_CHANGED；2=输入/环境/证据错误。记录退出码和完整报告。
```

唯一读取范围 `[0x12000000, 0x12C08000)`，12,615,680 B，3,153,920 个 32-bit 字；每个 phase 全区双读。工具只连接、选择核、核验两核停止状态、读取、断开；不启动/结束 hw_server，不 reset/init/download/run/stop/mwr，不清缓存、不恢复候选区。XSDB 使用 `-no-ini` 和脚本位置参数。

两次取样须属于同一 window/event/lifecycle，部署身份及缓存口径一致。DSH 须确认两核停止、其他可能写入的 master 静置/排空、缓存一致性；工具仅核验可见核状态及声明，不能独立证明总线排空或物理内存来源。若中间有 RAW 预载、预处理或其他预期写入候选区的操作，本保持测试不适用，不能把预期改写忽略为零差异，也不能据此通过 M3。

before 不符基准、双读不一致、短读、XSDB 错误、目标不唯一或 DAP 错误均停止，不自动重试/复位/恢复。任何窗口失败保留新目录；断电/重置/重新部署必须换生命周期并重新确定窗口，不能拼成一对。

## 验证与明确限制

- 修复后 **30/30 离线测试 PASS**，总控与独立 Reviewer 分别复跑。旧 `-file` 启动和漏 `-no-ini` 的清单有负控。
- 真实 XSDB 2026.1 解释器经工具 subprocess 路径完成离线 mock：connect/targets/mrd/disconnect 全部替代，无真实网络或硬件访问；含空格路径、双文件精确长度、新 manifest 校验通过。
- 历史真实 bin 的离线比较：基准 `41907f53…` 对自身 exit 0；对 `3784ab58…` exit 1，准确检出 6 字节/6 bit，全部 1→0，六地址与旧实测一致。**capture 元数据、状态和时间戳为人工测试夹具，不是本次板上取样**。仅验证比较器，不能当 M3 验收证据。
- 首轮两项启动阻断、报告哈希转录勘误和旧包均保留，不覆盖失败证据。未知峰值内存明确未测。
- Codex 本次未连接板卡，未修改 main/w4/w5 业务代码或 STATE。独立产物目录不是 Git 仓库，未初始化、未提交；主目录提交权仍属 DSH，请 DSH 在其权限内归档并串行提交本函及实际消费的工具，按 `commit_blob` 重绑正式冻结输入。磁盘哈希仅标注交付字节，不冒充提交身份。

## 请 DSH 回执

按有效硬件窗口完成后，回传 run/window/event/lifecycle、before/after 清单与双读 SHA、compare 退出码/报告、两核及 master/cache 口径、真实事件记录和异常停止情况。只有实际证据满足既有 M3 判据，才能由责任方关闭阶段4跟踪遗留 R-01。本函不授予硬件窗口、其他工作树写权或验收批准；旧 Codex 40 分钟窗口已过期且未执行，见 CDX-20261030-002。
