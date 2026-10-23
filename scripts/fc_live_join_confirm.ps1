# Read-only private post-change confirmation; no raw player names, logs or passwords.
param([Parameter(Mandatory=$true)][string]$Server,
      [Parameter(Mandatory=$true)][string]$Copy)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      (Split-Path -Leaf $Copy) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Copy)) -cne 'bootable-no-clumps-39598696934') {
    throw 'Unexpected server/copy'
  }
  $project=Split-Path -Parent $Server
  $runId='39618302299'
  $backup=Join-Path $project ('Arena-Private-Backups/offline-' + $runId)
  $rollback=Join-Path $project ('Arena-Private-Rollback/forge-trial-' + $runId)
  $manifest=Get-Content -LiteralPath (Join-Path $backup 'private-manifest.json') -Raw -ErrorAction Stop | ConvertFrom-Json
  $backupOk=$manifest.schema -eq 1 -and $manifest.source -ceq 'offline' -and
    $manifest.consistent_offline_snapshot -eq $true -and $manifest.independent_restore_copy_verified -eq $true
  $clumpsStored=Test-Path -LiteralPath (Join-Path $rollback 'Clumps-6.0.0.28.jar') -PathType Leaf
  $clumpsLive=Test-Path -LiteralPath (Join-Path $Server 'mods/Clumps-6.0.0.28.jar') -PathType Leaf
  $stageVoice=Get-Content -LiteralPath (Join-Path (Split-Path -Parent $Copy) 'private-voicechat-trial.json') -Raw -ErrorAction Stop | ConvertFrom-Json
  $liveJars=@(Get-ChildItem -LiteralPath (Join-Path $Server 'mods') -File -Filter '*.jar' -ErrorAction Stop)
  $copyJars=@(Get-ChildItem -LiteralPath (Join-Path $Copy 'mods') -File -Filter '*.jar' -ErrorAction Stop)
  $voice=@($copyJars | Where-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash -ceq $stageVoice.client_voicechat_sha256 })
  $voiceMatches=$voice.Count -eq 1 -and
    (Test-Path -LiteralPath (Join-Path (Join-Path $Server 'mods') $voice[0].Name) -PathType Leaf) -and
    (Get-FileHash -LiteralPath (Join-Path (Join-Path $Server 'mods') $voice[0].Name) -Algorithm SHA256).Hash -ceq $stageVoice.client_voicechat_sha256
  $procs=@(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
    $_.CommandLine -and $_.CommandLine.IndexOf($Server,[StringComparison]::OrdinalIgnoreCase) -ge 0
  })
  $portOwned=$false
  if ($procs.Count -eq 1) {
    $portOwned=@(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue |
      Where-Object { $_.OwningProcess -eq $procs[0].ProcessId }).Count -eq 1
  }
  Write-Output ('::notice title=Forge live trial read-only::BACKUP_RESTORE_VERIFIED=' + $backupOk +
    ' CLUMPS_PRIVATE_ROLLBACK=' + $clumpsStored + ' CLUMPS_LIVE_ABSENT=' + (-not $clumpsLive) +
    ' VOICECHAT_EXACT_SHA=' + $voiceMatches + ' LIVE_MOD_JARS=' + $liveJars.Count +
    ' ORIGINAL_PROCESS_UNIQUE=' + ($procs.Count -eq 1) + ' GAME_PORT_OWNED=' + $portOwned +
    '; CLIENT_JOIN_REPORTED_BY_OWNER=true; READ_ONLY=true')
  $rcon=@(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command list)
  if ($LASTEXITCODE -ne 0) { throw 'RCON unavailable' }
  $state=@($rcon | Where-Object { $_ -match 'AUTH_OK=true PLAYER_STATE=(ACTIVE|ZERO|UNKNOWN)' })
  if ($state.Count -ne 1) { throw 'RCON state ambiguous' }
  $playerState=[regex]::Match($state[0],'PLAYER_STATE=(ACTIVE|ZERO|UNKNOWN)').Groups[1].Value
  Write-Output ('::notice title=Forge live player count::PLAYER_STATE=' + $playerState + '; NAMES_NOT_OUTPUT=true READ_ONLY=true')
  & (Join-Path $PSScriptRoot 'fc_local_status_ping.ps1') -Port 25565
  if ($LASTEXITCODE -ne 0) { throw 'Status ping unavailable' }
  if (-not $backupOk -or -not $clumpsStored -or $clumpsLive -or -not $voiceMatches -or
      $liveJars.Count -ne 34 -or -not $portOwned) { throw 'Post-change gate failed' }
  exit 0
} catch {
  Write-Output ('::error title=Forge live trial read-only::CONFIRMATION_UNAVAILABLE TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; LIVE_UNCHANGED=true')
  exit 2
}
