$ErrorActionPreference='Stop'
$attemptRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05\attempt05'
$productionRunner=Join-Path $attemptRoot 'run05_runner_attempt05_safe.ps1'
$testRoot=(Get-Item -LiteralPath $PSScriptRoot -Force -ErrorAction Stop).FullName
$fixturesRoot=Join-Path $testRoot 'fixtures'
if(Test-Path -LiteralPath $fixturesRoot){throw "离线夹具目录已存在，拒绝覆盖：$fixturesRoot"}
New-Item -ItemType Directory -Path $fixturesRoot | Out-Null
$utf8NoBom=New-Object System.Text.UTF8Encoding($false)
$results=New-Object 'System.Collections.Generic.List[object]'

function Get-TestSha256([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Write-TestJson([string]$path,$value){[IO.File]::WriteAllText($path,($value|ConvertTo-Json -Depth 20),$utf8NoBom)}
function Get-FixtureSnapshot([string]$root){
    $items=New-Object 'System.Collections.Generic.List[string]'
    foreach($item in @(Get-ChildItem -LiteralPath $root -Force -Recurse | Sort-Object FullName)){
        $relative=$item.FullName.Substring($root.Length).TrimStart([char[]]@('\','/'))
        if($item.PSIsContainer){$items.Add(('D|'+$relative))}
        else{$items.Add(('F|'+$relative+'|'+$item.Length+'|'+(Get-TestSha256 $item.FullName)))}
    }
    return ($items -join "`n")
}
function New-ManifestFixture([string]$name){
    $root=Join-Path $fixturesRoot $name
    New-Item -ItemType Directory -Path $root | Out-Null
    $runnerPath=Join-Path $root 'run05_runner_attempt05_safe.ps1'
    Copy-Item -LiteralPath $productionRunner -Destination $runnerPath
    $entries=New-Object 'System.Collections.Generic.List[object]'
    for($index=1;$index -le 21;$index++){
        $leaf=('input_{0:D2}.bin' -f $index)
        $path=Join-Path $root $leaf
        $bytes=[Text.Encoding]::UTF8.GetBytes(('fixture-input-{0:D2}' -f $index))
        [IO.File]::WriteAllBytes($path,$bytes)
        $entries.Add([pscustomobject]@{path=$path;bytes=$bytes.Length;sha256=(Get-TestSha256 $path)})
    }
    $runnerInfo=Get-Item -LiteralPath $runnerPath -Force
    $runnerHash=Get-TestSha256 $runnerPath
    $entries.Add([pscustomobject]@{path=$runnerPath;bytes=$runnerInfo.Length;sha256=$runnerHash})
    $manifest=[ordered]@{
        schema='S2A-T61-attempt-input-manifest-v2'
        task_id='S2A-T61'
        run_id='run05'
        attempt='attempt05'
        status='PREPARED_NOT_RUN'
        execution_runner=$runnerPath
        execution_runner_bytes=[long]$runnerInfo.Length
        execution_runner_sha256=$runnerHash
        file_count=22
        files=@($entries.ToArray())
    }
    $manifestPath=Join-Path $root 'input_manifest.json'
    Write-TestJson $manifestPath $manifest
    return [pscustomobject]@{root=$root;runner=$runnerPath;manifest=$manifestPath}
}
function Set-FixtureManifest([string]$manifestPath,$manifest){Write-TestJson $manifestPath $manifest}
function Invoke-ManifestCase([string]$name,[bool]$expectPass,[string]$expectedMessage=''){
    $fixture=New-ManifestFixture $name
    $manifest=Get-Content -LiteralPath $fixture.manifest -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop
    switch($name){
        'bad_schema' {$manifest.schema='wrong-schema';Set-FixtureManifest $fixture.manifest $manifest}
        'bad_task' {$manifest.task_id='wrong-task';Set-FixtureManifest $fixture.manifest $manifest}
        'bad_run' {$manifest.run_id='wrong-run';Set-FixtureManifest $fixture.manifest $manifest}
        'bad_attempt' {$manifest.attempt='attempt04';Set-FixtureManifest $fixture.manifest $manifest}
        'bad_status' {$manifest.status='RUN_COMPLETED';Set-FixtureManifest $fixture.manifest $manifest}
        'bad_file_count' {$manifest.file_count=21;Set-FixtureManifest $fixture.manifest $manifest}
        'runner_path_mismatch' {$manifest.execution_runner=($fixture.runner+'.copy');Set-FixtureManifest $fixture.manifest $manifest}
        'bad_input_sha' {$manifest.files[0].sha256=('0'*64);Set-FixtureManifest $fixture.manifest $manifest}
        'missing_input' {Remove-Item -LiteralPath $manifest.files[0].path -Force}
        'path_escape' {$manifest.files[0].path=[IO.Path]::GetFullPath((Join-Path $fixture.root '..\escaped.bin'));Set-FixtureManifest $fixture.manifest $manifest}
        'duplicate_path' {$manifest.files[1].path=$manifest.files[0].path;Set-FixtureManifest $fixture.manifest $manifest}
        'bad_runner_sha' {$manifest.execution_runner_sha256=('0'*64);Set-FixtureManifest $fixture.manifest $manifest}
        'bad_runner_bytes' {$manifest.execution_runner_bytes=[long]$manifest.execution_runner_bytes+1;Set-FixtureManifest $fixture.manifest $manifest}
        'bad_runner_file_sha' {$manifest.files[21].sha256=('0'*64);Set-FixtureManifest $fixture.manifest $manifest}
        default {}
    }
    $before=Get-FixtureSnapshot $fixture.root
    $caught=$false
    $failure=''
    $output=''
    try{
        $captured=@(& $fixture.runner -ValidateManifestOnly 2>&1)
        $output=($captured|ForEach-Object {[string]$_}) -join "`n"
    }catch{$caught=$true;$failure=$_.Exception.Message}
    $after=Get-FixtureSnapshot $fixture.root
    $noWrites=[string]::Equals($before,$after,[StringComparison]::Ordinal)
    $hasPass=$output.Contains('T61_MANIFEST_VALIDATION_PASS')
    $message=$failure
    if(-not $message){$message=$output}
    $accepted=$false
    if($expectPass){$accepted=(-not $caught -and $hasPass -and $noWrites)}
    else{
        $rejected=($caught -or -not $hasPass)
        $messageMatches=($expectedMessage.Length -eq 0 -or $message.Contains($expectedMessage))
        $accepted=($rejected -and $messageMatches -and $noWrites)
    }
    $results.Add([pscustomobject]@{case=$name;expected=$(if($expectPass){'PASS'}else{'REJECT'});actual=$(if($hasPass){'PASS'}elseif($caught){'REJECT'}else{'NO_PASS'});assertion=$(if($accepted){'PASS'}else{'FAIL'});no_files_written=$noWrites;message=$message})
}

try{
    Invoke-ManifestCase 'valid' $true
    Invoke-ManifestCase 'bad_schema' $false 'schema 不匹配'
    Invoke-ManifestCase 'bad_task' $false 'task_id 不匹配'
    Invoke-ManifestCase 'bad_run' $false 'run_id 不匹配'
    Invoke-ManifestCase 'bad_attempt' $false 'attempt 不匹配'
    Invoke-ManifestCase 'bad_status' $false 'status 不匹配'
    Invoke-ManifestCase 'bad_file_count' $false 'file_count 必须是整数 22'
    Invoke-ManifestCase 'runner_path_mismatch' $false 'execution_runner 不一致'
    Invoke-ManifestCase 'bad_input_sha' $false 'SHA-256 不匹配'
    Invoke-ManifestCase 'missing_input' $false
    Invoke-ManifestCase 'path_escape' $false '越出 attempt05 根目录'
    Invoke-ManifestCase 'duplicate_path' $false '重复路径'
    Invoke-ManifestCase 'bad_runner_sha' $false '顶层绑定不匹配'
    Invoke-ManifestCase 'bad_runner_bytes' $false '顶层绑定不匹配'
    Invoke-ManifestCase 'bad_runner_file_sha' $false 'SHA-256 不匹配'
    $failed=@($results | Where-Object {$_.assertion -ne 'PASS'})
    foreach($result in $results){[Console]::Out.WriteLine(('CASE_{0} {1} no_writes={2}' -f $result.assertion.ToUpperInvariant(),$result.case,$result.no_files_written))}
    if($failed.Count -gt 0){[Console]::Error.WriteLine(('MANIFEST_GUARD_OFFLINE_FAIL failed={0} total={1} simulation=NO_SIMULATION' -f $failed.Count,$results.Count));exit 1}
    [Console]::Out.WriteLine(('MANIFEST_GUARD_OFFLINE_PASS tests={0} simulation=NO_SIMULATION' -f $results.Count))
    exit 0
}finally{
    foreach($definition in @(
        [pscustomobject]@{parent=(Join-Path $testRoot 'static_r4_ps7');name='fault_fixtures_r3_ps7'},
        [pscustomobject]@{parent=(Join-Path $testRoot 'static_r4_ps51');name='fault_fixtures_r3_ps51'},
        [pscustomobject]@{parent=(Join-Path $testRoot 'static_r5_ps7');name='fault_fixtures_r3_ps7'},
        [pscustomobject]@{parent=(Join-Path $testRoot 'static_r5_ps51');name='fault_fixtures_r3_ps51'}
    )){
        if(Test-Path -LiteralPath $definition.parent -PathType Container){
            $parentFull=(Get-Item -LiteralPath $definition.parent -Force -ErrorAction Stop).FullName
            $staticFixture=Join-Path $definition.parent $definition.name
            if(Test-Path -LiteralPath $staticFixture){
            $staticFull=(Resolve-Path -LiteralPath $staticFixture -ErrorAction Stop).Path
            $staticItem=Get-Item -LiteralPath $staticFull -Force
            if(-not [string]::Equals($staticFull,[IO.Path]::GetFullPath($staticFixture),[StringComparison]::Ordinal) -or -not $staticFull.StartsWith($parentFull+'\',[StringComparison]::OrdinalIgnoreCase) -or -not $staticItem.PSIsContainer -or (($staticItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)){throw "静态测试临时目录路径或类型异常：$staticFull"}
            foreach($item in @(Get-ChildItem -LiteralPath $staticFull -Force -Recurse)){
                if(-not $item.FullName.StartsWith($staticFull+'\',[StringComparison]::OrdinalIgnoreCase) -or (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)){throw "静态测试临时目录含重解析或越界路径：$($item.FullName)"}
            }
            Remove-Item -LiteralPath $staticFull -Recurse -Force
            }
        }
    }
    $fixturePath=(Get-Item -LiteralPath $fixturesRoot -Force -ErrorAction Stop).FullName
    $expectedFixturePath=[IO.Path]::GetFullPath((Join-Path $testRoot 'fixtures'))
    if(-not [string]::Equals($fixturePath,$expectedFixturePath,[StringComparison]::Ordinal)){throw '清理目标不是本轮离线夹具目录'}
    $fixtureItem=Get-Item -LiteralPath $fixturePath -Force
    if(-not $fixtureItem.PSIsContainer -or (($fixtureItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)){throw '清理目标不是普通目录'}
    Remove-Item -LiteralPath $fixturePath -Recurse -Force
}
