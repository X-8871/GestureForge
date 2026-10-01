# Stage 2A T68 本地无人值守运行说明

更新日期：2026-10-02（南京时间）

## 用途与范围

这份说明介绍如何在本机用 PowerShell 7 启动 T68 Verilator 仿真，让本地进程自行完成编译、仿真、108 个剩余样本的批跑和最终 D9 对照。启动后不需要 AI 操作或周期监视。

该流程只运行数字仿真，不烧录 FPGA，也不执行 Vivado 综合或板上验证。仿真通过不等于 Stage 2A 已冻结；冻结还需要完成项目规定的独立审查、阶段验收和 G5 记录。

## 快速启动当前批次：你启动，本机自行接续

下面的命令用于接续当前已建立的 `batch109_r3`。你只需在本机 **PowerShell 7.6.5** 粘贴并运行一次；仿真协调程序随后在隐藏进程中等待 sample0 终态、接续或等待已有的 108 样本批次，并运行 D9 对照。它是本地 PowerShell 程序，不需要 AI 继续操控。

运行期间保持电脑通电且不要让 Windows 睡眠、注销或重启。启动命令返回后可以关闭这个 PowerShell 窗口；仿真进程独立运行。不要并发启动同一个 RunId：协调程序用互斥锁拒绝并发实例。若上次异常中断且没有终态 summary，可以重新启动同一命令，它会安全等待已有批次或只读复核已有 D9 报告，不会重复派发或覆盖；若已生成终态失败/超时 summary，则保留该 RunId 和证据。诊断后如需重跑，必须新建 RunId 和证据目录。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
$pwsh = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$scriptPath = Join-Path $repoRoot 'verification\run_s2a_t68_unattended_continuation.ps1'
$runId = 'batch109_r3'
$evidenceRoot = Join-Path $repoRoot 'report\evidence\S2A-T68\batch109_r3'
$backendSha256 = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'

if (-not (Test-Path -LiteralPath $pwsh -PathType Leaf)) { throw "找不到 PowerShell 7：$pwsh" }
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw "找不到协调程序：$scriptPath" }
if (-not (Test-Path -LiteralPath $evidenceRoot -PathType Container)) { throw "证据目录不存在：$evidenceRoot" }

$launchId = [Guid]::NewGuid().ToString('N')
$stdoutPath = Join-Path $evidenceRoot "manual_continuation_${launchId}_stdout.txt"
$stderrPath = Join-Path $evidenceRoot "manual_continuation_${launchId}_stderr.txt"
$arguments = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $scriptPath,
    '-EvidenceDirectory', $evidenceRoot,
    '-RunId', $runId,
    '-ExpectedBackendSha256', $backendSha256
)
Start-Process -FilePath $pwsh -ArgumentList $arguments `
    -WorkingDirectory $repoRoot -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
Write-Host "已启动本地后台协调程序。完成结果写入：$(Join-Path $evidenceRoot 'unattended_continuation_batch109_r3.json')" -ForegroundColor Green
Write-Host "启动器标准输出：$stdoutPath"
Write-Host "启动器标准错误：$stderrPath"
```

程序完成后检查 `unattended_continuation_batch109_r3.json` 的 `status`。`PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9` 表示 109 个实际 PL 样本的 D9 对照通过；它仍不等于 Stage 2A 冻结。若该文件尚未出现，说明协调程序尚未写入终态结果，或启动/运行中断；可查看上面打印出的标准输出、标准错误文件路径。出现失败状态时保留整个证据目录，不要覆盖或清理。

这个启动器只接续 `batch109_r3`：sample0 最多等待 24 小时；发现已有 scheduler 时最长等待其终态 72 小时且不会再次派发。要从零新跑完整 109 样本，请使用下文“如何让任务自己运行”的新 RunId 命令块。

相关程序：

- `verification/run_s2a_network_backend_verilator.ps1`：准备并运行一个样本；编译和仿真在同一次调用中执行。
- `verification/run_s2a_t68_batch_verilator.ps1`：确认 sample0 已通过后，并行运行 sample1 至 sample108，最多 8 个 worker。
- `verification/verify_s2a_t68_d9_outputs.py`：对 109 个实际 PL head 导出执行冻结 CPU D9 对照。

本基线固定 RTL SHA-256：`3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154`。runner 会检查该值以及本机绑定的工具链。工具链目录为 `D:\FPGA_S2A_MSYS2_20261001\env`；本机已验证 PowerShell 为 7.6.5，固定 Python 为 3.12.14。

## 如何让任务自己运行

1. 在 Windows 开始菜单打开 **PowerShell 7**。运行 `$PSVersionTable.PSVersion`，本机应显示 `7.6.5`。
2. 复制下方完整命令块，粘贴到 PowerShell 7 后按 Enter。
3. 命令会创建唯一的新证据目录，依次等待 sample0、108 样本批跑和 D9 对照完成。仿真 worker 在隐藏窗口运行，输出写入证据目录。
4. 外层 PowerShell 会一直等待整个流程结束。可以最小化窗口；保持电脑通电、唤醒并连接当前 Windows 用户会话，直到出现最终成功消息。不要关闭 PowerShell 窗口、注销或关机。

命令块会在同一个 T68 证据目录下生成 `manual_时间戳` RunId。运行前会拒绝已存在的同名目录，并核对 backend 哈希、Python、PowerShell 和 Verilator 安装位置。它不会使用 runner 的默认 `run01` 路径。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
Set-Location -LiteralPath $repoRoot

$runId = 'manual_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$evidenceRoot = Join-Path $repoRoot "report\evidence\S2A-T68\$runId"
if (Test-Path -LiteralPath $evidenceRoot) {
    throw "证据目录已存在。请重新生成 RunId 后再启动：$evidenceRoot"
}
[void](New-Item -ItemType Directory -Path $evidenceRoot -ErrorAction Stop)

$expectedBackend = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
$backendPath = Join-Path $repoRoot 'src\s2a_network_backend.sv'
$actualBackend = (Get-FileHash -LiteralPath $backendPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualBackend -cne $expectedBackend) {
    throw "backend 与冻结版本不符。实际 SHA-256：$actualBackend"
}

$pwsh = (Get-Command -Name pwsh -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$pwshVersion = (& $pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()').Trim()
if ($pwshVersion -ne '7.6.5') {
    throw "需要 PowerShell 7.6.5；当前版本是 $pwshVersion"
}

$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "找不到已验证的 Python 解释器：$python"
}
$env:PATH = "$(Split-Path -LiteralPath $python -Parent);$env:PATH"
$resolvedPython = (Get-Command -Name python -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
if ([System.IO.Path]::GetFullPath($resolvedPython) -ine [System.IO.Path]::GetFullPath($python)) {
    throw "worker 默认会调用 python；PATH 当前解析到 $resolvedPython"
}
$pythonVersion = (& $python --version).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Python 启动失败。' }
if ($pythonVersion -cne 'Python 3.12.14') { throw "需要 Python 3.12.14；当前版本是 $pythonVersion" }

$verilator = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe'
if (-not (Test-Path -LiteralPath $verilator -PathType Leaf)) {
    throw "找不到项目固定的 Verilator：$verilator"
}

$sampleRunner = Join-Path $repoRoot 'verification\run_s2a_network_backend_verilator.ps1'
$sampleArgs = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $sampleRunner,
    '-SampleIndex', '0',
    '-RunId', $runId,
    '-EvidenceDirectory', $evidenceRoot,
    '-ExpectedBackendSha256', $expectedBackend,
    '-MaxCycles', '4294967295',
    '-PythonExecutable', $python,
    '-Compile', '-RunSimulation'
)
$sampleProcess = Start-Process -FilePath $pwsh -ArgumentList $sampleArgs `
    -WorkingDirectory $repoRoot -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput (Join-Path $evidenceRoot 'sample0_launcher_stdout.txt') `
    -RedirectStandardError (Join-Path $evidenceRoot 'sample0_launcher_stderr.txt')
if ($sampleProcess.ExitCode -ne 0) {
    throw "sample0 失败，退出码 $($sampleProcess.ExitCode)。保留证据目录并检查失败信息。"
}

$batchRunner = Join-Path $repoRoot 'verification\run_s2a_t68_batch_verilator.ps1'
$batchArgs = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $batchRunner,
    '-EvidenceDirectory', $evidenceRoot,
    '-RunId', $runId,
    '-ExpectedBackendSha256', $expectedBackend,
    '-FirstIndex', '1', '-LastIndex', '108', '-MaxWorkers', '8'
)
$batchProcess = Start-Process -FilePath $pwsh -ArgumentList $batchArgs `
    -WorkingDirectory $repoRoot -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput (Join-Path $evidenceRoot 'batch_launcher_stdout.txt') `
    -RedirectStandardError (Join-Path $evidenceRoot 'batch_launcher_stderr.txt')
if ($batchProcess.ExitCode -ne 0) {
    throw "108 样本调度失败，退出码 $($batchProcess.ExitCode)。保留证据目录。"
}
$batchSummaryPath = Join-Path $evidenceRoot 'batch_dispatch\batch_summary.json'
$batchSummary = Get-Content -LiteralPath $batchSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($batchSummary.status -cne 'PASS_108_RUNNERS') {
    throw "108 样本没有全部通过；batch_summary.status=$($batchSummary.status)"
}

$reportPath = Join-Path $evidenceRoot 'd9_109_sample_report.json'
if (Test-Path -LiteralPath $reportPath) { throw "D9 报告已存在，拒绝覆盖：$reportPath" }
$d9Verifier = Join-Path $repoRoot 'verification\verify_s2a_t68_d9_outputs.py'
& $python -B $d9Verifier --evidence-root $evidenceRoot --run-id $runId --report $reportPath
if ($LASTEXITCODE -ne 0) { throw "109 样本 D9 对照失败，退出码 $LASTEXITCODE。保留证据目录。" }
$d9Report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (($d9Report.status -cne 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9') -or ($d9Report.sample_count -ne 109)) {
    throw "D9 报告状态或样本数不符：status=$($d9Report.status), sample_count=$($d9Report.sample_count)"
}

Write-Host "T68 109 样本仿真和 D9 对照全部通过。" -ForegroundColor Green
Write-Host "证据目录：$evidenceRoot"
Write-Host "D9 报告：$reportPath"
```

## 接续当前已启动的批次

当前 Stage 2A 任务已经把 sample0 分配到以下证据目录。不要对这个 RunId 再启动一次 sample0，也不要覆盖该目录：

```text
D:\FPGA_Competition\report\evidence\S2A-T68\batch109_r3
```

等 sample0 自己结束后，在 PowerShell 7 粘贴下方命令。批跑器会自行检查 sample0 的完整 PASS 记录和冻结输入；如果它尚未通过，批跑器会拒绝派发 worker。通过后批跑器运行 sample1 至 sample108 并写出 `PASS_108_RUNNERS`；随后，此命令块再单独调用 D9 verifier。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
Set-Location -LiteralPath $repoRoot
$runId = 'batch109_r3'
$evidenceRoot = Join-Path $repoRoot 'report\evidence\S2A-T68\batch109_r3'
$expectedBackend = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $evidenceRoot -PathType Container)) { throw "证据目录不存在：$evidenceRoot" }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Python 不存在：$python" }
$env:PATH = "$(Split-Path -LiteralPath $python -Parent);$env:PATH"
$pwsh = (Get-Command -Name pwsh -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source

$batchRunner = Join-Path $repoRoot 'verification\run_s2a_t68_batch_verilator.ps1'
$batchArgs = @(
    '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
    '-File', $batchRunner,
    '-EvidenceDirectory', $evidenceRoot,
    '-RunId', $runId,
    '-ExpectedBackendSha256', $expectedBackend,
    '-FirstIndex', '1', '-LastIndex', '108', '-MaxWorkers', '8'
)
$batchProcess = Start-Process -FilePath $pwsh -ArgumentList $batchArgs `
    -WorkingDirectory $repoRoot -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput (Join-Path $evidenceRoot 'batch_launcher_stdout.txt') `
    -RedirectStandardError (Join-Path $evidenceRoot 'batch_launcher_stderr.txt')
if ($batchProcess.ExitCode -ne 0) {
    throw "108 样本调度失败，退出码 $($batchProcess.ExitCode)。保留证据目录。"
}
$batchSummaryPath = Join-Path $evidenceRoot 'batch_dispatch\batch_summary.json'
$batchSummary = Get-Content -LiteralPath $batchSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($batchSummary.status -cne 'PASS_108_RUNNERS') {
    throw "108 样本没有全部通过；batch_summary.status=$($batchSummary.status)"
}

$reportPath = Join-Path $evidenceRoot 'd9_109_sample_report.json'
if (Test-Path -LiteralPath $reportPath) { throw "D9 报告已存在，拒绝覆盖：$reportPath" }
$d9Verifier = Join-Path $repoRoot 'verification\verify_s2a_t68_d9_outputs.py'
& $python -B $d9Verifier --evidence-root $evidenceRoot --run-id $runId --report $reportPath
if ($LASTEXITCODE -ne 0) { throw "109 样本 D9 对照失败，退出码 $LASTEXITCODE。保留证据目录。" }
$d9Report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (($d9Report.status -cne 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9') -or ($d9Report.sample_count -ne 109)) {
    throw "D9 报告状态或样本数不符：status=$($d9Report.status), sample_count=$($d9Report.sample_count)"
}
Write-Host "T68 109 样本仿真和 D9 对照全部通过。" -ForegroundColor Green
Write-Host "证据目录：$evidenceRoot"
Write-Host "D9 报告：$reportPath"
```

## 如何判定结果

依次确认以下结果，不能只看窗口是否关闭：

1. sample0 runner 退出码为 `0`，其逐层 golden 和 head 导出记录通过。
2. `batch_dispatch\batch_summary.json` 中 `status` 为 `PASS_108_RUNNERS`，代表 sample1 至 sample108 的 runner 都成功。这一项还不是 D9 对照或 Stage 2A 冻结结论。
3. 最终报告 `d9_109_sample_report.json` 中 `status` 为 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9` 且 `sample_count` 为 `109`。
4. 将证据目录和最终 D9 报告交给 Stage 2A 总控，继续完成独立审查及阶段 G4/G5 验收。

## 失败、重跑和证据保留

- 任何步骤退出码非零或状态不是上面的 PASS 值，都按失败处理；不要删改失败目录里的记录或产物。
- 失败后不要在同一证据目录里覆盖重跑。新一轮使用新的时间戳 RunId 和证据目录，从 sample0 开始完整运行，以保证 109 个样本属于同一批冻结输入和同一份 RTL。
- 如果当前 `batch109_r3` 的 sample0 失败，不要在该 RunId 下启动 sample1 至 sample108；保留记录并用新的 RunId 重新跑完整批次。
- 不要把“仿真进程还在运行”当作完成，也不要因长时间没有窗口输出就关闭它。runner 自带周期进展检查和最大 cycle 限制；若它报告失败，保留原始证据以便诊断。
- 这些命令不会自动推送 Git、操作 Vivado、烧录板卡或修改 FPGA 实物。
