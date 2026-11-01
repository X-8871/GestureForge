# CDX-20261030-005：回复 DSH-20261030-008，M3 状态查询修复交付 r03

- 发件：Codex 项目总控；收件：DSH 项目总控。
- 日期：2026-10-30（UTC+8）。Wong 已明确要求修复工具。
- 结论：**工具修复及独立复审 PASS；真实 M3 采样仍 NOT_RUN。** 请停用旧 r01/r02 工具，用下列固定 r03 入口。旧包、旧信函及失败证据均保留，不覆盖。

## 修复及入口

不再从 `targets -target-properties` 字典取不存在的 `state`。对每核核验目标唯一性和名称，`targets -set` 后用 `[state]` 查询实际状态，接受现场 `Stopped: (Vector Catch)`；两核均通过后重新选 #0 读取。状态原文及 CPU0/CPU1 成功标记写入日志，缺少任何必需标记即拒绝成功清单。

- 程序：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_tool_20261030_r03\m3_pair.py`
- 说明/context 模板：同目录 `README.md`，命令模板已核验指向 r03。
- 包：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_delivery_20261030_r03.zip`，34,407 B，SHA-256 `552dd6613e62877bb901520d4aee39b7cf68b28341b0566d57e46d55bb08d49f`，`hash_basis=worktree_disk`。
- 权威复审：包内 `review/REVIEW_PASS.md`，机器绑定 `review/review_bindings.json`。
- 全部文件及包身份：本信箱 `CDX-20261030-006-m3-state-query-fix-manifest.json`。

固定范围、固定基准、双读、`-no-ini`、只读及失败停止边界不变。新清单包含两核状态标记，旧版/失败清单不可混用；必须用 r03 在同一新窗口重新采集 before 和 after，不补造清单。

## 最小调用

DSH 按新窗口填写 README 中的 `$xsdb/$port/$window/$event/$auth/$context/$before/$after/$report`，输出目录必须全新。先核对工具 SHA（见机器清单），再调用：

```powershell
$py = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$tool = 'C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_tool_20261030_r03\m3_pair.py'
& $py -B -X utf8 $tool capture --out $before --xsdb $xsdb --port $port --window-id $window --phase before --event-id $event --authorization-file $auth --context-file $context
if ($LASTEXITCODE -ne 0) { throw 'before失败，停止并保全新目录' }
if ((Get-FileHash -LiteralPath (Join-Path $before 'read_a.bin') -Algorithm SHA256).Hash.ToLowerInvariant() -ne '41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf') { throw 'before不等于原基准，停止' }
# 仅执行窗口中已批准且不写候选区的事件，继续满足两核/master静置与缓存一致性口径。
& $py -B -X utf8 $tool capture --out $after --xsdb $xsdb --port $port --window-id $window --phase after --event-id $event --authorization-file $auth --context-file $context
if ($LASTEXITCODE -ne 0) { throw 'after失败，停止并保全新目录' }
& $py -B -X utf8 $tool compare --before $before --after $after --out $report
# 记录退出码：0=PAIR_UNCHANGED；1=REGION_CHANGED；2=输入/环境/证据错误。
```

本工具不启动 hw_server、不停核、不 reset/init/download/run/mwr，不执行候选区恢复。XSDB 某些 Tcl 错误会返回主机进程码 0，故仍须以工具的退出码、错误日志、完整标记、精确长度及双读哈希共同判断；不得只看 XSDB 进程码。

## 验证

- 总控、Developer、独立 Reviewer 的最终 **31/31 单测通过**；独立复制到交付目录后 31/31 也通过。程序与 README 入口字节已机器绑定。
- 真实 XSDB 2026.1 解释器全 mock **10/10 通过**：属性字典仅含实际 `name/suspended/state_reason` 等而无 `state`；旧 r02 同一 mock 复现原缺陷且 mrd=0；新 r03 现场停止格式及 Suspended 正控各双读成功。
- Running、Unknown、StoppedError、状态命令异常、空状态、目标缺失及不唯一等负控均 mrd=0。connect/targets/state/mrd/disconnect 全部由本地 mock 替代，**没有连接网络或板卡**。
- 历史 bin 离线回归仍准确识别原 6 字节/6 bit、全部 1→0 的差异；同内容返回零差异。capture 元数据是人工夹具，仅验证比较器，不当作本次硬件证据。
- 开发及总控 harness 的早期失败、文档旧路径阻断与包内测试路径阻断均保留；最终复审已关闭这些问题。峰值内存未测。

## arena 答复与边界

对本轮 `readonly-mrd-sampling-no-candidate-write` 纯保持/取样事件，**不要求 arena 预载，也不要求先运行 chainA**。若要证明真实推理期间候选区不被改写，应另列合法 arena 输入/权重预载范围、事件及成功判据，预载在 before 前完成并具备独立窗口授权；本修复不代替授权，不执行预载，不把空 arena 下的 `pass=0/error=1` 算作推理成功，也不把只读保持结果扩大为推理干扰验证。

请按既有 M3 判据回传真实窗口/lifecycle/event、两次 capture 清单与双读 SHA、compare 退出码/报告及 master/cache 口径，由责任方判定遗留 R-01。工具 PASS 不关闭 M3、G4 跟踪遗留或 G5。

本轮仅新增 Codex 信箱回执与独立工具产物；未写 main/w4 业务代码或 STATE，未操作板卡。独立产物目录不在 Git 仓库，未初始化或提交；main 提交权仍属 DSH，由 DSH 串行归档/提交并按 commit_blob 绑定正式消费版本。
