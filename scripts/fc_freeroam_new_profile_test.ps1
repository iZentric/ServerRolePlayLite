# Hosted fixture: builds an independent 22-JAR Prism instance, never a real profile.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'CI-only fixture' }
$root = Join-Path $env:RUNNER_TEMP ('fc-new-profile-synthetic-' + $env:GITHUB_RUN_ID)
$source = Join-Path $root 'PrismLauncher/instances/Freeroam 1.0.0'
$target = Join-Path $root 'PrismLauncher/instances/FunCity RP Lite'
$mods = Join-Path $source '.minecraft/mods'
if (Test-Path -LiteralPath $root) { throw 'Fixture already exists' }
try {
  New-Item -ItemType Directory -Path $mods -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $source '.minecraft/saves/private-world') -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $source '.minecraft/saves/private-world/level.dat'), 'fixture-world')
  [IO.File]::WriteAllText((Join-Path $source '.minecraft/accounts.json'), 'fixture-private-account')
  [IO.File]::WriteAllText((Join-Path $source 'instance.cfg'), "[General]`nname=Freeroam 1.0.0`n")
  [IO.File]::WriteAllText((Join-Path $source 'mmc-pack.json'), '{"formatVersion":1,"components":[]}')
  $declared = Get-Content -LiteralPath agent/FREEROAM-LISTA-DECLARATA.json -Raw | ConvertFrom-Json
  $selection = Get-Content -LiteralPath agent/FUNCITY-RP-LITE-SELECTIE.json -Raw | ConvertFrom-Json
  foreach ($name in $declared.jar_names) { [IO.File]::WriteAllText((Join-Path $mods $name), ('fixture:' + $name)) }
  & ./scripts/fc_freeroam_new_profile.ps1 -Source $source -SyntheticDiagnostics
  if ($LASTEXITCODE -ne 0) { throw 'Profile creation failed on fixture' }
  if (@(Get-ChildItem -LiteralPath (Join-Path $target '.minecraft/mods') -File -Filter '*.jar').Count -ne 22 -or
      @(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar').Count -ne 28) { throw 'Wrong original or new inventory' }
  foreach ($name in $selection.retained_in_future_target) {
    if ([IO.File]::ReadAllText((Join-Path $target '.minecraft/mods' $name)) -cne ('fixture:' + $name)) { throw 'Retained byte changed' }
  }
  foreach ($name in $selection.removed_from_future_target) {
    if (Test-Path -LiteralPath (Join-Path $target '.minecraft/mods' $name)) { throw 'Excluded file copied' }
    if (-not (Test-Path -LiteralPath (Join-Path $mods $name))) { throw 'Original file removed' }
  }
  if ((Get-Content -LiteralPath (Join-Path $target 'instance.cfg') -Raw) -notmatch 'name=FunCity RP Lite' -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/saves')) -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/accounts.json')) -or
      (Test-Path -LiteralPath (Join-Path $target '.minecraft/config'))) { throw 'Private data copied or metadata wrong' }
  Write-Output 'PASS: fixture separate Prism 22/28; original intact; no saves/accounts copied'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
