# Hosted fixture: read-only full pre-maintenance copy with local SHA verification.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'Hosted fixture only' }
$root = Join-Path $env:RUNNER_TEMP ('fc-server-prebackup-' + $env:GITHUB_RUN_ID)
$server = Join-Path $root 'FunCityLocal/server'
$dest = Join-Path $root ('FunCityLocal/Arena-Private-Backups/pre-maintenance-' + $env:GITHUB_RUN_ID)
if (Test-Path -LiteralPath $root) { throw 'Fixture already exists' }
try {
  foreach ($dir in @('mods','world','plugins','logs')) { New-Item -ItemType Directory -Path (Join-Path $server $dir) -Force | Out-Null }
  for ($i=1; $i -le 105; $i++) { [IO.File]::WriteAllText((Join-Path $server ('mods/fixture-' + $i + '.jar')),'fixture') }
  $world = Join-Path $server 'world/level.dat'
  [IO.File]::WriteAllBytes($world,(New-Object byte[] (11*1024*1024)))
  [IO.File]::WriteAllText((Join-Path $server 'server.properties'),'rcon.password=DO_NOT_PRINT_ME')
  [IO.File]::WriteAllText((Join-Path $server 'plugins/private.db'),'PRIVATE_PLUGIN_DATA')
  [IO.File]::WriteAllText((Join-Path $server 'logs/latest.log'),'PRIVATE_PLAYER_ID')
  $hash = (Get-FileHash -LiteralPath $world -Algorithm SHA256).Hash
  $result = @(& ./scripts/fc_server_prebackup.ps1 -Server $server)
  if ($LASTEXITCODE -ne 0 -or ($result -join '') -notmatch 'CONSISTENT_OFFLINE_BACKUP=false') { throw 'Prebackup fixture failed' }
  $copied = Join-Path $dest 'world/level.dat'
  if (-not (Test-Path -LiteralPath $copied) -or
      (Get-FileHash -LiteralPath $copied -Algorithm SHA256).Hash -ne $hash -or
      (Get-FileHash -LiteralPath $world -Algorithm SHA256).Hash -ne $hash -or
      (Test-Path -LiteralPath (Join-Path $dest 'logs/latest.log'))) { throw 'World copy/hash or volatile exclusions wrong' }
  $manifest = Get-Content -LiteralPath (Join-Path $dest 'private-manifest.json') -Raw | ConvertFrom-Json
  if ($manifest.consistent_offline_snapshot -ne $false -or $manifest.restore_tested -ne $false -or
      ($result -join '') -match 'PRIVATE_|DO_NOT_PRINT_ME|level.dat|FunCityLocal') { throw 'Privacy or status wrong' }
  Write-Output 'PASS: synthetic online prebackup copied/hash-checked private world; no server state changed'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
