# Restricted local RCON control for the identified FunCityLocal server only.
# Never prints password, RCON response, names, address, command lines or paths.
param([Parameter(Mandatory=$true)][string]$Server,
      [ValidateSet('list','save-all flush','stop')][string]$Command = 'list',
      [switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$phase = 'CONFIG'
function Read-Exactly([IO.Stream]$Stream,[int]$Count) {
  $buffer = New-Object 'byte[]' $Count
  $offset = 0
  while ($offset -lt $Count) {
    $n = $Stream.Read($buffer,$offset,$Count-$offset)
    if ($n -le 0) { throw 'Incomplete RCON packet' }
    $offset += $n
  }
  return ,$buffer
}
function Send-Packet([IO.Stream]$Stream,[int]$Id,[int]$Type,[string]$Payload) {
  $data = [Text.Encoding]::UTF8.GetBytes($Payload)
  if ($data.Length -gt 1024) { throw 'Excessive RCON payload' }
  # A single fixed byte frame avoids Windows PowerShell 5.1 BinaryWriter overload coercion.
  $frame = New-Object 'byte[]' ($data.Length + 14)
  [Array]::Copy([BitConverter]::GetBytes([int]($data.Length + 10)),0,$frame,0,4)
  [Array]::Copy([BitConverter]::GetBytes([int]$Id),0,$frame,4,4)
  [Array]::Copy([BitConverter]::GetBytes([int]$Type),0,$frame,8,4)
  [Array]::Copy($data,0,$frame,12,$data.Length)
  $Stream.Write($frame,0,$frame.Length)
  $Stream.Flush()
}
function Read-Packet([IO.Stream]$Stream) {
  $size = [BitConverter]::ToInt32((Read-Exactly $Stream 4),0)
  if ($size -lt 10 -or $size -gt 65536) { throw 'Invalid RCON packet size' }
  $body = Read-Exactly $Stream $size
  if ($body[$size-1] -ne 0 -or $body[$size-2] -ne 0) { throw 'Invalid RCON packet terminator' }
  return @{ id=[BitConverter]::ToInt32($body,0); type=[BitConverter]::ToInt32($body,4);
            text=[Text.Encoding]::UTF8.GetString($body,8,$size-10) }
}
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Wrong server' }
  $cfg = Join-Path $Server 'server.properties'
  $item = Get-Item -LiteralPath $cfg -ErrorAction Stop
  if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe config' }
  $lines = @(Get-Content -LiteralPath $cfg -ErrorAction Stop)
  $enabled = @($lines | Where-Object { $_ -ceq 'enable-rcon=true' })
  $ports = @($lines | Where-Object { $_ -match '^rcon\.port=[0-9]+$' })
  $passwords = @($lines | Where-Object { $_ -match '^rcon\.password=.+$' })
  if ($enabled.Count -ne 1 -or $ports.Count -ne 1 -or $passwords.Count -ne 1) { throw 'RCON not configured exactly once' }
  $port = [int](($ports[0] -split '=',2)[1])
  $password = ($passwords[0] -split '=',2)[1]
  if ($port -lt 1 -or $port -gt 65535 -or $password.Length -lt 8) { throw 'Invalid local RCON' }
  $phase = 'IDENTITY'
  if (-not $Synthetic) {
    $procs = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
      $_.CommandLine -and $_.CommandLine.IndexOf($Server,[StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    if ($procs.Count -ne 1 -or @(
      Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop | Where-Object {
        $_.OwningProcess -eq $procs[0].ProcessId -and $_.LocalAddress -eq '127.0.0.1'
      }).Count -ne 1) { throw 'Unidentified RCON server' }
  }
  $phase = 'CONNECT'
  $socket = [Net.Sockets.TcpClient]::new()
  try {
    $async = $socket.BeginConnect('127.0.0.1',$port,$null,$null)
    if (-not $async.AsyncWaitHandle.WaitOne(3000)) { throw 'RCON connect timeout' }
    $socket.EndConnect($async)
    $socket.ReceiveTimeout = 3000
    $socket.SendTimeout = 3000
    $stream = $socket.GetStream()
    $phase = 'AUTH'
    Send-Packet $stream 89321 3 $password
    $authed = $false
    for ($i=0;$i -lt 3;$i++) {
      $packet = Read-Packet $stream
      if ($packet.id -eq -1) { throw 'RCON auth refused' }
      if ($packet.id -eq 89321 -and $packet.type -eq 2) { $authed=$true; break }
    }
    if (-not $authed) { throw 'No RCON auth confirmation' }
    $phase = 'COMMAND'
    Send-Packet $stream 89322 2 $Command
    if ($Command -eq 'stop') {
      # The server may close the socket before sending the stop response.
      Write-Output '::notice title=FunCity local RCON::AUTH_OK=true STOP_REQUEST_SENT=true; PROCESS_EXIT_NOT_YET_VERIFIED=true'
      exit 0
    }
    $packet = Read-Packet $stream
    if ($packet.id -ne 89322 -or $packet.type -ne 0) { throw 'Unexpected RCON response' }
    if ($Command -eq 'list') {
      # Minecraft/plugin consoles may prepend ANSI color control codes to the count.
      $plainList = [regex]::Replace($packet.text,'\x1b\[[0-9;]*[A-Za-z]','')
      $plainList = [regex]::Replace($plainList,'[\x00-\x1f]',' ')
      $count = [regex]::Match($plainList,'(?is)there are\s+(\d+)\b.{0,120}players.{0,30}online')
      $playerState = if ($count.Success -and [int]$count.Groups[1].Value -eq 0) { 'ZERO' }
                     elseif ($count.Success) { 'ACTIVE' } else { 'UNKNOWN' }
      # Print length/whitelisted grammar signals only, never the response or player names.
      $shape = if ($packet.text.Length -eq 0) { 'EMPTY' }
               elseif ($packet.text -match '(?i)there are') { 'VANILLA_PHRASE' }
               elseif ($packet.text -match '(?i)online players|players online') { 'ONLINE_PHRASE' }
               else { 'OTHER' }
      $hasPlayers = [bool]($packet.text -match '(?i)\bplayers\b')
      $hasOnline = [bool]($packet.text -match '(?i)\bonline\b')
      $thereAreNumber = [bool]($packet.text -match '(?is)\bthere are\b.{0,120}?\b\d+\b')
      $hasNoPlayers = [bool]($packet.text -match '(?i)\bno players\b')
      $digitCount = [regex]::Matches($packet.text,'[0-9]').Count
      $controlCount = [regex]::Matches($packet.text,'[\x00-\x1f]').Count
      $colorCount = [regex]::Matches($packet.text,'§').Count
      $phraseAt = $packet.text.IndexOf('There are',[StringComparison]::OrdinalIgnoreCase)
      $firstDigit = [regex]::Match($packet.text,'[0-9]').Index
      $digitOffsets = @([regex]::Matches($packet.text,'[0-9]') | ForEach-Object { $_.Index }) -join ','
      $playersAt = $packet.text.IndexOf('players',[StringComparison]::OrdinalIgnoreCase)
      $onlineAt = $packet.text.IndexOf('online',[StringComparison]::OrdinalIgnoreCase)
      # Structural mask stops before the player list and replaces all letters/digits.
      $safePrefix = $packet.text.Substring(0,[Math]::Min($playersAt + 7,60))
      $safePrefix = [regex]::Replace($safePrefix,'[A-Za-z]','A')
      $safePrefix = [regex]::Replace($safePrefix,'[0-9]','#')
      $safePrefix = [regex]::Replace($safePrefix,'[\x00-\x20]','_')
      $safePrefix = [regex]::Replace($safePrefix,'[^A#_/:;.,()\[\]{}+-]','?')
      Write-Output ('::notice title=FunCity local RCON::AUTH_OK=true PLAYER_STATE=' + $playerState + ' MASK=' + $safePrefix + ' RESPONSE_SHAPE=' + $shape + ' RESPONSE_LENGTH=' + $packet.text.Length + ' HAS_PLAYERS=' + $hasPlayers + ' HAS_ONLINE=' + $hasOnline + ' THERE_ARE_NUMBER=' + $thereAreNumber + ' NO_PLAYERS_PHRASE=' + $hasNoPlayers + ' DIGITS=' + $digitCount + ' CONTROLS=' + $controlCount + ' COLORS=' + $colorCount + ' PHRASE_AT=' + $phraseAt + ' DIGIT_AT=' + $firstDigit + ' DIGIT_OFFSETS=' + $digitOffsets + ' PLAYERS_AT=' + $playersAt + ' ONLINE_AT=' + $onlineAt + '; RAW_PLAYER_DATA_NOT_OUTPUT=true')
    } else { Write-Output '::notice title=FunCity local RCON::AUTH_OK=true SAVE_ALL_RESPONSE_RECEIVED=true; WORLD_NOT_MODIFIED_BY_AGENT=true' }
  } finally { $socket.Close() }
  exit 0
} catch {
  # The phase, exception class and fixed enum disclose no private payload or path.
  $reason = if ($_.Exception.Message -ceq 'RCON auth refused') { 'AUTH_REJECTED' } else { 'UNCLASSIFIED' }
  Write-Output ('::notice title=FunCity local RCON::AUTH_OR_COMMAND_UNVERIFIED PHASE=' + $phase + ' REASON=' + $reason + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; PASSWORD_AND_RESPONSE_NOT_OUTPUT=true')
  exit 2
}
