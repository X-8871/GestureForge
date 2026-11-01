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

截至 2026-10-05，本节记录终态验收门及本次实际状态。109 样本 PL、实际 head 对照 CPU D9、运行快照到冻结源码映射、T25 干净副本恢复与 CPU D9 重验均已完成；逐样本报告、失败恢复记录和逐文件归档清单见 [G4/G5 候选验收记录](../report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md)。最新版 Vault 阶段计划另要求综合无错误/非预期锁存器、资源可容纳性和时钟风险报告；此综合证据及独立 G4/G5 Reviewer 签收尚未完成。全量 109 样本 PL 干净副本重跑没有执行，是否属于本阶段硬性门由 Reviewer 按当前正式标准判断。

1. **整网结果门：已完成。** `repair109_20261003_194620` 逐样本审计确认索引 0–108 恰为 109 个样本，覆盖 cfg 层 0–37，均为 `PASS_LAYERWISE_EXACT_GOLDEN`、`feature_write_bytes=11382150 mismatches=0`、`head13_bytes=5070 head26_bytes=20280`。Coordinator 的 `PASS_108_RUNNERS` 仅是索引 1–108；sample000 是同 RunId 独立运行并通过。验收以逐样本审计合并两者，不把 coordinator 摘要误称为 `PASS_109`。
2. **实际 head/D9 门：已完成。** `d9_109_sample_report.json` 为 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`、109 样本；冻结绑定、head 字节、离散检测字段和数值误差均通过，最大 score/xyxy 绝对误差为 0。原报告和 SHA 见 G4/G5 候选验收记录。
3. **版本门：已完成。** `source_snapshot_git_binding_repair109_20261003_194620.json` 为 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE`、109 样本；源码闭包固定为 commit `fecbf1f8f37fcee8b25e6e2517b9621850912a4e` / tree `094e1492396a6788cc33b3b5866dd304387c02da`，闭包 JSON 为 `static_source_closure_20261003_worker_crlf.json`。后续只修改记录的提交不替代本批次编译源码版本。
4. **单元与协议证据：待独立审查其适用范围。** T02/T08/T10–T21 的原始结果仍按各自被测版本和口径引用；T17/T20 是历史串行 engine/pilot，不能宣称为新 8×8 tile / 8-lane 的等价套件。当前 tile 以 T70 算术、内存、边界及 T68 protocol_directed05/06 的原始证据分别支持；独立 Reviewer 应检查覆盖边界，不能把静态 PASS、stub 控制路径和真实 backend 测试混为一谈。
5. **综合与恢复门：综合待执行，CPU 恢复已完成。** 按最新版阶段计划，先完成冻结 RTL 的无错误/非预期锁存器综合检查、资源可容纳性统计和时钟风险报告；随后核验 T25 干净副本 109×38 shards 实际恢复及 109 样本 CPU D9 canonical replay 的命令、退出码、耗时、版本与 SHA。T68 归档逐文件校验通过。以上证据固定后由独立 Reviewer 检查覆盖、版本、历史适用性和归档可恢复材料；审核前最终状态为 `PENDING`。

准备报告 `report/stage2a_acceptance_preparation_20261002.json` 只记录当时静态核查范围；它不替代本次 runtime、干净副本恢复、归档和最终独立审查证据。该旧报告的综合 N/A 项来自旧版仓库快照；Vault 当前阶段计划已更新并要求综合/资源/时钟风险证据。仓库计划快照已精确对齐此 Vault 源；请以 2026-10-05 候选验收记录和新增综合证据为当前证据索引。

Stage 2A 的 G3 板上验证为 `N/A`：T01 明确本阶段不授权板测、烧录、摄像头或 HDMI。当前阶段计划将综合/资源/时钟风险报告列为 2A 证据要求，须按冻结源码和准确器件基线生成；综合结果不能被写成板上时序通过。G4/G5 适用且必须完成，不因 G3 为 N/A 而免除。

## 干净副本重建与 T25 恢复（CPU 恢复已完成；完整 PL 重跑未执行）

Git 只保存已跟踪材料。T25 的 `tensors/` 有 109 个未跟踪 shard，共 `390700998` B；`t25_shard_recovery_manifest_20261002.json` 已纳入 Git，它只是文件名、长度和哈希清单，**本身不是 shard 备份**。实际 shard 已另复制到 `D:\FPGA_Competition\archive\S2A-T25\clean_restore_20261002_160036`，并由 archive manifest 逐文件验证。T68 runtime evidence 同样由 `D:\FPGA_Competition\archive\S2A-T68\repair109_20261003_194620` 独立目录保存并核验；这些归档仍与源同在 D 盘，不是异盘备份。`git clone` 只生成源码和已跟踪清单，不能单独承担完整交付物恢复。

T25 恢复已在独立干净 Git 副本真实执行并通过：109×38 shard 恢复 exit 0、耗时 2,283.61 秒；CPU D9 canonical replay 109 样本、exit 0、耗时 12.359 秒；总耗时 2,296.36 秒。环境为 Python 3.12.10、NumPy 2.4.6、OpenCV 4.13.0。记录位于 `report/evidence/S2A-T25/clean_restore_20261002_160036/recovery_execution_record.json` 和 `final_evidence_integrity.json`。以下命令保留为复现步骤，不表示需要再次运行当前已通过的 CPU 恢复。

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

恢复命令成功门为退出码 0 及 `S2A-T25 shards restored: 109/109 samples, 38 layers/sample`；恢复器逐个检查压缩和解压长度/SHA-256，所有分片验证后才原子发布 `tensors/`。CPU D9 门为第二条 Python 命令退出码 0、109 个唯一样本且重建报告与冻结 T29 canonical bytes 一致。本次实际运行均已通过；合成恢复测试不能替代这些真实结果。

也可以从已核验的 shard 备份按 recovery manifest 的精确相对路径还原 109 文件，并逐项重新计算长度和 SHA-256，再执行副本 CPU D9 门。不存在备份时采用上面的重算流程；旧生成器全量新建要求目录不存在，而 Git 副本已含 index，不能直接调用全量新建替代恢复；旧 `--resume` 也不能补回缺失 shard。

如需在干净副本重建 PL 全流程：CPU 恢复通过后，从独立 Windows PowerShell 使用本说明原“全新无人值守启动”命令，将 `$repoRoot` 指向已验证的 `$cleanRoot`，先核对副本 backend/闭包/工具版本，使用新 RunId，不复制旧进度做续跑。执行 109 + D9 后，在同一个副本用原映射命令（同样指定此副本 `$repoRoot`）核验，再交给独立审查。全量 PL 干净副本重跑尚未执行；由当前独立 G4/G5 Reviewer 按正式验收标准判定是否必需。如需执行，应单独评估时间、空间和运行窗口，不得把已有 RunId 续跑记录复制到新副本。

旧 runtime 的 compile/run records 记录绝对源码、夹具与工具路径。将旧证据复制到另一个位置不等于验证器可直接重验；保留原运行路径及归档路径映射，恢复时先核对路径绑定。需要迁移位置时先由总控明确可验证的恢复方案，不能改写记录中的路径或重用旧 RunId 来伪造相同执行。

## 冻结前必须保留的材料

以同一个 RunId 建立逐文件清单、字节数与 SHA-256，记录原精确路径、归档路径、可恢复位置和版本；校验真实复制/归档结果以后才允许按另行授权清理。本轮在 manifest 校验通过后仅清理可重建的 109 个 PL build 缓存与 4 个 T68/T70 build/obj_dir 缓存；不得全量暂存运行目录、构建缓存或模型数据。

- T01 正式规格、`tiny416_model_manifest.json`、`fixed_test_samples.json`、源模型/量化包及原图标签绑定；T25 index、109 shards、`t25_shard_recovery_manifest_20261002.json`；T29 `cpu_decode_nms_reference.json` 和冻结参考源码。
- 当前成功 RunId 的协调报告、`batch_dispatch/batch_summary.json`、D9 和源码映射报告；109 样本的 compile-source snapshot、compile/simulation execution records、逐层 `result_summary.txt`、真实 head13/head26 输出、输入夹具 manifest 与它引用的必要文件、工具清单和命令/退出码/进展及错误日志。D9 与映射验证器引用的文件均必须可恢复，不能只保存总报告。
- 固定静态源码闭包、绑定的 Git commits/trees、源码和 testbench、runner/协调器/验证器版本、Verilator/MSYS2/PowerShell/Python 及依赖版本；从干净副本重建的准确步骤与真实恢复证据。
- T02/T08/T10–T21 原始定名 JSON、引用的单元/协议结果与被审版本（入口见本轮准备 JSON）；T17/T20 历史串行 engine/pilot 与新 tile 的适用性及差异回归结果，T68 `protocol_directed05/06` 真实 backend 结果及 `backend_fault_recovery.vcd` 等适用原始证据；随机种子、样本数、误差口径和独立审查结论。G3 板上验证为 N/A；G4 须保留综合错误/锁存器、器件资源与时钟风险报告及最终签收记录。
- 失败批次保持独立诊断归档，不纳入成功批次计数。构建缓存是否可清理须在列清所有验证器依赖并完成恢复核验后决定，不能在正在运行的目录中删除。

## 2026-10-03 至 2026-10-05 batch109 终态

失败批次 `repair109_20261003_124125` 的 sample000 与 8 个 worker 仿真曾实际完成，但 worker 因 CRLF 摘要校验缺陷被拒；保留为失败诊断，不计入成功批次。修复后 RunId `repair109_20261003_194620` 从 sample000 全新运行。逐样本审计已核实索引 0–108 全部通过，D9 和快照映射各覆盖 109 个样本；初始 STOP_BATCH_FAILED 与两次 recovery 记录也保留，不能因进程或旧启动日志判断当前仍在跑。完整结论和 SHA 见 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。

本批次 PL 与 D9 已结束，禁止重复启动。已校验归档后删除的仅是可重建编译缓存；T68/T25/T70 的输入、结果和关键日志保留在原证据路径及 `D:\FPGA_Competition\archive\`。归档与原始材料同属 D 盘物理卷，并非异盘备份。Stage 2A 当前等待独立 G4/G5 签收；109 样本 PL 干净副本重跑尚未执行，审查按正式门判断其必要性。
