Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'Hosted fixture only' }
$root = Join-Path $env:RUNNER_TEMP ('fc-server-gate-' + $env:GITHUB_RUN_ID)
$server = Join-Path $root 'FunCityLocal/server'
if (Test-Path -LiteralPath $root) { throw 'Fixture already exists' }
try {
  New-Item -ItemType Directory -Path (Join-Path $server 'world') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'mods') -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $server 'world/level.dat'),'PRIVATE_WORLD_FIXTURE')
  [IO.File]::WriteAllText((Join-Path $server 'mods/content.jar'),'test')
  [IO.File]::WriteAllText((Join-Path $server 'server.properties'),"enable-rcon=true`nrcon.port=25575`nrcon.password=DO_NOT_PRINT_ME`n")
  $text = @(& ./scripts/fc_server_upgrade_gate.ps1 -Server $server -Synthetic)
  if ($LASTEXITCODE -ne 0 -or ($text -join '') -notmatch 'SOURCE_FILES=3' -or
      ($text -join '') -notmatch 'RCON_CONFIGURED=True' -or
      ($text -join '') -match 'PRIVATE|DO_NOT_PRINT_ME|level.dat|FunCityLocal') { throw 'Unsafe or incorrect fixture gate' }
  Write-Output 'PASS: metadata-only server sizing; RCON password/world data remain private'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
