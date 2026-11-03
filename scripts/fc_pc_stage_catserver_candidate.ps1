# Stage a SHA-pinned PUBLIC CatServer candidate by SFTP to a NEW file only.
# No rename of server.jar, no server stop/start, no world/config/plugin writes.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$temp=$null
try {
    if (-not $env:RUNNER_TEMP -or -not $env:USERPROFILE -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $key=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    $backup=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups\offline-39843776626'
    $engine=Join-Path $backup 'server\FunCityEngine.jar'
    $manifestPath=Join-Path $backup 'private-manifest.json'
    foreach ($file in @($key,$engine,$manifestPath)) {
        $item=Get-Item -LiteralPath $file -Force -ErrorAction Stop
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_PC_SOURCE' }
    }
    $manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    $expected=$manifest.sha256.PSObject.Properties['FunCityEngine.jar']
    if ($manifest.consistent_offline_snapshot -ne $true -or $null -eq $expected -or
        (Get-FileHash -LiteralPath $engine -Algorithm SHA256).Hash -cne $expected.Value) { throw 'BACKUP_ENGINE_UNVERIFIED' }
    $temp=Join-Path $env:RUNNER_TEMP ('fc-public-catserver-stage-' + $env:GITHUB_RUN_ID)
    if (Test-Path -LiteralPath $temp) { throw 'TEMP_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $publicJar=Join-Path $temp 'official.jar'
    $candidateHash='8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0'
    $url='https://github.com/Luohuayu/CatServer/releases/download/23.05.26-1/CatServer-1.16.5-1d8d6313-server.jar'
    Invoke-WebRequest -Uri $url -OutFile $publicJar -UseBasicParsing -MaximumRedirection 5 -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $publicJar -Algorithm SHA256).Hash -ine $candidateHash) { throw 'UPSTREAM_SHA_MISMATCH' }
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $batch=Join-Path $temp 'commands.txt'
    $known=Join-Path $temp 'known_hosts'
    $privateOutput=Join-Path $temp 'private-output.txt'
    $old=Join-Path $temp 'active-server.jar'
    $readback=Join-Path $temp 'candidate-readback.jar'
    $destination='izentric-150380.6ddc2b7d@olivia.hidencloud.com'
    $args=@('-q','-b',$batch,'-P','2022','-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15')
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECT_FAILED' }
    $fp=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fp.Count -ne 1 -or
        $fp[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'SFTP_HOST_KEY_CHANGED' }
    $pinned=$args+@('-o','StrictHostKeyChecking=yes')
    $candidate='server.jar.catserver-official-candidate-' + $env:GITHUB_RUN_ID
    [IO.File]::WriteAllText($batch,('get server.jar "' + $old.Replace([char]92,[char]47) + '"' + "`nbye`n"),[Text.Encoding]::ASCII)
    & $sftp @pinned $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $old -PathType Leaf) -or
        (Get-FileHash -LiteralPath $old -Algorithm SHA256).Hash -cne $expected.Value) { throw 'LIVE_JAR_CHANGED' }
    # This unique name does not end with .jar and cannot be the current startup jar.
    [IO.File]::WriteAllText($batch,"ls -1`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @pinned $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or @(Get-Content -LiteralPath $privateOutput -ErrorAction Stop |
        Where-Object { $_.Trim() -ceq $candidate }).Count -gt 0) { throw 'CANDIDATE_TARGET_UNSAFE' }
    $src=$publicJar.Replace([char]92,[char]47)
    [IO.File]::WriteAllText($batch,('put "' + $src + '" ' + $candidate + "`nbye`n"),[Text.Encoding]::ASCII)
    & $sftp @pinned $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'CANDIDATE_UPLOAD_FAILED' }
    [IO.File]::WriteAllText($batch,('get ' + $candidate + ' "' + $readback.Replace([char]92,[char]47) + '"' + "`nbye`n"),[Text.Encoding]::ASCII)
    & $sftp @pinned $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $readback -PathType Leaf) -or
        (Get-FileHash -LiteralPath $readback -Algorithm SHA256).Hash -ine $candidateHash) { throw 'CANDIDATE_READBACK_SHA_FAILED' }
    Write-Output ('::notice title=CatServer staged only::OFFICIAL_JAR_SHA_VERIFIED=true CANDIDATE_SHA_READBACK_VERIFIED=true CANDIDATE_NAME=' +
        $candidate + ' ACTIVE_ENGINE_UNCHANGED=true WORLD_MODS_PLUGINS_CONFIG_UNCHANGED=true SERVER_NOT_STOPPED=true NO_PROMOTION=true')
} catch {
    Write-Output '::error title=CatServer staged only::STAGING_FAILED_OR_UNVERIFIED; active engine/world not intentionally modified; inspect before any swap'
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
}
