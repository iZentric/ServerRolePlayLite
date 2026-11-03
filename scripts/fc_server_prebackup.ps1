# Private pre-maintenance copy of selected existing server. READ/COPY ONLY:
# no process stop, world edit, upload, RCON, port change or second server.
# An online copy is a safety net, NOT a consistent offline/restore-tested backup.
param([Parameter(Mandatory=$true)][string]$Server)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$staging = $null
$owned = $false
$phase = 'VALIDATE'
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong source or run id' }
  $project = Split-Path -Parent $Server
  foreach ($dir in @($project,$Server)) {
    $item = [IO.DirectoryInfo]::new($dir)
    if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe source' }
  }
  $phase = 'ENUMERATE'
  $queue = [System.Collections.Generic.Queue[string]]::new()
  $queue.Enqueue($Server)
  $entries = New-Object 'System.Collections.Generic.List[object]'
  $bytes = 0L
  while ($queue.Count -gt 0) {
    $dir = $queue.Dequeue()
    foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop)) {
      if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point' }
      $relative = $item.FullName.Substring($Server.TrimEnd([char[]]@([char]92,[char]47)).Length).TrimStart([char[]]@([char]92,[char]47))
      # Logs and session.lock are volatile and not needed to restore game state.
      if ($relative -match '^(?i:logs|crash-reports)[\\/]' -or
          $relative -match '(^|[\\/])session\.lock$') { continue }
      if ($item.PSIsContainer) { $queue.Enqueue($item.FullName) }
      else {
        $entries.Add([pscustomobject]@{relative=$relative; bytes=$item.Length})
        $bytes += $item.Length
      }
      if ($entries.Count -gt 200000 -or $bytes -gt 200000000000L) { throw 'Oversized source' }
    }
  }
  if ($entries.Count -lt 100 -or $bytes -lt 10000000) { throw 'Incomplete server tree' }
  $backupParent = Join-Path $project 'Arena-Private-Backups'
  if (Test-Path -LiteralPath $backupParent) {
    $item = [IO.DirectoryInfo]::new($backupParent)
    if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe backup parent' }
  }
  $dest = Join-Path $backupParent ('pre-maintenance-' + $env:GITHUB_RUN_ID)
  $staging = $dest + '.staging'
  if ((Test-Path -LiteralPath $dest) -or (Test-Path -LiteralPath $staging)) { throw 'Existing backup' }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($project))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes * 2 + 1073741824L)) { throw 'Insufficient backup space' }
  $phase = 'COPY_HASH_VERIFY'
  New-Item -ItemType Directory -Path $staging -Force -ErrorAction Stop | Out-Null
  $owned = $true
  $hashes = @{}
  foreach ($entry in $entries) {
    $source = Join-Path $Server $entry.relative
    $copy = Join-Path $staging $entry.relative
    $parent = Split-Path -Parent $copy
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force -ErrorAction Stop | Out-Null }
    $sourceItem = Get-Item -LiteralPath $source -ErrorAction Stop
    if (($sourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $sourceItem.Length -ne $entry.bytes) { throw 'Source changed' }
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $source -Destination $copy -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $hash -or
        (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $hash) { throw 'Backup digest mismatch' }
    $hashes[$entry.relative] = $hash
  }
  $phase = 'PRIVATE_MANIFEST'
  # Private local manifest; never expose world names, account material or server passwords.
  @{ schema=1; files=$entries.Count; bytes=$bytes; sha256=$hashes;
     live_source=$true; consistent_offline_snapshot=$false; restore_tested=$false } |
     ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $staging 'private-manifest.json') -Encoding UTF8
  $phase = 'FINALIZE'
  [IO.Directory]::Move($staging,$dest)
  $owned = $false
  Write-Output ('::notice title=Server private prebackup::FILES_COPIED_AND_HASHED=' + $entries.Count + ' SOURCE_UNCHANGED_DURING_EACH_COPY=true; WORLD_CONFIG_MODS_PLUGINS_PRIVATE=true; SERVER_NOT_STOPPED=true; CONSISTENT_OFFLINE_BACKUP=false; RESTORE_NOT_TESTED=true')
  exit 0
} catch {
  # Only code-defined phase/type/line, never the exception message or private path.
  Write-Output ('::error title=Server private prebackup::COPY_BLOCKED_OR_FAILED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; LIVE_SERVER_UNCHANGED=true; NO_UPLOAD=true')
  exit 2
} finally {
  if ($owned -and $staging -and (Test-Path -LiteralPath $staging)) {
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
  }
}
