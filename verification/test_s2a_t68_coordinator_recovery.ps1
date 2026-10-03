[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$path = Join-Path $PSScriptRoot 'run_s2a_t68_unattended_continuation.ps1'
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
if($errors.Count){throw $errors[0].Message}
foreach($name in @('Get-Sha256Literal','Assert-NormalFile','Read-JsonObject','Assert-FailedCoordinatorRecovery')){
    $functionName=$name
    $node=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $functionName},$true)
    . ([scriptblock]::Create($node.Extent.Text))
}
$root=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$evidence=(Get-Item -LiteralPath (Join-Path $root 'report/evidence/S2A-T68/manual_20261002_140325')).FullName
$run='manual_20261002_140325'
$summary=Join-Path $evidence ('unattended_continuation_'+$run+'.json')
$hash='f1a38f2c37d94fbf27d3ba8de959b8067dc8657ee87bbb62d7982856ea873a9e'
$backend='3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
Assert-FailedCoordinatorRecovery -SummaryPath $summary -ExpectedSummaryHash $hash -EvidenceRoot $evidence -ExpectedRunId $run -ExpectedBackendHash $backend
$count=1
foreach($change in @(@{ExpectedSummaryHash=('0'*64)},@{ExpectedRunId='wrong_run'},@{ExpectedBackendHash=('0'*64)},@{EvidenceRoot=$root})){
    $arguments=@{SummaryPath=$summary;ExpectedSummaryHash=$hash;EvidenceRoot=$evidence;ExpectedRunId=$run;ExpectedBackendHash=$backend}
    foreach($key in $change.Keys){$arguments[$key]=$change[$key]}
    $rejected=$false
    try {Assert-FailedCoordinatorRecovery @arguments} catch {$rejected=$true}
    if(-not $rejected){throw '非法恢复绑定被接受'}
    $count++
}
if((Get-Sha256Literal -Path $summary) -cne $hash){throw '旧summary发生变化'}
[ordered]@{status='PASS';cases=$count;coordinator_sha256=(Get-Sha256Literal -Path $path);original_summary_sha256=$hash;original_summary_unchanged=$true;simulator_invocations=0} | ConvertTo-Json