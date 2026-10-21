# Synthetic no-PC fixture: checks strict two-profile scope, time span and private-data redaction.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-client-log-audit-' + [guid]::NewGuid().ToString('N'))
$instances=Join-Path $root 'PrismLauncher/instances'
try {
  foreach ($profile in @('FunCity RP Lite','FunCity RP Lite Embeddium TEST')) {
    $logDir=Join-Path (Join-Path $instances $profile) '.minecraft/logs'
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    $rows=@(
      '[22Oct2026 10:00:00.100] [main/INFO]: ModLauncher running PRIVATE_NAME PRIVATE_IP',
      '[22Oct2026 10:00:35.010] [Render thread/INFO]: Sound engine started',
      '[22Oct2026 10:00:45.100] [Render thread/WARN]: PRIVATE_PASSWORD warning',
      '[22Oct2026 10:01:00.020] [Render thread/INFO]: Connecting to PRIVATE_IP'
    )
    if ($profile -match 'TEST$') { $rows+= '[22Oct2026 10:01:10.000] [Render thread/ERROR]: Embeddium PRIVATE_NAME' }
    [IO.File]::WriteAllLines((Join-Path $logDir 'latest.log'),$rows)
  }
  $result=@(& ./scripts/fc_client_log_comparison.ps1 -Instances $instances)
  if ($LASTEXITCODE -ne 0 -or $result.Count -ne 2 -or
      -not (@($result | Where-Object { $_ -match 'RUBIDIUM' -and $_ -match 'LOG_SPAN_SECONDS=60' }).Count -eq 1) -or
      -not (@($result | Where-Object { $_ -match 'EMBEDDIUM_TEST' -and $_ -match 'LOG_SPAN_SECONDS=70' -and $_ -match 'RENDERER_ERROR_LINES=1' }).Count -eq 1) -or
      $result -match 'PRIVATE|fc-client-log-audit') { throw 'Sanitized log comparison fixture failed' }
  Write-Output 'PASS: bounded log span is not load time; warnings/errors counted; no private data emitted'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
