# Reversible compatibility experiment: add exactly the server's Clumps JAR to
# the separate Lite client. No server, original profile, world or account write.
param([Parameter(Mandatory=$true)][string]$Profile,
      [Parameter(Mandatory=$true)][string]$Server)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$staging = $null
$stageOwned = $false
function Assert-Dir([string]$Path) {
  $dir = [IO.DirectoryInfo]::new($Path)
  if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe directory' }
}
function Assert-File([string]$Path) {
  $item = Get-Item -LiteralPath $Path -ErrorAction Stop
  if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe file' }
}
function Assert-ClientStopped([string]$ServerPath) {
  if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { return }
  if (@(Get-Process -Name 'prismlauncher','minecraft' -ErrorAction SilentlyContinue).Count -gt 0) { throw 'Prism or client active' }
  $jvms = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop)
  if ($jvms.Count -eq 0) { return }
  $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop)
  foreach ($jvm in $jvms) {
    if (-not $jvm.CommandLine -or
        $jvm.CommandLine.IndexOf($ServerPath, [StringComparison]::OrdinalIgnoreCase) -lt 0 -or
        @($listeners | Where-Object { $_.OwningProcess -eq $jvm.ProcessId }).Count -eq 0) {
      throw 'Unclassified Java process active'
    }
  }
}
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances' -or
      (Split-Path -Leaf (Split-Path -Parent (Split-Path -Parent $Profile))) -cne 'PrismLauncher' -or
      (Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Wrong owner-selected paths' }
  if (-not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Missing run id' }
  $instances = Split-Path -Parent $Profile
  $original = Join-Path $instances 'Freeroam 1.0.0'
  $gameChoices = @(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) })
  if ($gameChoices.Count -ne 1) { throw 'Ambiguous game directory' }
  $game = $gameChoices[0]
  $mods = Join-Path (Join-Path $Profile $game) 'mods'
  $originalMods = Join-Path (Join-Path $original $game) 'mods'
  $serverMods = Join-Path $Server 'mods'
  foreach ($dir in @($instances,$original,$Profile,(Join-Path $Profile $game),$mods,$Server,$serverMods)) { Assert-Dir $dir }
  Assert-ClientStopped $Server
  $selection = Get-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'agent/FUNCITY-RP-LITE-SELECTIE.json') -Raw | ConvertFrom-Json
  $kept = @($selection.retained_in_future_target)
  $listed = @(Get-ChildItem -LiteralPath $mods -Force -ErrorAction Stop)
  if ($kept.Count -ne 22 -or $listed.Count -ne 22) { throw 'Not the original Lite baseline' }
  $baseline = @{}
  foreach ($item in $listed) {
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $kept -cnotcontains $item.Name) { throw 'Unexpected Lite file' }
    $baseline[$item.Name] = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    if ($baseline[$item.Name] -ne (Get-FileHash -LiteralPath (Join-Path $originalMods $item.Name) -Algorithm SHA256).Hash) {
      throw 'Lite changed since original copy'
    }
  }
  $filename = 'Clumps-6.0.0.28.jar'
  $source = Join-Path $serverMods $filename
  $dest = Join-Path $mods $filename
  $staging = Join-Path $mods ($filename + '.staging.' + $env:GITHUB_RUN_ID)
  if ((Test-Path -LiteralPath $dest) -or (Test-Path -LiteralPath $staging)) { throw 'Already installed or staging exists' }
  Assert-File $source
  try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
  $zip = [IO.Compression.ZipFile]::OpenRead($source)
  try {
    $entry = $zip.GetEntry('META-INF/mods.toml')
    if ($null -eq $entry -or $entry.Length -gt 1048576) { throw 'Missing Forge metadata' }
    $reader = [IO.StreamReader]::new($entry.Open(),[Text.Encoding]::UTF8)
    try { $toml = $reader.ReadToEnd() } finally { $reader.Dispose() }
    if ($toml -notmatch '(?m)^\s*modId\s*=\s*["'']clumps["'']') { throw 'Wrong mod ID' }
  } finally { $zip.Dispose() }
  $sha = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
  $bytes = (Get-Item -LiteralPath $source).Length
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($instances))
  if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes + 16777216L)) { throw 'Insufficient space' }
  Copy-Item -LiteralPath $source -Destination $staging -ErrorAction Stop
  $stageOwned = $true
  if ((Get-FileHash -LiteralPath $staging -Algorithm SHA256).Hash -ne $sha -or
      (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $sha) { throw 'Source changed during copy' }
  foreach ($name in $kept) {
    if ((Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash -ne $baseline[$name]) { throw 'Lite changed during copy' }
  }
  Assert-ClientStopped $Server
  if (Test-Path -LiteralPath $dest) { throw 'Clumps appeared' }
  [IO.File]::Move($staging,$dest)
  $stageOwned = $false
  Write-Output '::notice title=Lite Clumps compatibility::LITE_JARS=23; CLUMPS_COPIED_FROM_SELECTED_SERVER=true; HASH_MATCH=true; ORIGINAL_28_UNCHANGED=true; SERVER_UNCHANGED=true; CLIENT_JOIN=NOT_TESTED'
  exit 0
} catch {
  Write-Output '::error title=Lite Clumps compatibility::APPLY_BLOCKED_OR_FAILED; ORIGINAL_UNCHANGED=true; SERVER_UNCHANGED=true'
  exit 2
} finally {
  if ($stageOwned -and $staging -and (Test-Path -LiteralPath $staging)) {
    Remove-Item -LiteralPath $staging -Force -ErrorAction SilentlyContinue
  }
}
