# Local, world-free compatibility stage. Copies all server mod JARs except Clumps,
# preserving Clumps separately, while leaving the running server completely untouched.
param([Parameter(Mandatory=$true)][string]$Server)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$stage = $null
$owned = $false
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong source or run id' }
  $project = Split-Path -Parent $Server
  $mods = Join-Path $Server 'mods'
  foreach ($path in @($project,$Server,$mods)) {
    $dir = [IO.DirectoryInfo]::new($path)
    if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe source directory' }
  }
  $files = @(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar' -Force -ErrorAction Stop)
  if ($files.Count -ne 34 -or @($files | Where-Object { $_.Name -ceq 'Clumps-6.0.0.28.jar' }).Count -ne 1) {
    throw 'Server mod inventory changed'
  }
  $hashes = @{}
  $bytes = 0L
  foreach ($item in $files) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $item.Length -gt 300000000 -or
        -not [regex]::IsMatch($item.Name,'^[A-Za-z0-9 _().+\-]{1,160}\.jar$',[Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
      throw 'Unsafe server JAR'
    }
    $hashes[$item.Name] = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    $bytes += $item.Length
  }
  $parent = Join-Path $project 'Arena-CompatStages'
  if (Test-Path -LiteralPath $parent) {
    $dir = [IO.DirectoryInfo]::new($parent)
    if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe stage parent' }
  }
  $dest = Join-Path $parent ('server-no-clumps-' + $env:GITHUB_RUN_ID)
  $stage = $dest + '.staging'
  if ((Test-Path -LiteralPath $dest) -or (Test-Path -LiteralPath $stage)) { throw 'Stage already exists' }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($project))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes + 16777216L)) { throw 'Insufficient space' }
  New-Item -ItemType Directory -Path (Join-Path $stage 'mods') -Force -ErrorAction Stop | Out-Null
  $owned = $true
  New-Item -ItemType Directory -Path (Join-Path $stage 'excluded-backup') -Force -ErrorAction Stop | Out-Null
  foreach ($item in $files) {
    $targetDir = if ($item.Name -ceq 'Clumps-6.0.0.28.jar') { 'excluded-backup' } else { 'mods' }
    $copy = Join-Path (Join-Path $stage $targetDir) $item.Name
    Copy-Item -LiteralPath $item.FullName -Destination $copy -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $hashes[$item.Name] -or
        (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash -ne $hashes[$item.Name]) { throw 'Digest mismatch' }
  }
  if (@(Get-ChildItem -LiteralPath (Join-Path $stage 'mods') -File -Filter '*.jar').Count -ne 33 -or
      @(Get-ChildItem -LiteralPath (Join-Path $stage 'excluded-backup') -File -Filter '*.jar').Count -ne 1) { throw 'Stage count mismatch' }
  @{ schema=1; source_jar_count=34; stage_jar_count=33; excluded='Clumps-6.0.0.28.jar'; hashes=$hashes; world_copied=$false } |
    ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage 'private-manifest.json') -Encoding UTF8
  [IO.Directory]::Move($stage,$dest)
  $owned = $false
  Write-Output '::notice title=Server compatibility stage::STAGE_MOD_JARS=33; CLUMPS_PRIVATE_BACKUP=true; SOURCE_MOD_JARS=34; SOURCE_UNCHANGED=true; WORLD_CONFIG_PLUGINS_NOT_COPIED=true; NO_SERVER_STARTED=true; JOIN_NOT_TESTED=true'
  exit 0
} catch {
  # No exception text; it can disclose private paths.
  Write-Output '::error title=Server compatibility stage::STAGE_BLOCKED_OR_FAILED; SERVER_UNCHANGED=true; NO_WORLD_READ=true'
  exit 2
} finally {
  if ($owned -and $stage -and (Test-Path -LiteralPath $stage)) {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
  }
}
