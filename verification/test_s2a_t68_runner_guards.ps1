[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-TestCondition {
    param([Parameter(Mandatory = $true)][bool]$Condition, [Parameter(Mandatory = $true)][string]$Message)
    if (-not $Condition) { throw $Message }
}

function Assert-ExpectedFailure {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    try {
        & $Action | Out-Null
    } catch {
        return
    }
    throw "负向测试未拒绝：$Name"
}

function New-TestSummary {
    param([Parameter(Mandatory = $true)][string[]]$Lines, [Parameter(Mandatory = $true)][string]$NewLine)
    return (($Lines -join $NewLine) + $NewLine)
}

$runnerPath = Join-Path $PSScriptRoot 'run_s2a_network_backend_verilator.ps1'
$coordinatorPath = Join-Path $PSScriptRoot 'run_s2a_t68_unattended_continuation.ps1'
foreach ($functionBinding in @(
    @{ path = $runnerPath; name = 'Test-S2aNetworkBackendResultSummary' },
    @{ path = $coordinatorPath; name = 'Assert-ApprovedPythonCommandResolution' }
)) {
    $tokens = $null
    $parseErrors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($functionBinding.path, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) { throw "PowerShell 解析失败：$($functionBinding.path)；$($parseErrors[0].Message)" }
    $functionName = [string]$functionBinding.name
    $functionAst = $ast.Find({
        param($node)
        ($node -is [System.Management.Automation.Language.FunctionDefinitionAst]) -and ($node.Name -ceq $functionName)
    }, $true)
    if ($null -eq $functionAst) { throw "未找到测试目标函数：$functionName ($($functionBinding.path))" }
    . ([scriptblock]::Create($functionAst.Extent.Text))
}

$validLines = @(
    'status=PASS_LAYERWISE_EXACT_GOLDEN',
    'feature_write_bytes=11382150 mismatches=0 cycles=972865374',
    'head13_bytes=5070 head26_bytes=20280'
)
$summaryCases = 0
foreach ($newLine in @("`n", "`r`n")) {
    $validSummary = New-TestSummary -Lines $validLines -NewLine $newLine
    Assert-TestCondition -Condition (Test-S2aNetworkBackendResultSummary -Text $validSummary) -Message '有效 LF/CRLF 摘要应被接受。'
    $summaryCases++

    $badCases = @(
        @{ name = 'wrong status'; lines = @('status=FAIL', $validLines[1], $validLines[2]) },
        @{ name = 'nonzero mismatch'; lines = @($validLines[0], 'feature_write_bytes=11382150 mismatches=1 cycles=972865374', $validLines[2]) },
        @{ name = 'wrong feature bytes'; lines = @($validLines[0], 'feature_write_bytes=11382149 mismatches=0 cycles=972865374', $validLines[2]) },
        @{ name = 'missing output field'; lines = @($validLines[0], $validLines[1]) },
        @{ name = 'wrong head bytes'; lines = @($validLines[0], $validLines[1], 'head13_bytes=5070 head26_bytes=20281') }
    )
    foreach ($badCase in $badCases) {
        $badSummary = New-TestSummary -Lines $badCase.lines -NewLine $newLine
        Assert-TestCondition -Condition (-not (Test-S2aNetworkBackendResultSummary -Text $badSummary)) -Message "错误摘要被接受：$($badCase.name)"
        $summaryCases++
    }
}

$temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('s2a-t68-python-path-test-' + [guid]::NewGuid().ToString('N'))
$temporaryRoot = [System.IO.Path]::GetFullPath($temporaryRoot)
$approvedDirectory = Join-Path $temporaryRoot 'approved'
$otherDirectories = @(
    (Join-Path $temporaryRoot 'other-a'),
    (Join-Path $temporaryRoot 'other-b'),
    (Join-Path $temporaryRoot 'other-c')
)
$approvedPython = Join-Path $approvedDirectory 'python.exe'
$originalPath = $env:PATH
$pythonPathCases = 0
try {
    $null = [System.IO.Directory]::CreateDirectory($approvedDirectory)
    foreach ($directory in $otherDirectories) { $null = [System.IO.Directory]::CreateDirectory($directory) }
    [System.IO.File]::WriteAllBytes($approvedPython, [byte[]]@())
    foreach ($directory in $otherDirectories) {
        [System.IO.File]::WriteAllBytes((Join-Path $directory 'python.exe'), [byte[]]@())
    }

    $env:PATH = (@($approvedDirectory) + $otherDirectories + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $preferredCommands = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-TestCondition -Condition ($preferredCommands.Count -ge 4) -Message '测试 PATH 未解析到多个 python.exe 候选。'
    $selectedPython = Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $preferredCommands
    Assert-TestCondition -Condition ($selectedPython -ieq [System.IO.Path]::GetFullPath($approvedPython)) -Message '固定路径首选解析未被接受。'
    $pythonPathCases++

    $env:PATH = (@($otherDirectories[0], $approvedDirectory) + $otherDirectories[1..2] + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $wrongFirstCommands = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-TestCondition -Condition ($wrongFirstCommands.Count -ge 4) -Message '首选不一致用例缺少多个 python.exe 候选。'
    Assert-ExpectedFailure -Name '首选解析不一致' -Action {
        Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $wrongFirstCommands
    }
    $pythonPathCases++

    Remove-Item -LiteralPath $approvedPython -Force
    $env:PATH = (@($approvedDirectory) + $otherDirectories + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $withoutApprovedFile = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-ExpectedFailure -Name '固定 Python 文件不可用' -Action {
        Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $withoutApprovedFile
    }
    $pythonPathCases++
} finally {
    $env:PATH = $originalPath
    $tempParent = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $temporaryRoot.StartsWith($tempParent, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "合成测试临时目录超出系统 Temp：$temporaryRoot"
    }
    if (Test-Path -LiteralPath $temporaryRoot) {
        $temporaryItem = Get-Item -LiteralPath $temporaryRoot -ErrorAction Stop
        if (-not $temporaryItem.PSIsContainer -or (($temporaryItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "拒绝清理非普通临时目录：$temporaryRoot"
        }
        Remove-Item -LiteralPath $temporaryRoot -Recurse -Force
    }
}

[pscustomobject]@{
    status = 'PASS'
    powershell_version = $PSVersionTable.PSVersion.ToString()
    powershell_executable = Join-Path $PSHOME 'pwsh.exe'
    summary_cases = $summaryCases
    python_path_resolution_cases = $pythonPathCases
    python_interpreter_invocations = 0
    simulation_invocations = 0
} | ConvertTo-Json -Compress
