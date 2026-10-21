# Owner-selected lower server view: zero players -> normal save/stop -> NEW private
# whole-tree offline backup/restore rehearsal -> only view-distance 6->5 -> restart.
# No live JAR/world/plugin edits, uploads, forced stops or second server.
param([Parameter(Mandatory=$true)][string]$Server)
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
$viewChanged = $false
$cfg = $null
$rollbackFile = $null
$oldHash = $null
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
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong server or run id' }
  $taskAction = Assert-RestartTask
  $taskExecutable = $taskAction.Execute
  $taskArguments = $taskAction.Arguments
  $cfg = Join-Path $Server 'server.properties'
  $cfgItem=Get-Item -LiteralPath $cfg -ErrorAction Stop
  if ($cfgItem.PSIsContainer -or ($cfgItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $cfgItem.Length -gt 1000000) { throw 'Unsafe config' }
  # Java properties are byte-oriented ISO-8859-1; preserve all non-target bytes.
  $cfgEncoding=[Text.Encoding]::GetEncoding(28591)
  $oldText=[IO.File]::ReadAllText($cfg,$cfgEncoding)
  $pattern='(?m)^view-distance=6(\r?)$'
  if ([regex]::Matches($oldText,'(?m)^view-distance=[^\r\n]*\r?$').Count -ne 1 -or
      [regex]::Matches($oldText,$pattern).Count -ne 1) { throw 'Expected one current server view-distance=6' }
  $newText=[regex]::Replace($oldText,$pattern,'view-distance=5$1')
  $oldHash=(Get-FileHash -LiteralPath $cfg -Algorithm SHA256).Hash
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
  $phase='APPLY_VIEW_FIVE_OFFLINE'
  $backupDir=Join-Path (Join-Path (Split-Path -Parent $Server) 'Arena-Private-Backups') ('offline-' + $env:GITHUB_RUN_ID)
  $offlineConfig=Join-Path $backupDir 'server/server.properties'
  if ((Get-FileHash -LiteralPath $offlineConfig -Algorithm SHA256 -ErrorAction Stop).Hash -cne $oldHash -or
      (Get-FileHash -LiteralPath $cfg -Algorithm SHA256 -ErrorAction Stop).Hash -cne $oldHash) {
    throw 'Server config changed or offline copy mismatch'
  }
  $rollback=Join-Path (Join-Path (Split-Path -Parent $Server) 'Arena-Private-Rollback') ('view-5-' + $env:GITHUB_RUN_ID)
  if (Test-Path -LiteralPath $rollback) { throw 'Rollback dir exists' }
  New-Item -ItemType Directory -Path $rollback -Force -ErrorAction Stop | Out-Null
  $rollbackFile=Join-Path $rollback 'original-server.properties'
  Copy-Item -LiteralPath $cfg -Destination $rollbackFile -ErrorAction Stop
  if ((Get-FileHash -LiteralPath $rollbackFile -Algorithm SHA256).Hash -cne $oldHash) { throw 'Config rollback copy digest mismatch' }
  $rehearsal=Join-Path $rollback 'restore-check.properties'
  Copy-Item -LiteralPath $rollbackFile -Destination $rehearsal -ErrorAction Stop
  if ((Get-FileHash -LiteralPath $rehearsal -Algorithm SHA256).Hash -cne $oldHash) { throw 'Config restore rehearsal mismatch' }
  Remove-Item -LiteralPath $rehearsal -Force -ErrorAction Stop
  $temp=Join-Path $rollback 'new-server.properties'
  $swap=Join-Path $rollback 'atomic-original.properties'
  [IO.File]::WriteAllText($temp,$newText,$cfgEncoding)
  # Treat a failed replace as uncertain: the finally block must restore from
  # the SHA-verified copy before restarting, even if Replace throws midway.
  $viewChanged = $true
  [IO.File]::Replace($temp,$cfg,$swap)
  if ((Get-FileHash -LiteralPath $swap -Algorithm SHA256).Hash -cne $oldHash -or
      [IO.File]::ReadAllText($cfg,$cfgEncoding) -cne $newText) { throw 'Atomic config replacement mismatch' }
  Write-Output '::notice title=Five-chunk server config::OFFLINE_BACKUP_VERIFIED=true RESTORE_REHEARSED=true SERVER_VIEW_DISTANCE=5; SERVER_STILL_STOPPED=true WORLD_JARS_UNCHANGED=true'
} catch {
  $failed = $true
  Write-Output ('::error title=FunCity maintenance::BLOCKED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_LIVE_JAR_CHANGED=true')
} finally {
  if ($stopSent) {
    $phase = 'RESTART_ORIGINAL'
    try {
      # A failed offline config change is reverted before starting any server.
      if ($failed -and $viewChanged) {
        if (@(Server-Procs).Count -ne 0 -or
            @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue).Count -ne 0 -or
            -not (Test-Path -LiteralPath $rollbackFile -PathType Leaf) -or
            (Get-FileHash -LiteralPath $rollbackFile -Algorithm SHA256).Hash -cne $oldHash) {
          throw 'Unsafe config rollback; do not launch duplicate'
        }
        $restoreTemp=Join-Path (Split-Path -Parent $rollbackFile) 'restore-original-temp.properties'
        Copy-Item -LiteralPath $rollbackFile -Destination $restoreTemp -ErrorAction Stop
        [IO.File]::Replace($restoreTemp,$cfg,$null)
        if ((Get-FileHash -LiteralPath $cfg -Algorithm SHA256).Hash -cne $oldHash) { throw 'Config rollback digest mismatch' }
        $viewChanged=$false
      }
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
      $rconReady=$false
      for ($i=0;$i -lt 30;$i++) {
        $probe=@(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Server -Command list)
        if ($LASTEXITCODE -eq 0 -and @($probe | Where-Object { $_ -match 'AUTH_OK=true PLAYER_STATE=(ZERO|ACTIVE)\b' }).Count -eq 1) {
          $rconReady=$true; break
        }
        Start-Sleep -Seconds 2
      }
      if (-not $rconReady) { throw 'Original restarted but RCON unverified' }
      $expectedView=if ($viewChanged) { '5' } else { '6' }
      if ([regex]::Matches([IO.File]::ReadAllText($cfg,[Text.Encoding]::GetEncoding(28591)),
          '(?m)^view-distance=' + $expectedView + '\r?$').Count -ne 1) {
        throw 'Configured view distance not as expected after restart'
      }
    } catch {
      $failed = $true
      Write-Output ('::error title=FunCity restart::ORIGINAL_RESTART_UNVERIFIED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true; NO_SECOND_INSTANCE=true')
      # If the task failed with no running server at all, restore the old config
      # from the verified private copy and make ONE guarded attempt to revive it.
      if ($viewChanged) {
        try {
          if (@(Server-Procs).Count -ne 0 -or
              @(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue).Count -ne 0 -or
              (Get-FileHash -LiteralPath $rollbackFile -Algorithm SHA256).Hash -cne $oldHash) {
            throw 'Running or rollback uncertain; no forced stop'
          }
          $restoreTemp=Join-Path (Split-Path -Parent $rollbackFile) 'fallback-original-temp.properties'
          Copy-Item -LiteralPath $rollbackFile -Destination $restoreTemp -ErrorAction Stop
          [IO.File]::Replace($restoreTemp,$cfg,$null)
          if ((Get-FileHash -LiteralPath $cfg -Algorithm SHA256).Hash -cne $oldHash) { throw 'Fallback config digest mismatch' }
          $viewChanged=$false
          $null=Assert-RestartTask
          Start-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
          for ($i=0;$i -lt 90;$i++) {
            $new=@(Server-Procs)
            $port=@(Get-NetTCPConnection -LocalPort 25565 -State Listen -ErrorAction SilentlyContinue)
            if ($new.Count -eq 1 -and $port.Count -eq 1 -and $port[0].OwningProcess -eq $new[0].ProcessId) {
              $restartVerified=$true; break
            }
            Start-Sleep -Seconds 2
          }
          Write-Output ('::notice title=Server view rollback::OLD_CONFIG_RESTORED=true ORIGINAL_PORT_RESTORED=' + $restartVerified)
        } catch {
          Write-Output ('::error title=Server view rollback::MANUAL_RECOVERY_REQUIRED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true NO_SECOND_INSTANCE=true')
        }
      }
    }
  }
  Write-Output ('::notice title=FunCity view-five result::STOP_SENT=' + $stopSent + ' FRESH_BACKUP_VERIFIED=' + $backupVerified + ' RESTORE_REHEARSED=' + $backupVerified + ' SERVER_PORT_READY=' + $restartVerified + ' VIEW_FIVE_ACTIVE=' + ($viewChanged -and -not $failed) + ' LIVE_JARS_CHANGED=false CLIENT_UNCHANGED=true')
}
if ($failed -or -not $backupVerified -or -not $restartVerified -or -not $viewChanged) { exit 2 }
exit 0
