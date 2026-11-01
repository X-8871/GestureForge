# 执行已独立审查的入口，原生启动器码与入口逻辑结果分别保存。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261013_r03'
$taskConfig = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_prepare_20261013_r01\visibility_probe_config_r03.json'
$taskEntry = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\vitis\run_s2b_visibility_probe.py'
$taskVitis = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\vitis.bat'
if (-not $taskRun.PSIsContainer -or $taskEntry.PSIsContainer -or $taskConfig.PSIsContainer -or $taskVitis.PSIsContainer) {throw '路径类型错误'}
if ((Get-FileHash -LiteralPath $taskConfig.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne '06c669da0e006c093628162c555cc77bf790d02a9cabf8d9b97d9f1c22de42ab') {throw '配置漂移'}
if ((Get-FileHash -LiteralPath $taskEntry.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne '2015542ac9766110657112030040dd30d0f333223f8d60b5d31348bd65bd9638') {throw '已审入口漂移'}
$taskRecord = Join-Path $taskRun.FullName 'vitis_execution.json'
$taskStdout = Join-Path $taskRun.FullName 'vitis_stdout.log'
$taskStderr = Join-Path $taskRun.FullName 'vitis_stderr.log'
foreach ($taskPath in @($taskRecord,$taskStdout,$taskStderr)) {if (Test-Path -LiteralPath $taskPath) {throw '拒绝覆盖'}}
$taskPreviousConfig = $env:S2B_VISIBILITY_PROBE_CONFIG
$taskPreviousEncoding = $env:PYTHONIOENCODING
$taskStarted = Get-Date -Format o
try {
    $env:S2B_VISIBILITY_PROBE_CONFIG = $taskConfig.FullName
    $env:PYTHONIOENCODING = 'utf-8'
    & $taskVitis.FullName -s $taskEntry.FullName 1> $taskStdout 2> $taskStderr
    $taskCode = $LASTEXITCODE
    $taskResult = [pscustomobject]@{command=@($taskVitis.FullName,'-s',$taskEntry.FullName);config_path=$taskConfig.FullName;config_sha256='06c669da0e006c093628162c555cc77bf790d02a9cabf8d9b97d9f1c22de42ab';started_at_utc8=$taskStarted;finished_at_utc8=(Get-Date -Format o);native_exit_code=$taskCode;result_semantics='启动器退出码不是缓存验收；以入口visibility_probe_result.json及真实原始观察判定'}
    $taskEncoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($taskRecord,($taskResult | ConvertTo-Json -Depth 5)+"`n",$taskEncoding)
    $taskResult | ConvertTo-Json -Depth 5
} finally {
    $env:S2B_VISIBILITY_PROBE_CONFIG = $taskPreviousConfig
    $env:PYTHONIOENCODING = $taskPreviousEncoding
}
