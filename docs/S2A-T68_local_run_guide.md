# Stage 2A T68 本地无人值守运行说明

更新日期：2026-10-02（南京时间）

## 用途与范围

这份说明介绍如何在本机用 PowerShell 7 启动 T68 Verilator 仿真，让本地进程自行完成编译、仿真、108 个剩余样本的批跑和最终 D9 对照。启动后不需要 AI 操作或周期监视。

该流程只运行数字仿真，不烧录 FPGA，也不执行 Vivado 综合或板上验证。仿真通过不等于 Stage 2A 已冻结；冻结还需要完成项目规定的独立审查、阶段验收和 G5 记录。

## 全新无人值守启动（推荐）

旧 RunId `batch109_r3` 已终止：sample0 的 RTL 仿真实际完成 38 层且 0 mismatch，但 Windows CRLF 摘要被旧 runner 误拒；协调器随后又在派发其余样本前遇到 Python 多候选解析错误。该目录是失败证据，必须保留，不要用同一 RunId 重跑。修复已提交；下面命令会创建一个新的 RunId 和证据目录。

在 **PowerShell 7.6.5** 粘贴并运行一次。命令会隐藏启动 sample0 runner 和无人值守协调器；协调器等待 sample0 写出终态记录后，自动运行最多 8 个 worker 的剩余 108 个样本并做 D9 对照。启动命令返回后不需要 AI 操作或周期监视，也可以关闭启动用的 PowerShell 窗口。保持电脑通电、唤醒并保持 Windows 用户会话登录；不要睡眠、注销或重启。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
Set-Location -LiteralPath $repoRoot
$runId = 'manual_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$evidenceParent = Join-Path $repoRoot 'report\evidence\S2A-T68'
$evidenceRoot = Join-Path $evidenceParent $runId
$pwsh = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$backendSha256 = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
$sampleRunner = Join-Path $repoRoot 'verification\run_s2a_network_backend_verilator.ps1'
$coordinator = Join-Path $repoRoot 'verification\run_s2a_t68_unattended_continuation.ps1'
$backendPath = Join-Path $repoRoot 'src\s2a_network_backend.sv'

if (-not (Test-Path -LiteralPath $evidenceParent -PathType Container)) { throw "证据父目录不存在：$evidenceParent" }
if (Test-Path -LiteralPath $evidenceRoot) { throw "新 RunId 目录已存在；请稍后重新生成：$evidenceRoot" }
foreach ($path in @($pwsh, $python, $sampleRunner, $coordinator, $backendPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "必需文件不存在：$path" }
}
$pwshVersion = (& $pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()').Trim()
if ($pwshVersion -cne '7.6.5') { throw "需要 PowerShell 7.6.5；当前是 $pwshVersion" }
$pythonVersion = (& $python --version).Trim()
if ($LASTEXITCODE -ne 0 -or $pythonVersion -cne 'Python 3.12.14') { throw "固定 Python 版本不符：$pythonVersion" }
$actualBackendSha256 = (Get-FileHash -LiteralPath $backendPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualBackendSha256 -cne $backendSha256) { throw "backend SHA-256 不符：$actualBackendSha256" }
[void](New-Item -ItemType Directory -Path $evidenceRoot -ErrorAction Stop)

$sampleStdout = Join-Path $evidenceRoot 'manual_sample0_stdout.txt'
$sampleStderr = Join-Path $evidenceRoot 'manual_sample0_stderr.txt'
$sampleArguments = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $sampleRunner,
    '-SampleIndex', '0', '-RunId', $runId,
    '-EvidenceDirectory', $evidenceRoot,
    '-ExpectedBackendSha256', $backendSha256,
    '-MaxCycles', '4294967295',
    '-PythonExecutable', $python,
    '-Compile', '-RunSimulation'
)
$sampleProcess = Start-Process -FilePath $pwsh -ArgumentList $sampleArguments `
    -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $sampleStdout -RedirectStandardError $sampleStderr
if ($null -eq $sampleProcess) { throw 'sample0 runner 未能启动。' }

$coordinatorStdout = Join-Path $evidenceRoot 'manual_coordinator_stdout.txt'
$coordinatorStderr = Join-Path $evidenceRoot 'manual_coordinator_stderr.txt'
$coordinatorArguments = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $coordinator,
    '-EvidenceDirectory', $evidenceRoot,
    '-RunId', $runId,
    '-ExpectedBackendSha256', $backendSha256
)
try {
    $coordinatorProcess = Start-Process -FilePath $pwsh -ArgumentList $coordinatorArguments `
        -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $coordinatorStdout -RedirectStandardError $coordinatorStderr
} catch {
    throw "sample0 已启动 PID=$($sampleProcess.Id)，未重启它。协调器启动失败；保留目录并查看 $coordinatorStderr。原错误：$($_.Exception.Message)"
}
if ($null -eq $coordinatorProcess) { throw "sample0 已启动 PID=$($sampleProcess.Id)；协调器未能启动。保留目录。" }

Write-Host "已启动无人值守 2A 仿真。RunId：$runId" -ForegroundColor Green
Write-Host "sample0 PID：$($sampleProcess.Id)；协调器 PID：$($coordinatorProcess.Id)"
$summaryPath = Join-Path $evidenceRoot "unattended_continuation_${runId}.json"
Write-Host "最终协调结果：$summaryPath"
Write-Host "证据目录：$evidenceRoot"
Write-Host "如需稍后核验，日志均保存在该目录；不要覆盖或清理失败结果。"
```

程序完成后，协调器报告 `status=PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9` 才代表 109 个 PL 样本的 D9 对照通过；它仍不表示 G4/G5 或 Stage 2A 已冻结。失败或超时状态都保留原证据目录；需要重跑时用新的 RunId 从 sample0 完整开始。

相关程序：

- `verification/run_s2a_network_backend_verilator.ps1`：准备并运行一个样本；编译和仿真在同一次调用中执行。
- `verification/run_s2a_t68_batch_verilator.ps1`：确认 sample0 已通过后，并行运行 sample1 至 sample108，最多 8 个 worker。
- `verification/verify_s2a_t68_d9_outputs.py`：对 109 个实际 PL head 导出执行冻结 CPU D9 对照。
- `verification/verify_s2a_t68_snapshot_git_binding.py`：在 D9 通过后，将 109 个编译源码快照映射到固定静态源码闭包和冻结 Git tree；输出只说明源码映射核验结果。

本基线固定 RTL SHA-256：`3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154`。runner 会检查该值以及本机绑定的工具链。工具链目录为 `D:\FPGA_S2A_MSYS2_20261001\env`；本机已验证 PowerShell 为 7.6.5，固定 Python 为 3.12.14。

## D9 通过后核验源码快照映射

无人值守协调器负责 sample0、108 样本批跑及 D9；109 样本 D9 通过后，再运行以下命令核对每个样本的 compile-source snapshot 是否映射到固定源码闭包和 Git tree。先把 `$runId` 改成启动时屏幕打印的 RunId。若报告已存在，工具会拒绝覆盖。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
$runId = 'manual_替换为启动时的RunId'
$evidenceRoot = Join-Path $repoRoot "report\evidence\S2A-T68\$runId"
$summaryPath = Join-Path $evidenceRoot "unattended_continuation_${runId}.json"
if (-not (Test-Path -LiteralPath $summaryPath -PathType Leaf)) { throw "协调结果不存在：$summaryPath" }
$summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$pass = 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9'
if (($summary.status -cne $pass) -or ($summary.d9.passed -ne $true) -or
    ($summary.d9.report_status -cne $pass) -or ($summary.d9.sample_count -ne 109)) {
    throw '协调器未确认 109 样本 D9 PASS；保留证据并停止。'
}
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$snapshotVerifier = Join-Path $repoRoot 'verification\verify_s2a_t68_snapshot_git_binding.py'
$snapshotReport = Join-Path $evidenceRoot "source_snapshot_git_binding_${runId}.json"
if (Test-Path -LiteralPath $snapshotReport) { throw "源码映射报告已存在，拒绝覆盖：$snapshotReport" }
& $python -B $snapshotVerifier --evidence-root $evidenceRoot --run-id $runId
if ($LASTEXITCODE -ne 0) { throw "源码映射失败，退出码 $LASTEXITCODE；保留证据。" }
$mapping = Get-Content -LiteralPath $snapshotReport -Raw -Encoding UTF8 | ConvertFrom-Json
if (($mapping.status -cne 'PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE') -or ($mapping.sample_count -ne 109)) {
    throw "源码映射结果不符：status=$($mapping.status), sample_count=$($mapping.sample_count)"
}
Write-Host "源码快照映射通过：$snapshotReport"
```

源码映射 PASS 只证明快照与固定源码闭包/Git tree 的映射关系；完成 G4/G5、阶段记录和独立验收后，才能冻结 Stage 2A。

## 旧批次 batch109_r3

`report\evidence\S2A-T68\batch109_r3` 是失败证据，必须保留。sample0 原始 RTL 模拟确实跑完，但旧 runner 未接受 CRLF 摘要；旧协调器也未派发其余 108 个样本。不要再用 `batch109_r3` 启动协调器或覆盖该目录。请按上面的“全新无人值守启动”创建新 RunId，从 sample0 开始运行完整 109 个样本。

## 如何判定结果

依次确认以下结果，不能只看窗口是否关闭：

1. sample0 runner 退出码为 `0`，其逐层 golden 和 head 导出记录通过。
2. `batch_dispatch\batch_summary.json` 中 `status` 为 `PASS_108_RUNNERS`，代表 sample1 至 sample108 的 runner 都成功。这一项还不是 D9 对照或 Stage 2A 冻结结论。
3. 最终报告 `d9_109_sample_report.json` 中 `status` 为 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9` 且 `sample_count` 为 `109`。
4. `source_snapshot_git_binding_<RunId>.json` 中 `status` 为 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE` 且 `sample_count` 为 `109`。此结果只证明 109 个编译源码快照映射到固定静态源码闭包和冻结 Git tree；不证明运行完成、D9、G4/G5 或阶段通过。若报告已存在，检查器会拒绝覆盖并保留原报告。
5. 将证据目录、D9 报告和源码映射报告交给 Stage 2A 总控，继续完成独立审查及阶段 G4/G5 验收。

## 失败、重跑和证据保留

- 任何步骤退出码非零或状态不是上面的 PASS 值，都按失败处理；不要删改失败目录里的记录或产物。
- 失败后不要在同一证据目录里覆盖重跑。新一轮使用新的时间戳 RunId 和证据目录，从 sample0 开始完整运行，以保证 109 个样本属于同一批冻结输入和同一份 RTL。
- 如果任何 RunId 的 sample0 失败，不要启动其余样本；保留终态记录，使用新的 RunId 从 sample0 重跑完整批次。
- 不要把“仿真进程还在运行”当作完成，也不要因长时间没有窗口输出就关闭它。runner 自带周期进展检查和最大 cycle 限制；若它报告失败，保留原始证据以便诊断。
- 这些命令不会自动推送 Git、操作 Vivado、烧录板卡或修改 FPGA 实物。
