[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Prepare', 'AuditInventory')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$script:ExpectedHead = '7278f2342de4f44d8da8e8002b3b92597b5e5050'
$script:RepoRoot = 'D:\FPGA_Competition'
$script:T59Root = 'D:\FPGA_Competition\report\evidence\S2A-T59'
$script:Run10Root = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10'
$script:Run11Root = 'D:\FPGA_Competition\report\evidence\S2A-T59\run11'
$script:NewTbPath = 'D:\FPGA_Competition\sim\tb_s2a_conv_layer35_attempt11.sv'
$script:SourceTbPath = 'D:\FPGA_Competition\sim\tb_s2a_conv_layer35_row23_all_channels.sv'
$script:SourcePythonPath = 'D:\FPGA_Competition\verification\test_s2a_conv_layer35_row23_all_channels_rtl.py'
$script:Run10SummaryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\prepare_summary.json'
$script:Run10BindingPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\project_preflight_binding.json'
$script:Run10ManifestPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\fixture\fixture_manifest.json'
$script:TargetXprPath = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$script:ExpectedSummarySha = '35a816aae2167e618b9c91fef1a3f5441bc59fe27d85468f47919d87beee83c1'
$script:ExpectedBindingSha = '2f7da35666c3238f1ace45ceed46ecbc9f5ab1c4bbf49919d077f73579ec6c8a'
$script:ExpectedManifestSha = '7bdb1ccc6e94b9ae7327f75facc1d0cbe5d541b8fdd9b63480598102f2e1e792'
$script:ExpectedGoldenSha = '95f93d520186a64693996fa6cf9184417539c37ea8535359a7cd1579f47fc07e'
$script:ExpectedXprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'

function Get-FileRecord {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) { throw "预期文件却得到目录：$Path" }
    $sha = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return [ordered]@{ path = $Path; bytes = [long]$item.Length; sha256 = $sha }
}

function Assert-NoReparseChain {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [switch]$AllowMissingLeaf
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $driveRoot = [System.IO.Path]::GetPathRoot($fullPath)
    $relative = $fullPath.Substring($driveRoot.Length).Trim('\')
    $parts = @($relative.Split('\', [System.StringSplitOptions]::RemoveEmptyEntries))
    $current = $driveRoot
    for ($index = 0; $index -lt $parts.Count; $index++) {
        $current = Join-Path -Path $current -ChildPath $parts[$index]
        if (-not (Test-Path -LiteralPath $current)) {
            if ($AllowMissingLeaf -and ($index -eq ($parts.Count - 1))) { return }
            throw "路径组件不存在：$current"
        }
        $entry = Get-Item -LiteralPath $current -Force
        if (($entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "拒绝重解析路径：$current"
        }
    }
}

function Assert-Equal {
    param(
        [Parameter(Mandatory = $true)]$Actual,
        [Parameter(Mandatory = $true)]$Expected,
        [Parameter(Mandatory = $true)][string]$Name
    )
    if ([string]$Actual -cne [string]$Expected) {
        throw "$Name 不匹配：实际=$Actual 期望=$Expected"
    }
}

function Get-HostGate {
    $repoFromScript = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    Assert-Equal $repoFromScript $script:RepoRoot '仓库根路径'

    $headText = & git -C $script:RepoRoot rev-parse HEAD
    $gitExitCode = $LASTEXITCODE
    if ($gitExitCode -ne 0) { throw "git rev-parse 退出码=$gitExitCode" }
    $headText = ([string]$headText).Trim()
    Assert-Equal $headText $script:ExpectedHead 'HEAD'

    $badNames = @('vivado', 'vivado_lab', 'xsim', 'xsimk', 'xelab', 'xvlog', 'xvhdl', 'xsct')
    $active = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $badNames -contains $_.ProcessName.ToLowerInvariant() })
    if ($active.Count -ne 0) { throw "检测到 Xilinx 进程：$($active.ProcessName -join ',')" }
    $listeners = @(Get-NetTCPConnection -State Listen -LocalPort 7654 -ErrorAction SilentlyContinue)
    if ($listeners.Count -ne 0) { throw '检测到 7654 监听端口' }

    return [ordered]@{
        repo_root = $repoFromScript
        git_head = $headText
        git_exit_code = [int]$gitExitCode
        xilinx_processes = @()
        listener_7654 = @()
        vivado_or_xsim_invoked_by_runner = $false
    }
}

function Get-ParentBinding {
    param([switch]$RequireRun11Absent)

    Assert-NoReparseChain $script:T59Root
    Assert-NoReparseChain $script:Run10Root
    Assert-NoReparseChain (Join-Path $script:Run10Root 'fixture')
    Assert-NoReparseChain $script:Run10SummaryPath
    Assert-NoReparseChain $script:Run10BindingPath
    Assert-NoReparseChain $script:Run10ManifestPath
    Assert-NoReparseChain $script:TargetXprPath
    Assert-NoReparseChain $script:SourceTbPath
    Assert-NoReparseChain $script:SourcePythonPath

    if ($RequireRun11Absent) {
        if (Test-Path -LiteralPath $script:Run11Root) { throw "run11 已存在，拒绝覆盖：$script:Run11Root" }
        Assert-NoReparseChain $script:Run11Root -AllowMissingLeaf
        if (Test-Path -LiteralPath $script:NewTbPath) { throw "attempt11 TB 已存在，拒绝覆盖：$script:NewTbPath" }
        Assert-NoReparseChain (Split-Path -Parent $script:NewTbPath)
    } elseif (Test-Path -LiteralPath $script:Run11Root) {
        Assert-NoReparseChain $script:Run11Root
        Assert-NoReparseChain $script:NewTbPath
    } else {
        Assert-NoReparseChain $script:Run11Root -AllowMissingLeaf
        if (Test-Path -LiteralPath $script:NewTbPath) { throw 'attempt11 TB 存在但 run11 根不存在' }
        Assert-NoReparseChain (Split-Path -Parent $script:NewTbPath)
    }

    $summaryRecord = Get-FileRecord $script:Run10SummaryPath
    Assert-Equal $summaryRecord.sha256 $script:ExpectedSummarySha 'run10 summary SHA256'
    $bindingRecord = Get-FileRecord $script:Run10BindingPath
    Assert-Equal $bindingRecord.sha256 $script:ExpectedBindingSha 'run10 project binding SHA256'
    $manifestRecord = Get-FileRecord $script:Run10ManifestPath
    Assert-Equal $manifestRecord.sha256 $script:ExpectedManifestSha 'run10 fixture manifest SHA256'

    $summary = Get-Content -LiteralPath $script:Run10SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $projectBinding = Get-Content -LiteralPath $script:Run10BindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifest = Get-Content -LiteralPath $script:Run10ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $summary.task_id 'S2A-T59' 'run10 task id'
    Assert-Equal $summary.run_id 'run10' 'run10 id'
    Assert-Equal $summary.status 'PREPARED_NOT_SIMULATED' 'run10 prepare status'
    Assert-Equal $summary.scope 'tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25' 'run10 scope'
    Assert-Equal $manifest.task_id 'S2A-T59' 'fixture manifest task id'
    Assert-Equal $manifest.run_id 'run10' 'fixture manifest run id'
    Assert-Equal $manifest.status 'PREPARED_NOT_SIMULATED' 'fixture manifest status'
    Assert-Equal $projectBinding.task_id 'S2A-T59' 'run10 project binding task id'
    Assert-Equal $projectBinding.run_id 'run10' 'run10 project binding id'
    Assert-Equal $projectBinding.status 'READ_ONLY_BOUND' 'run10 project binding status'
    Assert-Equal $projectBinding.project_xpr_path $script:TargetXprPath 'run10 target XPR path'
    Assert-Equal $projectBinding.target_xpr_sha256_before_prepare $script:ExpectedXprSha 'run10 XPR before SHA256'
    Assert-Equal $projectBinding.target_xpr_sha256_after_prepare $script:ExpectedXprSha 'run10 XPR after SHA256'
    Assert-Equal $projectBinding.target_xpr_unchanged $true 'run10 target XPR unchanged'

    $actualXpr = Get-FileRecord $script:TargetXprPath
    Assert-Equal $actualXpr.sha256 $script:ExpectedXprSha '当前目标 XPR SHA256'

    $fixtureFiles = [ordered]@{}
    foreach ($fixtureName in @('feature_input.bin', 'layer35_weights.bin', 'golden.bin', 'vectors.txt')) {
        $summaryFile = $summary.fixture.files.$fixtureName
        $manifestFile = $manifest.files.$fixtureName
        if ($null -eq $summaryFile -or $null -eq $manifestFile) { throw "父证据缺少 fixture 条目：$fixtureName" }
        Assert-Equal $summaryFile.path (Join-Path (Join-Path $script:Run10Root 'fixture') $fixtureName) "summary fixture path $fixtureName"
        Assert-Equal $manifestFile.path $summaryFile.path "manifest fixture path $fixtureName"
        Assert-Equal $manifestFile.bytes $summaryFile.bytes "manifest fixture bytes $fixtureName"
        Assert-Equal $manifestFile.sha256 $summaryFile.sha256 "manifest fixture SHA256 $fixtureName"
        $actual = Get-FileRecord $summaryFile.path
        Assert-Equal $actual.bytes $summaryFile.bytes "当前 fixture bytes $fixtureName"
        Assert-Equal $actual.sha256 $summaryFile.sha256 "当前 fixture SHA256 $fixtureName"
        if (($fixtureName -eq 'golden.bin') -and ($actual.sha256 -cne $script:ExpectedGoldenSha)) {
            throw 'golden SHA256 不符合冻结值'
        }
        $fixtureFiles[$fixtureName] = $actual
    }
    Assert-Equal $summary.fixture.golden_layout.raw_int32_le_bytes 26624 'raw golden bytes'
    Assert-Equal $summary.fixture.golden_layout.int8_bytes 6656 'INT8 golden bytes'
    Assert-Equal $summary.expected_counts.output_cases 6656 'run10 output case count'
    Assert-Equal $summary.oracle.raw_int32_count 6656 'run10 raw oracle count'
    Assert-Equal $summary.oracle.quantized_int8_count 6656 'run10 INT8 oracle count'
    Assert-Equal $summary.oracle.d2_t23_match_count 6656 'run10 D2/T23 match count'

    $sourceRecords = [ordered]@{}
    foreach ($sourceProp in $summary.bindings.T59_source_hashes.PSObject.Properties) {
        $sourcePath = Join-Path $script:RepoRoot $sourceProp.Name
        Assert-NoReparseChain $sourcePath
        $sourceRecord = Get-FileRecord $sourcePath
        Assert-Equal $sourceRecord.sha256 $sourceProp.Value "T59 source SHA256 $($sourceProp.Name)"
        $sourceRecords[$sourceProp.Name] = $sourceRecord
    }
    if (-not $sourceRecords.Contains('src/s2a_conv_layer35_channel_probe.sv')) { throw '父绑定未包含 layer35 probe RTL' }
    if (-not $sourceRecords.Contains('sim/tb_s2a_conv_layer35_row23_all_channels.sv')) { throw '父绑定未包含只读源 TB' }
    if (-not $sourceRecords.Contains('verification/test_s2a_conv_layer35_row23_all_channels_rtl.py')) { throw '父绑定未包含只读 Python verifier' }

    return [ordered]@{
        summary = $summary
        project_binding = $projectBinding
        fixture_manifest = $manifest
        summary_record = $summaryRecord
        project_binding_record = $bindingRecord
        manifest_record = $manifestRecord
        target_xpr = $actualXpr
        fixture_files = $fixtureFiles
        T59_source_hashes = $sourceRecords
    }
}

function Write-NewUtf8 {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    if (Test-Path -LiteralPath $Path) { throw "输出已存在，拒绝覆盖：$Path" }
    Assert-NoReparseChain (Split-Path -Parent $Path)
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $bytes = $encoding.GetBytes($Text)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Get-Utf8TextRecord {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() } finally { $sha.Dispose() }
    return [ordered]@{ path = $Path; bytes = [long]$bytes.Length; sha256 = $digest }
}

function Assert-ExistingUtf8Matches {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$ExpectedText)
    if (-not (Test-Path -LiteralPath $Path)) { throw "预期已有的部分工件缺失：$Path" }
    Assert-NoReparseChain $Path
    $expectedBytes = [System.Text.UTF8Encoding]::new($false).GetBytes($ExpectedText)
    $actualBytes = [System.IO.File]::ReadAllBytes($Path)
    if ($actualBytes.Length -ne $expectedBytes.Length) { throw "已有工件长度与本轮重算内容不一致：$Path" }
    for ($index = 0; $index -lt $actualBytes.Length; $index++) {
        if ($actualBytes[$index] -ne $expectedBytes[$index]) { throw "已有工件字节与本轮重算内容不一致：$Path offset=$index" }
    }
}

function Write-OrVerifyUtf8 {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    if (Test-Path -LiteralPath $Path) {
        Assert-ExistingUtf8Matches $Path $Text
    } else {
        Write-NewUtf8 $Path $Text
    }
}

function ConvertTo-Utf8Json {
    param([Parameter(Mandatory = $true)]$Object)
    $jsonText = ConvertTo-Json -InputObject $Object -Depth 32
    return (($jsonText -replace "`r`n", "`n") + "`n")
}

function New-TbCloneText {
    $originalText = [System.IO.File]::ReadAllText($script:SourceTbPath, [System.Text.Encoding]::UTF8)
    $newline = if ($originalText.Contains("`r`n")) { "`r`n" } else { "`n" }
    $updated = $originalText
    $replacements = @(
        [ordered]@{
            old = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_raw.bin'
            new = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run11\\observed_raw.bin'
        },
        [ordered]@{
            old = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_output.bin'
            new = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run11\\observed_output.bin'
        }
    )
    foreach ($replacement in $replacements) {
        $occurrences = ([regex]::Matches($updated, [regex]::Escape($replacement.old))).Count
        Assert-Equal $occurrences 1 "TB output path occurrence $($replacement.old)"
        $updated = $updated.Replace($replacement.old, $replacement.new)
    }
    $finishMatches = [regex]::Matches($updated, '(?s)\$display\("PASS T59 outputs=.*?\);\s*\$finish;')
    Assert-Equal $finishMatches.Count 1 'PASS/$finish region count'
    if ([regex]::IsMatch($updated, 'T59_XSIM_SENTINEL')) { throw '源 TB 已含 sentinel，拒绝重复插入' }
    $finishIndex = $updated.IndexOf('$finish;', $finishMatches[0].Index, [System.StringComparison]::Ordinal)
    if ($finishIndex -lt 0) { throw 'PASS 后未找到 $finish' }
    $updated = $updated.Insert($finishIndex, '$display("T59_XSIM_SENTINEL=PASS_RUN11");' + $newline + '        ')

    foreach ($inputName in @('feature_input.bin', 'layer35_weights.bin', 'golden.bin', 'vectors.txt')) {
        $expectedInput = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\' + $inputName
        if (-not $updated.Contains($expectedInput)) { throw "TB 输入路径不是 run10：$inputName" }
    }
    foreach ($oldOutput in @('run10\\observed_raw.bin', 'run10\\observed_output.bin')) {
        if ($updated.Contains($oldOutput)) { throw "TB 仍有 run10 输出路径：$oldOutput" }
    }
    Assert-Equal ([regex]::Matches($updated, 'T59_XSIM_SENTINEL=PASS_RUN11').Count) 1 'run11 sentinel count'

    $reverse = $updated.Replace('$display("T59_XSIM_SENTINEL=PASS_RUN11");' + $newline + '        ', '')
    foreach ($replacement in $replacements) { $reverse = $reverse.Replace($replacement.new, $replacement.old) }
    if ($reverse -cne $originalText) { throw 'attempt11 TB 除两条输出路径和 sentinel 外还有额外差异' }
    return [ordered]@{ text = $updated; newline = if ($newline -eq "`r`n") { 'CRLF' } else { 'LF' } }
}

function New-TclFiles {
    $projectDir = Join-Path $script:Run11Root 'isolated_project'
    $projectXpr = Join-Path $projectDir 's2a_t59_row23_attempt11.xpr'
    $rtlPaths = @(
        'D:\FPGA_Competition\src\int8_conv_tap_geometry.sv',
        'D:\FPGA_Competition\src\int8_conv_weight_address.sv',
        'D:\FPGA_Competition\src\int8_mac_accumulator.sv',
        'D:\FPGA_Competition\src\s2a_conv_engine.sv',
        'D:\FPGA_Competition\src\s2a_conv_layer35_channel_probe.sv'
    )
    $projectLines = [System.Collections.Generic.List[string]]::new()
    $projectLines.Add("create_project s2a_t59_row23_attempt11 {$projectDir} -part xc7z020clg400-1")
    $projectLines.Add('set_property target_language Verilog [current_project]')
    $projectLines.Add('set_property simulator_language Mixed [current_project]')
    foreach ($rtlPath in $rtlPaths) { $projectLines.Add("add_files -fileset sources_1 -norecurse {$rtlPath}") }
    $projectLines.Add("add_files -fileset sim_1 -norecurse {$script:NewTbPath}")
    $projectLines.Add('set_property top tb_s2a_conv_layer35_row23_all_channels [get_filesets sim_1]')
    $projectLines.Add('update_compile_order -fileset sources_1')
    $projectLines.Add('update_compile_order -fileset sim_1')
    $projectTclText = [string]::Join("`n", $projectLines) + "`n"

    $projectTclPath = Join-Path $projectDir 'create_project.tcl'
    $simLines = [System.Collections.Generic.List[string]]::new()
    $simLines.Add("source {$projectTclPath}")
    $simLines.Add('launch_simulation -simset sim_1 -mode behavioral')
    $simLines.Add('run all')
    $simLines.Add('close_sim')
    $simLines.Add('close_project')
    $simTclText = [string]::Join("`n", $simLines) + "`n"

    $projectCommandLines = @($projectTclText -split "`n" | Where-Object { $_.Length -gt 0 })
    Assert-Equal $projectCommandLines.Count $projectLines.Count 'project Tcl command count'
    for ($index = 0; $index -lt $projectLines.Count; $index++) {
        Assert-Equal $projectCommandLines[$index] $projectLines[$index] "project Tcl command order $index"
        if ($projectCommandLines[$index].Contains(';')) { throw "project Tcl 存在多命令分隔符：$($projectCommandLines[$index])" }
    }
    if ($projectTclText.Contains("`r")) { throw 'project Tcl 不是 LF 分隔' }
    $simCommandLines = @($simTclText -split "`n" | Where-Object { $_.Length -gt 0 })
    Assert-Equal $simCommandLines.Count $simLines.Count 'simulation Tcl command count'
    for ($index = 0; $index -lt $simLines.Count; $index++) {
        Assert-Equal $simCommandLines[$index] $simLines[$index] "simulation Tcl command order $index"
        if ($simCommandLines[$index].Contains(';')) { throw "simulation Tcl 存在多命令分隔符：$($simCommandLines[$index])" }
    }
    if ($simTclText.Contains("`r")) { throw 'simulation Tcl 不是 LF 分隔' }
    if ($projectTclText.Contains($script:TargetXprPath) -or $simTclText.Contains($script:TargetXprPath)) {
        throw '生成 Tcl 意外引用主工程 XPR'
    }
    return [ordered]@{
        project_path = $projectXpr
        project_tcl_path = $projectTclPath
        project_tcl_text = $projectTclText
        project_command_lines = @($projectLines.ToArray())
        simulation_tcl_path = (Join-Path $projectDir 'run_project_sim.tcl')
        simulation_tcl_text = $simTclText
        simulation_command_lines = @($simLines.ToArray())
    }
}

function Get-Run11InventoryRecords {
    $allFiles = @(Get-ChildItem -LiteralPath $script:Run11Root -File -Recurse -Force)
    $records = @()
    foreach ($entry in $allFiles) {
        Assert-NoReparseChain $entry.FullName
        $relative = $entry.FullName.Substring($script:Run11Root.Length + 1)
        if ($relative -ieq 'run11_inventory.json') { continue }
        $records += [ordered]@{
            path = $relative
            bytes = [long]$entry.Length
            sha256 = (Get-FileHash -LiteralPath $entry.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    return @($records | Sort-Object -Property path)
}

function Assert-PartialPrepareShape {
    param(
        [Parameter(Mandatory = $true)][string]$TbText,
        [Parameter(Mandatory = $true)][string]$ProjectTclText,
        [Parameter(Mandatory = $true)][string]$SimulationTclText,
        [Parameter(Mandatory = $true)][string]$ContractText
    )
    $expected = [ordered]@{
        'static_tcl_contract.json' = $ContractText
        'isolated_project\create_project.tcl' = $ProjectTclText
        'isolated_project\run_project_sim.tcl' = $SimulationTclText
    }
    $allFiles = @(Get-ChildItem -LiteralPath $script:Run11Root -File -Recurse -Force)
    $actualRelative = @($allFiles | ForEach-Object { $_.FullName.Substring($script:Run11Root.Length + 1) } | Sort-Object)
    $expectedRelative = @($expected.Keys | Sort-Object)
    if (($actualRelative -join "`n") -cne ($expectedRelative -join "`n")) {
        throw "部分 run11 文件集合不符合已知失败快照：$($actualRelative -join ',')"
    }
    $allDirectories = @(Get-ChildItem -LiteralPath $script:Run11Root -Directory -Recurse -Force)
    $actualDirectories = @($allDirectories | ForEach-Object { $_.FullName.Substring($script:Run11Root.Length + 1) } | Sort-Object)
    if (($actualDirectories -join "`n") -cne 'isolated_project') { throw '部分 run11 目录集合不符合已知失败快照' }
    foreach ($relativePath in $expected.Keys) {
        $absolutePath = Join-Path $script:Run11Root $relativePath
        Assert-ExistingUtf8Matches $absolutePath $expected[$relativePath]
    }
    Assert-ExistingUtf8Matches $script:NewTbPath $TbText
    foreach ($missingName in @('project_preflight_binding.json', 'prepare_summary.json', 'prepare.log', 'run11_inventory.json')) {
        if (Test-Path -LiteralPath (Join-Path $script:Run11Root $missingName)) { throw "部分 run11 中存在未预期工件：$missingName" }
    }
    $records = @()
    foreach ($relativePath in $expectedRelative) { $records += Get-FileRecord (Join-Path $script:Run11Root $relativePath) }
    return @($records)
}

function Invoke-Prepare {
    $hostGateBefore = Get-HostGate
    $resumePartial = Test-Path -LiteralPath $script:Run11Root
    if ($resumePartial -ne (Test-Path -LiteralPath $script:NewTbPath)) { throw 'run11 根与 attempt11 TB 只有一方存在，拒绝续写' }
    $parent = Get-ParentBinding -RequireRun11Absent:(-not $resumePartial)
    $tbClone = New-TbCloneText
    $tcl = New-TclFiles
    $tbTextRecord = Get-Utf8TextRecord $script:NewTbPath $tbClone.text
    $projectTclTextRecord = Get-Utf8TextRecord $tcl.project_tcl_path $tcl.project_tcl_text
    $simTclTextRecord = Get-Utf8TextRecord $tcl.simulation_tcl_path $tcl.simulation_tcl_text
    $contract = [ordered]@{
        schema = 'GestureForge-S2A-T59-run11-tcl-contract-v1'
        status = 'PASS_STATIC_ONLY'
        project_tcl = $projectTclTextRecord
        project_command_count = $tcl.project_command_lines.Count
        project_commands = $tcl.project_command_lines
        simulation_tcl = $simTclTextRecord
        simulation_command_count = $tcl.simulation_command_lines.Count
        simulation_commands = $tcl.simulation_command_lines
        separators = 'literal LF; exactly one Tcl command per line'
        target_xpr_opened = $false
        project_is_independent = $true
    }
    $contractPath = Join-Path $script:Run11Root 'static_tcl_contract.json'
    $contractText = ConvertTo-Utf8Json $contract
    $contractTextRecord = Get-Utf8TextRecord $contractPath $contractText

    $partialRecords = @()
    if ($resumePartial) {
        $partialRecords = Assert-PartialPrepareShape -TbText $tbClone.text -ProjectTclText $tcl.project_tcl_text -SimulationTclText $tcl.simulation_tcl_text -ContractText $contractText
    } else {
        if ((Test-Path -LiteralPath $script:Run11Root) -or (Test-Path -LiteralPath $script:NewTbPath)) { throw '新 attempt11 输出路径已出现，拒绝写入' }
        [System.IO.Directory]::CreateDirectory($script:Run11Root) | Out-Null
        [System.IO.Directory]::CreateDirectory((Join-Path $script:Run11Root 'isolated_project')) | Out-Null
    }

    Write-OrVerifyUtf8 $script:NewTbPath $tbClone.text
    Write-OrVerifyUtf8 $tcl.project_tcl_path $tcl.project_tcl_text
    Write-OrVerifyUtf8 $tcl.simulation_tcl_path $tcl.simulation_tcl_text
    Write-OrVerifyUtf8 $contractPath $contractText

    $tbRecord = Get-FileRecord $script:NewTbPath
    $runnerRecord = Get-FileRecord $PSCommandPath
    $projectTclRecord = Get-FileRecord $tcl.project_tcl_path
    $simTclRecord = Get-FileRecord $tcl.simulation_tcl_path
    $contractRecord = Get-FileRecord $contractPath

    $binding = [ordered]@{
        schema = 'GestureForge-S2A-T59-run11-project-preflight-binding-v1'
        task_id = 'S2A-T59'
        run_id = 'run11'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        baseline_head = $script:ExpectedHead
        current_head = $hostGateBefore.git_head
        resumed_existing_partial = [bool]$resumePartial
        run10_parent = [ordered]@{
            summary = $parent.summary_record
            project_preflight_binding = $parent.project_binding_record
            fixture_manifest = $parent.manifest_record
            fixture_files = $parent.fixture_files
            verification_status = 'run10 --verify-only PASS was provided by the parent task card; this Prepare runner did not execute it'
        }
        target_xpr = $parent.target_xpr
        T59_source_hashes = $parent.T59_source_hashes
        attempt11_testbench = $tbRecord
        runner = $runnerRecord
        project_tcl = $projectTclRecord
        simulation_tcl = $simTclRecord
        static_tcl_contract = $contractRecord
        tb_io_paths = [ordered]@{
            fixture_inputs = @($parent.fixture_files['feature_input.bin'].path, $parent.fixture_files['layer35_weights.bin'].path, $parent.fixture_files['golden.bin'].path, $parent.fixture_files['vectors.txt'].path)
            observed_outputs = @((Join-Path $script:Run11Root 'observed_raw.bin'), (Join-Path $script:Run11Root 'observed_output.bin'))
        }
        opened_target_xpr = $false
        vivado_cli_invoked = $false
        xsim_cli_invoked = $false
    }
    $bindingPath = Join-Path $script:Run11Root 'project_preflight_binding.json'
    Write-NewUtf8 $bindingPath (ConvertTo-Utf8Json $binding)
    $bindingFileRecord = Get-FileRecord $bindingPath

    $summary = [ordered]@{
        schema = 'GestureForge-S2A-T59-run11-preparation-summary-v1'
        task_id = 'S2A-T59'
        run_id = 'run11'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        baseline_head = $script:ExpectedHead
        current_head = $hostGateBefore.git_head
        resumed_existing_partial = [bool]$resumePartial
        scope = 'tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25'
        expected_counts = [ordered]@{ output_cases = 6656; raw_int32_compares = 6656; quantized_int8_compares = 6656 }
        prepare_attempt_history = @(
            [ordered]@{
                attempt = 1
                actual_exit_code = 1
                failure_reason = 'Get-NetTCPConnection 在 7654 无匹配对象时抛出 CIM no-match。'
                files_written = $false
                failure_timestamp_captured = $false
            },
            [ordered]@{
                attempt = 2
                actual_exit_code = 1
                failure_reason = 'PowerShell OrderedDictionary 对带点键 feature_input.bin 使用了错误的点号属性访问。'
                files_written = $true
                failure_timestamp_captured = $false
                preexisting_partial_artifacts = $partialRecords
                partial_artifacts_revalidated_byte_for_byte = [bool]$resumePartial
            }
        )
        parent_run10_summary = $parent.summary_record
        parent_run10_manifest = $parent.manifest_record
        parent_run10_binding = $parent.project_binding_record
        run10_four_fixture_inputs = $parent.fixture_files
        T59_source_hashes = $parent.T59_source_hashes
        target_xpr = $parent.target_xpr
        attempt11_testbench = $tbRecord
        runner = $runnerRecord
        project_preflight_binding = $bindingFileRecord
        static_tcl_contract = $contractRecord
        project_tcl = $projectTclRecord
        simulation_tcl = $simTclRecord
        tb_io_paths = $binding.tb_io_paths
        logs = [ordered]@{ prepare_log = (Join-Path $script:Run11Root 'prepare.log'); future_simulation_log = (Join-Path $script:Run11Root 'simulate.log') }
        runtime_preflight = $hostGateBefore
        simulation = [ordered]@{ status = 'NOT_RUN'; vivado_cli_invoked = $false; xsim_cli_invoked = $false; mcp_used = $false }
        limitations = @('此证据仅为 run11 静态准备，不是 RTL 仿真结果。', 'run10 --verify-only PASS 来自任务卡陈述，本脚本未重跑。', '不得推及整层/整网、G3、G4 或 G5。')
    }
    $summaryPath = Join-Path $script:Run11Root 'prepare_summary.json'
    Write-NewUtf8 $summaryPath (ConvertTo-Utf8Json $summary)
    $summaryFileRecord = Get-FileRecord $summaryPath

    $logText = @(
        'task=S2A-T59 run=run11 mode=Prepare'
        "command=pwsh -NoProfile -File `"$PSCommandPath`" -Mode Prepare"
        "cwd=$script:RepoRoot"
        "head=$($hostGateBefore.git_head)"
        "resumed_existing_partial=$([bool]$resumePartial)"
        'prior_attempt_1=FAIL exit_code=1 writes=false cause=listener_probe_no_match'
        'prior_attempt_2=FAIL exit_code=1 partial_outputs_byte_verified_no_overwrite=true cause=fixture_key_dot_access'
        'vivado_cli_invoked=false'
        'xsim_cli_invoked=false'
        "attempt11_tb_sha256=$($tbRecord.sha256)"
        "project_tcl_sha256=$($projectTclRecord.sha256)"
        "simulation_tcl_sha256=$($simTclRecord.sha256)"
        'status=DRYRUN_READY_NOT_SIMULATED'
        'exit_code=0'
    ) -join "`n"
    Write-NewUtf8 (Join-Path $script:Run11Root 'prepare.log') ($logText + "`n")

    $hostGateAfter = Get-HostGate
    Assert-Equal $hostGateAfter.git_head $hostGateBefore.git_head 'Prepare 后 HEAD'
    $xprAfter = Get-FileRecord $script:TargetXprPath
    Assert-Equal $xprAfter.sha256 $parent.target_xpr.sha256 'Prepare 后目标 XPR SHA256'
    $inventoryRecords = Get-Run11InventoryRecords
    $inventory = [ordered]@{
        schema = 'GestureForge-S2A-T59-run11-inventory-v1'
        task_id = 'S2A-T59'
        run_id = 'run11'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        baseline_head = $script:ExpectedHead
        file_count = $inventoryRecords.Count
        files = $inventoryRecords
    }
    Write-NewUtf8 (Join-Path $script:Run11Root 'run11_inventory.json') (ConvertTo-Utf8Json $inventory)
    Write-Output 'PREPARE=PASS status=DRYRUN_READY_NOT_SIMULATED files=6 fixture_inputs=4 outputs=run11_only'
    Write-Output "TB_SHA256=$($tbRecord.sha256)"
    Write-Output "RUNNER_SHA256=$($runnerRecord.sha256)"
    Write-Output "SUMMARY_SHA256=$($summaryFileRecord.sha256)"
}

function Invoke-AuditInventory {
    $hostGate = Get-HostGate
    $parent = Get-ParentBinding
    $inventoryPath = Join-Path $script:Run11Root 'run11_inventory.json'
    Assert-NoReparseChain $inventoryPath
    $inventoryRecord = Get-FileRecord $inventoryPath
    $inventory = Get-Content -LiteralPath $inventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $inventory.task_id 'S2A-T59' 'run11 inventory task id'
    Assert-Equal $inventory.run_id 'run11' 'run11 inventory id'
    Assert-Equal $inventory.status 'DRYRUN_READY_NOT_SIMULATED' 'run11 inventory status'
    Assert-Equal $inventory.baseline_head $script:ExpectedHead 'run11 inventory baseline'

    $actualRecords = Get-Run11InventoryRecords
    Assert-Equal $inventory.file_count $actualRecords.Count 'run11 inventory file count'
    $expectedByPath = @{}
    foreach ($entry in $inventory.files) { $expectedByPath[[string]$entry.path] = $entry }
    foreach ($actual in $actualRecords) {
        if (-not $expectedByPath.ContainsKey([string]$actual.path)) { throw "inventory 缺少文件：$($actual.path)" }
        Assert-Equal $actual.bytes $expectedByPath[[string]$actual.path].bytes "inventory bytes $($actual.path)"
        Assert-Equal $actual.sha256 $expectedByPath[[string]$actual.path].sha256 "inventory SHA256 $($actual.path)"
    }
    foreach ($entry in $inventory.files) {
        if (-not ($actualRecords.path -contains [string]$entry.path)) { throw "inventory 指向不存在文件：$($entry.path)" }
    }

    $summaryPath = Join-Path $script:Run11Root 'prepare_summary.json'
    $bindingPath = Join-Path $script:Run11Root 'project_preflight_binding.json'
    $contractPath = Join-Path $script:Run11Root 'static_tcl_contract.json'
    $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $binding = Get-Content -LiteralPath $bindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $contract = Get-Content -LiteralPath $contractPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $summary.status 'DRYRUN_READY_NOT_SIMULATED' 'run11 summary status'
    Assert-Equal $summary.current_head $hostGate.git_head 'run11 summary HEAD'
    Assert-Equal $binding.status 'DRYRUN_READY_NOT_SIMULATED' 'run11 binding status'
    Assert-Equal $binding.target_xpr.sha256 $parent.target_xpr.sha256 'run11 XPR binding'
    Assert-Equal $binding.attempt11_testbench.sha256 (Get-FileRecord $script:NewTbPath).sha256 'run11 TB binding'
    Assert-Equal $binding.runner.sha256 (Get-FileRecord $PSCommandPath).sha256 'run11 runner binding'
    Assert-Equal $contract.status 'PASS_STATIC_ONLY' 'run11 Tcl contract status'
    if ($contract.project_tcl.sha256 -cne (Get-FileRecord $contract.project_tcl.path).sha256) { throw 'project Tcl SHA256 与合同不符' }
    if ($contract.simulation_tcl.sha256 -cne (Get-FileRecord $contract.simulation_tcl.path).sha256) { throw 'simulation Tcl SHA256 与合同不符' }
    if ($contract.project_tcl.bytes -le 0 -or $contract.simulation_tcl.bytes -le 0) { throw 'Tcl 文件为空' }
    $xprAfter = Get-FileRecord $script:TargetXprPath
    Assert-Equal $xprAfter.sha256 $parent.target_xpr.sha256 'AuditInventory 目标 XPR SHA256'

    Write-Output 'AUDIT_INVENTORY=PASS status=DRYRUN_READY_NOT_SIMULATED'
    Write-Output "INVENTORY_SHA256=$($inventoryRecord.sha256)"
    Write-Output "INVENTORY_FILES=$($inventory.file_count)"
    Write-Output "CURRENT_HEAD=$($hostGate.git_head)"
}

if ($Mode -eq 'Prepare') {
    Invoke-Prepare
} else {
    Invoke-AuditInventory
}
