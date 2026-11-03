# Bounded private compatibility boot, ONLY after owner stopped original.
# No world/JAR changes to original; try RCON and console 'stop' for disposable copy;
# restart original task ONLY after copy fully exited. Never force-kill either JVM.
param([Parameter(Mandatory=$true)][string]$Server,
      [Parameter(Mandatory=$true)][string]$Copy)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$phase='PREFLIGHT'
$testBooted=$false
$originalRestored=$false
$failed=$false
$started=$false
$process=$null
function Matching-Procs([string]$Path) {
  return @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
    $_.CommandLine -and $_.CommandLine.IndexOf($Path,[StringComparison]::OrdinalIgnoreCase) -ge 0
  })
}
function Listeners {
  return @(Get-NetTCPConnection -State Listen -LocalPort 25565 -ErrorAction SilentlyContinue)
}
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal' -or
      (Split-Path -Leaf $Copy) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Copy)) -cne 'bootable-no-clumps-39598696934' -or
      -not $Copy.StartsWith((Split-Path -Parent $Server),[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Wrong original or copy'
  }
  $task=Get-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
  $actions=@($task.Actions)
  if ($task.State -eq 'Disabled' -or $actions.Count -ne 1 -or
      -not $actions[0].WorkingDirectory.Equals($Server,[StringComparison]::OrdinalIgnoreCase) -or
      $actions[0].Arguments -notmatch '(?i)-jar\s+FunCityEngine\.jar\s+nogui' -or
      -not (Test-Path -LiteralPath $actions[0].Execute -PathType Leaf)) { throw 'Original restart task invalid' }
  if (@(Matching-Procs $Server).Count -ne 0 -or @(Matching-Procs $Copy).Count -ne 0 -or @(Listeners).Count -ne 0) {
    throw 'Original or another game process is active; never start a second server'
  }
  $stage=Split-Path -Parent $Copy
  $base=(Get-Content -LiteralPath (Join-Path $stage 'private-copy-manifest.json') -Raw -ErrorAction Stop | ConvertFrom-Json)
  $voice=(Get-Content -LiteralPath (Join-Path $stage 'private-voicechat-trial.json') -Raw -ErrorAction Stop | ConvertFrom-Json)
  if ($base.copy_hash_verified -ne $true -or $base.source_verified_offline -ne $true -or
      $voice.voicechat_added_to_private_copy -ne $true -or $voice.clumps_removed_from_private_copy -ne $true -or
      -not (Test-Path -LiteralPath (Join-Path (Split-Path -Parent $Server) 'Arena-Private-Backups/offline-39597824602/private-manifest.json'))) {
    throw 'No verified rollback and private trial'
  }
  $jar=Join-Path $Copy 'FunCityEngine.jar'
  $java=Join-Path $Copy 'java11/bin/java.exe'
  if (-not (Test-Path -LiteralPath $jar -PathType Leaf) -or -not (Test-Path -LiteralPath $java -PathType Leaf) -or
      @(Get-ChildItem -LiteralPath (Join-Path $Copy 'mods') -File -Filter '*.jar' -ErrorAction Stop).Count -ne 34 -or
      (Test-Path -LiteralPath (Join-Path $Copy 'mods/Clumps-6.0.0.28.jar'))) { throw 'Trial engine/mods mismatch' }
  $phase='BOOT_PRIVATE_COPY'
  $process=[Diagnostics.Process]::new()
  $process.StartInfo.FileName=$java
  $process.StartInfo.Arguments='-Xms2G -Xmx6G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -jar FunCityEngine.jar nogui'
  $process.StartInfo.WorkingDirectory=$Copy
  $process.StartInfo.UseShellExecute=$false
  $process.StartInfo.CreateNoWindow=$true
  $process.StartInfo.RedirectStandardInput=$true
  $process.StartInfo.RedirectStandardOutput=$true
  $process.StartInfo.RedirectStandardError=$true
  if (-not $process.Start()) { throw 'Private Java did not start' }
  $started=$true
  # Drain privately; never send console output, logs or usernames to GitHub.
  $stdoutDrain=$process.StandardOutput.ReadToEndAsync()
  $stderrDrain=$process.StandardError.ReadToEndAsync()
  for ($i=0;$i -lt 90;$i++) {
    if ($process.HasExited) { break }
    $port=@(Listeners)
    if ($port.Count -eq 1 -and $port[0].OwningProcess -eq $process.Id) {
      $list=@(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Copy -PrivateCopy -Command list)
      if ($LASTEXITCODE -eq 0 -and @($list | Where-Object { $_ -match 'AUTH_OK=true PLAYER_STATE=ZERO\b' }).Count -eq 1) {
        $testBooted=$true
        break
      }
    }
    Start-Sleep -Seconds 2
  }
  if (-not $testBooted) { throw 'Copy did not become RCON-ready before deadline' }
  Write-Output '::notice title=Private Forge compatibility boot::COPY_BOOT_RCON_READY=true NO_CLUMPS=true VOICECHAT_FROM_LITE=true ORIGINAL_JARS_UNCHANGED=true; CLIENT_LOGIN_NOT_TESTED=true'
} catch {
  $failed=$true
  Write-Output ('::error title=Private Forge compatibility boot::COPY_BOOT_UNVERIFIED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; ORIGINAL_JARS_UNCHANGED=true')
} finally {
  if ($started -and $process) {
    $phase='STOP_PRIVATE_COPY'
    try {
      if (-not $process.HasExited) {
        $port=@(Listeners)
        if ($port.Count -eq 1 -and $port[0].OwningProcess -eq $process.Id) {
          $stop=@(& (Join-Path $PSScriptRoot 'fc_local_rcon.ps1') -Server $Copy -PrivateCopy -Command stop)
          # Even if the response is lost, also send a normal console stop as fallback.
        }
        $process.StandardInput.WriteLine('stop')
        $process.StandardInput.Flush()
        if (-not $process.WaitForExit(180000)) { throw 'Private copy did not exit normally; do not launch second JVM' }
      }
    } catch {
      $failed=$true
      Write-Output ('::error title=Private copy cleanup::COPY_STOP_UNVERIFIED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; ORIGINAL_NOT_STARTED_OVER_COPY=true')
    }
  }
  $phase='RESTART_ORIGINAL'
  try {
    if (@(Matching-Procs $Copy).Count -ne 0 -or @(Matching-Procs $Server).Count -ne 0 -or @(Listeners).Count -ne 0) {
      throw 'Unexpected running server; no second instance'
    }
    $task=Get-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
    if ($task.State -eq 'Disabled' -or @($task.Actions).Count -ne 1 -or
        -not $task.Actions[0].WorkingDirectory.Equals($Server,[StringComparison]::OrdinalIgnoreCase)) {
      throw 'Restart task changed'
    }
    Start-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction Stop
    for ($i=0;$i -lt 90;$i++) {
      $original=@(Matching-Procs $Server)
      $port=@(Listeners)
      if ($original.Count -eq 1 -and $port.Count -eq 1 -and $port[0].OwningProcess -eq $original[0].ProcessId) {
        $originalRestored=$true; break
      }
      Start-Sleep -Seconds 2
    }
    if (-not $originalRestored) { throw 'Original task did not restore game port' }
  } catch {
    $failed=$true
    Write-Output ('::error title=Original restart::ORIGINAL_RESTART_UNVERIFIED TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCE_KILL=true')
  }
  Write-Output ('::notice title=Forge copy trial result::COPY_BOOTED=' + $testBooted + ' COPY_STOPPED=' + (-not $started -or ($process -and $process.HasExited)) + ' ORIGINAL_RESTARTED=' + $originalRestored + ' ORIGINAL_JARS_CHANGED=false CLIENT_LOGIN_TESTED=false')
  if ($process) { $process.Dispose() }
}
if ($failed -or -not $testBooted -or -not $originalRestored) { exit 2 }
exit 0
