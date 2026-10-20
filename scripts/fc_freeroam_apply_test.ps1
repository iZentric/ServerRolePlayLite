# Fixture-only exercise of the in-place client update + local rollback proof.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'CI-only synthetic test' }
$root = Join-Path $env:RUNNER_TEMP ('fc-apply-synthetic-' + $env:GITHUB_RUN_ID)
$launcher = Join-Path $root 'PrismLauncher'
$profile = Join-Path $launcher 'instances/Freeroam 1.0.0'
$mods = Join-Path $profile '.minecraft/mods'
if (Test-Path -LiteralPath $root) { throw 'Fixture already exists' }
try {
  New-Item -ItemType Directory -Path $mods -Force | Out-Null
  $declared = Get-Content -LiteralPath agent/FREEROAM-LISTA-DECLARATA.json -Raw | ConvertFrom-Json
  foreach ($n in $declared.jar_names) { [IO.File]::WriteAllText((Join-Path $mods $n), ('fixture:' + $n)) }
  & ./scripts/fc_freeroam_apply.ps1 -Profile $profile
  if ($LASTEXITCODE -ne 0) { throw 'Apply fixture failed' }
  $backup = Join-Path $launcher ('Arena-Mods-Backups/fc-lite-' + $env:GITHUB_RUN_ID)
  $selection = Get-Content -LiteralPath agent/FUNCITY-RP-LITE-SELECTIE.json -Raw | ConvertFrom-Json
  if (@(Get-ChildItem -LiteralPath $mods -Filter '*.jar').Count -ne 22) { throw 'Wrong target count' }
  foreach ($n in $selection.removed_from_future_target) {
    if (Test-Path -LiteralPath (Join-Path $mods $n)) { throw 'Unremoved fixture JAR' }
    if (-not (Test-Path -LiteralPath (Join-Path $backup $n))) { throw 'Backup absent' }
    Copy-Item -LiteralPath (Join-Path $backup $n) -Destination (Join-Path $mods $n)
  }
  if (@(Get-ChildItem -LiteralPath $mods -Filter '*.jar').Count -ne 28) { throw 'Rollback fixture count' }
  foreach ($n in $declared.jar_names) {
    if ([IO.File]::ReadAllText((Join-Path $mods $n)) -cne ('fixture:' + $n)) { throw 'Rollback fixture bytes' }
  }
  Write-Output 'PASS: isolated fixture 28 to 22, six local backups, restore 28; no real Prism touched'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
