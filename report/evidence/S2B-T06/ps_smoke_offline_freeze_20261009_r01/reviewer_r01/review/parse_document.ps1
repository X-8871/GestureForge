param([Parameter(Mandatory=$true)][string]$BlocksPath)
# 只调用PowerShell语法解析器，不执行文档中的任何命令。
$blocks = [System.IO.File]::ReadAllText($BlocksPath, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
$result = @()
foreach ($block in $blocks) {
    if ($block.language -eq 'powershell') {
        $tokens = $null
        $parseErrors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseInput([string]$block.source, [ref]$tokens, [ref]$parseErrors)
        $result += @{index=$block.index; language=$block.language; errors=@($parseErrors | ForEach-Object { $_.Message })}
    }
}
$result | ConvertTo-Json -Depth 5
if (@($result | Where-Object { $_.errors.Count -ne 0 }).Count -ne 0) { exit 1 }
exit 0
