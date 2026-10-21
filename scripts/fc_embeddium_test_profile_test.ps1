# Hosted-only synthetic integration test: never use the real PC or download binaries.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-embeddium-fixture-' + [guid]::NewGuid().ToString('N'))
$source=Join-Path $root 'PrismLauncher/instances/FunCity RP Lite'
$target=Join-Path $root 'PrismLauncher/instances/FunCity RP Lite Embeddium TEST'
$downloads=Join-Path $root 'Downloads'
$mods=Join-Path $source '.minecraft/mods'
$env:GITHUB_RUN_ID='21471234'
function Fixture-Jar([string]$File,[string]$Id) {
  $archive=[IO.Compression.ZipFile]::Open($File,[IO.Compression.ZipArchiveMode]::Create)
  try {
    $entry=$archive.CreateEntry('META-INF/mods.toml')
    $writer=[IO.StreamWriter]::new($entry.Open())
    try { $writer.Write('modLoader="javafml"' + "`n" + '[[mods]]' + "`n" + 'modId="' + $Id + '"' + "`n") }
    finally { $writer.Dispose() }
  } finally { $archive.Dispose() }
}
try {
  New-Item -ItemType Directory -Path $mods,$downloads -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $source '.minecraft/saves/SECRET-WORLD') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $source '.minecraft/config') -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $source 'instance.cfg'),"[General]`nname=FunCity RP Lite`n")
  [IO.File]::WriteAllText((Join-Path $source 'mmc-pack.json'),'{}')
  [IO.File]::WriteAllText((Join-Path $source '.minecraft/accounts.json'),'PRIVATE_ACCOUNT')
  [IO.File]::WriteAllText((Join-Path $source '.minecraft/config/secret.toml'),'PRIVATE_SETTING')
  [IO.File]::WriteAllText((Join-Path $source '.minecraft/saves/SECRET-WORLD/level.dat'),'PRIVATE_WORLD')
  $manifest=Get-Content -LiteralPath agent/FUNCITY-RP-LITE-SELECTIE.json -Raw | ConvertFrom-Json
  foreach ($name in $manifest.retained_in_future_target) {
    [IO.File]::WriteAllText((Join-Path $mods $name),('fixture:' + $name))
  }
  Write-Output '::notice title=Embeddium fixture::PHASE=BEFORE_MISSING_BINARIES'
  & ./scripts/fc_embeddium_test_profile.ps1 -Source $source -Downloads $downloads -Synthetic | Out-Null
  Write-Output ('::notice title=Embeddium fixture::PHASE=AFTER_MISSING_BINARIES EXIT=' + $LASTEXITCODE)
  if ($LASTEXITCODE -eq 0 -or (Test-Path -LiteralPath $target)) { throw 'Missing candidates should fail without creating profile' }
  Fixture-Jar (Join-Path $downloads 'embeddium-0.3.18+mc1.16.5.jar') 'embeddium'
  Fixture-Jar (Join-Path $downloads 'textrue_embeddium_options-0.1.1+mc1.16.5.jar') 'textrues_embeddium_options'
  Write-Output '::notice title=Embeddium fixture::PHASE=BEFORE_CREATE'
  $result=& ./scripts/fc_embeddium_test_profile.ps1 -Source $source -Downloads $downloads -Synthetic
  Write-Output ('::notice title=Embeddium fixture::PHASE=AFTER_CREATE EXIT=' + $LASTEXITCODE)
  if ($LASTEXITCODE -ne 0 -or -not ($result -match 'SEPARATE_TEST_PROFILE_CREATED=true')) { throw 'Separate candidate not built on fixture' }
  $copy=Join-Path $target '.minecraft/mods'
  if (@(Get-ChildItem -LiteralPath $copy -File -Filter '*.jar').Count -ne 22 -or
      @(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar').Count -ne 22) { throw 'Unexpected source/target JAR count' }
  foreach ($name in $manifest.retained_in_future_target) {
    if ($name -match '^rubidium-|^TextruesRubidiumOptions-') {
      if (Test-Path -LiteralPath (Join-Path $copy $name)) { throw 'Old renderer in new test profile' }
    } elseif ((Get-FileHash -LiteralPath (Join-Path $copy $name) -Algorithm SHA256).Hash -cne
              (Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash) { throw 'RP JAR changed' }
  }
  foreach ($name in @('embeddium-0.3.18+mc1.16.5.jar','textrue_embeddium_options-0.1.1+mc1.16.5.jar')) {
    if (-not (Test-Path -LiteralPath (Join-Path $copy $name))) { throw 'Missing new renderer/opitions JAR' }
  }
  $preset=Get-Content -LiteralPath (Join-Path $target '.minecraft/options.txt') -Raw
  if ($preset -notmatch 'renderDistance:5' -or $preset -notmatch 'graphicsMode:0' -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/saves')) -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/config')) -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/accounts.json')) -or
      $result -match 'PRIVATE|SECRET|fc-embeddium-fixture') { throw 'Settings or private data leaked' }
  & ./scripts/fc_embeddium_test_profile.ps1 -Source $source -Downloads $downloads -Synthetic | Out-Null
  if ($LASTEXITCODE -eq 0 -or -not (Test-Path -LiteralPath $target)) { throw 'Must not overwrite test profile' }
  Write-Output 'PASS: separate candidate with 20 byte-identical retained JARs, two replacements, 5-chunk preset, original/client accounts/world untouched'
} catch {
  Write-Output ('::error title=Hosted Embeddium fixture::TYPE=' + $_.Exception.GetType().Name +
    ' MESSAGE=' + $_.Exception.Message + ' LINE=' + $_.InvocationInfo.ScriptLineNumber)
  throw
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
