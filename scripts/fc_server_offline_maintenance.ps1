# Authorized maintenance only: zero players -> RCON save/stop -> private whole-tree
# offline backup + independent restore-copy check -> restart the ORIGINAL task.
# No live JAR edits, no test server, no uploads or forced process termination.
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
} catch {
  $failed = $true
  Write-Output ('::error title=FunCity maintenance::BLOCKED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_LIVE_JAR_CHANGED=true')
} finally {
  if ($stopSent) {
    $phase = 'RESTART_ORIGINAL'
    try {
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
      Write-Output ('::error title=FunCity restart::ORIGINAL_RESTART_UNVERIFIED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true; NO_SECOND_INSTANCE=true')
    }
  }
  Write-Output ('::notice title=FunCity maintenance result::STOP_SENT=' + $stopSent + ' BACKUP_VERIFIED=' + $backupVerified + ' RESTORE_COPY_VERIFIED=' + $backupVerified + ' ORIGINAL_RESTARTED=' + $restartVerified + ' LIVE_JARS_CHANGED=false JOIN_TESTED=false')
}
if ($failed -or -not $backupVerified -or -not $restartVerified) { exit 2 }
exit 0
