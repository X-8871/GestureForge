param([Parameter(Mandatory=$true)][string]$Plan)
# 仅使用Windows原生只读接口；所有删除操作留在Git Bash。
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$auditPlan = [System.IO.File]::ReadAllText($Plan,[System.Text.Encoding]::UTF8) | ConvertFrom-Json
if ($auditPlan.run_id -ne 'cache_cleanup_20261012_r01' -or $auditPlan.files.Count -ne 1470) { throw '清单身份不符' }
$auditParents = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
foreach ($auditFile in $auditPlan.files) {
    $auditAttr = [System.IO.File]::GetAttributes($auditFile.path)
    if (($auditAttr -band [System.IO.FileAttributes]::Directory) -or ($auditAttr -band [System.IO.FileAttributes]::ReparsePoint)) { throw ('不是普通文件：'+$auditFile.path) }
    if ((New-Object System.IO.FileInfo($auditFile.path)).Length -ne $auditFile.bytes) { throw ('文件大小变化：'+$auditFile.path) }
    $auditParent = [System.IO.Path]::GetDirectoryName($auditFile.path)
    while ($auditParent) {
        [void]$auditParents.Add($auditParent)
        $auditNext = [System.IO.Path]::GetDirectoryName($auditParent)
        if ($auditNext -eq $auditParent) { break }
        $auditParent = $auditNext
    }
}
foreach ($auditParent in $auditParents) {
    $auditAttr = [System.IO.File]::GetAttributes($auditParent)
    if (-not ($auditAttr -band [System.IO.FileAttributes]::Directory) -or ($auditAttr -band [System.IO.FileAttributes]::ReparsePoint)) { throw ('父路径类型异常：'+$auditParent) }
}
$auditRefs = @('C:\SWSetup\sp160053')
foreach ($auditFile in $auditPlan.allowed_update_files) { $auditRefs += [System.IO.Path]::GetDirectoryName($auditFile) }
$auditBlocked = @()
foreach ($auditProc in (Get-CimInstance Win32_Process)) {
    $auditMatch = $auditProc.Name -match '^(msiexec|setup|HPUP)\.exe$'
    foreach ($auditRef in $auditRefs) {
        if (($auditProc.ExecutablePath -and $auditProc.ExecutablePath.IndexOf($auditRef,[StringComparison]::OrdinalIgnoreCase) -ge 0) -or ($auditProc.CommandLine -and $auditProc.CommandLine.IndexOf($auditRef,[StringComparison]::OrdinalIgnoreCase) -ge 0)) { $auditMatch = $true }
    }
    if ($auditMatch) { $auditBlocked += [PSCustomObject]@{Kind='process';Name=$auditProc.Name;Id=$auditProc.ProcessId} }
}
foreach ($auditClass in @('Win32_Service','Win32_SystemDriver')) {
    foreach ($auditSvc in (Get-CimInstance $auditClass)) {
        foreach ($auditRef in $auditRefs) {
            if ($auditSvc.PathName -and $auditSvc.PathName.IndexOf($auditRef,[StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $auditBlocked += [PSCustomObject]@{Kind=$auditClass;Name=$auditSvc.Name}
                break
            }
        }
    }
}
if ($auditBlocked.Count) { $auditBlocked | ConvertTo-Json -Depth 4 -Compress; throw '存在安装任务或目标依赖，停止清理' }
[PSCustomObject]@{Status='WINDOWS_GUARD_OK';Utc=[DateTime]::UtcNow.ToString('o');Files=$auditPlan.files.Count;AncestorDirectories=$auditParents.Count;ReparsePoints=0;BlockedOwners=0} | ConvertTo-Json -Compress

