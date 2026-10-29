# In-place Freeroam client mod update, only after an exact read-only inventory match.
# Writes ONLY the six owner-approved JAR removals and a local backup outside instances.
param([Parameter(Mandatory=$true)][string]$Profile)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$approved = @(
  'CTM-MC1.16.1-1.1.2.6.jar',
  'DynamicSurroundings-1.16.5-4.0.5.0.jar',
  'InGameAccountSwitcher-Forge-1.16-8.0.1.jar',
  'lightfallclient-1.0.0.jar',
  'notenoughanimations-1.2.4.jar',
  'TRansliterationLib-1.0.4.jar'
)
$backupReady = $false
$backup = $null
$mods = $null
$baseline = @{}
function Assert-GameStopped {
  if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
    if (@(Get-Process -Name 'prismlauncher','java','javaw','minecraft' -ErrorAction SilentlyContinue).Count -gt 0) {
      throw 'Prism or Minecraft or Java is active'
    }
  }
}
try {
  if ((Split-Path -Path $Profile -Leaf) -cne 'Freeroam 1.0.0') { throw 'Wrong profile' }
  $instances = Split-Path -Parent $Profile
  $launcher = Split-Path -Parent $instances
  if ((Split-Path -Leaf $instances) -cne 'instances' -or
      (Split-Path -Leaf $launcher) -cne 'PrismLauncher') { throw 'Wrong parent' }
  if (-not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'No unique run id' }
  foreach ($p in @($launcher, $instances, $Profile)) {
    $entry = Get-Item -LiteralPath $p -ErrorAction Stop
    if (-not $entry.PSIsContainer -or ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe directory' }
  }
  Assert-GameStopped
  # The preflight reads only .minecraft/mods and rejects any unknown/missing JAR.
  & (Join-Path $PSScriptRoot 'fc_freeroam_target_preflight.ps1') -Profile $Profile -Quiet
  if ($LASTEXITCODE -ne 0) { throw 'Freeroam inventory did not match declaration' }
  $game = Join-Path $Profile '.minecraft'
  if (-not (Test-Path -LiteralPath $game -PathType Container)) {
    $game = Join-Path $Profile 'minecraft'
  }
  $mods = Join-Path $game 'mods'
  if (-not (Test-Path -LiteralPath $mods -PathType Container)) { throw 'No mods directory' }
  $list = @((Get-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'agent/FREEROAM-LISTA-DECLARATA.json') -Raw | ConvertFrom-Json).jar_names)
  foreach ($name in $list) {
    $baseline[$name] = (Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash
  }
  $backupParent = Join-Path $launcher 'Arena-Mods-Backups'
  if (Test-Path -LiteralPath $backupParent) {
    $b = Get-Item -LiteralPath $backupParent -ErrorAction Stop
    if (-not $b.PSIsContainer -or ($b.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe backup location' }
  }
  $backup = Join-Path $backupParent ('fc-lite-' + $env:GITHUB_RUN_ID)
  if (Test-Path -LiteralPath $backup) { throw 'Existing backup' }
  $bytes = 0L
  foreach ($name in $approved) { $bytes += (Get-Item -LiteralPath (Join-Path $mods $name)).Length }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($launcher))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes * 2 + 16777216L)) { throw 'Insufficient backup space' }
  New-Item -ItemType Directory -Path $backup -ErrorAction Stop | Out-Null
  # Private local manifest, never uploaded to GitHub, worlds and account data untouched.
  @{ original_jar_count=28; target_jar_count=22; original_hashes=$baseline; excluded=$approved } |
    ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backup 'manifest.json') -Encoding UTF8
  foreach ($name in $approved) {
    $src = Join-Path $mods $name
    $copy = Join-Path $backup $name
    Copy-Item -LiteralPath $src -Destination $copy -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $baseline[$name]) { throw 'Backup digest mismatch' }
  }
  $backupReady = $true
  Assert-GameStopped
  foreach ($name in $approved) {
    $src = Join-Path $mods $name
    if ((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash -ne $baseline[$name]) { throw 'Source changed during backup' }
    Remove-Item -LiteralPath $src -Force -ErrorAction Stop
  }
  $jars = @(Get-ChildItem -LiteralPath $mods -Force | Where-Object { $_.Name -match '\.jar$' })
  if ($jars.Count -ne 22) { throw 'Unexpected target count' }
  foreach ($name in $list) {
    $src = Join-Path $mods $name
    if ($approved -ccontains $name) {
      if (Test-Path -LiteralPath $src) { throw 'Approved JAR still present' }
    } elseif ((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash -ne $baseline[$name]) {
      throw 'Retained JAR modified'
    }
  }
  Write-Output '::notice title=Freeroam client::MODS_22_APPLIED; SIX_BACKUPS_LOCAL=true; PROFILE_WORLD_ACCOUNT_UNTOUCHED=true; CLIENT_JOIN=NOT_TESTED'
  exit 0
} catch {
  $restored = $true
  if ($backupReady) {
    foreach ($name in $approved) {
      try {
        $src = Join-Path $mods $name
        if (-not (Test-Path -LiteralPath $src)) {
          Copy-Item -LiteralPath (Join-Path $backup $name) -Destination $src -ErrorAction Stop
        }
        if ((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash -ne $baseline[$name]) { $restored = $false }
      } catch { $restored = $false }
    }
  }
  if ($backupReady -and -not $restored) {
    Write-Output '::error title=Freeroam client::RECOVERY_REQUIRED; PRIVATE_BACKUP_LOCAL=true; NO_SERVER_STARTED=true'
  } elseif ($backupReady) {
    Write-Output '::error title=Freeroam client::APPLY_BLOCKED_AND_RESTORED; PRIVATE_BACKUP_LOCAL=true; NO_SERVER_STARTED=true'
  } else {
    Write-Output '::error title=Freeroam client::APPLY_BLOCKED_BEFORE_REMOVAL; NO_SERVER_STARTED=true'
  }
  # Discard exception text: it can include private machine paths.
  exit 2
}
