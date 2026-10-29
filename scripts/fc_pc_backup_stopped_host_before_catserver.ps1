# Private SFTP readback of every original backup top-level entry from STOPPED
# HidenCloud active root. Never modifies remote files or GitHub artifacts.
# Preserve extras on host, but do not claim extras were backed up.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$temp=$null
$checkpoint=$null
$complete=$false
try {
    if ($env:OWNER_CONFIRMED_OFFLINE -ne 'true' -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or -not $env:USERPROFILE -or -not $env:RUNNER_TEMP -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'OFFLINE_OWNER_CONFIRMATION_REQUIRED' }
    $base=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups'
    $original=Join-Path $base 'offline-39843776626'
    $source=Join-Path $original 'server'
    $manifestFile=Join-Path $original 'private-manifest.json'
    $key=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    foreach ($path in @($base,$original,$source,$manifestFile,$key)) {
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'UNSAFE_PC_PATH' }
    }
    $originalManifest=Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($originalManifest.consistent_offline_snapshot -ne $true -or
        $originalManifest.independent_restore_copy_verified -ne $true -or
        [int]$originalManifest.files -ne 3994 -or [long]$originalManifest.bytes -ne 852735002L) { throw 'SOURCE_BACKUP_UNVERIFIED' }
    $top=@(Get-ChildItem -LiteralPath $source -Force -ErrorAction Stop)
    if ($top.Count -lt 10 -or $top.Count -gt 300) { throw 'UNSAFE_SOURCE_INVENTORY' }
    foreach ($item in $top) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            $item.Name -notmatch '^(?!\.\.?$)(?!-)[A-Za-z0-9._ -]+$' -or
            $item.Name.Contains('"')) { throw 'UNSAFE_SFTP_ENTRY_NAME' }
    }
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($base))
    if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt (2L*[long]$originalManifest.bytes + 1073741824L)) {
        throw 'INSUFFICIENT_PRIVATE_BACKUP_SPACE'
    }
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $temp=Join-Path $env:RUNNER_TEMP ('fc-host-checkpoint-' + $env:GITHUB_RUN_ID)
    $checkpoint=Join-Path $base ('host-before-catserver-' + $env:GITHUB_RUN_ID)
    if ((Test-Path -LiteralPath $temp) -or (Test-Path -LiteralPath $checkpoint)) { throw 'TARGET_EXISTS' }
    [void](New-Item -ItemType Directory -Path $temp -ErrorAction Stop)
    $copy=Join-Path $checkpoint 'server'
    [void](New-Item -ItemType Directory -Path $copy -ErrorAction Stop)
    $incomplete=Join-Path $checkpoint 'INCOMPLETE.txt'
    [IO.File]::WriteAllText($incomplete,'Never restore from this directory until the SHA manifest exists.',[Text.Encoding]::ASCII)
    $batch=Join-Path $temp 'commands.txt'
    $known=Join-Path $temp 'known_hosts'
    $output=Join-Path $temp 'private-sftp-output.txt'
    $destination='izentric-150380.6ddc2b7d@olivia.hidencloud.com'
    $args=@('-q','-b',$batch,'-P','2022','-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=15',
        '-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3')
    [IO.File]::WriteAllText($batch,"pwd`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$output 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_CONNECT_FAILED' }
    $fp=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fp.Count -ne 1 -or
        $fp[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') { throw 'SFTP_HOST_KEY_CHANGED' }
    $copySftp=$copy.Replace([char]92,[char]47)
    $commands=[Collections.Generic.List[string]]::new()
    foreach ($item in $top) {
        $prefix=if ($item.PSIsContainer) { 'get -r ' } else { 'get ' }
        $commands.Add($prefix + '"' + $item.Name + '" "' + $copySftp + '/' + $item.Name + '"')
    }
    $commands.Add('bye')
    [IO.File]::WriteAllLines($batch,$commands,[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=yes' $destination 1>$output 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'HOST_READBACK_INCOMPLETE' }
    foreach ($item in $top) {
        $downloaded=Join-Path $copy $item.Name
        if (-not (Test-Path -LiteralPath $downloaded)) { throw 'EXPECTED_TOP_ENTRY_MISSING' }
    }
    $dirs=@(Get-ChildItem -LiteralPath $copy -Directory -Recurse -Force -ErrorAction Stop)
    if (@($dirs | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count -gt 0) {
        throw 'REPARSE_DIRECTORY_IN_HOST_READBACK'
    }
    $files=@(Get-ChildItem -LiteralPath $copy -File -Recurse -Force -ErrorAction Stop)
    if ($files.Count -lt [int]$originalManifest.files) { throw 'BACKUP_FEWER_FILES_THAN_ORIGINAL' }
    $hashes=[ordered]@{}
    $bytes=0L
    foreach ($file in $files) {
        if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_HOST_READBACK' }
        $rel=$file.FullName.Substring($copy.Length).TrimStart([char[]]@([char]92,[char]47))
        if (-not $rel -or $rel.StartsWith('..') -or [IO.Path]::IsPathRooted($rel)) { throw 'UNSAFE_BACKUP_RELATIVE_PATH' }
        $hashes[$rel]=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256 -ErrorAction Stop).Hash
        $bytes += $file.Length
    }
    $privateManifest=Join-Path $checkpoint 'private-manifest.json'
    [pscustomobject]@{ owner_confirmed_offline=$true; expected_top_entries=$top.Count; files=$files.Count;
        bytes=$bytes; sha256=$hashes; host_extra_entries_not_backed_up=$true } |
        ConvertTo-Json -Depth 5 -Compress | Set-Content -LiteralPath $privateManifest -Encoding UTF8
    $check=Get-Content -LiteralPath $privateManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([int]$check.files -ne $files.Count -or [long]$check.bytes -ne $bytes -or
        @($check.sha256.PSObject.Properties).Count -ne $files.Count) { throw 'PRIVATE_MANIFEST_READBACK_FAILED' }
    Remove-Item -LiteralPath $incomplete -Force -ErrorAction Stop
    $complete=$true
    Write-Output ('::notice title=Host offline checkpoint::OWNER_CONFIRMED_OFFLINE=true PRIVATE_PC_SHA_BACKUP_VALID=true' +
        ' FILES=' + $files.Count + ' BYTES=' + $bytes +
        ' EXPECTED_TOP_ENTRIES=' + $top.Count + ' EXTRA_HOST_ENTRIES_NOT_BACKED_UP=true' +
        ' ACTIVE_ENGINE_NOT_SWAPPED=true HOST_FILES_READ_ONLY=true NO_PRIVATE_ARTIFACTS=true')
} catch {
    Write-Output '::error title=Host offline checkpoint::BACKUP_NOT_VERIFIED; no host writes; never promote engine'
    exit 2
} finally {
    if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue }
    # Keep an incomplete private readback for diagnosis; never treat it as rollback.
}
