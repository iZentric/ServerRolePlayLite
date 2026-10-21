# Build a SEPARATE Prism Forge 1.16.5 candidate, using exact owner-downloaded jars.
# Never edit the original Freeroam or functional Lite, server, worlds, accounts or launcher processes.
param([Parameter(Mandatory=$true)][string]$Source,
      [Parameter(Mandatory=$true)][string]$Downloads,
      [switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression
$phase='PREFLIGHT'
$stage=$null
$stageOwned=$false
function Safe-Directory([string]$Path) {
  $dir=[IO.DirectoryInfo]::new($Path)
  if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe folder' }
}
function Safe-File([string]$Path) {
  $file=Get-Item -LiteralPath $Path -ErrorAction Stop
  if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe file' }
  return $file
}
function Assert-GameClosed {
  if ($Synthetic) { return }
  if (@(Get-Process -Name 'prismlauncher','minecraft' -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Prism or client active; close normally'
  }
  $server='C:\Users\Administrator\Desktop\FunCityLocal\server'
  $jvms=@(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop)
  if ($jvms.Count -gt 0) {
    $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)
    foreach ($jvm in $jvms) {
      if (-not $jvm.CommandLine -or
          $jvm.CommandLine.IndexOf($server,[StringComparison]::OrdinalIgnoreCase) -lt 0 -or
          @($listeners | Where-Object { $_.OwningProcess -eq $jvm.ProcessId }).Count -eq 0) {
        throw 'Unclassified game JVM active'
      }
    }
  }
}
function Assert-ModJar([string]$Path,[string]$ModId) {
  $archive=[IO.Compression.ZipFile]::OpenRead($Path)
  try {
    $entry=$archive.GetEntry('META-INF/mods.toml')
    if (-not $entry -or $entry.Length -gt 50000) { throw 'Missing/unsafe Forge mod metadata' }
    $reader=[IO.StreamReader]::new($entry.Open())
    try { $toml=$reader.ReadToEnd() } finally { $reader.Dispose() }
    if ($toml -notmatch ('(?im)^\s*modId\s*=\s*"' + [regex]::Escape($ModId) + '"\s*$')) {
      throw 'Unexpected Forge mod id'
    }
  } finally { $archive.Dispose() }
}
try {
  $instances=Split-Path -Parent $Source
  $launcher=Split-Path -Parent $instances
  if ((Split-Path -Leaf $Source) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf $instances) -cne 'instances' -or
      (Split-Path -Leaf $launcher) -cne 'PrismLauncher' -or
      (Split-Path -Leaf $Downloads) -cne 'Downloads' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong profile/downloads/run id' }
  $target=Join-Path $instances 'FunCity RP Lite Embeddium TEST'
  $stage=Join-Path $instances ('FunCity RP Lite Embeddium TEST.staging.' + $env:GITHUB_RUN_ID)
  if ((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $stage)) { throw 'Test profile/stage already exists' }
  foreach ($dir in @($launcher,$instances,$Source,$Downloads)) { Safe-Directory $dir }
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Source $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous game directory' }
  $game=Join-Path $Source $games[0]
  $mods=Join-Path $game 'mods'
  foreach ($dir in @($game,$mods)) { Safe-Directory $dir }
  $cfg=Join-Path $Source 'instance.cfg'
  $pack=Join-Path $Source 'mmc-pack.json'
  $null=Safe-File $cfg
  $null=Safe-File $pack
  $null=(Get-Content -LiteralPath $pack -Raw -ErrorAction Stop | ConvertFrom-Json)
  if (Test-Path -LiteralPath (Join-Path $Source 'patches')) { throw 'Loader patches require manual review' }
  Assert-GameClosed
  $phase='EXACT_MODS_AND_BINARIES'
  $manifest=Get-Content -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) 'agent/FUNCITY-RP-LITE-SELECTIE.json') -Raw | ConvertFrom-Json
  $names=@($manifest.retained_in_future_target)
  $rubidium='rubidium-mc1.16.5-0.2.13.jar'
  $rubidiumOptions='TextruesRubidiumOptions-1.0.8-mc1.16.5.jar'
  $embeddium='embeddium-0.3.18+mc1.16.5.jar'
  $embeddiumOptions='textrue_embeddium_options-0.1.1+mc1.16.5.jar'
  if ($names.Count -ne 22 -or @($names | Where-Object { $_ -ceq $rubidium }).Count -ne 1 -or
      @($names | Where-Object { $_ -ceq $rubidiumOptions }).Count -ne 1) { throw 'Manifest changed' }
  $actual=@(Get-ChildItem -LiteralPath $mods -Force -ErrorAction Stop)
  if ($actual.Count -ne 22 -or @($actual | Where-Object {
    $_.PSIsContainer -or $_.Extension -cne '.jar' -or
    ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $names -cnotcontains $_.Name
  }).Count -gt 0) { throw 'Lite mods drifted/unsafe' }
  $hashes=@{}
  $bytes=0L
  foreach ($name in $names) {
    $jar=Safe-File (Join-Path $mods $name)
    $hashes[$name]=(Get-FileHash -LiteralPath $jar.FullName -Algorithm SHA256).Hash
    $bytes+=$jar.Length
  }
  $replacements=@($embeddium,$embeddiumOptions)
  foreach ($name in $replacements) {
    $jar=Safe-File (Join-Path $Downloads $name)
    if ((-not $Synthetic -and $jar.Length -lt 20000) -or $jar.Length -gt 5000000) { throw 'Candidate JAR size outside bound' }
    if (-not $Synthetic -and $name -ceq $embeddiumOptions -and $jar.Length -ne 132116) {
      throw 'TexTrue size differs from author GitHub release'
    }
    $hashes[$name]=(Get-FileHash -LiteralPath $jar.FullName -Algorithm SHA256).Hash
    $bytes+=$jar.Length
    if ($name -ceq $embeddium) { Assert-ModJar $jar.FullName 'embeddium' }
    if ($name -ceq $embeddiumOptions) { Assert-ModJar $jar.FullName 'textrues_embeddium_options' }
  }
  $cfgText=[IO.File]::ReadAllText($cfg,[Text.Encoding]::UTF8)
  if ([regex]::Matches($cfgText,'(?im)^name=.*$').Count -ne 1) { throw 'Instance name missing/duplicate' }
  $cfgText=[regex]::Replace($cfgText,'(?im)^name=.*$','name=FunCity RP Lite Embeddium TEST')
  if (-not $Synthetic) {
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($instances))
    if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($bytes + 16777216L)) { throw 'Insufficient disk space' }
  }
  $phase='COPY_NEW_PROFILE_ONLY'
  $stageMods=Join-Path (Join-Path $stage $games[0]) 'mods'
  New-Item -ItemType Directory -Path $stageMods -ErrorAction Stop -Force | Out-Null
  $stageOwned=$true
  [IO.File]::WriteAllText((Join-Path $stage 'instance.cfg'),$cfgText,[Text.UTF8Encoding]::new($false))
  Copy-Item -LiteralPath $pack -Destination (Join-Path $stage 'mmc-pack.json') -ErrorAction Stop
  $copyNames=@($names | Where-Object { $_ -cne $rubidium -and $_ -cne $rubidiumOptions })
  foreach ($name in $copyNames) {
    Copy-Item -LiteralPath (Join-Path $mods $name) -Destination (Join-Path $stageMods $name) -ErrorAction Stop
    if ((Get-FileHash -LiteralPath (Join-Path $stageMods $name) -Algorithm SHA256).Hash -cne $hashes[$name] -or
        (Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash -cne $hashes[$name]) {
      throw 'Lite source/copy changed'
    }
  }
  foreach ($name in $replacements) {
    Copy-Item -LiteralPath (Join-Path $Downloads $name) -Destination (Join-Path $stageMods $name) -ErrorAction Stop
    if ((Get-FileHash -LiteralPath (Join-Path $stageMods $name) -Algorithm SHA256).Hash -cne $hashes[$name] -or
        (Get-FileHash -LiteralPath (Join-Path $Downloads $name) -Algorithm SHA256).Hash -cne $hashes[$name]) {
      throw 'Candidate source/copy changed'
    }
  }
  if (@(Get-ChildItem -LiteralPath $stageMods -File -Filter '*.jar').Count -ne 22) { throw 'Target inventory mismatch' }
  # Fresh non-personal graphics options; NEVER copy worlds/accounts, configs, logs or last server.
  $preset="version:2586`nrenderDistance:5`ngraphicsMode:0`nparticles:1`nmipmapLevels:0`nentityShadows:false`n"
  [IO.File]::WriteAllText((Join-Path (Join-Path $stage $games[0]) 'options.txt'),$preset,[Text.UTF8Encoding]::new($false))
  Assert-GameClosed
  if (Test-Path -LiteralPath $target) { throw 'Target appeared during staging' }
  [IO.Directory]::Move($stage,$target)
  $stageOwned=$false
  Write-Output '::notice title=Prism Embeddium A/B::SEPARATE_TEST_PROFILE_CREATED=true JARS=22 RP_JARS_PRESERVED=true OLD_RENDERER_REMOVED_ONLY_IN_TEST=true CLIENT_RENDER=5 GRAPHICS=FAST PARTICLES=DECREASED SHADERS=NOT_COPIED SOURCE_LITE_UNCHANGED=true SOURCE_ORIGINAL_UNCHANGED=true SERVER_UNCHANGED=true LOGIN=NOT_TESTED FPS=NOT_MEASURED'
  exit 0
} catch {
  Write-Output ('::error title=Prism Embeddium A/B::CREATION_BLOCKED_OR_FAILED PHASE=' + $phase +
    ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber +
    '; SOURCE_UNCHANGED=true NO_FORCED_PROCESS=true')
  exit 2
} finally {
  if ($stageOwned -and $stage -and (Test-Path -LiteralPath $stage)) {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
  }
}
