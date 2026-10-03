[CmdletBinding()]
param()

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Test-WindowsPathWithin {
    param(
        [Parameter(Mandatory = $true)][string]$Candidate,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $candidatePath = [System.IO.Path]::GetFullPath($Candidate)
    $rootPath = [System.IO.Path]::GetFullPath($Root)
    $separators = [char[]]@(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $rootPath = $rootPath.TrimEnd($separators)
    if ([string]::IsNullOrEmpty($rootPath)) {
        $rootPath = [System.IO.Path]::GetPathRoot([System.IO.Path]::GetFullPath($Root))
    }

    if ([string]::Equals(
            $candidatePath,
            $rootPath,
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        return $true
    }

    $rootPrefix = $rootPath + [System.IO.Path]::DirectorySeparatorChar
    return $candidatePath.StartsWith(
        $rootPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

try {
    $scriptPath = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
    $repoRoot = [System.IO.Directory]::GetParent($PSScriptRoot).FullName
    $tclPath = [System.IO.Path]::GetFullPath(
        (Join-Path $PSScriptRoot 's3_probe_debug_hub_opt.tcl')
    )
    $isolatedRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $repoRoot 'tmp\s3s05')
    )
    $outsideBase = [System.IO.Directory]::GetParent($isolatedRoot).FullName
    $expectedTclSha256 = 'f2c04c75ed6016089e32e940f72ade9a339bc4aa4a1b02dd538a00acde88762d'

    $scriptSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $scriptPath).Hash.ToLowerInvariant()
    $tclSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $tclPath).Hash.ToLowerInvariant()
    $tclSource = [System.IO.File]::ReadAllText($tclPath, [System.Text.Encoding]::UTF8)
    $procMatch = [regex]::Match(
        $tclSource,
        '(?ms)^proc\s+s3_path_within\s+\{candidate\s+root\}\s+\{(?<body>.*?)^\}'
    )

    $scriptPassed = $true
    [System.Console]::Out.WriteLine(('SCRIPT_PATH="{0}"' -f $scriptPath))
    [System.Console]::Out.WriteLine(('SCRIPT_SHA256={0}' -f $scriptSha256))
    [System.Console]::Out.WriteLine(('TCL_PATH="{0}"' -f $tclPath))
    $hashResult = 'PASS'
    if ($tclSha256 -ne $expectedTclSha256) {
        $hashResult = 'FAIL'
        $scriptPassed = $false
    }
    [System.Console]::Out.WriteLine((
        'TCL_SHA256 expected={0} actual={1} result={2}' -f
        $expectedTclSha256, $tclSha256, $hashResult
    ))

    $contractResults = @()
    if ($procMatch.Success) {
        $body = $procMatch.Groups['body'].Value
        $bodyFlat = [regex]::Replace($body, '\s+', ' ').Trim()
        $contractResults += New-Object PSObject -Property @{
            name = 'procedure_definition'
            passed = $true
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'candidate_normalized'
            passed = [regex]::IsMatch($body, '(?m)^\s*set candidate \[file normalize \$candidate\]\s*$')
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'root_normalized'
            passed = $bodyFlat.Contains('set root [string trimright [file normalize $root] "/\\"]')
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'exact_root_allowed_case_insensitively'
            passed = $bodyFlat.Contains('if {[string equal -nocase $candidate $root]} { return 1 }')
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'prefix_comparison_case_insensitive'
            passed = ([regex]::Matches($body, 'string equal -nocase').Count -ge 2)
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'descendant_boundary_requires_separator'
            passed = (
                $bodyFlat.Contains('set separator [string index $candidate $root_length]') -and
                $bodyFlat.Contains('return [expr {$separator eq "/" || $separator eq "\\"}]')
            )
        }
        $contractResults += New-Object PSObject -Property @{
            name = 'non_descendants_rejected'
            passed = $bodyFlat.Contains(
                'if {[string length $candidate] <= $root_length || ![string equal -nocase [string range $candidate 0 [expr {$root_length - 1}]] $root]} { return 0 }'
            )
        }
    }
    else {
        $contractResults += New-Object PSObject -Property @{
            name = 'procedure_definition'
            passed = $false
        }
    }

    foreach ($contract in $contractResults) {
        $result = 'PASS'
        if (-not $contract.passed) {
            $result = 'FAIL'
            $scriptPassed = $false
        }
        [System.Console]::Out.WriteLine((
            'CONTRACT name={0} result={1}' -f $contract.name, $result
        ))
    }

    $matrix = @(
        New-Object PSObject -Property @{
            name = 'inside_project'
            candidate = Join-Path $isolatedRoot.ToUpperInvariant() 'project\design_1.xpr'
            expected = $true
        }
        New-Object PSObject -Property @{
            name = 'outside_project'
            candidate = Join-Path $outsideBase 's3s05_outside\project\design_1.xpr'
            expected = $false
        }
        New-Object PSObject -Property @{
            name = 'prefix_sibling'
            candidate = ($isolatedRoot + '_sibling\project\design_1.xpr')
            expected = $false
        }
        New-Object PSObject -Property @{
            name = 'dotdot_escape'
            candidate = Join-Path $isolatedRoot '..\s3s05_dotdot_escape\project\design_1.xpr'
            expected = $false
        }
        New-Object PSObject -Property @{
            name = 'inside_result'
            candidate = Join-Path $isolatedRoot 'guard_result\result.txt'
            expected = $true
        }
        New-Object PSObject -Property @{
            name = 'outside_result'
            candidate = Join-Path $outsideBase 's3s05_guard_outside_output'
            expected = $false
        }
    )

    $caseCount = 0
    $caseFailures = 0
    foreach ($case in $matrix) {
        $candidateInput = [string]$case.candidate
        $candidateIsAbsolute = [System.IO.Path]::IsPathRooted($candidateInput)
        $canonicalCandidate = [System.IO.Path]::GetFullPath($candidateInput)
        $actual = $false
        if ($candidateIsAbsolute) {
            $actual = Test-WindowsPathWithin -Candidate $candidateInput -Root $isolatedRoot
        }
        $caseCount++
        $result = 'PASS'
        if ((-not $candidateIsAbsolute) -or ($actual -ne $case.expected)) {
            $result = 'FAIL'
            $caseFailures++
            $scriptPassed = $false
        }
        $expectedText = 'REJECT'
        $actualText = 'REJECT'
        if ($case.expected) {
            $expectedText = 'ALLOW'
        }
        if ($actual) {
            $actualText = 'ALLOW'
        }
        [System.Console]::Out.WriteLine((
            'CASE name={0} input="{1}" canonical="{2}" root="{3}" expected={4} actual={5} result={6}' -f
            $case.name, $candidateInput, $canonicalCandidate, $isolatedRoot, $expectedText, $actualText, $result
        ))
    }

    $contractFailures = @($contractResults | Where-Object { -not $_.passed }).Count
    if ($scriptPassed) {
        $exitCode = 0
    }
    else {
        $exitCode = 1
    }
    [System.Console]::Out.WriteLine((
        'SUMMARY contracts={0} contract_failures={1} cases={2} case_failures={3} result={4}' -f
        $contractResults.Count, $contractFailures, $caseCount, $caseFailures,
        $(if ($scriptPassed) { 'PASS' } else { 'FAIL' })
    ))
    [System.Console]::Out.WriteLine(('EXIT_CODE={0}' -f $exitCode))
    exit $exitCode
}
catch {
    [System.Console]::Error.WriteLine(('ERROR: {0}' -f $_.Exception.Message))
    [System.Console]::Out.WriteLine('EXIT_CODE=1')
    exit 1
}
