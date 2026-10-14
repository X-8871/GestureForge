$ErrorActionPreference = 'Stop'
$path = [IO.Path]::GetFullPath('tmp/2B/S2B-T19/board_run_20261014_r02/start_owned_server.ps1')
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
$result = [ordered]@{
    path = $path
    powershell_version = $PSVersionTable.PSVersion.ToString()
    parse_error_count = @($errors).Count
    parse_errors = @($errors | ForEach-Object Message)
}
$result | ConvertTo-Json -Depth 4
if (@($errors).Count -ne 0) { exit 1 }
