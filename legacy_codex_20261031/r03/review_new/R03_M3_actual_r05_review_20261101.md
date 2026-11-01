# M3 实际 r05 证据独立审查

## 结论

**PASS（限定为 r05 的固定事件、候选区只读双读一致与受控清理）**。r05 的执行记录、launcher、上下文、授权快照、Tcl、原始读回与比较报告相互吻合；restore/event 使用修复后的 XSA 映射。结论不表示真实推理负载期间的 DDR 保持，也不确定历史 6-bit 异常的硬件根因。

本次仅检查 `D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261101_r05` 及其固定输入、已审核心验证代码。r03 未启动失败与 r04 软件映射拒绝不并入本次 r05 结果。

## Run、授权与输入身份

- RunId：`m3_pair_20261101_r05`；lease `Wong-DSH030-M3-r05`；window `Wong-DSH030-M3-20261101-r05`；event `readonly-mrd-sampling-no-candidate-write`；context lifecycle `Wong-POR2-E1-20261101-r01`。
- lease 时段为 2026-11-01 00:08:44–00:17:44（UTC+8），最长 9 分钟；`max_seconds=520`。`authorization.md` 的 SHA 与 lease 声明一致，文件记载了本次独占授权、R04 后新 POR/E1 与本轮只执行一次 init。该文件哈希绑定只确认被审文本身份，不构成签名认证。
- `context.json` SHA 与 lease 一致；13 项 host/tool/input 身份的 pre/post 路径、SHA、字节数逐项一致。两次 host query 均 exit 0，监听列表均为空。两次快照分别记录 4 个、2 个 `vivado.exe` 进程；没有因本次收尾而终止这些进程。
- `init/init.tcl` SHA 为 `49bb18dd919e5103394a54a5714ad89060181615b0a62fa015320390ac028120`。实际记录 `init_count_this_por=1`，init result 与 launcher exit 均为 0，stdout 含 `M3_SINGLE_INIT_COMPLETED`。脚本仅有一次 `loadhw`、一次固定 init ELF `dow`、一次 `con` 和 2500 ms 后 stop，无 `rst`/`reset` 命令。固定 init ELF 与 context 的 SHA 一致。

## Tcl、执行顺序与 launcher

r05 的 setup/restore/event/close Tcl 与冻结模板逐字节一致。restore 与 event 都在 connect 后唯一选择 Cortex-A9 #0，再执行固定 XSA 的 `loadhw`，映射为 `{0x00000000 0x7FFFFFFF}`，与 setup 相同。

- setup 实际 exit 0，记录 `M3_SETUP_OK_APP_NOT_RUN`；日志中两核为 Stopped (Suspended)，CSR ID 为 1395802704（0x53324250）、status 为 1024（idle mask 命中为 0）。固定 bitstream 已编程，app 只 `dow`，没有 `con`。
- restore 实际 exit 0，记录 `M3_RESTORED_FROM_ORIGINAL_SNAPSHOT`；只将既有快照写回 `0x12000000`，3153920 words。固定快照大小为 12615680 bytes，SHA 为比较要求的 baseline。
- event 实际 exit 0，记录 `M3_READONLY_EVENT_OK`；两核状态通过，连续三组 CSR/GT `mrd` 返回预期 ID 与 idle 状态。event Tcl 无 `mwr`、`fpga`、`dow`、`con`、`rst` 或 `reset`。
- before/event/after/close 的顺序与 `orchestration_result.json` 一致，所有步骤 exit 0。所有单步 launcher 均为官方 `D:\Xilinx\2026.1\Vitis\bin\xsdb.bat` 经 `cmd.exe /d /q /v:off /s /c` 和 `-no-ini -eval source {...}` 执行；测试夹具标记为 false，单步 root exit 0、未超时、清理成功。官方 bat SHA 与 pre/post 工具快照及 before/after v2 launcher 记录一致。

## 原始捕获与比较

使用只读 `m3_pair.verify_capture()` 分别验证 before/after；两次均通过 v2 manifest、SHA 旁证、raw log marker/error、launcher execution/plan、batch 快照、context 与 authorization 快照核验。四份 `read_a.bin` / `read_b.bin` 每份均 12615680 bytes，SHA 都为 `41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf`，实际 bytes 两两相等。

离线 pair report 的 SHA 与 `.sha256` 旁证相符；只读 `verify_manifest_checksum()` 返回成功。报告为 `PAIR_UNCHANGED`、`hardware_launcher_v2_bound=true`，全区 `[0x12000000,0x12C08000)` 共 12615680 bytes，changed bytes/bits 均为 0，before/after 都满足固定 baseline。`orchestration_result.json` 记录 compare exit 0，after 时间晚于 before。

## 收尾与解释边界

close 的单步 Tcl/launcher exit 0，marker `M3_CLOSE_CORES_STOPPED`，两核均为 Stopped (Suspended)。`server_close.json` 记录 `normal_stop_requested=true`、`close_status=CLOSED_BY_REQUEST`、`cleanup_status=CLEANUP_CONFIRMED`、`thread_joined=true`、Job 清理后 ActiveProcesses=0/PID 列表为空、root wait=0；holder 运行 505.125 秒（RESULT 四舍五入为 506 秒），未越过 lease。

同时如实记录：嵌套 `server/job/execution.json` 的 root exit code 为 **124**，launcher 状态为 `NONZERO_EXIT`，`timed_out=false`、`errors=[]`。核对的 `job_launcher.py` 显示受控 `TerminateJobObject` 使用退出码 124；故这表示收到 stop 后受控 Job 终止 server 树，不是 server 以 exit 0 正常返回。清理凭据通过，但不把嵌套 server 进程描述成 exit 0。host post 快照监听为空，close 状态为 CLOSED_BY_REQUEST。

本次证明的是 POR 后配置、恢复固定 baseline 后，在 `readonly-mrd-sampling-no-candidate-write` 静止事件期间的固定区域双读未发现变化。它不覆盖真实推理活动期间保持性，不证明 cache/coherency 机制，也未定历史 6-bit 异常根因。最终权威提交仍需 DSH 串行提交后按 `commit_blob` 运行 strict。

## 关键文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `RESULT.json` | `7d8b96bc6e7e3d1a3c79c5314b67ebf29b1189a8abdf883fc79f05cfcd7f60f4` |
| `orchestration_result.json` | `171110320c3d5bfae91bb89254c3b79e7e212076cb70433253a088d2d1dc7851` |
| `lease.json` | `adfe53fe84da51c215613388a07c0402f1c9473788ce99b9ef690ab3865fdceb` |
| `authorization.md` | `dfeb18d19ad929763c642ee5a006aa52442fa8d9d6c896198d34ef3c3cb76a07` |
| `context.json` | `ce9c79d489dc9ff823c13ceadf3920fb8c2b0b9b994baf793e0c60e8d578d2d6` |
| `capture_before/capture_manifest.json` | `6fe8954b576f7c1dadaecd14f441c3d38db8e02eda48806dc390ab86f579d556` |
| `capture_after/capture_manifest.json` | `6daeb02ab5907e761add10ec6f6816ad5925ec6edf9b015246573c904654cc82` |
| `comparison/pair_report.json` | `769933f040eec133f159d681170e9e3784ef48b59ecb1f589568c4f15b6524c9` |
| `server/server_start.json` | `a110ec84c4a8d9b2058e81fcc153a4980d5707fb218468f1d6f44f230a21a0d1` |
| `server/server_close.json` | `1f038da22d4078edf4d4442cae91a0f447f510595531fcaa5b4b6387bdd4cfea` |
| `server/job/execution.json` | `2cd95b8f9bff4801997b19e3a91a4b8c61c449c380037e2e3ca5739e3cd11ec3` |

## 核验命令与限制

- PowerShell 只读 SHA/JSON/Tcl/时间线核对：exit 0。
- 桌面 Python `-B -X utf8 -c` 调用 `m3_pair.verify_capture()` 验证 before/after：exit 0；调用 `verify_manifest_checksum()` 验证 pair report：exit 0。没有重跑 compare，没有创建或覆盖 r05 文件。
- 未启动 XSDB、hw_server、Vivado、socket 或板卡；未改源、r05 证据或 Git。