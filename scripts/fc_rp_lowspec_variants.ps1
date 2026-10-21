# Build ONE additional, isolated Prism profile from existing local Lite/Embeddium TEST.
# No downloads, server access, world/account copies, or changes to source profiles.
param(
  [Parameter(Mandatory=$true)][ValidateSet('low_rubidium','no_oculus_test','embeddium_test')][string]$Variant,
  [Parameter(Mandatory=$true)][string]$Lite,
  [string]$EmbeddiumTest,
  [switch]$Synthetic
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$stage=$null
$stageOwned=$false
$phase='PREFLIGHT'
function Safe-Dir([string]$Path) {
  $dir=[IO.DirectoryInfo]::new($Path)
  if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe or missing directory' }
}
function Safe-File([string]$Path) {
  $file=Get-Item -LiteralPath $Path -ErrorAction Stop
  if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe file' }
  return $file
}
function Assert-Closed {
  if ($Synthetic) { return }
  if (@(Get-Process -Name 'prismlauncher','minecraft' -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'Prism or Minecraft active: close normally before making a new profile'
  }
  # Leave the one known existing server alone. Fail closed on other Java processes.
  $server='C:\Users\Administrator\Desktop\FunCityLocal\server'
  $jvms=@(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop)
  if ($jvms.Count -gt 0) {
    $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)
    foreach ($jvm in $jvms) {
      if (-not $jvm.CommandLine -or
          $jvm.CommandLine.IndexOf($server,[StringComparison]::OrdinalIgnoreCase) -lt 0 -or
          @($listeners | Where-Object { $_.OwningProcess -eq $jvm.ProcessId }).Count -eq 0) {
        throw 'Unclassified Java process active'
      }
    }
  }
}
function Read-Profile([string]$Profile,[string[]]$Names) {
  Safe-Dir $Profile
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Missing or ambiguous game folder' }
  $game=Join-Path $Profile $games[0]
  $mods=Join-Path $game 'mods'
  Safe-Dir $game
  Safe-Dir $mods
  $cfg=Safe-File (Join-Path $Profile 'instance.cfg')
  $pack=Safe-File (Join-Path $Profile 'mmc-pack.json')
  $null=(Get-Content -LiteralPath $pack.FullName -Raw -ErrorAction Stop | ConvertFrom-Json)
  if (Test-Path -LiteralPath (Join-Path $Profile 'patches')) { throw 'Custom loader patches require manual review' }
  $actual=@(Get-ChildItem -LiteralPath $mods -Force -ErrorAction Stop)
  if ($actual.Count -ne $Names.Count -or $Names.Count -ne @($Names | Select-Object -Unique).Count) {
    throw 'Mod inventory count changed'
  }
  foreach ($file in $actual) {
    if ($file.PSIsContainer -or $file.Extension -cne '.jar' -or
        ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $Names -cnotcontains $file.Name) { throw 'Unexpected or unsafe mod file' }
  }
  $hashes=@{}
  $bytes=0L
  foreach ($name in $Names) {
    $jar=Safe-File (Join-Path $mods $name)
    $hashes[$name]=(Get-FileHash -LiteralPath $jar.FullName -Algorithm SHA256).Hash
    $bytes+=$jar.Length
  }
  return @{ profile=$Profile; gameName=$games[0]; mods=$mods; cfg=$cfg.FullName; pack=$pack.FullName; hashes=$hashes; bytes=$bytes }
}
function Assert-ForgeId([string]$Path,[string]$Id) {
  Add-Type -AssemblyName System.IO.Compression
  try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
  $archive=[IO.Compression.ZipFile]::OpenRead($Path)
  try {
    $entry=$archive.GetEntry('META-INF/mods.toml')
    if (-not $entry -or $entry.Length -gt 50000) { throw 'Candidate missing Forge metadata' }
    $reader=[IO.StreamReader]::new($entry.Open())
    try { $toml=$reader.ReadToEnd() } finally { $reader.Dispose() }
    if ($toml -notmatch ('(?im)^\s*modId\s*=\s*"' + [regex]::Escape($Id) + '"\s*$')) {
      throw 'Unexpected candidate Forge mod id'
    }
  } finally { $archive.Dispose() }
}
try {
  if ($Synthetic -and [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
    throw 'Synthetic bypass not permitted on Windows'
  }
  $instances=Split-Path -Parent $Lite
  $launcher=Split-Path -Parent $instances
  if ((Split-Path -Leaf $Lite) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf $instances) -cne 'instances' -or
      (Split-Path -Leaf $launcher) -cne 'PrismLauncher') { throw 'Wrong Lite profile path' }
  foreach ($dir in @($launcher,$instances)) { Safe-Dir $dir }
  if ($Variant -eq 'embeddium_test') {
    if (-not $EmbeddiumTest -or
        (Split-Path -Leaf $EmbeddiumTest) -cne 'FunCity RP Lite Embeddium TEST' -or
        (Split-Path -Parent $EmbeddiumTest) -cne $instances) { throw 'Wrong existing TEST profile path' }
  }
  Assert-Closed
  $root=Split-Path -Parent $PSScriptRoot
  $base=Get-Content -LiteralPath (Join-Path $root 'agent/FUNCITY-RP-LITE-SELECTIE.json') -Raw | ConvertFrom-Json
  $plan=Get-Content -LiteralPath (Join-Path $root 'agent/FUNCITY-RP-VARIANTE-LOWSPEC.json') -Raw | ConvertFrom-Json
  $names=@($base.retained_in_future_target)
  $optionsName='oculus-mc1.16.5-1.4.7.jar'
  $rubidium='rubidium-mc1.16.5-0.2.13.jar'
  $rubidiumOptions='TextruesRubidiumOptions-1.0.8-mc1.16.5.jar'
  $embeddium='embeddium-0.3.18+mc1.16.5.jar'
  $embeddiumOptions='textrue_embeddium_options-0.1.1+mc1.16.5.jar'
  if ($plan.schema -ne 1 -or $plan.minecraft -cne '1.16.5' -or $plan.loader -cne 'Forge' -or
      $names.Count -ne 22 -or @($names | Select-Object -Unique).Count -ne 22 -or
      @($names | Where-Object { $_ -ceq $optionsName -or $_ -ceq $rubidium -or $_ -ceq $rubidiumOptions }).Count -ne 3) {
    throw 'Baseline manifest drifted'
  }
  $expected=@($plan.variants | Where-Object { $_.id -ceq $Variant })
  if ($expected.Count -ne 1 -or $plan.variants.Count -ne 3) { throw 'Variant manifest drifted' }
  $profileNames=@{
    low_rubidium='FunCity RP LowSpec Rubidium'
    no_oculus_test='FunCity RP LowSpec fara Oculus TEST'
    embeddium_test='FunCity RP LowSpec Embeddium fara Oculus TEST'
  }
  $sourceName=if ($Variant -eq 'embeddium_test') { 'FunCity RP Lite Embeddium TEST' } else { 'FunCity RP Lite' }
  $targetName=$profileNames[$Variant]
  $embSource=@($names | Where-Object { $_ -cne $rubidium -and $_ -cne $rubidiumOptions }) + @($embeddium,$embeddiumOptions)
  $desired=if ($Variant -eq 'embeddium_test') { @($embSource) } else { @($names) }
  if ($Variant -ne 'low_rubidium') { $desired=@($desired | Where-Object { $_ -cne $optionsName }) }
  # The manifest may describe the variants, but it cannot authorize any new changes.
  $removed=@($expected[0].removed_only_in_variant)
  if ($expected[0].prism_name -cne $targetName -or $expected[0].source_prism_name -cne $sourceName -or
      $expected[0].jar_count -ne $desired.Count -or
      ($Variant -ne 'low_rubidium' -and ($removed.Count -ne 1 -or $removed[0] -cne $optionsName)) -or
      ($Variant -eq 'low_rubidium' -and $removed.Count -ne 0)) { throw 'Unsafe variant description' }
  $swaps=$expected[0].replaced_only_in_variant
  if ($Variant -eq 'embeddium_test') {
    if (@($swaps.PSObject.Properties).Count -ne 2 -or
        $swaps.$rubidium -cne $embeddium -or $swaps.$rubidiumOptions -cne $embeddiumOptions) {
      throw 'Unsafe renderer pair description'
    }
  } elseif (@($swaps.PSObject.Properties).Count -ne 0) { throw 'Unexpected renderer swap' }
  $graphics=$plan.graphics_preset
  if ($graphics.renderDistance -ne 5 -or $graphics.graphicsMode -ne 0 -or
      $graphics.particles -ne 1 -or $graphics.mipmapLevels -ne 0 -or
      $graphics.entityShadows -ne $false -or $graphics.shaderpacks_copied -ne $false) {
    throw 'Graphics preset drifted'
  }
  $phase='SOURCE_AND_TARGET_INVENTORY'
  $liteProfile=Read-Profile $Lite $names
  if ($Variant -eq 'embeddium_test') {
    $source=Read-Profile $EmbeddiumTest $embSource
    foreach ($name in $names) {
      if ($name -cne $rubidium -and $name -cne $rubidiumOptions -and
          $liteProfile.hashes[$name] -cne $source.hashes[$name]) { throw 'Shared RP JAR differs in TEST' }
    }
    $pins=@{
      'embeddium-0.3.18+mc1.16.5.jar'='5B5E25B96BD8ACEDE00882F2DC32DCCF9E21841778DA8BF88D3E3955440A3A52'
      'textrue_embeddium_options-0.1.1+mc1.16.5.jar'='77F58855FF2E48DA559D0B9E14D65662E5F564066A3B1D418DCD96C4ADDED461'
    }
    if (-not $Synthetic) {
      foreach ($name in @($embeddium,$embeddiumOptions)) {
        if ($source.hashes[$name] -cne $pins[$name]) { throw 'TEST candidate binary differs from E drive audit' }
      }
      Assert-ForgeId (Join-Path $source.mods $embeddium) 'embeddium'
      Assert-ForgeId (Join-Path $source.mods $embeddiumOptions) 'textrues_embeddium_options'
    }
  } else { $source=$liteProfile }
  if ($source.gameName -cne $liteProfile.gameName) { throw 'Prism game paths differ' }
  $target=Join-Path $instances $targetName
  $stage=Join-Path $instances ($targetName + '.staging.' + [guid]::NewGuid().ToString('N'))
  if ((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $stage)) { throw 'Destination already exists' }
  if (-not $Synthetic) {
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($instances))
    if (-not $drive.IsReady -or $drive.AvailableFreeSpace -lt ($source.bytes + 16777216L)) {
      throw 'Insufficient space for separate profile'
    }
  }
  $cfgText=[IO.File]::ReadAllText($source.cfg,[Text.Encoding]::UTF8)
  if ([regex]::Matches($cfgText,'(?im)^name=.*$').Count -ne 1) { throw 'Prism instance name missing or duplicated' }
  $cfgText=[regex]::Replace($cfgText,'(?im)^name=.*$',('name=' + $targetName))
  $phase='STAGE_NEW_PROFILE_ONLY'
  $stageGame=Join-Path $stage $source.gameName
  $stageMods=Join-Path $stageGame 'mods'
  New-Item -ItemType Directory -Path $stageMods -ErrorAction Stop -Force | Out-Null
  $stageOwned=$true
  [IO.File]::WriteAllText((Join-Path $stage 'instance.cfg'),$cfgText,[Text.UTF8Encoding]::new($false))
  Copy-Item -LiteralPath $source.pack -Destination (Join-Path $stage 'mmc-pack.json') -ErrorAction Stop
  if ((Get-FileHash -LiteralPath (Join-Path $stage 'mmc-pack.json') -Algorithm SHA256).Hash -cne
      (Get-FileHash -LiteralPath $source.pack -Algorithm SHA256).Hash) { throw 'Loader metadata copy mismatch' }
  foreach ($name in $desired) {
    $from=Join-Path $source.mods $name
    $to=Join-Path $stageMods $name
    Copy-Item -LiteralPath $from -Destination $to -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $to -Algorithm SHA256).Hash -cne $source.hashes[$name] -or
        (Get-FileHash -LiteralPath $from -Algorithm SHA256).Hash -cne $source.hashes[$name]) {
      throw 'Mod JAR changed during copy'
    }
  }
  if (@(Get-ChildItem -LiteralPath $stageMods -Force).Count -ne $desired.Count) {
    throw 'Unexpected staged JAR count'
  }
  # This is a NEW, non-personal options file. No FPS cap, no shaderpacks, and
  # no worlds, accounts, config, custom resourcepacks or private server data.
  $preset="version:2586`nrenderDistance:5`ngraphicsMode:0`nparticles:1`nmipmapLevels:0`nentityShadows:false`n"
  [IO.File]::WriteAllText((Join-Path $stageGame 'options.txt'),$preset,[Text.UTF8Encoding]::new($false))
  $phase='PUBLISH_ISOLATED_PROFILE'
  Assert-Closed
  if (Test-Path -LiteralPath $target) { throw 'Destination appeared while copying' }
  [IO.Directory]::Move($stage,$target)
  $stageOwned=$false
  Write-Output ('PROFILE_CREATED_FOR_TEST=true VARIANT=' + $Variant + ' JARS=' + $desired.Count +
    ' RENDER=5 GRAPHICS=FAST FPS_CAP=UNMODIFIED RP_JARS_PRESERVED=true SOURCES_UNCHANGED=true' +
    ' SERVER_UNCHANGED=true LOGIN=NOT_TESTED FPS=NOT_MEASURED')
  exit 0
} catch {
  Write-Output ('PROFILE_NOT_CREATED_OR_INCOMPLETE=true PHASE=' + $phase +
    ' ERROR_TYPE=' + $_.Exception.GetType().Name + ' NO_FORCED_PROCESS=true')
  exit 2
} finally {
  if ($stageOwned -and $stage -and (Test-Path -LiteralPath $stage)) {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
  }
}
