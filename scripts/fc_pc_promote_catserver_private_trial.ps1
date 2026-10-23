# Atomically promote staged official CatServer to the STOPPED HidenCloud root.
# Requires owner's Offline confirmation and a completed PRIVATE PC checkpoint.
# Only the two root JAR names may change; never touches world/config/mods/plugins.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$temp=$null
$oldMoved=$false
$promoted=$false
$rollbackVerified=$false
$rollbackName=$null
$failedName=$null
$oldHash=$null
try {
    if ($env:OWNER_CONFIRMED_OFFLINE -ne 'true' -or -not $env:FC_CHECKPOINT_RUN_ID -or
        $env:FC_CHECKPOINT_RUN_ID -notmatch '^\d+$' -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or -not $env:RUNNER_TEMP -or -not $env:USERPROFILE -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'OFFLINE_AND_CHECKPOINT_REQUIRED' }
    $base=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups'
    $original=Join-Path $base 'offline-39843776626'
    $engine=Join-Path $original 'server\FunCityEngine.jar'
    $originalManifest=Join-Path $original 'private-manifest.json'
    $checkpoint=Join-Path $base ('host-before-catserver-' + $env:FC_CHECKPOINT_RUN_ID)
    $snapshot=Join-Path $checkpoint 'server'
    $privateManifest=Join-Path $checkpoint 'private-manifest.json'
    $incomplete=Join-Path $checkpoint 'INCOMPLETE.txt'
    $key=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    foreach ($path in @($engine,$originalManifest,$checkpoint,$snapshot,$privateManifest,$key)) {
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_PC_SOURCE' }
    }
    if (Test-Path -LiteralPath $incomplete) { throw 'CHECKPOINT_INCOMPLETE' }
    $sourceMeta=Get-Content -LiteralPath $originalManifest -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    $checkpointMeta=Get-Content -LiteralPath $privateManifest -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($sourceMeta.consistent_offline_snapshot -ne $true -or
        $checkpointMeta.owner_confirmed_offline -ne $true -or
        [int]$checkpointMeta.files -lt 3994 -or [long]$checkpointMeta.bytes -lt 800000000L -or
        @($checkpointMeta.sha256.PSObject.Properties).Count -ne [int]$checkpointMeta.files) {
        throw 'PRIVATE_CHECKPOINT_NOT_VERIFIED'
    }
    $oldHash=(Get-FileHash -LiteralPath (Join-Path $snapshot 'server.jar') -Algorithm SHA256 -ErrorAction Stop).Hash
    $expected=$sourceMeta.sha256.PSObject.Properties['FunCityEngine.jar']
    if ($null -eq $expected -or $oldHash -cne $expected.Value -or
        (Get-FileHash -LiteralPath $engine -Algorithm SHA256).Hash -cne $expected.Value -or
        $checkpointMeta.sha256.PSObject.Properties['server.jar'].Value -cne $oldHash -or
        -not (Test-Path -LiteralPath (Join-Path $snapshot 'world') -PathType Container) -or
        -not (Test-Path -LiteralPath (Join-Path $snapshot 'mods') -PathType Container) -or
        -not (Test-Path -LiteralPath (Join-Path $snapshot 'plugins') -PathType Container)) {
        throw 'CHECKPOINT_OR_ENGINE_SHA_MISMATCH'
    }
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $temp=Join-Path $env:RUNNER_TEMP ('fc-catserver-promote-' + $env:GITHUB_RUN_ID)
    if (Test-Path -LiteralPath $temp) { throw 'TEMP_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $known=Join-Path $temp 'known_hosts'
    $batch=Join-Path $temp 'commands.txt'
    $output=Join-Path $temp 'private-output.txt'
    $destination='izentric-150380.6ddc2b7d@olivia.hidencloud.com'
    $args=@('-q','-b',$batch,'-P','2022','-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15')
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$output 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECT_FAILED' }
    $fp=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fp.Count -ne 1 -or
        $fp[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'SFTP_HOST_KEY_CHANGED' }
    $pinned=$args+@('-o','StrictHostKeyChecking=yes')
    function Invoke-PrivateSftp([string]$command) {
        [IO.File]::WriteAllText($script:batch,$command + "`nbye`n",[Text.Encoding]::ASCII)
        $arguments=$script:pinned
        & $script:sftp @arguments $script:destination 1>$script:output 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'SFTP_OPERATION_FAILED' }
    }
    $candidate='server.jar.catserver-official-candidate-39986252615'
    $candidateHash='8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0'
    $rollbackName='server.jar.rollback-catserver-trial-' + $env:GITHUB_RUN_ID
    $failedName='server.jar.failed-catserver-trial-' + $env:GITHUB_RUN_ID
    Invoke-PrivateSftp 'ls -1'
    $names=@(Get-Content -LiteralPath $output -ErrorAction Stop | ForEach-Object { $_.Trim() })
    if (@($names | Where-Object { $_ -ceq $candidate }).Count -ne 1 -or
        @($names | Where-Object { $_ -ceq $rollbackName -or $_ -ceq $failedName }).Count -gt 0) {
        throw 'CANDIDATE_OR_ROLLBACK_NAME_UNEXPECTED'
    }
    $activeLocal=Join-Path $temp 'active-before.jar'
    Invoke-PrivateSftp ('get server.jar "' + $activeLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $activeLocal -Algorithm SHA256).Hash -cne $oldHash) { throw 'HOST_ENGINE_CHANGED_AFTER_BACKUP' }
    $candidateLocal=Join-Path $temp 'candidate.jar'
    Invoke-PrivateSftp ('get ' + $candidate + ' "' + $candidateLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $candidateLocal -Algorithm SHA256).Hash -ine $candidateHash) { throw 'STAGED_CANDIDATE_SHA_CHANGED' }
    Invoke-PrivateSftp ('rename server.jar ' + $rollbackName)
    $oldMoved=$true
    $rollbackLocal=Join-Path $temp 'rollback.jar'
    Invoke-PrivateSftp ('get ' + $rollbackName + ' "' + $rollbackLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $rollbackLocal -Algorithm SHA256).Hash -cne $oldHash) { throw 'ROLLBACK_SHA_MISMATCH' }
    Invoke-PrivateSftp ('rename ' + $candidate + ' server.jar')
    $promoted=$true
    $newLocal=Join-Path $temp 'active-after.jar'
    Invoke-PrivateSftp ('get server.jar "' + $newLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $newLocal -Algorithm SHA256).Hash -ine $candidateHash) { throw 'PROMOTED_CANDIDATE_SHA_MISMATCH' }
    Write-Output ('::notice title=CatServer private trial::CANDIDATE_NOW_ACTIVE_JAR=true OFFICIAL_SHA_READBACK_VERIFIED=true' +
        ' PREVIOUS_ENGINE_ROLLBACK_SAVED=true ROLLBACK_NAME=' + $rollbackName +
        ' STOPPED_WORLD_CHECKPOINT_VERIFIED=true WORLD_MODS_PLUGINS_CONFIG_UNCHANGED=true' +
        ' SERVER_NOT_STARTED_BY_AGENT=true JAVA11_RUNTIME_AND_RP_NOT_TESTED=true')
} catch {
    if ($oldMoved -and $rollbackName) {
        try {
            if ($promoted) { Invoke-PrivateSftp ('rename server.jar ' + $failedName) }
            Invoke-PrivateSftp ('rename ' + $rollbackName + ' server.jar')
            $restored=Join-Path $temp 'restored.jar'
            Invoke-PrivateSftp ('get server.jar "' + $restored.Replace([char]92,[char]47) + '"')
            $rollbackVerified=((Get-FileHash -LiteralPath $restored -Algorithm SHA256).Hash -ceq $oldHash)
        } catch { $rollbackVerified=$false }
    }
    Write-Output ('::error title=CatServer private trial::PROMOTION_FAILED ROLLBACK_VERIFIED=' + $rollbackVerified +
        '; do not start host before active jar is checked')
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
