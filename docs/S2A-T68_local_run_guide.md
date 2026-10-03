# Stage 2A T68 本地无人值守运行说明

更新日期：2026-10-03（南京时间）

## 用途与范围

这份说明介绍如何在本机用 PowerShell 7 启动 T68 Verilator 仿真，让本地进程自行完成编译、仿真、108 个剩余样本的批跑和最终 D9 对照。启动后不需要 AI 操作或周期监视。

该流程只运行数字仿真，不烧录 FPGA，也不执行 Vivado 综合或板上验证。仿真通过不等于 Stage 2A 已冻结；冻结还需要完成项目规定的独立审查、阶段验收和 G5 记录。

## 全新无人值守启动（推荐）

旧 RunId `batch109_r3` 已终止：sample0 的 RTL 仿真实际完成 38 层且 0 mismatch，但 Windows CRLF 摘要被旧 runner 误拒；协调器随后又在派发其余样本前遇到 Python 多候选解析错误。该目录是失败证据，必须保留，不要用同一 RunId 重跑。修复已提交；下面命令会创建一个新的 RunId 和证据目录。

从 Windows 开始菜单打开独立的 **PowerShell 7.6.5** 窗口，在该窗口粘贴并运行一次；不要从 Codex 的工具执行器启动。原手动批次 `manual_20261002_140325` 已停止：sample0 通过，但调度器 CRLF 判断和协调器空日志处理失败；2026-10-03 修复恢复尝试又发现固定 Python 缺少 cv2，前 8 个任务在输入准备阶段退出。所有旧记录保留。新启动必须通过下面的 NumPy/OpenCV 预检，使用新的 RunId。Codex 工具启动的进程在关闭应用后是否存活，尚无官方保证；独立 Windows 窗口启动可避免将运行生命周期交给 Codex。命令会隐藏启动 sample0 runner 和无人值守协调器；协调器等待 sample0 写出终态记录后，自动运行最多 8 个 worker 的剩余 108 个样本并做 D9 对照。启动命令返回后不需要 AI 操作或周期监视，也可以关闭启动用的 PowerShell 窗口。保持电脑通电、唤醒并保持 Windows 用户会话登录；不要睡眠、注销或重启。

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\FPGA_Competition'
Set-Location -LiteralPath $repoRoot
$runId = 'manual_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$evidenceParent = Join-Path $repoRoot 'report\evidence\S2A-T68'
$evidenceRoot = Join-Path $evidenceParent $runId
$pwsh = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$dependencyRoot = 'C:\Users\22061\AppData\Local\Programs\Python\Python312\Lib\site-packages'
if (-not (Test-Path -LiteralPath $dependencyRoot -PathType Container)) { throw "冻结依赖目录不存在：$dependencyRoot" }
$env:PYTHONPATH = (Get-Item -LiteralPath $dependencyRoot).FullName
$dependencyVersions = (& $python -B -c 'import numpy,cv2; print(numpy.__version__ + "|" + cv2.__version__)').Trim()
if ($LASTEXITCODE -ne 0 -or $dependencyVersions -cne '2.4.6|4.13.0') { throw '固定 Python 的 NumPy/OpenCV 预检失败；停止启动。' }
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

## Stage 2A 验收准备与终态门

截至 2026-10-02，本节是验收准备步骤，实际 109 样本结果、runtime 源码映射、干净副本恢复/重验及最终 G4/G5 独立审查均为 `PENDING`。前面的启动确认、T25 CPU `COMPLETE`、静态实施资格审查 `PASS` 均不改变这些状态。当前程序自行运行；本节命令在对应前提满足后执行，准备阶段不轮询当前批次、不读取当前运行日志。

1. **整网结果门**：待无人值守脚本终止且协调结果符合前面的 PASS 检查，逐样本核对 `runs/sample_000/<RunId>` 至 `runs/sample_108/<RunId>` 的仿真记录、`result_summary.txt` 和 head 导出。必须是同一个 RunId 的精确 0..108 样本集合，各样本完整 38 层、`status=PASS_LAYERWISE_EXACT_GOLDEN`、`feature_write_bytes=11382150 mismatches=0`、`head13_bytes=5070 head26_bytes=20280`。仅一个 sample0 通过不能签收整网。
2. **实际 head/D9 门**：保留并核验 `d9_109_sample_report.json`，要求 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`、109 样本。验证器会核对 T01/T25/T29 冻结绑定、实际 head 字节、类别/顺序/框数等离散字段一致、score 与坐标绝对误差不超过 `1e-6`，并从 T25 重建 CPU D9 作 canonical 比较。缺任何样本、头部长度/哈希或冻结绑定不符、NaN/Inf、误差超限，立即停止验收并保留原报告。
3. **版本门**：按上面的“D9 通过后核验源码快照映射”原命令生成独占的新报告。要求 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE`、109 样本；固定闭包为 `report/evidence/S2A-T68/static_source_closure_20261002.json`，SHA-256 为 `93df3e1947e618f72324444268640382416dd6d631b4ae260e0c49f07fc51b8f`，对应源码基线 `a1298dbc4b41eb9ac54caca77e18fd00bee30538` / tree `dbac6be3f860e1ade64eaf55add4e1915ea74545`。记录最终归档提交与此源码基线的关系；后来只改文档的提交不自动成为本批次编译源码版本。映射失败不得改写快照或把另批样本拼入。
4. **已有结果合并门**：逐项保留 T02/T08/T10–T21 的原始定名 JSON 及其引用文件，准确入口见 `report/stage2a_acceptance_preparation_20261002.json` 的证据目录；审计确认不存在 T69 目录，不能用 T69 标签当作归档位置。核对 T02 MAC、T08 YOLO、T13 upsample、T14 maxpool、T15 route 的随机/定向样本数与原记录口径；T17/T20 是历史串行 engine/pilot 的证据，不能宣称新的 8×8 tile / 8-lane 实现已经通过同等套件。协议按 T10–T12/T18–T21 与 T68 `protocol_directed05/06` 的适用性合并，保留固定 stall、错误、取消、timeout、ACK/restart、真实 backend code6/7→INTERNAL、待决写取消/无迟到副作用等原始证据和被审版本。单元、协议、全网分别列状态；静态 PASS、stub 控制路径和真实 backend 测试不得混作相同覆盖。最终按历史被测实现与本批次 tile/backend 的差异判断适用性并补必要回归；证据缺失、版本变化影响结论或适用回归尚未完成时，保持该项 `PENDING`，不能用全网通过推定它通过。
5. **恢复门及独立签收**：完成下节干净副本的真实恢复与约定复验，保存准确命令、退出码、耗时、工具版本、产物哈希及恢复位置。Developer 停止改动后，总控固定最终源码/证据哈希，再由独立 Reviewer 检查真实结果、覆盖、版本和恢复材料；阻断问题关闭后才形成 G4/G5 阶段验收记录。审查前状态仍为 `PENDING`。

准备报告 `report/stage2a_acceptance_preparation_20261002.json` 仅记录主控本轮实际静态核查的范围和结果；它不证明当前运行结果、旧单元记录可替代新 backend 整网结果，或实际 clean-copy 恢复。该报告须与真实 runtime、恢复及最终独立审查记录分开读取。此前 ZIP 归档在执行前被策略拒绝，未生成归档；本轮不生成 ZIP 或备份，也不换工具绕过该拒绝。下节复制与重算是后续恢复步骤，不是本轮已完成事实。

Stage 2A 的 G3 板上验证为 `N/A`：T01 明确本阶段只做 PL RTL 仿真，不授权板测、烧录、摄像头或 HDMI。综合、资源与时序亦为 `N/A`，不能写资源/时序通过；这些属于后续阶段边界。G4/G5 则适用且必须完成，不因 G3 为 N/A 而免除。

## 干净副本重建与 T25 恢复（实际执行仍 PENDING）

Git 只保存已跟踪材料。T25 的 `tensors/` 有 109 个未跟踪 shard，共 `390700998` B；`t25_shard_recovery_manifest_20261002.json` 已纳入 Git，但它只是文件名、长度和哈希清单，**不是另一份 shard 备份**。T68 runtime evidence 也不能因存在 Git 仓库而视为已备份。`git clone` 只生成源码和已跟踪清单，不能直接承担完整交付物恢复。

以下流程在独立、尚不存在的目录执行，不能在当前运行工作树执行恢复或切换提交。预计 T25 重算上限为工具默认全程 7,200 s、每样本 600 s，实际耗时未实测；它会占用 CPU/磁盘，应在当前批跑完成后安排，或先明确资源余量。日志为副本根目录的 `clean_copy_restore_transcript.txt`，检查点为冻结 T25 index；这是整套 CPU shard 恢复，没有中间 shard 续跑机制。超时、缺失数据、哈希/运行时不符、目录已存在或工具返回非零时停止，保留控制台记录，不能删掉已有目标来绕过检查。

前提：保留 T01 绑定的原始图片/标签、cfg、Darknet weights、GF8 包和校准/数据清单；恢复器沿用它们冻结的精确路径与哈希。PL runner 固定 Python 3.12.14；T25 恢复则严格要求 index.runtime 冻结的 Python 3.12.10、NumPy 2.4.6、OpenCV 4.13.0，不能用 PL runner 的 Python 代替。先提供并核验该冻结 T25 环境的精确完整可执行文件路径；本文不猜测安装位置。外部模型/数据和工具链没有被 Git clone 复制。当前环境和路径被核验之后再执行，缺失时先恢复授权备份，不能擅自换路径或重建一份不同数据。

下面使用已存在的 `D:\` 作为新副本父目录，并为新目标生成独占名称；执行前核对空间足够和目标名称。准备基线为 `cd362b47e7e4ad768b40c9e55b6ea8db88ed4ee5`，包含恢复工具但不代表 Stage 2A 冻结版本；最终签收时必须将 `$sourceCommit` 换成记录中的最终交付提交，并复核它包含此冻结源码闭包与恢复工具。

```powershell
$ErrorActionPreference = 'Stop'
$sourceRoot = 'D:\FPGA_Competition'
$sourceCommit = 'cd362b47e7e4ad768b40c9e55b6ea8db88ed4ee5'
$cleanParent = 'D:\'
$cleanName = 'FPGA_Competition_clean_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) { throw '源仓库不存在。' }
if (-not (Test-Path -LiteralPath $cleanParent -PathType Container)) { throw '副本父目录不存在。' }
$sourceRoot = (Get-Item -LiteralPath $sourceRoot).FullName
$cleanParent = (Get-Item -LiteralPath $cleanParent).FullName
$cleanRoot = Join-Path $cleanParent $cleanName
if (Test-Path -LiteralPath $cleanRoot) { throw "副本目标已存在，拒绝覆盖：$cleanRoot" }
& git -C $sourceRoot cat-file -e "${sourceCommit}^{commit}"
if ($LASTEXITCODE -ne 0) { throw '交付提交不存在。' }
$python = Read-Host '请输入冻结 T25 Python 3.12.10 可执行文件的精确完整绝对路径（不加引号）'
if (-not [System.IO.Path]::IsPathFullyQualified($python)) { throw '必须输入精确完整绝对路径。' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw '冻结 T25 Python 文件不存在；停止，不猜测替代路径。' }
$python = (Get-Item -LiteralPath $python).FullName
$t25IndexPath = Join-Path $sourceRoot 'report\evidence\S2A-T25\cpu_layer_golden_index.json'
if (-not (Test-Path -LiteralPath $t25IndexPath -PathType Leaf)) { throw '冻结 T25 index 不存在。' }
$t25Runtime = (Get-Content -LiteralPath $t25IndexPath -Raw -Encoding UTF8 | ConvertFrom-Json).runtime
$observedRuntimeText = & $python -B -c 'import json, platform, numpy, cv2; print(json.dumps({"python": platform.python_version(), "numpy": numpy.__version__, "opencv": cv2.__version__}))'
if ($LASTEXITCODE -ne 0) { throw '冻结 T25 Python 或依赖无法运行；停止。' }
$observedRuntime = ($observedRuntimeText -join "`n") | ConvertFrom-Json
foreach ($key in @('python', 'numpy', 'opencv')) {
    if ($observedRuntime.$key -cne $t25Runtime.$key) { throw "T25 runtime $key 不符：$($observedRuntime.$key) != $($t25Runtime.$key)；停止。" }
}
& git clone --no-hardlinks --no-checkout --config core.autocrlf=false -- $sourceRoot $cleanRoot
if ($LASTEXITCODE -ne 0) { throw '克隆失败；停止并保留现场。' }
$cleanRoot = (Get-Item -LiteralPath $cleanRoot).FullName
& git -C $cleanRoot checkout --detach $sourceCommit
if ($LASTEXITCODE -ne 0) { throw '副本检出失败。' }
$cleanIndexPath = Join-Path $cleanRoot 'report\evidence\S2A-T25\cpu_layer_golden_index.json'
if (-not (Test-Path -LiteralPath $cleanIndexPath -PathType Leaf)) { throw '副本冻结 T25 index 不存在。' }
$cleanRuntime = (Get-Content -LiteralPath $cleanIndexPath -Raw -Encoding UTF8 | ConvertFrom-Json).runtime
foreach ($key in @('python', 'numpy', 'opencv')) {
    if ($cleanRuntime.$key -cne $t25Runtime.$key) { throw "副本冻结 T25 runtime $key 与预检版本不符；停止。" }
}
$restoreTool = Join-Path $cleanRoot 'verification\restore_s2a_t25_shards.py'
$tensors = Join-Path $cleanRoot 'report\evidence\S2A-T25\tensors'
foreach ($path in @($python, $restoreTool)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "文件不存在：$path" }
}
if (Test-Path -LiteralPath $tensors) { throw '副本已有 tensors；禁止覆盖，先停止核对。' }
$transcript = Join-Path $cleanRoot 'clean_copy_restore_transcript.txt'
if (Test-Path -LiteralPath $transcript) { throw '记录已存在，禁止覆盖。' }
Start-Transcript -LiteralPath $transcript -NoClobber
try {
    & $python -B $restoreTool --repo-root $cleanRoot --max-sample-seconds 600 --max-total-seconds 7200
    if ($LASTEXITCODE -ne 0) { throw "恢复失败，退出码 $LASTEXITCODE；停止。" }
    Set-Location -LiteralPath $cleanRoot
    & $python -B -c 'from verification.verify_s2a_t68_d9_outputs import verify_frozen_cpu_baseline; report, rows = verify_frozen_cpu_baseline(); assert len(rows) == 109; print("CPU frozen T25/T29 canonical replay: 109/109")'
    if ($LASTEXITCODE -ne 0) { throw "副本 CPU D9 重验失败，退出码 $LASTEXITCODE；停止。" }
    Write-Host "副本 CPU 恢复和 D9 重验完成：$cleanRoot；仅覆盖 CPU oracle 恢复。"
} finally {
    Stop-Transcript
}
```

恢复命令真实成功的门是退出码 0 及 `S2A-T25 shards restored: 109/109 samples, 38 layers/sample`；恢复器逐个检查压缩及解压长度/SHA-256，所有分片验证后才原子发布 `tensors/`。之后 CPU D9 门是第二条 Python 命令退出码 0、109 个唯一样本且重建报告与冻结 T29 canonical bytes 一致。现有合成恢复测试的 PASS 不替代这两条实际结果；本次准备不运行它们。

也可以从已核验的 shard 备份按 recovery manifest 的精确相对路径还原 109 文件，并逐项重新计算长度和 SHA-256，再执行副本 CPU D9 门。不存在备份时采用上面的重算流程；旧生成器全量新建要求目录不存在，而 Git 副本已含 index，不能直接调用全量新建替代恢复；旧 `--resume` 也不能补回缺失 shard。

如需在干净副本重建 PL 全流程：CPU 恢复通过后，从独立 Windows PowerShell 使用本说明原“全新无人值守启动”命令，将 `$repoRoot` 指向已验证的 `$cleanRoot`，先核对副本 backend/闭包/工具版本，使用新 RunId，不复制旧进度做续跑。执行 109 + D9 后，在同一个副本用原映射命令（同样指定此副本 `$repoRoot`）核验，再交给独立审查。耗时及存储空间按完整批跑预算准备；此完整副本重跑仍 `PENDING`，不在当前准备阶段并行启动。

旧 runtime 的 compile/run records 记录绝对源码、夹具与工具路径。将旧证据复制到另一个位置不等于验证器可直接重验；保留原运行路径及归档路径映射，恢复时先核对路径绑定。需要迁移位置时先由总控明确可验证的恢复方案，不能改写记录中的路径或重用旧 RunId 来伪造相同执行。

## 冻结前必须保留的材料

以同一个 RunId 建立逐文件清单、字节数与 SHA-256，记录原精确路径、归档路径、可恢复位置和版本；校验真实复制/归档结果以后才允许按另行授权清理。不得全量暂存运行目录、构建缓存或模型数据。

- T01 正式规格、`tiny416_model_manifest.json`、`fixed_test_samples.json`、源模型/量化包及原图标签绑定；T25 index、109 shards、`t25_shard_recovery_manifest_20261002.json`；T29 `cpu_decode_nms_reference.json` 和冻结参考源码。
- 当前成功 RunId 的协调报告、`batch_dispatch/batch_summary.json`、D9 和源码映射报告；109 样本的 compile-source snapshot、compile/simulation execution records、逐层 `result_summary.txt`、真实 head13/head26 输出、输入夹具 manifest 与它引用的必要文件、工具清单和命令/退出码/进展及错误日志。D9 与映射验证器引用的文件均必须可恢复，不能只保存总报告。
- 固定静态源码闭包、绑定的 Git commits/trees、源码和 testbench、runner/协调器/验证器版本、Verilator/MSYS2/PowerShell/Python 及依赖版本；从干净副本重建的准确步骤与真实恢复证据。
- T02/T08/T10–T21 原始定名 JSON、引用的单元/协议结果与被审版本（入口见本轮准备 JSON）；T17/T20 历史串行 engine/pilot 与新 tile 的适用性及差异回归结果，T68 `protocol_directed05/06` 真实 backend 结果及 `backend_fault_recovery.vcd` 等适用原始证据；随机种子、样本数、误差口径和独立审查结论。G3/综合 N/A 理由及实际 G4/G5 签收记录。
- 失败批次保持独立诊断归档，不纳入成功批次计数。构建缓存是否可清理须在列清所有验证器依赖并完成恢复核验后决定，不能在正在运行的目录中删除。
