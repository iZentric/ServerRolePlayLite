# Read-only Minecraft status handshake, loopback only. NEVER log the raw JSON:
# it may contain MOTD, player names, addresses or Forge mod metadata.
param([int]$Port = 25565, [switch]$SelfTest)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Write-VarInt([IO.Stream]$Stream, [int]$Number) {
  if ($Number -lt 0) { throw 'Negative VarInt' }
  do {
    $part = $Number -band 127
    $Number = $Number -shr 7
    if ($Number -gt 0) { $part = $part -bor 128 }
    $Stream.WriteByte([byte]$part)
  } while ($Number -gt 0)
}
function Read-VarInt([IO.Stream]$Stream) {
  $value = 0
  for ($i = 0; $i -lt 5; $i++) {
    $part = $Stream.ReadByte()
    if ($part -lt 0) { throw 'Truncated VarInt' }
    $value = $value -bor (($part -band 127) -shl ($i * 7))
    if (($part -band 128) -eq 0) { return $value }
  }
  throw 'Excessive VarInt'
}
try {
  if ($SelfTest) {
    foreach ($n in @(0,1,127,128,754,65535,1048576)) {
      $stream = New-Object IO.MemoryStream
      Write-VarInt $stream $n
      $stream.Position = 0
      if ((Read-VarInt $stream) -ne $n) { throw 'VarInt fixture mismatch' }
      $stream.Dispose()
    }
    Write-Output 'PASS: local status ping VarInt fixture only'
    exit 0
  }
  if ($Port -lt 1 -or $Port -gt 65535) { throw 'Invalid port' }
  $socket = New-Object Net.Sockets.TcpClient
  try {
    $connect = $socket.BeginConnect('127.0.0.1', $Port, $null, $null)
    if (-not $connect.AsyncWaitHandle.WaitOne(3000)) { throw 'Connect timeout' }
    $socket.EndConnect($connect)
    $socket.ReceiveTimeout = 3000
    $socket.SendTimeout = 3000
    $stream = $socket.GetStream()
    $hostBytes = [Text.Encoding]::UTF8.GetBytes('localhost')
    $packet = New-Object IO.MemoryStream
    Write-VarInt $packet 0       # handshake packet id
    Write-VarInt $packet 754     # Minecraft 1.16.5 status protocol
    Write-VarInt $packet $hostBytes.Length
    $packet.Write($hostBytes,0,$hostBytes.Length)
    $packet.WriteByte([byte](($Port -shr 8) -band 255))
    $packet.WriteByte([byte]($Port -band 255))
    Write-VarInt $packet 1       # next state: status, not login
    $request = $packet.ToArray()
    Write-VarInt $stream $request.Length
    $stream.Write($request,0,$request.Length)
    $stream.Write([byte[]]@(1,0),0,2) # length=1; status request packet=0
    $size = Read-VarInt $stream
    if ($size -lt 2 -or $size -gt 1048576) { throw 'Invalid response length' }
    $raw = New-Object 'byte[]' $size
    $offset = 0
    while ($offset -lt $size) {
      $received = $stream.Read($raw,$offset,$size-$offset)
      if ($received -le 0) { throw 'Truncated status response' }
      $offset += $received
    }
    $message = [IO.MemoryStream]::new($raw)
    if ((Read-VarInt $message) -ne 0) { throw 'Not a status response' }
    $jsonLength = Read-VarInt $message
    if ($jsonLength -lt 1 -or $jsonLength -gt 1048576 -or
        ($message.Position + $jsonLength) -ne $size) { throw 'Invalid JSON length' }
    $json = [Text.Encoding]::UTF8.GetString($raw,[int]$message.Position,$jsonLength) | ConvertFrom-Json
    $protocol = [int]$json.version.protocol
    $players = [int]$json.players.online
    if ($protocol -lt 1 -or $players -lt 0) { throw 'Invalid status values' }
    Write-Output ('::notice title=Minecraft local status::STATUS_PING=READY PROTOCOL=' + $protocol + ' PLAYERS_ONLINE=' + $players + '; LOOPBACK_ONLY=true CLIENT_JOIN=NOT_TESTED')
  } finally { $socket.Close() }
  exit 0
} catch {
  # No exception text: it can embed private paths, hostnames or status content.
  Write-Output '::notice title=Minecraft local status::STATUS_PING=UNKNOWN; LOOPBACK_ONLY=true CLIENT_JOIN=NOT_TESTED'
  exit 2
}
