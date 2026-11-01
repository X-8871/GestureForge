#!/usr/bin/env bash
set -euo pipefail
export HOME="$(cygpath -u "$HOME")"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export TMPDIR="$(cygpath -u "$TMPDIR")"
powershell.exe -NoLogo -NoProfile -Command '$PSVersionTable | Out-String; Write-Output "PSHOME=$PSHOME"; Write-Output "PSModulePath=$env:PSModulePath"; Write-Output "PATH=$env:PATH"; Get-Command Get-FileHash -ErrorAction SilentlyContinue; Import-Module Microsoft.PowerShell.Utility -ErrorAction Continue; Get-Command Get-FileHash -ErrorAction Continue'