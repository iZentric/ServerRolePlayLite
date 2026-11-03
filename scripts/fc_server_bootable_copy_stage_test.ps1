$ErrorActionPreference='Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) ('fc-copy-test-' + [guid]::NewGuid().ToString('N'))
$server = Join-Path (Join-Path $root 'FunCityLocal') 'server'
try {
  New-Item -ItemType Directory -Path (Join-Path $server 'mods') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'world') -Force | Out-Null
  [IO.File]::WriteAllBytes((Join-Path $server 'world/level.dat'),[byte[]](1,2,3,4,5))
  1..33 | ForEach-Object { [IO.File]::WriteAllBytes((Join-Path $server ('mods/mod' + $_ + '.jar')),[byte[]]($_ % 255)) }
  [IO.File]::WriteAllBytes((Join-Path $server 'mods/Clumps-6.0.0.28.jar'),[byte[]](41,42))
  $env:GITHUB_RUN_ID='98761'
  $backup = & (Join-Path $PSScriptRoot 'fc_server_offline_backup.ps1') -Server $server -Synthetic
  if ($LASTEXITCODE -ne 0 -or -not ($backup -match 'BACKUP_VERIFIED=true')) { throw 'Fixture backup failed' }
  $env:GITHUB_RUN_ID='98762'
  $result = & (Join-Path $PSScriptRoot 'fc_server_bootable_copy_stage.ps1') -Server $server -BackupRunId '98761'
  if ($LASTEXITCODE -ne 0 -or -not ($result -match 'COPY_PREPARED=true')) { throw 'Fixture stage failed' }
  $stage = Join-Path (Join-Path (Split-Path -Parent $server) 'Arena-CompatStages') 'bootable-no-clumps-98762'
  if (@(Get-ChildItem (Join-Path $stage 'server/mods') -Filter '*.jar').Count -ne 33 -or
      -not (Test-Path (Join-Path $stage 'server/world/level.dat')) -or
      -not (Test-Path (Join-Path $stage 'excluded-backup/Clumps-6.0.0.28.jar')) -or
      (Test-Path (Join-Path $stage 'server/mods/Clumps-6.0.0.28.jar')) -or
      @(Get-ChildItem (Join-Path $server 'mods') -Filter '*.jar').Count -ne 34) { throw 'Fixture contents invalid' }
  Write-Output 'PASS: private complete server copy from verified offline backup; 34 source -> 33 copy, Clumps rollback preserved, original unchanged'
} finally {
  Remove-Item -LiteralPath $root -Force -Recurse -ErrorAction SilentlyContinue
}
