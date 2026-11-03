# Read-only numeric/boolean graphics and server view-distance audit.
# Never print user paths, accounts, world names, addresses or raw file contents.
param([Parameter(Mandatory=$true)][string]$Profile,
      [Parameter(Mandatory=$true)][string]$Server)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Value-Of([string[]]$Lines,[string]$Key,[string]$Separator) {
  $match = @($Lines | Where-Object { $_ -match ('^' + [regex]::Escape($Key + $Separator)) })
  if ($match.Count -ne 1) { return 'UNKNOWN' }
  return ($match[0].Substring(($Key + $Separator).Length)).Trim()
}
function Safe-Int([string]$Value,[int]$Min,[int]$Max) {
  if ($Value -notmatch '^[0-9]{1,4}$') { return 'UNKNOWN' }
  $number=[int]$Value
  if ($number -lt $Min -or $number -gt $Max) { return 'UNKNOWN' }
  return "$number"
}
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances' -or
      (Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Wrong profile/server' }
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous game folder' }
  $serverFile=Get-Item -LiteralPath (Join-Path $Server 'server.properties') -ErrorAction Stop
  if ($serverFile.PSIsContainer -or ($serverFile.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $serverFile.Length -gt 1000000) { throw 'Unsafe server config' }
  $serverLines=@(Get-Content -LiteralPath $serverFile.FullName -ErrorAction Stop)
  $view=Safe-Int (Value-Of $serverLines 'view-distance' '=') 2 32
  $optionsPath=Join-Path (Join-Path $Profile $games[0]) 'options.txt'
  $clientPresent=Test-Path -LiteralPath $optionsPath -PathType Leaf
  $render='UNKNOWN'; $graphics='UNKNOWN'; $particles='UNKNOWN'; $mipmap='UNKNOWN'; $shadows='UNKNOWN'
  if ($clientPresent) {
    $clientFile=Get-Item -LiteralPath $optionsPath -ErrorAction Stop
    if (($clientFile.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $clientFile.Length -gt 1000000) { throw 'Unsafe options' }
    $lines=@(Get-Content -LiteralPath $optionsPath -ErrorAction Stop)
    $render=Safe-Int (Value-Of $lines 'renderDistance' ':') 2 32
    $graphics=Safe-Int (Value-Of $lines 'graphicsMode' ':') 0 3
    $particles=Safe-Int (Value-Of $lines 'particles' ':') 0 2
    $mipmap=Safe-Int (Value-Of $lines 'mipmapLevels' ':') 0 4
    $shadowValue=Value-Of $lines 'entityShadows' ':'
    if ($shadowValue -match '^(true|false)$') { $shadows=$shadowValue.ToUpperInvariant() }
  }
  Write-Output ('::notice title=Lite graphics read-only::SERVER_VIEW_DISTANCE=' + $view +
    ' CLIENT_OPTIONS_PRESENT=' + $clientPresent + ' CLIENT_RENDER_DISTANCE=' + $render +
    ' GRAPHICS_MODE_CODE=' + $graphics + ' PARTICLES_CODE=' + $particles +
    ' MIPMAP_LEVELS=' + $mipmap + ' ENTITY_SHADOWS=' + $shadows +
    '; SHADER_STATE=NOT_READ; READ_ONLY=true; FPS_NOT_MEASURED=true')
  exit 0
} catch {
  Write-Output ('::notice title=Lite graphics read-only::GATE_UNAVAILABLE TYPE=' + $_.Exception.GetType().Name +
    ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; READ_ONLY=true; RAW_CONFIG_NOT_OUTPUT=true')
  exit 2
}
