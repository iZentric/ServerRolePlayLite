# Hosted fixture only: source 34 stays untouched; stage 33 plus Clumps rollback copy.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'CI fixture only' }
$root = Join-Path $env:RUNNER_TEMP ('fc-server-stage-fixture-' + $env:GITHUB_RUN_ID)
$server = Join-Path $root 'FunCityLocal/server'
$mods = Join-Path $server 'mods'
$stage = Join-Path $root ('FunCityLocal/Arena-CompatStages/server-no-clumps-' + $env:GITHUB_RUN_ID)
if (Test-Path -LiteralPath $root) { throw 'Fixture exists' }
try {
  New-Item -ItemType Directory -Path $mods -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'world') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'plugins') -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $server 'world/level.dat'),'PRIVATE_WORLD_FIXTURE')
  [IO.File]::WriteAllText((Join-Path $server 'plugins/private.conf'),'PRIVATE_PLUGIN_FIXTURE')
  for ($i=1; $i -le 33; $i++) {
    [IO.File]::WriteAllText((Join-Path $mods ('content-' + $i + '.jar')),('fixture:' + $i))
  }
  [IO.File]::WriteAllText((Join-Path $mods 'Clumps-6.0.0.28.jar'),'fixture:clumps')
  $clumpsSha = (Get-FileHash -LiteralPath (Join-Path $mods 'Clumps-6.0.0.28.jar') -Algorithm SHA256).Hash
  & ./scripts/fc_server_no_clumps_stage.ps1 -Server $server
  if ($LASTEXITCODE -ne 0) { throw 'Stage fixture failed' }
  if (@(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar').Count -ne 34 -or
      @(Get-ChildItem -LiteralPath (Join-Path $stage 'mods') -File -Filter '*.jar').Count -ne 33 -or
      @(Get-ChildItem -LiteralPath (Join-Path $stage 'excluded-backup') -File -Filter '*.jar').Count -ne 1 -or
      (Get-FileHash -LiteralPath (Join-Path $stage 'excluded-backup/Clumps-6.0.0.28.jar') -Algorithm SHA256).Hash -ne $clumpsSha -or
      (Test-Path -LiteralPath (Join-Path $stage 'world')) -or
      (Test-Path -LiteralPath (Join-Path $stage 'plugins')) -or
      (Test-Path -LiteralPath (Join-Path $stage 'mods/Clumps-6.0.0.28.jar'))) { throw 'Incorrect stage inventory or private data copied' }
  $manifest = Get-Content -LiteralPath (Join-Path $stage 'private-manifest.json') -Raw | ConvertFrom-Json
  if ($manifest.source_jar_count -ne 34 -or $manifest.stage_jar_count -ne 33 -or $manifest.world_copied -ne $false) { throw 'Bad private manifest' }
  Write-Output 'PASS: synthetic server stage 34->33, Clumps rollback copied, source and world untouched'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
