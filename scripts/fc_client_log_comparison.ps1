# Read-only, privacy-preserving comparison of the last local Minecraft logs in two approved Prism profiles.
# Reports timing of the LOG WINDOW, not FPS or launch/menu benchmark. No raw lines, paths, IPs, usernames or logs leave PC.
param([Parameter(Mandatory=$true)][string]$Instances)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Safe-Folder([string]$Path) {
  $item=[IO.DirectoryInfo]::new($Path)
  if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unavailable/unsafe folder' }
}
function Audit([string]$Root,[string]$Label) {
  Safe-Folder $Root
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Root $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous game folder' }
  $game=Join-Path $Root $games[0]
  Safe-Folder $game
  $logs=Join-Path $game 'logs'
  Safe-Folder $logs
  $log=Join-Path $logs 'latest.log'
  $file=Get-Item -LiteralPath $log -ErrorAction Stop
  if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $file.Length -gt 50000000) { throw 'Unsafe/oversized last log' }
  $lines=@(Get-Content -LiteralPath $log -ErrorAction Stop)
  if ($lines.Count -gt 400000) { throw 'Too many log lines' }
  $errorCount=0; $fatalCount=0; $warningCount=0
  $crashHints=0; $rendererErrors=0; $rendererWarnings=0
  $joinHints=0; $disconnectHints=0; $startupHints=0; $soundHints=0; $stopHints=0
  $first=$null; $last=$null; $firstSound=$null; $firstJoin=$null; $day=0; $prev=$null; $timedLines=0
  foreach ($line in $lines) {
    # Forge 1.16 can prefix the timestamp with 22Oct2026 and include milliseconds.
    $match=[regex]::Match($line,'^\[(?:(?:\d{1,2}[A-Za-z]{3}\d{4}|\d{4}-\d{2}-\d{2})\s+)?(\d\d):(\d\d):(\d\d)(?:[.,]\d{1,6})?\]')
    if ($match.Success) {
      $hh=[int]$match.Groups[1].Value; $mm=[int]$match.Groups[2].Value; $ss=[int]$match.Groups[3].Value
      if ($hh -lt 24 -and $mm -lt 60 -and $ss -lt 60) {
        $seconds=$hh*3600+$mm*60+$ss
        if ($prev -ne $null -and $seconds -lt $prev) { $day++ }
        $sec=$seconds + 86400*$day
        if ($first -eq $null) { $first=$sec }
        $last=$sec
        $prev=$seconds
        $timedLines++
      }
    }
    $isError=$line -match '\[[^\]]+/(ERROR|FATAL)\]'
    $isWarn=$line -match '\[[^\]]+/WARN\]'
    if ($isError) { $errorCount++ }
    if ($line -match '\[[^\]]+/FATAL\]') { $fatalCount++ }
    if ($isWarn) { $warningCount++ }
    if ($line -match '(?i)uncaught exception|crash report saved|mixin apply failed|noclassdeffounderror|exception in thread') { $crashHints++ }
    if ($line -match '(?i)(embeddium|rubidium|oculus)' -and $isError) { $rendererErrors++ }
    if ($line -match '(?i)(embeddium|rubidium|oculus)' -and $isWarn) { $rendererWarnings++ }
    if ($line -match '(?i)ModLauncher running|Launching target .fmlclient.|Launching minecraft|Starting Minecraft') { $startupHints++ }
    if ($line -match '(?i)OpenAL initialized|Sound engine started') {
      $soundHints++
      if ($firstSound -eq $null -and $last -ne $null) { $firstSound=$last }
    }
    if ($line -match '(?i)connecting to |logged in with entity id|join(?:ed|ing) world|connected to server') {
      $joinHints++
      if ($firstJoin -eq $null -and $last -ne $null) { $firstJoin=$last }
    }
    if ($line -match '(?i)disconnected|lost connection|connection closed') { $disconnectHints++ }
    if ($line -match '(?i)Stopping!|Shutting down') { $stopHints++ }
  }
  $span='UNKNOWN'; $toSound='UNKNOWN'; $toJoin='UNKNOWN'
  if ($first -ne $null -and $last -ne $null -and $last -ge $first) { $span="$($last-$first)" }
  if ($first -ne $null -and $firstSound -ne $null -and $firstSound -ge $first) { $toSound="$($firstSound-$first)" }
  if ($first -ne $null -and $firstJoin -ne $null -and $firstJoin -ge $first) { $toJoin="$($firstJoin-$first)" }
  $rotated=@(Get-ChildItem -LiteralPath $logs -File -Filter '*.log.gz' -ErrorAction Stop).Count
  # These intervals are log milestones, NOT game menu load time or comparable FPS.
  Write-Output ('::notice title=Client sanitized log ' + $Label + '::LOG_PRESENT=true BYTES=' + $file.Length +
    ' LINE_COUNT=' + $lines.Count + ' TIMED_LINES=' + $timedLines + ' LOG_SPAN_SECONDS=' + $span +
    ' TO_FIRST_SOUND_SECONDS=' + $toSound + ' TO_FIRST_CONNECT_HINT_SECONDS=' + $toJoin +
    ' STARTUP_HINTS=' + $startupHints + ' STOP_HINTS=' + $stopHints +
    ' SOUND_HINTS=' + $soundHints + ' JOIN_HINTS=' + $joinHints + ' DISCONNECT_HINTS=' + $disconnectHints +
    ' WARN_LINES=' + $warningCount + ' ERROR_LINES=' + $errorCount + ' FATAL_LINES=' + $fatalCount +
    ' CRASH_HINTS=' + $crashHints + ' RENDERER_ERROR_LINES=' + $rendererErrors +
    ' RENDERER_WARN_LINES=' + $rendererWarnings + ' ROTATED_LOGS=' + $rotated +
    '; LOG_SPAN_IS_NOT_LOAD_TIME=true; FPS_NOT_IN_LOG=true; NO_RAW_DATA=true')
}
try {
  if ((Split-Path -Leaf $Instances) -cne 'instances' -or
      (Split-Path -Leaf (Split-Path -Parent $Instances)) -cne 'PrismLauncher') { throw 'Wrong launcher' }
  Safe-Folder $Instances
  Audit (Join-Path $Instances 'FunCity RP Lite') 'RUBIDIUM'
  Audit (Join-Path $Instances 'FunCity RP Lite Embeddium TEST') 'EMBEDDIUM_TEST'
  exit 0
} catch {
  Write-Output ('::notice title=Client sanitized logs::AUDIT_UNAVAILABLE TYPE=' + $_.Exception.GetType().Name +
    ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_RAW_DATA=true')
  exit 2
}
