# Replace ONLY the host root server.jar with the byte-identical working PC
# FunCityEngine.jar from a SHA-verified private offline backup. Keep the old
# host JAR for rollback. No world, config, plugins, mods or server start changes.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$phase='PREFLIGHT'
$temp=$null
$oldMoved=$false
$promoted=$false
$rollbackVerified=$false
$known=$null
$batch=$null
$output=$null
$sftp=$null
$pinnedArgs=$null
$destination='izentric-150380.6ddc2b7d@olivia.hidencloud.com'
$oldHash=$null
$rollbackName=$null
$failedName=$null
function Invoke-PrivateSftp([string]$commands) {
    [IO.File]::WriteAllText($script:batch,$commands + "`nbye`n",[Text.Encoding]::ASCII)
    $arguments=$script:pinnedArgs
    & $script:sftp @arguments $script:destination 1>$script:output 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'SFTP_OPERATION_FAILED' }
}
try {
    if (-not $env:RUNNER_TEMP -or -not $env:USERPROFILE -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $phase='PC_SOURCE_PATHS'
    $base=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups\offline-39843776626'
    $source=Join-Path $base 'server\FunCityEngine.jar'
    $manifestFile=Join-Path $base 'private-manifest.json'
    $clientKey=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    foreach ($file in @($source,$manifestFile,$clientKey)) {
        $item=Get-Item -LiteralPath $file -Force -ErrorAction Stop
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_SOURCE' }
    }
    $phase='BACKUP_MANIFEST'
    $manifest=Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($manifest.consistent_offline_snapshot -ne $true -or $manifest.independent_restore_copy_verified -ne $true) { throw 'NOT_A_VERIFIED_OFFLINE_BACKUP' }
    $engineExpected=$manifest.sha256.PSObject.Properties['FunCityEngine.jar']
    $oldExpected=$manifest.sha256.PSObject.Properties['server.jar']
    if ($null -eq $engineExpected -or $null -eq $oldExpected) { throw 'SOURCE_JAR_NOT_IN_BACKUP_MANIFEST' }
    $phase='SOURCE_SHA'
    $engineHash=(Get-FileHash -LiteralPath $source -Algorithm SHA256 -ErrorAction Stop).Hash
    if ($engineHash -cne $engineExpected.Value -or $engineHash -ceq $oldExpected.Value) { throw 'SOURCE_SHA_UNEXPECTED' }
    $phase='PC_OPENSSH_CLIENT'
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $phase='PC_TEMP_PATH'
    $temp=Join-Path $env:RUNNER_TEMP ('fc-host-engine-' + $env:GITHUB_RUN_ID)
    if (Test-Path -LiteralPath $temp) { throw 'TEMP_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $known=Join-Path $temp 'known_hosts'
    $batch=Join-Path $temp 'commands.txt'
    $output=Join-Path $temp 'private-output.txt'
    $args=@('-q','-b',$batch,'-P','2022','-i',$clientKey,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15',
        '-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3')
    $phase='PIN_PREVIOUS_HOST_KEY'
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$output 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECTION_FAILED' }
    $fp=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fp.Count -ne 1 -or
        $fp[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'HOST_KEY_CHANGED' }
    $pinnedArgs=$args + @('-o','StrictHostKeyChecking=yes')

    $phase='VERIFY_CURRENT_ROOT_ENGINE'
    $oldLocal=Join-Path $temp 'previous-server.jar'
    $oldLocalArg=$oldLocal.Replace([char]92,[char]47)
    Invoke-PrivateSftp ('get server.jar "' + $oldLocalArg + '"')
    $oldHash=(Get-FileHash -LiteralPath $oldLocal -Algorithm SHA256 -ErrorAction Stop).Hash
    if ($oldHash -cne $oldExpected.Value) { throw 'HOST_JAR_CHANGED_SINCE_FULL_SHA_CHECK' }

    $phase='UPLOAD_NEW_JAR_CANDIDATE'
    $candidate='server.jar.funcity-candidate-' + $env:GITHUB_RUN_ID
    $rollbackName='server.jar.rollback-' + $env:GITHUB_RUN_ID
    $failedName='server.jar.failed-' + $env:GITHUB_RUN_ID
    Invoke-PrivateSftp 'ls -1'
    $existing=@(Get-Content -LiteralPath $output -ErrorAction Stop | ForEach-Object { $_.Trim() })
    foreach ($name in @($candidate,$rollbackName,$failedName)) {
        if (@($existing | Where-Object { $_ -ceq $name }).Count -gt 0) { throw 'REMOTE_TARGET_ALREADY_EXISTS' }
    }
    $srcArg=$source.Replace([char]92,[char]47)
    if ($srcArg -match '["\r\n]') { throw 'UNSAFE_SOURCE_PATH' }
    Invoke-PrivateSftp ('put "' + $srcArg + '" ' + $candidate)
    $candidateLocal=Join-Path $temp 'candidate.jar'
    Invoke-PrivateSftp ('get ' + $candidate + ' "' + $candidateLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $candidateLocal -Algorithm SHA256 -ErrorAction Stop).Hash -cne $engineHash) { throw 'UPLOAD_SHA_MISMATCH' }

    $phase='SAVE_OLD_JAR_UNDER_UNIQUE_ROLLBACK_NAME'
    Invoke-PrivateSftp ('rename server.jar ' + $rollbackName)
    $oldMoved=$true
    $phase='PROMOTE_VERIFIED_ENGINE'
    Invoke-PrivateSftp ('rename ' + $candidate + ' server.jar')
    $promoted=$true
    $phase='VERIFY_ACTIVE_ENGINE'
    $activeLocal=Join-Path $temp 'new-active.jar'
    Invoke-PrivateSftp ('get server.jar "' + $activeLocal.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $activeLocal -Algorithm SHA256 -ErrorAction Stop).Hash -cne $engineHash) { throw 'ACTIVE_ENGINE_SHA_MISMATCH' }
    Write-Output ('::notice title=HidenCloud motor::ACTIVE_SERVER_JAR_MATCHES_WORKING_PC_ENGINE=true OLD_JAR_ROLLBACK_SAVED=true ROLLBACK_NAME=' +
        $rollbackName + ' WORLD_CONFIG_MODS_PLUGINS_UNCHANGED=true SERVER_NOT_STARTED_BY_AGENT=true')
    exit 0
} catch {
    # If the first rename succeeded but promotion failed, restore the old JAR.
    if ($oldMoved -and $pinnedArgs -and $rollbackName) {
        try {
            if ($promoted) { Invoke-PrivateSftp ('rename server.jar ' + $failedName) }
            Invoke-PrivateSftp ('rename ' + $rollbackName + ' server.jar')
            $restored=Join-Path $temp 'restored-old.jar'
            Invoke-PrivateSftp ('get server.jar "' + $restored.Replace([char]92,[char]47) + '"')
            $rollbackVerified=((Get-FileHash -LiteralPath $restored -Algorithm SHA256).Hash -ceq $oldHash)
        } catch { $rollbackVerified=$false }
    }
    Write-Output ('::error title=HidenCloud motor::CORRECTION_UNVERIFIED PHASE=' + $phase +
        ' ROLLBACK_VERIFIED=' + $rollbackVerified + '; do NOT start host until active jar is checked')
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
