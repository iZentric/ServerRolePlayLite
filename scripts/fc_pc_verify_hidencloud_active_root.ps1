# READ-ONLY: download only the files/directories from the verified offline PC
# backup that should be present in the HidenCloud SFTP root (/home/container).
# Compare EVERY file with the private backup SHA manifest. Ignore extra host
# entries, but never treat them as verified. No remote writes or public artifacts.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$phase = 'PREFLIGHT'
$temp = $null
$copyRoot = $null
function Snapshot-Tree([string]$root) {
    $base = [IO.DirectoryInfo]::new($root)
    if (-not $base.Exists -or ($base.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_ROOT' }
    $queue = [System.Collections.Generic.Queue[string]]::new()
    $queue.Enqueue($root)
    $files = [System.Collections.Generic.List[string]]::new()
    $dirs = [System.Collections.Generic.List[string]]::new()
    $bytes = 0L
    $rootLen = $root.TrimEnd([char[]]@([char]92,[char]47)).Length
    while ($queue.Count -gt 0) {
        foreach ($item in @(Get-ChildItem -LiteralPath $queue.Dequeue() -Force -ErrorAction Stop)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_ENTRY' }
            $rel = $item.FullName.Substring($rootLen).TrimStart([char[]]@([char]92,[char]47))
            if (-not $rel -or $rel.StartsWith('..') -or [IO.Path]::IsPathRooted($rel)) { throw 'UNSAFE_RELATIVE_PATH' }
            if ($item.PSIsContainer) { $dirs.Add($rel); $queue.Enqueue($item.FullName) }
            else { $files.Add($rel); $bytes += $item.Length }
            if ($files.Count -gt 200000 -or $bytes -gt 200000000000L) { throw 'UNEXPECTED_SIZE' }
        }
    }
    return [pscustomobject]@{ Files=$files; Dirs=$dirs; Bytes=$bytes }
}
try {
    if (-not $env:USERPROFILE -or -not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $project = Join-Path $env:USERPROFILE 'Desktop\FunCityLocal'
    $backups = Join-Path $project 'Arena-Private-Backups'
    $backup = Join-Path $backups 'offline-39843776626'
    $source = Join-Path $backup 'server'
    $manifestFile = Join-Path $backup 'private-manifest.json'
    $clientKey = Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    foreach ($path in @($backups,$backup,$source,$manifestFile,$clientKey)) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_PC_PATH' }
    }
    $manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($manifest.consistent_offline_snapshot -ne $true -or $manifest.independent_restore_copy_verified -ne $true) { throw 'BACKUP_NOT_VERIFIED' }
    $local = Snapshot-Tree $source
    if ($local.Files.Count -ne [int]$manifest.files -or $local.Dirs.Count -ne [int]$manifest.directories -or
        $local.Bytes -ne [long]$manifest.bytes) { throw 'SOURCE_CHANGED' }
    $top = @(Get-ChildItem -LiteralPath $source -Force -ErrorAction Stop)
    if ($top.Count -lt 10 -or $top.Count -gt 300) { throw 'UNEXPECTED_TOP_LEVEL_COUNT' }
    foreach ($entry in $top) {
        if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            $entry.Name -notmatch '^(?!\.\.?$)(?!-)[A-Za-z0-9._ -]+$' -or
            $entry.Name.Contains('"')) { throw 'UNSAFE_SFTP_ENTRY_NAME' }
    }
    $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($backups))
    if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ([long]$manifest.bytes + 536870912L)) { throw 'INSUFFICIENT_LOCAL_READBACK_SPACE' }
    $sftp = (Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen = (Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $temp = Join-Path $env:RUNNER_TEMP ('fc-active-verify-' + $env:GITHUB_RUN_ID)
    $copyRoot = Join-Path $backups ('host-active-readback-' + $env:GITHUB_RUN_ID)
    if ((Test-Path -LiteralPath $temp) -or (Test-Path -LiteralPath $copyRoot)) { throw 'TARGET_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $batch = Join-Path $temp 'read-only-batch.txt'
    $known = Join-Path $temp 'known_hosts'
    $privateOutput = Join-Path $temp 'private-sftp-output.txt'
    $common = @('-q','-b',$batch,'-P','2022','-i',$clientKey,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15',
        '-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3')
    $destination = 'izentric-150380.6ddc2b7d@olivia.hidencloud.com'
    $phase = 'PIN_PREVIOUS_HOST_KEY'
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @common -o 'StrictHostKeyChecking=accept-new' $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECTION_FAILED' }
    $fingerprints = @(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fingerprints.Count -ne 1 -or
        $fingerprints[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'HOST_KEY_CHANGED' }

    $phase = 'DOWNLOAD_ACTIVE_FILES_READ_ONLY'
    $copyServer = Join-Path $copyRoot 'server'
    [void](New-Item -ItemType Directory -Path $copyServer -ErrorAction Stop)
    $sftpRoot = $copyServer.Replace([char]92,[char]47)
    if ($sftpRoot -match '["\r\n]') { throw 'UNSAFE_READBACK_PATH' }
    $commands = [System.Collections.Generic.List[string]]::new()
    foreach ($entry in $top) {
        $name = $entry.Name
        $destinationFile = $sftpRoot + '/' + $name
        $prefix = if ($entry.PSIsContainer) { 'get -r ' } else { 'get ' }
        $commands.Add($prefix + '"' + $name + '" "' + $destinationFile + '"')
    }
    $commands.Add('bye')
    [IO.File]::WriteAllLines($batch,$commands,[Text.Encoding]::ASCII)
    & $sftp @common -o 'StrictHostKeyChecking=yes' $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'ACTIVE_ROOT_DOWNLOAD_INCOMPLETE' }

    $phase = 'COMPARE_ALL_PRIVATE_BACKUP_SHA'
    $remote = Snapshot-Tree $copyServer
    if ($remote.Files.Count -ne $local.Files.Count -or $remote.Dirs.Count -ne $local.Dirs.Count -or
        $remote.Bytes -ne $local.Bytes) { throw 'ACTIVE_ROOT_INVENTORY_DIFFERS' }
    foreach ($rel in $local.Dirs) {
        if (-not (Test-Path -LiteralPath (Join-Path $copyServer $rel) -PathType Container)) { throw 'ACTIVE_ROOT_DIR_MISSING' }
    }
    foreach ($rel in $remote.Files) {
        $property = $manifest.sha256.PSObject.Properties[$rel]
        if ($null -eq $property -or
            (Get-FileHash -LiteralPath (Join-Path $copyServer $rel) -Algorithm SHA256 -ErrorAction Stop).Hash -cne $property.Value) {
            throw 'ACTIVE_ROOT_FILE_SHA_DIFFERS'
        }
    }
    Write-Output ('::notice title=HidenCloud active root::ALL_BACKUP_FILES_PRESENT_AND_SHA_MATCH=true FILES=' +
        $remote.Files.Count + ' BYTES=' + $remote.Bytes +
        ' EXTRA_HOST_ENTRIES_NOT_VERIFIED=true ENGINE_AND_HOST_CONFIG_REQUIRE_SEPARATE_FIX=true SERVER_NOT_STARTED_BY_AGENT=true')
    exit 0
} catch {
    Write-Output ('::error title=HidenCloud active root::INTEGRITY_NOT_VERIFIED PHASE=' + $phase +
        ' TYPE=' + $_.Exception.GetType().Name + '; read-only; no remote names or data logged')
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
    # Keep private readback for diagnostics; never upload it to GitHub or overwrite live files.
}
