$ErrorActionPreference = 'Stop'
$root = Join-Path ([IO.Path]::GetTempPath()) ('fc-offline-test-' + [guid]::NewGuid().ToString('N'))
$server = Join-Path (Join-Path $root 'FunCityLocal') 'server'
try {
  New-Item -ItemType Directory -Path (Join-Path $server 'world') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'empty') -Force | Out-Null
  New-Item -ItemType Directory -Path (Join-Path $server 'mods') -Force | Out-Null
  [IO.File]::WriteAllBytes((Join-Path $server 'world/level.dat'),[byte[]](1,2,3,4))
  [IO.File]::WriteAllBytes((Join-Path $server 'mods/example.jar'),[byte[]](5,6))
  $env:GITHUB_RUN_ID = '9012'
  $result = & (Join-Path $PSScriptRoot 'fc_server_offline_backup.ps1') -Server $server -Synthetic
  if ($LASTEXITCODE -ne 0 -or -not ($result -match 'BACKUP_VERIFIED=true RESTORE_COPY_VERIFIED=true')) { throw 'Offline backup test failed' }
  $backup = Join-Path (Join-Path (Split-Path -Parent $server) 'Arena-Private-Backups') 'offline-9012'
  if (-not (Test-Path (Join-Path $backup 'server/empty')) -or
      -not (Test-Path (Join-Path $backup 'server/world/level.dat')) -or
      (Test-Path (Join-Path (Split-Path -Parent $backup) '.restore-test-9012'))) { throw 'Backup contents/rehearsal cleanup invalid' }
  $manifest = Get-Content (Join-Path $backup 'private-manifest.json') -Raw | ConvertFrom-Json
  if ($manifest.files -ne 2 -or $manifest.directories -ne 3 -or
      -not $manifest.consistent_offline_snapshot -or -not $manifest.independent_restore_copy_verified) { throw 'Invalid private manifest' }
  Write-Output 'PASS: whole-tree offline backup, SHA verification, independent restore-copy rehearsal and cleanup'
} finally {
  Remove-Item -LiteralPath $root -Force -Recurse -ErrorAction SilentlyContinue
}
