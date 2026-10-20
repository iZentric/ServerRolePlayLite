# Create a SEPARATE Prism instance from the verified original; never edit the original.
# Copy only Prism version metadata and 22 approved JARs. No saves, accounts, logs,
# config, resourcepacks or server files are read/copied/uploaded.
param([Parameter(Mandatory=$true)][string]$Source, [switch]$SyntheticDiagnostics)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$destination = $null
$staging = $null
$stagingOwned = $false

function Assert-NoActiveClient {
  if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { return }
  if (@(Get-Process -Name 'prismlauncher','minecraft' -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Launcher or game active'
  }
  # The owner-selected existing server can remain online; any other JVM fails closed.
  $server = 'C:\Users\Administrator\Desktop\FunCityLocal\server'
  $jvms = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop)
  if ($jvms.Count -eq 0) { return }
  $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop)
  foreach ($jvm in $jvms) {
    if (-not $jvm.CommandLine -or
        $jvm.CommandLine.IndexOf($server, [StringComparison]::OrdinalIgnoreCase) -lt 0 -or
        @($listeners | Where-Object { $_.OwningProcess -eq $jvm.ProcessId }).Count -eq 0) {
      throw 'Unclassified JVM active'
    }
  }
}
function Assert-SafeFile([string]$Path) {
  $item = Get-Item -LiteralPath $Path -ErrorAction Stop
  if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Unsafe source file'
  }
}
function Assert-SafeDirectory([string]$Path) {
  $item = Get-Item -LiteralPath $Path -ErrorAction Stop
  if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Unsafe source directory'
  }
}
try {
  if ((Split-Path -Path $Source -Leaf) -cne 'Freeroam 1.0.0') { throw 'Wrong source' }
  $instances = Split-Path -Parent $Source
  $launcher = Split-Path -Parent $instances
  if ((Split-Path -Leaf $instances) -cne 'instances' -or
      (Split-Path -Leaf $launcher) -cne 'PrismLauncher') { throw 'Wrong parent' }
  if (-not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'No unique run id' }
  $destination = Join-Path $instances 'FunCity RP Lite'
  $staging = Join-Path $instances ('FunCity RP Lite.staging.' + $env:GITHUB_RUN_ID)
  if ((Test-Path -LiteralPath $destination) -or (Test-Path -LiteralPath $staging)) { throw 'Destination exists' }
  foreach ($dir in @($launcher, $instances, $Source)) { Assert-SafeDirectory $dir }
  Assert-NoActiveClient
  # Exact-name inventory gate, including rejecting extra JARs, symlinks and drift.
  & (Join-Path $PSScriptRoot 'fc_freeroam_target_preflight.ps1') -Profile $Source -Quiet
  if ($LASTEXITCODE -ne 0) { throw 'Original inventory changed' }
  $gameCandidates = @(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Source $_) })
  if ($gameCandidates.Count -ne 1) { throw 'Ambiguous game folder' }
  $gameName = $gameCandidates[0]
  $game = Join-Path $Source $gameName
  $mods = Join-Path $game 'mods'
  foreach ($dir in @($game, $mods)) { Assert-SafeDirectory $dir }
  $cfg = Join-Path $Source 'instance.cfg'
  $pack = Join-Path $Source 'mmc-pack.json'
  foreach ($file in @($cfg, $pack)) { Assert-SafeFile $file }
  $null = Get-Content -LiteralPath $pack -Raw | ConvertFrom-Json
  # Custom version patches might be necessary for the loader; do not silently omit them.
  if (Test-Path -LiteralPath (Join-Path $Source 'patches')) { throw 'Custom patches require review' }
  $cfgText = Get-Content -LiteralPath $cfg -Raw
  $nameLines = @([regex]::Matches($cfgText, '(?im)^name=.*$'))
  if ($nameLines.Count -ne 1) { throw 'Missing or duplicate instance name' }
  $cfgText = [regex]::Replace($cfgText, '(?im)^name=.*$', 'name=FunCity RP Lite')
  $selection = Get-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'agent/FUNCITY-RP-LITE-SELECTIE.json') -Raw | ConvertFrom-Json
  $kept = @($selection.retained_in_future_target)
  if ($kept.Count -ne 22 -or @($selection.removed_from_future_target).Count -ne 6) { throw 'Invalid selection' }
  $hashes = @{}
  foreach ($name in $kept) {
    $jar = Join-Path $mods $name
    Assert-SafeFile $jar
    $hashes[$name] = (Get-FileHash -LiteralPath $jar -Algorithm SHA256).Hash
  }
  $bytes = 0L
  foreach ($name in $kept) { $bytes += (Get-Item -LiteralPath (Join-Path $mods $name)).Length }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($instances))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes + 16777216L)) { throw 'Insufficient space' }
  New-Item -ItemType Directory -Path (Join-Path (Join-Path $staging $gameName) 'mods') -Force -ErrorAction Stop | Out-Null
  $stagingOwned = $true
  [IO.File]::WriteAllText((Join-Path $staging 'instance.cfg'), $cfgText, [Text.UTF8Encoding]::new($false))
  Copy-Item -LiteralPath $pack -Destination (Join-Path $staging 'mmc-pack.json') -ErrorAction Stop
  foreach ($name in $kept) {
    Copy-Item -LiteralPath (Join-Path $mods $name) -Destination (Join-Path (Join-Path (Join-Path $staging $gameName) 'mods') $name) -ErrorAction Stop
    if ((Get-FileHash -LiteralPath (Join-Path (Join-Path (Join-Path $staging $gameName) 'mods') $name) -Algorithm SHA256).Hash -ne $hashes[$name] -or
        (Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash -ne $hashes[$name]) { throw 'Copy digest mismatch' }
  }
  if (@(Get-ChildItem -LiteralPath (Join-Path (Join-Path $staging $gameName) 'mods') -File -Filter '*.jar').Count -ne 22) { throw 'Target inventory mismatch' }
  Assert-NoActiveClient
  if (Test-Path -LiteralPath $destination) { throw 'Destination appeared' }
  [IO.Directory]::Move($staging, $destination)
  $stagingOwned = $false
  Write-Output '::notice title=Prism new profile::SEPARATE_LITE_PROFILE_CREATED=true; TARGET_JARS=22; SOURCE_JARS=28; SOURCE_UNCHANGED=true; WORLDS_ACCOUNTS_UNTOUCHED=true; CLIENT_JOIN=NOT_TESTED'
  exit 0
} catch {
  if ($SyntheticDiagnostics -and [Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    Write-Output ('::error title=Prism fixture::LINE=' + $_.InvocationInfo.ScriptLineNumber + ' TYPE=' + $_.Exception.GetType().Name)
  }
  Write-Output '::error title=Prism new profile::CREATION_BLOCKED_OR_FAILED; SOURCE_UNCHANGED=true; NO_SERVER_CHANGED=true'
  exit 2
} finally {
  if ($stagingOwned -and $staging -and (Test-Path -LiteralPath $staging)) {
    # Only the staging folder this run created. Never delete an existing profile.
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
  }
}
