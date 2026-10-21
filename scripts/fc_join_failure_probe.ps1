# Read-only, bounded, privacy-safe diagnostic of most recent Prism Lite join attempt.
# Never prints/ships raw log text, usernames, IPs, world data, config or secrets.
param([Parameter(Mandatory=$true)][string]$Profile,
      [Parameter(Mandatory=$true)][string]$Server)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Recent-Lines([string]$Path) {
  $file = Get-Item -LiteralPath $Path -ErrorAction Stop
  if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $file.Length -gt 100000000) { throw 'Unsafe log' }
  return @{ ageHours=[math]::Floor(((Get-Date).ToUniversalTime()-$file.LastWriteTimeUtc).TotalHours);
            lines=@(Get-Content -LiteralPath $Path -Tail 1500 -ErrorAction Stop) }
}
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances' -or
      (Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Unexpected location' }
  $games = @(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous Prism folder' }
  $client = Recent-Lines (Join-Path (Join-Path (Join-Path $Profile $games[0]) 'logs') 'latest.log')
  $serverLog = Recent-Lines (Join-Path (Join-Path $Server 'logs') 'latest.log')
  $clientLines = @($client.lines)
  $serverLines = @($serverLog.lines)
  $disconnects = @($serverLines | Where-Object { $_ -match '(?i)(lost connection|disconnected|disconnecting)' })
  $lastDisconnect = if ($disconnects.Count) { [string]$disconnects[-1] } else { '' }
  $reasonFlags = @{
    forge=[bool]($lastDisconnect -match '(?i)forge|fml')
    mod=[bool]($lastDisconnect -match '(?i)\bmod(s|ded)?\b')
    registry=[bool]($lastDisconnect -match '(?i)registr')
    timeout=[bool]($lastDisconnect -match '(?i)timed out|timeout')
    authentication=[bool]($lastDisconnect -match '(?i)auth|session|whitelist|banned')
    network=[bool]($lastDisconnect -match '(?i)network|packet|protocol')
  }
  $signals = @{
    attempted=@($clientLines | Where-Object { $_ -match '(?i)(connecting to|connect to|trying to connect|connecting:)'}).Count
    incomplete=@($clientLines | Where-Object { $_ -match '(?i)incomplete mod data|unvollst.ndige moddaten|incomplete set of tags' }).Count
    registry=@($clientLines | Where-Object { $_ -match '(?i)(failed to synchronize registr|missing registr|registry mismatch|registry remapping|registry data)' }).Count
    modlist=@($clientLines | Where-Object { $_ -match '(?i)(mod list mismatch|mismatched mods|missing mods|mod rejection|mod channel.*(missing|reject)|channel.*mismatch)' }).Count
    version=@($clientLines | Where-Object { $_ -match '(?i)(wrong version|version mismatch|incompatible version|out of date)' }).Count
    serverDisconnect=@($serverLines | Where-Object { $_ -match '(?i)(lost connection|disconnected|disconnecting)' }).Count
    serverRegistry=@($serverLines | Where-Object { $_ -match '(?i)(failed to synchronize registr|missing registr|registry mismatch|registry remapping)' }).Count
  }
  # Only a fixed allowlist of public mod IDs may be reported, never log tokens or player names.
  $ids=@('clumps','aiimprovements','bwncr','connectivity','fastbench','fastfurnace','fastsuite',
         'getittogetherdrops','incontrol','ksyxis','letmedespawn','memoryleakfix','placebo',
         'roadrunner','sf','smoothchunk')
  $hints=@($clientLines + $serverLines | Where-Object { $_ -match '(?i)(mod|registry|handshake|channel|disconnect)' })
  $mentioned=@($ids | Where-Object {
    $id=$_
    @($hints | Where-Object { $_ -match ('(?i)(?<![A-Za-z0-9_.-])' + [regex]::Escape($id) + '(?![A-Za-z0-9_.-])') }).Count -gt 0
  })
  Write-Output ('::notice title=Latest Forge join evidence::CLIENT_LOG_AGE_H=' + $client.ageHours + ' SERVER_LOG_AGE_H=' + $serverLog.ageHours +
    ' CLIENT_CONNECT_HINTS=' + $signals.attempted + ' CLIENT_INCOMPLETE_HINTS=' + $signals.incomplete +
    ' CLIENT_REGISTRY_HINTS=' + $signals.registry + ' CLIENT_MODLIST_HINTS=' + $signals.modlist +
    ' CLIENT_VERSION_HINTS=' + $signals.version + ' SERVER_DISCONNECT_HINTS=' + $signals.serverDisconnect +
    ' SERVER_REGISTRY_HINTS=' + $signals.serverRegistry + ' LAST_DISCONNECT_FORGE=' + $reasonFlags.forge +
    ' LAST_DISCONNECT_MOD=' + $reasonFlags.mod + ' LAST_DISCONNECT_REGISTRY=' + $reasonFlags.registry +
    ' LAST_DISCONNECT_TIMEOUT=' + $reasonFlags.timeout + ' LAST_DISCONNECT_AUTH=' + $reasonFlags.authentication +
    ' LAST_DISCONNECT_NETWORK=' + $reasonFlags.network + ' ALLOWLIST_MOD_IDS=' + ($mentioned -join ',') +
    '; RECENT_LOG_TAIL_ONLY=true RAW_LOG_NOT_UPLOADED=true JOIN_NOT_PROVEN=true')
  exit 0
} catch {
  Write-Output ('::notice title=Latest Forge join evidence::PROBE_UNAVAILABLE PHASE=' + $_.InvocationInfo.ScriptLineNumber + ' TYPE=' + $_.Exception.GetType().Name + '; RAW_LOG_NOT_UPLOADED=true')
  exit 2
}
