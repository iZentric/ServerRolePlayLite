# Host-only SAFE PRIVATE BOOT config: use allocated Minecraft port, disable
# RCON (copied PC credentials must not be exposed). KEEP loopback binding and
# offline-mode false until a tested anti-impersonation plan exists. Preserve
# all other server.properties bytes (ISO-8859-1) and a host rollback copy.
# No server start, world/mod/plugin changes, or public access enabled.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$phase='PREFLIGHT'
$temp=$null
$oldMoved=$false
$promoted=$false
$rollbackVerified=$false
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
    $key=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    $item=Get-Item -LiteralPath $key -Force -ErrorAction Stop
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_CLIENT_KEY' }
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $temp=Join-Path $env:RUNNER_TEMP ('fc-host-private-boot-' + $env:GITHUB_RUN_ID)
    if (Test-Path -LiteralPath $temp) { throw 'TEMP_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $batch=Join-Path $temp 'commands.txt'
    $output=Join-Path $temp 'private-output.txt'
    $known=Join-Path $temp 'known_hosts'
    $args=@('-q','-b',$batch,'-P','2022','-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15')
    $phase='PIN_PREVIOUS_HOST_KEY'
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$output 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECTION_FAILED' }
    $fp=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fp.Count -ne 1 -or
        $fp[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'HOST_KEY_CHANGED' }
    $pinnedArgs=$args + @('-o','StrictHostKeyChecking=yes')

    $phase='READ_CURRENT_HOST_CONFIG'
    $old=Join-Path $temp 'original.properties'
    Invoke-PrivateSftp ('get server.properties "' + $old.Replace([char]92,[char]47) + '"')
    $original=(Get-Item -LiteralPath $old -Force -ErrorAction Stop)
    if ($original.Length -lt 100 -or $original.Length -gt 1000000) { throw 'UNEXPECTED_PROPERTIES_SIZE' }
    $oldHash=(Get-FileHash -LiteralPath $old -Algorithm SHA256).Hash
    $enc=[Text.Encoding]::GetEncoding(28591)
    $text=[IO.File]::ReadAllText($old,$enc)
    foreach ($pattern in @('(?m)^server-port=\d+\r?$','(?m)^enable-rcon=true\r?$',
            '(?m)^server-ip=(127\.0\.0\.1|localhost)\r?$','(?m)^online-mode=false\r?$')) {
        if ([regex]::Matches($text,$pattern).Count -ne 1) { throw 'UNEXPECTED_LOCAL_CONFIG' }
    }
    if ([regex]::Matches($text,'(?m)^server-port=[^\r\n]*\r?$').Count -ne 1 -or
        [regex]::Matches($text,'(?m)^enable-rcon=[^\r\n]*\r?$').Count -ne 1) { throw 'DUPLICATE_CONFIG_KEY' }
    $new=[regex]::Replace($text,'(?m)^server-port=\d+(\r?)$','server-port=24595$1')
    $new=[regex]::Replace($new,'(?m)^enable-rcon=true(\r?)$','enable-rcon=false$1')
    if ($new -ceq $text -or
        [regex]::Matches($new,'(?m)^server-port=24595\r?$').Count -ne 1 -or
        [regex]::Matches($new,'(?m)^enable-rcon=false\r?$').Count -ne 1 -or
        [regex]::Matches($new,'(?m)^server-ip=(127\.0\.0\.1|localhost)\r?$').Count -ne 1 -or
        [regex]::Matches($new,'(?m)^online-mode=false\r?$').Count -ne 1) { throw 'NEW_CONFIG_INVARIANT_FAILED' }
    $candidateLocal=Join-Path $temp 'candidate.properties'
    [IO.File]::WriteAllText($candidateLocal,$new,$enc)
    $newHash=(Get-FileHash -LiteralPath $candidateLocal -Algorithm SHA256).Hash

    $phase='UPLOAD_PRIVATE_BOOT_CONFIG_CANDIDATE'
    $candidate='server.properties.funcity-candidate-' + $env:GITHUB_RUN_ID
    $rollbackName='server.properties.rollback-' + $env:GITHUB_RUN_ID
    $failedName='server.properties.failed-' + $env:GITHUB_RUN_ID
    Invoke-PrivateSftp 'ls -1'
    $existing=@(Get-Content -LiteralPath $output -ErrorAction Stop | ForEach-Object { $_.Trim() })
    foreach ($name in @($candidate,$rollbackName,$failedName)) {
        if (@($existing | Where-Object { $_ -ceq $name }).Count -gt 0) { throw 'REMOTE_TARGET_ALREADY_EXISTS' }
    }
    Invoke-PrivateSftp ('put "' + $candidateLocal.Replace([char]92,[char]47) + '" ' + $candidate)
    $candidateReadback=Join-Path $temp 'candidate-readback.properties'
    Invoke-PrivateSftp ('get ' + $candidate + ' "' + $candidateReadback.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $candidateReadback -Algorithm SHA256).Hash -cne $newHash) { throw 'CANDIDATE_SHA_MISMATCH' }
    $phase='PRESERVE_OLD_HOST_CONFIG'
    Invoke-PrivateSftp ('rename server.properties ' + $rollbackName)
    $oldMoved=$true
    $rollbackReadback=Join-Path $temp 'rollback-readback.properties'
    Invoke-PrivateSftp ('get ' + $rollbackName + ' "' + $rollbackReadback.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $rollbackReadback -Algorithm SHA256).Hash -cne $oldHash) { throw 'ROLLBACK_SHA_MISMATCH' }
    $phase='PROMOTE_AND_VERIFY_PRIVATE_CONFIG'
    Invoke-PrivateSftp ('rename ' + $candidate + ' server.properties')
    $promoted=$true
    $active=Join-Path $temp 'new-active.properties'
    Invoke-PrivateSftp ('get server.properties "' + $active.Replace([char]92,[char]47) + '"')
    if ((Get-FileHash -LiteralPath $active -Algorithm SHA256).Hash -cne $newHash) { throw 'ACTIVE_CONFIG_SHA_MISMATCH' }
    Write-Output ('::notice title=HidenCloud private boot config::HOST_GAME_PORT_CORRECT=true RCON_DISABLED=true IP_REMAINS_LOOPBACK=true OFFLINE_MODE_REMAINS_PRIVATE=true CONFIG_ROLLBACK_SAVED=true ROLLBACK_NAME=' +
        $rollbackName + ' WORLD_ENGINE_MODS_PLUGINS_UNCHANGED=true SERVER_NOT_STARTED_BY_AGENT=true')
    exit 0
} catch {
    if ($oldMoved -and $pinnedArgs -and $rollbackName) {
        try {
            if ($promoted) { Invoke-PrivateSftp ('rename server.properties ' + $failedName) }
            Invoke-PrivateSftp ('rename ' + $rollbackName + ' server.properties')
            $restored=Join-Path $temp 'restored-old.properties'
            Invoke-PrivateSftp ('get server.properties "' + $restored.Replace([char]92,[char]47) + '"')
            $rollbackVerified=((Get-FileHash -LiteralPath $restored -Algorithm SHA256).Hash -ceq $oldHash)
        } catch { $rollbackVerified=$false }
    }
    Write-Output ('::error title=HidenCloud private boot config::PREPARATION_UNVERIFIED PHASE=' + $phase +
        ' ROLLBACK_VERIFIED=' + $rollbackVerified + '; do NOT start until active config verified')
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
