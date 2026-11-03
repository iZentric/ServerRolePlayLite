# Owner-authorized live compatibility trial: normal stop, fresh whole-tree
# offline backup/restore rehearsal, exact Clumps/voicechat mod delta, task restart.
# Never force processes. If preflight/backup/copy fails, undo the delta and restart original.
param([Parameter(Mandatory=$true)][string]$Server,
      [Parameter(Mandatory=$true)][string]$Copy)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$phase = 'PREFLIGHT'
$stopSent = $false
$backupVerified = $false
$restartVerified = $false
$failed = $false
$originalPid = 0
$taskExecutable = $null
$taskArguments = $null
$copyVoiceJar = $null
$liveVoiceJar = $null
$liveClumps = $null
$rollbackClumps = $null
$rollbackDir = $null
$clumpsMoved = $false
$voiceCopied = $false
$trialApplied = $false
function Server-Procs {
  return @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
    $_.CommandLine -and $_.CommandLine.IndexOf($Server,[StringComparison]::OrdinalIgnoreCase) -ge 0
  })
}
function Assert-RestartTask {
  $task = Get-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
  $actions = @($task.Actions)
  if ($task.State -eq 'Disabled' -or $actions.Count -ne 1 -or
      -not $actions[0].WorkingDirectory -or
      -not $actions[0].WorkingDirectory.TrimEnd([char[]]@([char]92,[char]47)).Equals($Server.TrimEnd([char[]]@([char]92,[char]47)),[StringComparison]::OrdinalIgnoreCase) -or
      -not $actions[0].Arguments -or $actions[0].Arguments -notmatch '(?i)-jar\s+FunCityEngine\.jar\s+nogui' -or
      -not $actions[0].Execute -or -not (Test-Path -LiteralPath $actions[0].Execute -PathType Leaf)) {
    throw 'Restart task mismatch'
  }
  if ($taskExecutable -and (-not $taskExecutable.Equals($actions[0].Execute,[StringComparison]::OrdinalIgnoreCase) -or
      $taskArguments -cne $actions[0].Arguments)) { throw 'Restart task changed' }
  return $actions[0]
}
function Check-Zero {
  $result = @(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command list)
  if ($LASTEXITCODE -ne 0 -or @($result | Where-Object { $_ -match 'AUTH_OK=true PLAYER_STATE=ZERO\b' }).Count -ne 1) {
    throw 'Player count not positively zero'
  }
}
function Restore-Old-Mods {
  if (@(Server-Procs).Count -ne 0 -or
      @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue).Count -ne 0) {
    throw 'Never revert JARs while server running'
  }
  if ($voiceCopied) {
    if (-not (Test-Path -LiteralPath $liveVoiceJar -PathType Leaf) -or
        (Get-FileHash -LiteralPath $liveVoiceJar -Algorithm SHA256).Hash -cne $trial.client_voicechat_sha256) {
      throw 'Voicechat rollback file changed'
    }
    Remove-Item -LiteralPath $liveVoiceJar -Force -ErrorAction Stop
    $script:voiceCopied = $false
  }
  if ($clumpsMoved) {
    if ((Test-Path -LiteralPath $liveClumps) -or -not (Test-Path -LiteralPath $rollbackClumps -PathType Leaf)) {
      throw 'Clumps rollback ambiguous'
    }
    Move-Item -LiteralPath $rollbackClumps -Destination $liveClumps -ErrorAction Stop
    $script:clumpsMoved = $false
  }
  $script:trialApplied = $false
}
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong server or run id' }
  $taskAction = Assert-RestartTask
  $taskExecutable = $taskAction.Execute
  $taskArguments = $taskAction.Arguments
  $project = Split-Path -Parent $Server
  $stage = Split-Path -Parent $Copy
  if ((Split-Path -Leaf $Copy) -cne 'server' -or
      (Split-Path -Leaf $stage) -cne 'bootable-no-clumps-39598696934' -or
      (Split-Path -Leaf (Split-Path -Parent $stage)) -cne 'Arena-CompatStages' -or
      -not (Split-Path -Parent (Split-Path -Parent $stage)).Equals($project,[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Wrong tested copy'
  }
  $base = Get-Content -LiteralPath (Join-Path $stage 'private-copy-manifest.json') -Raw -ErrorAction Stop | ConvertFrom-Json
  $trial = Get-Content -LiteralPath (Join-Path $stage 'private-voicechat-trial.json') -Raw -ErrorAction Stop | ConvertFrom-Json
  if ($base.copy_hash_verified -ne $true -or $base.source_verified_offline -ne $true -or
      $trial.voicechat_added_to_private_copy -ne $true -or $trial.clumps_removed_from_private_copy -ne $true -or
      $trial.client_voicechat_sha256 -notmatch '^[A-Fa-f0-9]{64}$') { throw 'Untested private copy' }
  $stageMods = @(Get-ChildItem -LiteralPath (Join-Path $Copy 'mods') -File -Filter '*.jar' -Force -ErrorAction Stop)
  $liveMods = @(Get-ChildItem -LiteralPath (Join-Path $Server 'mods') -File -Filter '*.jar' -Force -ErrorAction Stop)
  $extra = @($stageMods | Where-Object { $name=$_.Name; @($liveMods | Where-Object { $_.Name -ceq $name }).Count -eq 0 })
  $liveClumps = Join-Path (Join-Path $Server 'mods') 'Clumps-6.0.0.28.jar'
  if ($stageMods.Count -ne 34 -or $liveMods.Count -ne 34 -or $extra.Count -ne 1 -or
      -not (Test-Path -LiteralPath $liveClumps -PathType Leaf) -or
      (Test-Path -LiteralPath (Join-Path (Join-Path $Copy 'mods') 'Clumps-6.0.0.28.jar')) -or
      $extra[0].Name -notmatch '(?i)voice' -or
      (Get-FileHash -LiteralPath $extra[0].FullName -Algorithm SHA256).Hash -cne $trial.client_voicechat_sha256) {
    throw 'Candidate mod delta mismatch'
  }
  $copyVoiceJar = $extra[0].FullName
  $liveVoiceJar = Join-Path (Join-Path $Server 'mods') $extra[0].Name
  $procs = @(Server-Procs)
  if ($procs.Count -ne 1) { throw 'Not one original server' }
  $originalPid = $procs[0].ProcessId
  $listeners = @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction Stop)
  if ($listeners.Count -ne 1 -or $listeners[0].OwningProcess -ne $originalPid) { throw 'Game port does not belong to original' }
  $phase = 'ZERO_PLAYERS_AND_SAVE'
  Check-Zero
  Start-Sleep -Seconds 2
  Check-Zero
  $save = @(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command 'save-all flush')
  if ($LASTEXITCODE -ne 0 -or @($save | Where-Object { $_ -match 'AUTH_OK=true SAVE_ALL_RESPONSE_RECEIVED=true' }).Count -ne 1) {
    throw 'Save acknowledgement missing'
  }
  Check-Zero
  if (@(Server-Procs).Count -ne 1 -or @(Server-Procs)[0].ProcessId -ne $originalPid) { throw 'Server identity changed before stop' }
  $phase = 'NORMAL_STOP'
  # A command can reach Java even when its RCON reply fails: always enter safe restart handling.
  $stopSent = $true
  $stop = @(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command stop)
  if ($LASTEXITCODE -ne 0 -or @($stop | Where-Object { $_ -match 'AUTH_OK=true STOP_REQUEST_SENT=true' }).Count -ne 1) {
    throw 'Stop command unverified'
  }
  for ($i=0;$i -lt 60;$i++) {
    if (-not (Get-Process -Id $originalPid -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Seconds 2
  }
  if (Get-Process -Id $originalPid -ErrorAction SilentlyContinue) { throw 'Normal stop timeout; never force process' }
  if (@(Server-Procs).Count -ne 0 -or
      @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue).Count -ne 0) {
    throw 'Another server appeared; do not back up or launch another'
  }
  $phase = 'OFFLINE_BACKUP_RESTORE_CHECK'
  $backup = @(& (Join-Path $PSScriptRoot 'fc_server_offline_backup.ps1') -Server $Server)
  if ($LASTEXITCODE -ne 0 -or @($backup | Where-Object { $_ -match 'BACKUP_VERIFIED=true RESTORE_COPY_VERIFIED=true' }).Count -ne 1) {
    throw 'Offline backup or restore-copy check failed'
  }
  $backupVerified = $true
  $phase = 'APPLY_REVERSIBLE_MOD_DELTA'
  $rollbackDir = Join-Path (Join-Path $project 'Arena-Private-Rollback') ('forge-trial-' + $env:GITHUB_RUN_ID)
  if (Test-Path -LiteralPath $rollbackDir) { throw 'Existing rollback folder' }
  New-Item -ItemType Directory -Path $rollbackDir -Force -ErrorAction Stop | Out-Null
  $rollbackClumps = Join-Path $rollbackDir 'Clumps-6.0.0.28.jar'
  $oldHash = (Get-FileHash -LiteralPath $liveClumps -Algorithm SHA256 -ErrorAction Stop).Hash
  Move-Item -LiteralPath $liveClumps -Destination $rollbackClumps -ErrorAction Stop
  $clumpsMoved = $true
  if ((Get-FileHash -LiteralPath $rollbackClumps -Algorithm SHA256 -ErrorAction Stop).Hash -cne $oldHash) { throw 'Clumps rollback digest mismatch' }
  Copy-Item -LiteralPath $copyVoiceJar -Destination $liveVoiceJar -ErrorAction Stop
  $voiceCopied = $true
  if ((Get-FileHash -LiteralPath $liveVoiceJar -Algorithm SHA256 -ErrorAction Stop).Hash -cne $trial.client_voicechat_sha256 -or
      @(Get-ChildItem -LiteralPath (Join-Path $Server 'mods') -File -Filter '*.jar').Count -ne 34) {
    throw 'Voicechat copy digest/count mismatch'
  }
  $trialApplied = $true
  Write-Output '::notice title=Live Forge compatibility trial::FRESH_OFFLINE_BACKUP=true RESTORE_REHEARSAL=true CLUMPS_QUARANTINED=true VOICECHAT_FROM_LITE=true; SERVER_STILL_STOPPED=true JOIN_NOT_TESTED=true'
} catch {
  $failed = $true
  Write-Output ('::error title=FunCity maintenance::BLOCKED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; BACKUP_VERIFIED=' + $backupVerified)
} finally {
  if ($stopSent) {
    $phase = 'RESTART_ORIGINAL'
    try {
      if ($failed -and ($clumpsMoved -or $voiceCopied)) { Restore-Old-Mods }
      # No restart if the original (or any replacement) is still running/listening.
      for ($i=0;$i -lt 60;$i++) {
        if (-not (Get-Process -Id $originalPid -ErrorAction SilentlyContinue)) { break }
        Start-Sleep -Seconds 2
      }
      if (Get-Process -Id $originalPid -ErrorAction SilentlyContinue) { throw 'Original still running; no second instance' }
      if (@(Server-Procs).Count -ne 0 -or
          @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue).Count -ne 0) {
        throw 'Existing server; do not launch second instance'
      }
      $taskNow = Assert-RestartTask
      Start-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
      for ($i=0;$i -lt 90;$i++) {
        $new = @(Server-Procs)
        if ($new.Count -eq 1 -and $new[0].ProcessId -ne $originalPid) {
          $port = @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue |
            Where-Object { $_.OwningProcess -eq $new[0].ProcessId })
          if ($port.Count -eq 1) { $restartVerified = $true; break }
        }
        Start-Sleep -Seconds 2
      }
      if (-not $restartVerified) { throw 'Task launched but original server port not ready' }
    } catch {
      $failed = $true
      Write-Output ('::error title=FunCity restart::CANDIDATE_START_UNVERIFIED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true; NO_SECOND_INSTANCE=true')
      # If the candidate exited, revert only our two JAR changes and retry original task once.
      if ($trialApplied) {
        try {
          $running = @(Server-Procs)
          $ports = @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue)
          if ($running.Count -eq 1 -and $ports.Count -eq 1 -and $ports[0].OwningProcess -eq $running[0].ProcessId) {
            Check-Zero
            $stop = @(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command stop)
            if ($LASTEXITCODE -ne 0) { throw 'Candidate RCON stop failed' }
            for ($i=0;$i -lt 60;$i++) {
              if (@(Server-Procs).Count -eq 0) { break }
              Start-Sleep -Seconds 2
            }
          }
          Restore-Old-Mods
          $taskNow = Assert-RestartTask
          Start-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
          for ($i=0;$i -lt 90;$i++) {
            $new = @(Server-Procs)
            $port = @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue)
            if ($new.Count -eq 1 -and $port.Count -eq 1 -and $port[0].OwningProcess -eq $new[0].ProcessId) {
              $restartVerified = $true; break
            }
            Start-Sleep -Seconds 2
          }
          Write-Output ('::notice title=FunCity fallback::ORIGINAL_JARS_RESTORED=true ORIGINAL_PORT_RESTORED=' + $restartVerified)
        } catch {
          Write-Output ('::error title=FunCity fallback::MANUAL_RECOVERY_REQUIRED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true; NO_SECOND_INSTANCE=true')
        }
      }
    }
  }
  Write-Output ('::notice title=FunCity Forge trial result::STOP_SENT=' + $stopSent + ' FRESH_BACKUP_VERIFIED=' + $backupVerified + ' RESTORE_REHEARSED=' + $backupVerified + ' SERVER_PORT_READY=' + $restartVerified + ' CANDIDATE_JARS_ACTIVE=' + $trialApplied + ' LIVE_JARS_CHANGED=' + $trialApplied + ' JOIN_TESTED=false')
}
if ($failed -or -not $backupVerified -or -not $restartVerified -or -not $trialApplied) { exit 2 }
exit 0
