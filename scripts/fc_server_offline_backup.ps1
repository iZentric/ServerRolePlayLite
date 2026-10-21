# Private, whole-tree offline backup and independent restore rehearsal.
# Never uploads content or changes the live server. The caller must stop it first.
param([Parameter(Mandatory=$true)][string]$Server,[switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$stage = $null
$rehearsal = $null
$stageOwned = $false
$rehearsalOwned = $false
$phase = 'PREFLIGHT'
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong source or run id' }
  $project = Split-Path -Parent $Server
  foreach ($path in @($project,$Server)) {
    $dir = [IO.DirectoryInfo]::new($path)
    if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe source root' }
  }
  if (-not $Synthetic) {
    $live = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
      $_.CommandLine -and $_.CommandLine.IndexOf($Server,[StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    if ($live.Count -ne 0 -or @(Get-NetTCPConnection -State Listen -LocalPort 25565 -ErrorAction SilentlyContinue).Count -ne 0) {
      throw 'Server is not confirmed offline'
    }
  }
  $phase = 'INVENTORY'
  $dirs = New-Object 'System.Collections.Generic.List[string]'
  $files = New-Object 'System.Collections.Generic.List[object]'
  $queue = [System.Collections.Generic.Queue[string]]::new()
  $queue.Enqueue($Server)
  $bytes = 0L
  $rootLen = $Server.TrimEnd([char[]]@([char]92,[char]47)).Length
  while ($queue.Count -gt 0) {
    $dir = $queue.Dequeue()
    foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop)) {
      if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe reparse entry' }
      $relative = $item.FullName.Substring($rootLen).TrimStart([char[]]@([char]92,[char]47))
      if ($relative.StartsWith('..') -or [IO.Path]::IsPathRooted($relative)) { throw 'Unsafe relative entry' }
      if ($item.PSIsContainer) { $dirs.Add($relative); $queue.Enqueue($item.FullName) }
      else { $files.Add([pscustomobject]@{ path=$relative; size=$item.Length }); $bytes += $item.Length }
      if ($files.Count -gt 200000 -or $bytes -gt 200000000000L) { throw 'Oversized source' }
    }
  }
  if (-not $Synthetic -and ($files.Count -lt 100 -or $bytes -lt 10000000)) { throw 'Incomplete server tree' }
  $backupParent = Join-Path $project 'Arena-Private-Backups'
  if (Test-Path -LiteralPath $backupParent) {
    $parent = [IO.DirectoryInfo]::new($backupParent)
    if (-not $parent.Exists -or ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe backup root' }
  }
  $dest = Join-Path $backupParent ('offline-' + $env:GITHUB_RUN_ID)
  $stage = $dest + '.staging'
  $rehearsal = Join-Path $backupParent ('.restore-test-' + $env:GITHUB_RUN_ID)
  foreach ($path in @($dest,$stage,$rehearsal)) { if (Test-Path -LiteralPath $path) { throw 'Target already exists' } }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($project))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes * 2 + 1073741824L)) {
    if (-not $Synthetic) { throw 'Insufficient space for two copies' }
  }
  $phase = 'COPY_AND_HASH'
  New-Item -ItemType Directory -Path (Join-Path $stage 'server') -Force -ErrorAction Stop | Out-Null
  $stageOwned = $true
  foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path (Join-Path (Join-Path $stage 'server') $dir) -Force -ErrorAction Stop | Out-Null
  }
  $hashes = @{}
  foreach ($file in $files) {
    $source = Join-Path $Server $file.path
    $copy = Join-Path (Join-Path $stage 'server') $file.path
    $item = Get-Item -LiteralPath $source -ErrorAction Stop
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -ne $file.size) { throw 'Source changed' }
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256 -ErrorAction Stop).Hash
    Copy-Item -LiteralPath $source -Destination $copy -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256 -ErrorAction Stop).Hash -ne $hash -or
        (Get-FileHash -LiteralPath $source -Algorithm SHA256 -ErrorAction Stop).Hash -ne $hash) { throw 'Copy digest mismatch' }
    $hashes[$file.path] = $hash
  }
  $phase = 'RESTORE_REHEARSAL'
  New-Item -ItemType Directory -Path (Join-Path $rehearsal 'server') -Force -ErrorAction Stop | Out-Null
  $rehearsalOwned = $true
  foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path (Join-Path (Join-Path $rehearsal 'server') $dir) -Force -ErrorAction Stop | Out-Null
  }
  foreach ($file in $files) {
    $copy = Join-Path (Join-Path $stage 'server') $file.path
    $restore = Join-Path (Join-Path $rehearsal 'server') $file.path
    Copy-Item -LiteralPath $copy -Destination $restore -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $restore -Algorithm SHA256 -ErrorAction Stop).Hash -ne $hashes[$file.path] -or
        (Get-FileHash -LiteralPath $copy -Algorithm SHA256 -ErrorAction Stop).Hash -ne $hashes[$file.path]) {
      throw 'Rehearsal digest mismatch'
    }
  }
  $restoredFiles = @(Get-ChildItem -LiteralPath (Join-Path $rehearsal 'server') -Recurse -File -Force -ErrorAction Stop)
  $restoredDirs = @(Get-ChildItem -LiteralPath (Join-Path $rehearsal 'server') -Recurse -Directory -Force -ErrorAction Stop)
  if ($restoredFiles.Count -ne $files.Count -or $restoredDirs.Count -ne $dirs.Count) { throw 'Rehearsal inventory mismatch' }
  $phase = 'FINALIZE'
  @{ schema=1; source='offline'; files=$files.Count; directories=$dirs.Count; bytes=$bytes; sha256=$hashes;
     consistent_offline_snapshot=$true; independent_restore_copy_verified=$true } |
     ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage 'private-manifest.json') -Encoding UTF8 -ErrorAction Stop
  [IO.Directory]::Move($stage,$dest)
  $stageOwned = $false
  Write-Output ('::notice title=Private offline backup::BACKUP_VERIFIED=true RESTORE_COPY_VERIFIED=true FILES=' + $files.Count + ' DIRECTORIES=' + $dirs.Count + ' PRIVATE_ONLY=true LIVE_JARS_UNCHANGED=true')
  exit 0
} catch {
  Write-Output ('::error title=Private offline backup::BACKUP_UNVERIFIED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; PRIVATE_ONLY=true LIVE_JARS_UNCHANGED=true')
  exit 2
} finally {
  if ($rehearsalOwned -and $rehearsal -and (Test-Path -LiteralPath $rehearsal)) {
    Remove-Item -LiteralPath $rehearsal -Recurse -Force -ErrorAction SilentlyContinue
  }
  if ($stageOwned -and $stage -and (Test-Path -LiteralPath $stage)) {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
  }
}
