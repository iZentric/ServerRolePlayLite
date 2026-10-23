# Read ONLY latest.log of the owner-selected new Prism Lite instance.
# Never upload or print raw lines, player names, IPs, accounts or paths.
param([Parameter(Mandatory=$true)][string]$Profile)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances') { throw 'Wrong profile' }
  $game = @(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($game.Count -ne 1) { throw 'Ambiguous folder' }
  $logs = Join-Path (Join-Path $Profile $game[0]) 'logs'
  $folder = [IO.DirectoryInfo]::new($logs)
  if (-not $folder.Exists -or ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe logs folder' }
  $path = Join-Path $logs 'latest.log'
  $file = Get-Item -LiteralPath $path -ErrorAction Stop
  if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $file.Length -gt 100000000) { throw 'Unsafe log file' }
  $tail = @(Get-Content -LiteralPath $path -Tail 350 -ErrorAction Stop)
  $bad = @($tail | Where-Object { $_ -match '(?i)incomplete mod data|unvollst.ndige moddaten|mismatched mods?|missing mods?|missing registry|mod rejection|mod list mismatch' })
  $handshake = @($tail | Where-Object { $_ -match '(?i)fml.*handshake|forge.*handshake|mismatch|missing mod|mod rejection|incomplete mod data' })
  $ids = @('aiimprovements','bwncr','clumps','connectivity','fastbench','fastfurnace','fastsuite','getittogetherdrops','incontrol','ksyxis','letmedespawn','memoryleakfix','placebo','roadrunner','sf','smoothchunk')
  $mentioned = @($ids | Where-Object {
    $id = $_
    @($handshake | Where-Object { $_ -match ('(?i)(?<![A-Za-z0-9_.-])' + [regex]::Escape($id) + '(?![A-Za-z0-9_.-])') }).Count -gt 0
  })
  $registry = @($tail | Where-Object { $_ -match '(?i)missing registry|registry data|failed to synchronize registr' }).Count
  $channels = @($tail | Where-Object { $_ -match '(?i)channel.*(mismatch|missing|reject)|network.*mod.*mismatch' }).Count
  $versions = @($tail | Where-Object { $_ -match '(?i)wrong version|version mismatch|out of date|neusten stand' }).Count
  Write-Output ('::notice title=Lite join local diagnosis::LATEST_LOG_FOUND=true RECENT_MOD_MISMATCH_LINES=' + $bad.Count + ' RECENT_HANDSHAKE_HINT_LINES=' + $handshake.Count + ' REGISTRY_HINTS=' + $registry + ' CHANNEL_HINTS=' + $channels + ' VERSION_HINTS=' + $versions + ' SERVER_ONLY_IDS_IN_HINTS=' + ($mentioned -join ',') + '; RAW_LOG_NOT_UPLOADED=true; CLIENT_JOIN=FAILED_SCREENSHOT')
  exit 0
} catch {
  Write-Output '::notice title=Lite join local diagnosis::LOCAL_LOG_UNAVAILABLE; RAW_LOG_NOT_UPLOADED=true'
  exit 2
}
