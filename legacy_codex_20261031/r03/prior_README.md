# M3 固定 DDR 区只读成对取样工具

此目录交付给 DSH 在其获准的硬件窗口内使用。本工具只读取候选 DDR 区并离线比较，不负责申请/核验硬件授权，也不启动或结束 `hw_server`。

## 固定范围与行为

- 唯一读取范围：`[0x12000000, 0x12C08000)`，共 12,615,680 字节、3,153,920 个 32 位字。
- `capture` 使用 XSDB 的 `-no-ini` 禁止加载用户初始化脚本，并将 Tcl 文件作为位置参数执行；随后运行只读 Tcl：连接 `127.0.0.1:<port>`，先唯一选择 Cortex-A9 #0/#1，再分别调用 XSDB `[state]` 读取所选核状态。接受 `Stopped`、`Stopped: (Vector Catch)`、`Suspended` 等以 Stopped/Suspended 开头的结果；拒绝 Running、Unknown、空状态、命令异常及目标缺失/不唯一。stdout 留存两个核的原始状态和状态通过标记。测试覆盖真实 `targets -target-properties` 返回字典中没有 `state` 键的结构。
- 有任何核未停止、目标缺失/不唯一、脚本标记不全、XSDB 非零退出、日志含 `error`/`failed`/`failure`、文件长度不符或 A/B SHA 不同，均拒绝产生 `CAPTURED` 清单。全零内容有效，不以非零作为成功条件。
- Tcl 不含 `reset`、`init`、`dow`、`con`、`mwr` 或 `stop`。不清缓存、不做缓存维护、不排空总线、不启停进程。DSH 必须在窗口内先停住两核并排空/静置所有可能写入该区域的 master，再按项目约定处理缓存协议；上下文中的 `masters_quiesced=true` 与 `cache_basis` 是责任方声明，本工具不独立证明这些条件。
- before/after 必须属于同一个 `window_id`、`event_id`、`lifecycle_id`，且目标、filter、bit、ELF、核状态、master 和 cache 身份完全一致。两次取样之间只能发生 DSH 明确记录且不会写入候选区的事件；不得 reset/init/download 或运行任何可能写该区的预处理/RAW 预载。如果中间事件有意写候选区，这不是保持测试；必须另行定义预期并审查，本工具不会自动忽略或恢复写入。
- before 的 SHA-256 必须等于固定 baseline `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf`。baseline 不可由命令行覆盖或通过新取样重建。
- 只读保持测试不需要预载 arena。若另行验证真实推理过程中的保持性，须在 before 采样前按单独批准的窗口预载真实输入/权重，并把此 DDR 写入列入授权与事件记录；本工具和本次工具修复不会执行或授权 arena 预载。
- 所有清单中的文件哈希标注 `hash_basis=worktree_disk`。sidecar SHA 用于发现清单单边/意外改动，不提供签名或来源认证。
- 比较结果只表示取样差异：`PAIR_UNCHANGED` 退出码 0；`REGION_CHANGED` 退出码 1；输入/环境/证据错误退出码 2。任何状态都不自动代表 M3 或阶段验收通过。

## Context JSON

两个 phase 使用同一份、相同内容的 JSON。SHA 字段填部署证据中的真实值；核状态须为现场已知的停止状态。未知时不得虚填。

```json
{
  "window_id": "DSH-approved-window-id",
  "event_id": "one-no-candidate-write-event",
  "lifecycle_id": "same-board-lifecycle-id",
  "target": "Cortex-A9 MPCore #0",
  "filter": "name =~ *Cortex-A9*#0",
  "bit_sha256": "填写64位十六进制SHA256",
  "init_elf_sha256": "填写64位十六进制SHA256",
  "app_elf_sha256": "填写64位十六进制SHA256",
  "cpu0_state": "Stopped",
  "cpu1_state": "Stopped",
  "masters_quiesced": true,
  "cache_basis": "填写窗口批准并执行的缓存/一致性口径"
}
```

`--authorization-file` 仅将给定文件的路径、长度和 SHA-256 记入清单；程序不解析其内容，不宣称已验证批准或授权有效。实际是否可上板由 DSH 按其窗口、项目门禁和资源规则判断。

## 执行模板

使用 Python 3，建议以 `-X utf8` 启动。每个输出目录必须是新目录。下例变量由 DSH 按其实际窗口填写；不要复用旧 RunId/目录。

```powershell
$py = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$tool = 'C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\m3_pair_tool_20261030_r03\m3_pair.py'
$xsdb = 'D:\Xilinx\2026.1\Vitis\bin\xsdb.bat'
$port = 3121
$window = '填写DSH批准的window_id'
$event = '填写同一个不写候选区的event_id'
$auth = '填写对应授权文件绝对路径'
$context = '填写完整的context.json绝对路径'

& $py -B -X utf8 $tool capture --out '填写全新before目录' --xsdb $xsdb --port $port --window-id $window --phase before --event-id $event --authorization-file $auth --context-file $context
# 只在记录的同一硬件生命周期中执行已明确批准且不会写入候选区的事件；不 reset/init/download。
& $py -B -X utf8 $tool capture --out '填写全新after目录' --xsdb $xsdb --port $port --window-id $window --phase after --event-id $event --authorization-file $auth --context-file $context
& $py -B -X utf8 $tool compare --before 'before目录' --after 'after目录' --out '填写全新比较报告目录'
```

XSDB 整体超时默认为 120 秒，可用 `--timeout-seconds N` 调整，允许 `1..600` 秒。脚本不自动重试；任何失败保留该新目录中的 Tcl/日志供复核，失败目录不能当成功输入。

## 输出与限制

成功 capture 写入 `read_a.bin`、`read_b.bin`、固定 Tcl、UTF-8 stdout/stderr 日志、`capture_manifest.json` 与 SHA sidecar。比较报告统计变化字节、变化 bit、1→0/0→1 bit，并列出最多 1,000 个变化字节地址及是否截断。完整变化计数不受地址列表上限影响。

程序只处理文件和 XSDB 子进程，不会清理输出、修改项目仓库、复位/初始化/下载/运行/停核或写候选 DDR。双读一致只说明两个读数相同；读数仍受 XSDB 目标、缓存与一致性口径影响，需结合 DSH 实际窗口证据解释。
