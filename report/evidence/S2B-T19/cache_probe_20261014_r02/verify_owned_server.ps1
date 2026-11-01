$ErrorActionPreference = 'Stop'
$identityPath = 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261014_r02\hw_server_identity.json'
$identity = Get-Content -LiteralPath $identityPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($identity.status -cne 'OWNED_SERVER_READY') { throw 'owned server receipt not ready' }
$native = $identity.native
$process = Get-CimInstance Win32_Process -Filter "ProcessId=$($native.ProcessId)"
if ($null -eq $process) { throw 'owned hw_server process absent' }
$birth = $process.CreationDate.ToFileTimeUtc().ToString()
$hash = (Get-FileHash -LiteralPath $process.ExecutablePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($birth -cne [string]$native.CreationTimeFileTimeUtc -or $process.ExecutablePath -cne [string]$native.ExecutablePath -or $process.CommandLine -cne [string]$native.CommandLine -or $hash -cne [string]$identity.native_sha256) { throw 'owned hw_server identity drift' }
$listeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction Stop)
if ($listeners.Count -ne 1 -or $listeners[0].OwningProcess -ne [int]$native.ProcessId) { throw '3121 listener identity mismatch' }
Write-Output ('OWNED_SERVER_HEALTHY pid={0} port=3121' -f [int]$native.ProcessId)
