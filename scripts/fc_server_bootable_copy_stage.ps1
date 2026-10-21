# Private, world-complete compatibility COPY sourced from the verified offline backup.
# Remove only Clumps from this new copy; never touch/stop/start the live server.
param([Parameter(Mandatory=$true)][string]$Server,
      [Parameter(Mandatory=$true)][ValidatePattern('^\d+$')][string]$BackupRunId)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$stage = $null
$owned = $false
$phase = 'VALIDATE'
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong project or run id' }
  $project = Split-Path -Parent $Server
  $backup = Join-Path (Join-Path $project 'Arena-Private-Backups') ('offline-' + $BackupRunId)
  $source = Join-Path $backup 'server'
  foreach ($dir in @($project,$backup,$source)) {
    $info = [IO.DirectoryInfo]::new($dir)
    if (-not $info.Exists -or ($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe source root' }
  }
  $manifestInfo = Get-Item -LiteralPath (Join-Path $backup 'private-manifest.json') -ErrorAction Stop
  if (($manifestInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe manifest' }
  $manifest = Get-Content -LiteralPath $manifestInfo.FullName -Raw -ErrorAction Stop | ConvertFrom-Json
  if ($manifest.schema -ne 1 -or $manifest.source -cne 'offline' -or
      $manifest.consistent_offline_snapshot -ne $true -or $manifest.independent_restore_copy_verified -ne $true) {
    throw 'Backup is not verified offline'
  }
  $phase = 'INVENTORY'
  $dirs = New-Object 'System.Collections.Generic.List[string]'
  $files = New-Object 'System.Collections.Generic.List[object]'
  $queue = [System.Collections.Generic.Queue[string]]::new()
  $queue.Enqueue($source)
  $rootLen = $source.TrimEnd([char[]]@([char]92,[char]47)).Length
  $bytes = 0L
  while ($queue.Count -gt 0) {
    $dir = $queue.Dequeue()
    foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop)) {
      if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe backup entry' }
      $rel = $item.FullName.Substring($rootLen).TrimStart([char[]]@([char]92,[char]47))
      if ($rel.StartsWith('..') -or [IO.Path]::IsPathRooted($rel)) { throw 'Unsafe relative path' }
      if ($item.PSIsContainer) { $dirs.Add($rel); $queue.Enqueue($item.FullName) }
      else { $files.Add([pscustomobject]@{ path=$rel; size=$item.Length }); $bytes += $item.Length }
    }
  }
  if ($files.Count -ne $manifest.files -or $dirs.Count -ne $manifest.directories -or
      $bytes -ne $manifest.bytes -or @($manifest.sha256.PSObject.Properties).Count -ne $files.Count) {
    throw 'Backup inventory changed'
  }
  $mods = @(Get-ChildItem -LiteralPath (Join-Path $source 'mods') -File -Filter '*.jar' -Force -ErrorAction Stop)
  $clumps = @($mods | Where-Object { $_.Name -ceq 'Clumps-6.0.0.28.jar' })
  if ($mods.Count -ne 34 -or $clumps.Count -ne 1) { throw 'Unexpected source mod inventory' }
  $stageParent = Join-Path $project 'Arena-CompatStages'
  if (Test-Path -LiteralPath $stageParent) {
    $info = [IO.DirectoryInfo]::new($stageParent)
    if (-not $info.Exists -or ($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe stage root' }
  }
  $dest = Join-Path $stageParent ('bootable-no-clumps-' + $env:GITHUB_RUN_ID)
  $stage = $dest + '.staging'
  if ((Test-Path -LiteralPath $dest) -or (Test-Path -LiteralPath $stage)) { throw 'Existing stage' }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($project))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes + 536870912L)) { throw 'Insufficient copy space' }
  $phase = 'HASH_COPY'
  New-Item -ItemType Directory -Path (Join-Path $stage 'server') -Force -ErrorAction Stop | Out-Null
  $owned = $true
  New-Item -ItemType Directory -Path (Join-Path $stage 'excluded-backup') -Force -ErrorAction Stop | Out-Null
  foreach ($dir in $dirs) { New-Item -ItemType Directory -Path (Join-Path (Join-Path $stage 'server') $dir) -Force -ErrorAction Stop | Out-Null }
  $clumpsPath = Join-Path 'mods' 'Clumps-6.0.0.28.jar'
  foreach ($file in $files) {
    $expected = $manifest.sha256.PSObject.Properties[$file.path]
    if (-not $expected -or $expected.Value -notmatch '^[A-Fa-f0-9]{64}$') { throw 'Backup manifest missing hash' }
    $sourceFile = Join-Path $source $file.path
    $copy = if ($file.path -ceq $clumpsPath) {
      Join-Path (Join-Path $stage 'excluded-backup') 'Clumps-6.0.0.28.jar'
    } else { Join-Path (Join-Path $stage 'server') $file.path }
    if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256 -ErrorAction Stop).Hash -ne $expected.Value) {
      throw 'Backup hash changed'
    }
    Copy-Item -LiteralPath $sourceFile -Destination $copy -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256 -ErrorAction Stop).Hash -ne $expected.Value) {
      throw 'Compatibility copy hash mismatch'
    }
  }
  if (@(Get-ChildItem -LiteralPath (Join-Path $stage 'server/mods') -File -Filter '*.jar').Count -ne 33 -or
      -not (Test-Path -LiteralPath (Join-Path $stage 'excluded-backup/Clumps-6.0.0.28.jar')) -or
      @(Get-ChildItem -LiteralPath (Join-Path $stage 'server') -Recurse -File -Force).Count -ne $files.Count - 1) {
    throw 'Copy inventory mismatch'
  }
  $phase = 'FINALIZE'
  @{ schema=1; backup_run=$BackupRunId; source_verified_offline=$true; copy_hash_verified=$true;
     copied_files=$files.Count; removed_from_runnable_copy='Clumps-6.0.0.28.jar';
     live_server_unchanged=$true; test_server_started=$false; client_join_tested=$false } |
     ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage 'private-copy-manifest.json') -Encoding UTF8
  [IO.Directory]::Move($stage,$dest)
  $owned = $false
  Write-Output '::notice title=No-Clumps runnable copy::COPY_PREPARED=true SOURCE_OFFLINE_BACKUP_VERIFIED=true COPY_HASH_VERIFIED=true COPY_MODS=33 EXCLUDED_CLUMPS_PRESERVED=true; LIVE_SERVER_UNCHANGED=true TEST_SERVER_STARTED=false JOIN_TESTED=false PRIVATE_ONLY=true'
  exit 0
} catch {
  Write-Output ('::error title=No-Clumps runnable copy::STAGE_FAILED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; LIVE_SERVER_UNCHANGED=true PRIVATE_ONLY=true')
  exit 2
} finally {
  if ($owned -and $stage -and (Test-Path -LiteralPath $stage)) {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
  }
}
