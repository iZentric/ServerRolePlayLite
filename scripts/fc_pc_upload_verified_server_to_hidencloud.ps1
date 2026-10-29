# Copy the complete, SHA-verified OFFLINE PC backup to a NEW SFTP directory.
# Never log paths/names, file contents, player data, config values or private keys.
# Never overwrite/delete any existing host entry or alter the local live server.
# A successful upload is NOT a server startup/cutover or a public release.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$phase = 'PREFLIGHT'
$serverHost = 'olivia.hidencloud.com'
$port = 2022
$login = 'izentric-150380.6ddc2b7d'
$expectedClient = 'AAAAC3NzaC1lZDI1NTE5AAAAILm8LdLcmC0AO9bHH5poxjEu7IS8Sa5KA7gx8kqetuGl'
# Observed twice on PC, not independently confirmed by provider.
$expectedHost = 'SHA256:8B88Xl+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4'
$backupRunId = '39843776626'
$work = $null
$readback = $null

function Snapshot-Tree([string]$root) {
    $base = [IO.DirectoryInfo]::new($root)
    if (-not $base.Exists -or ($base.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_TREE_ROOT' }
    $queue = [System.Collections.Generic.Queue[string]]::new()
    $queue.Enqueue($root)
    $files = [System.Collections.Generic.List[string]]::new()
    $dirs = [System.Collections.Generic.List[string]]::new()
    $bytes = 0L
    $rootLen = $root.TrimEnd([char[]]@([char]92,[char]47)).Length
    while ($queue.Count -gt 0) {
        foreach ($item in @(Get-ChildItem -LiteralPath $queue.Dequeue() -Force -ErrorAction Stop)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_ENTRY' }
            $relative = $item.FullName.Substring($rootLen).TrimStart([char[]]@([char]92,[char]47))
            if (-not $relative -or $relative.StartsWith('..') -or [IO.Path]::IsPathRooted($relative)) { throw 'UNSAFE_RELATIVE_PATH' }
            if ($item.PSIsContainer) { $dirs.Add($relative); $queue.Enqueue($item.FullName) }
            else { $files.Add($relative); $bytes += $item.Length }
            if ($files.Count -gt 200000 -or $bytes -gt 200000000000L) { throw 'UNEXPECTED_SIZE' }
        }
    }
    return [pscustomobject]@{ Files=$files; Dirs=$dirs; Bytes=$bytes }
}

try {
    if (-not $env:USERPROFILE -or -not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $project = Join-Path $env:USERPROFILE 'Desktop\FunCityLocal'
    $backup = Join-Path $project ('Arena-Private-Backups\offline-' + $backupRunId)
    $source = Join-Path $backup 'server'
    $manifestPath = Join-Path $backup 'private-manifest.json'
    $key = Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    $pub = $key + '.pub'
    foreach ($path in @($project,$backup,$source,$manifestPath,$key,$pub)) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_PC_PATH' }
    }
    $pubLine = (Get-Content -LiteralPath $pub -Raw -Encoding ASCII).Trim()
    if ($pubLine -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+(?: .*)?$' -or
        ($pubLine -split ' ')[1] -ne $expectedClient) { throw 'WRONG_PC_CLIENT_KEY' }
    $sftp = (Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen = (Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($manifest.consistent_offline_snapshot -ne $true -or
        $manifest.independent_restore_copy_verified -ne $true -or
        $manifest.files -lt 100 -or $manifest.bytes -lt 10000000) { throw 'BACKUP_MANIFEST_NOT_VERIFIED' }
    $before = Snapshot-Tree $source
    if ($before.Files.Count -ne [int]$manifest.files -or
        $before.Dirs.Count -ne [int]$manifest.directories -or
        $before.Bytes -ne [long]$manifest.bytes) { throw 'BACKUP_INVENTORY_MISMATCH' }
    foreach ($rel in $before.Files) {
        $property = $manifest.sha256.PSObject.Properties[$rel]
        if ($null -eq $property -or
            (Get-FileHash -LiteralPath (Join-Path $source $rel) -Algorithm SHA256 -ErrorAction Stop).Hash -cne $property.Value) {
            throw 'BACKUP_SHA_MISMATCH'
        }
    }
    Write-Output ('::notice title=Private source validation::OFFLINE_BACKUP_SHA_VERIFIED=true FILES=' + $before.Files.Count + '; no private files in logs')

    $phase = 'HOST_KEY_PIN'
    $work = Join-Path $env:RUNNER_TEMP ('fc-upload-' + $env:GITHUB_RUN_ID)
    $readback = Join-Path (Join-Path $project 'Arena-Private-Backups') ('host-readback-' + $env:GITHUB_RUN_ID)
    if ((Test-Path -LiteralPath $work) -or (Test-Path -LiteralPath $readback)) { throw 'STAGING_PATH_EXISTS' }
    [void](New-Item -ItemType Directory -Path $work -ErrorAction Stop)
    $known = Join-Path $work 'known_hosts'
    $batch = Join-Path $work 'batch.txt'
    $output = Join-Path $work 'private-sftp-output.txt'
    $common = @('-q','-b',$batch,'-P',[string]$port,'-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes',
        '-o','PreferredAuthentications=publickey','-o','PasswordAuthentication=no',
        '-o','KbdInteractiveAuthentication=no', '-o',('UserKnownHostsFile=' + $known),
        '-o','ConnectTimeout=15','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3',
        "${login}@${serverHost}")
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    $argsFirst = @($common[0..($common.Count-2)]) + @('-o','StrictHostKeyChecking=accept-new',$common[-1])
    & $sftp @argsFirst 1>$output 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'HOST_KEY_PREFLIGHT_FAILED' }
    $fingerprints = @(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fingerprints.Count -ne 1 -or
        $fingerprints[0] -notmatch ('\s' + [regex]::Escape($expectedHost) + '\s')) {
        throw 'HOST_KEY_DIFFERS_FROM_PRIOR_PC_PROBES'
    }
    $argsPinned = @($common[0..($common.Count-2)]) + @('-o','StrictHostKeyChecking=yes',$common[-1])
    Write-Output '::notice title=SSH trust::HOSTKEY_MATCHES_PRIOR_PC_TOFU=true; provider fingerprint still unconfirmed'

    $phase = 'REMOTE_NEW_DIRECTORY_AND_UPLOAD'
    $partial = 'funcity-upload-' + $env:GITHUB_RUN_ID + '.partial'
    $final = 'funcity-server-' + $env:GITHUB_RUN_ID
    # Fixed PC paths contain no quotes/newlines. Never construct a batch from remote listing.
    $sftpSource = $source.Replace([char]92,[char]47)
    if ($sftpSource -match '["\r\n]' -or $sftpSource -notmatch '^[A-Za-z]:/') { throw 'UNSAFE_SFTP_SOURCE_PATH' }
    [IO.File]::WriteAllText($batch,
        ('mkdir ' + $partial + "`n" + 'put -r "' + $sftpSource + '" "' + $partial + '/server"' + "`nbye`n"),
        [Text.Encoding]::ASCII)
    & $sftp @argsPinned 1>$output 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'SFTP_UPLOAD_INCOMPLETE_PARTIAL_DIRECTORY_LEFT_UNTOUCHED' }

    $phase = 'DOWNLOAD_AND_VERIFY_SHA'
    [void](New-Item -ItemType Directory -Path $readback -ErrorAction Stop)
    $localCopy = Join-Path $readback 'server'
    $sftpCopy = $localCopy.Replace([char]92,[char]47)
    if ($sftpCopy -match '["\r\n]') { throw 'UNSAFE_SFTP_READBACK_PATH' }
    [IO.File]::WriteAllText($batch,
        ('get -r "' + $partial + '/server" "' + $sftpCopy + '"' + "`nbye`n"),
        [Text.Encoding]::ASCII)
    & $sftp @argsPinned 1>$output 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'SFTP_READBACK_INCOMPLETE_PARTIAL_DIRECTORY_LEFT_UNTOUCHED' }
    $after = Snapshot-Tree $localCopy
    if ($after.Files.Count -ne $before.Files.Count -or
        $after.Dirs.Count -ne $before.Dirs.Count -or $after.Bytes -ne $before.Bytes) {
        throw 'REMOTE_READBACK_INVENTORY_MISMATCH'
    }
    foreach ($rel in $after.Dirs) {
        if (-not (Test-Path -LiteralPath (Join-Path $source $rel) -PathType Container)) { throw 'REMOTE_READBACK_DIR_MISMATCH' }
    }
    foreach ($rel in $after.Files) {
        $property = $manifest.sha256.PSObject.Properties[$rel]
        if ($null -eq $property -or
            (Get-FileHash -LiteralPath (Join-Path $localCopy $rel) -Algorithm SHA256 -ErrorAction Stop).Hash -cne $property.Value) {
            throw 'REMOTE_READBACK_SHA_MISMATCH'
        }
    }
    # Never overwrite an existing destination; the run ID gives each stage a unique name.
    $phase = 'FINALIZE_UNDER_NEW_HOST_DIRECTORY'
    [IO.File]::WriteAllText($batch,('rename ' + $partial + ' ' + $final + "`nbye`n"),[Text.Encoding]::ASCII)
    & $sftp @argsPinned 1>$output 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'REMOTE_RENAME_FAILED_VERIFIED_PARTIAL_DIRECTORY_REMAINS' }
    Write-Output ('::notice title=HidenCloud private staged upload::FULL_SERVER_STAGED_AND_READBACK_SHA_VERIFIED=true FILES=' +
        $after.Files.Count + ' BYTES=' + $after.Bytes + ' REMOTE_FOLDER=' + $final +
        ' EXISTING_ROOT_UNTOUCHED=true STARTED=false RELEASE_PUBLISHED=false')
    exit 0
} catch {
    Write-Output ('::error title=HidenCloud private staged upload::BLOCKED_PHASE=' + $phase +
        ' TYPE=' + $_.Exception.GetType().Name + '; existing host entries and PC live server NOT modified; partial remote folder may remain')
    exit 2
} finally {
    if ($work -and (Test-Path -LiteralPath $work)) {
        Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
    }
    # Keep successful or partial readback privately on the PC for inspection,
    # never attach it as an artifact or push it to Git.
}
