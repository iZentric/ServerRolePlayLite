# Read-only SHA parity for Forge metadata in common approved client/server JARs.
# No raw JAR entries, world files, logs, user names, IPs or binary uploads.
param([Parameter(Mandatory=$true)][string]$ClientMods,
      [Parameter(Mandatory=$true)][string]$ServerMods,
      [Parameter(Mandatory=$true)][string]$Manifest)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
function Hash-Entry([string]$Jar,[string]$Entry) {
  $zip=[IO.Compression.ZipFile]::OpenRead($Jar)
  $sha=[Security.Cryptography.SHA256]::Create()
  try {
    if ($zip.Entries.Count -gt 60000) { throw 'Archive too large' }
    $entry=$zip.GetEntry($Entry)
    if (-not $entry) { return '<absent>' }
    if ($entry.Length -gt 1048576) { throw 'Metadata entry too large' }
    $stream=$entry.Open()
    try { return [Convert]::ToBase64String($sha.ComputeHash($stream)) }
    finally { $stream.Dispose() }
  } finally { $zip.Dispose(); $sha.Dispose() }
}
try {
  foreach ($folder in @($ClientMods,$ServerMods)) {
    $dir=[IO.DirectoryInfo]::new($folder)
    if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe mods folder' }
  }
  $names=@((Get-Content -LiteralPath $Manifest -Raw -ErrorAction Stop | ConvertFrom-Json).retained_in_future_target)
  if ($names.Count -ne 22) { throw 'Wrong approved selection' }
  $pairs=0
  $wholeDifferent=0
  $tomlDifferent=@()
  $atDifferent=@()
  $manifestDifferent=@()
  foreach ($name in $names) {
    if (-not [regex]::IsMatch($name,'^[A-Za-z0-9 _().+\-]{1,160}\.jar$',[Text.RegularExpressions.RegexOptions]::IgnoreCase)) { throw 'Unsafe approved JAR name' }
    $client=Join-Path $ClientMods $name
    $server=Join-Path $ServerMods $name
    if (-not (Test-Path -LiteralPath $server -PathType Leaf)) { continue }
    foreach ($file in @($client,$server)) {
      $item=Get-Item -LiteralPath $file -ErrorAction Stop
      if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
          $item.Length -gt 300000000) { throw 'Unsafe JAR' }
    }
    $pairs++
    if ((Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $server -Algorithm SHA256).Hash) { $wholeDifferent++ }
    if ((Hash-Entry $client 'META-INF/mods.toml') -cne (Hash-Entry $server 'META-INF/mods.toml')) { $tomlDifferent += $name }
    if ((Hash-Entry $client 'META-INF/accesstransformer.cfg') -cne (Hash-Entry $server 'META-INF/accesstransformer.cfg')) { $atDifferent += $name }
    if ((Hash-Entry $client 'META-INF/MANIFEST.MF') -cne (Hash-Entry $server 'META-INF/MANIFEST.MF')) { $manifestDifferent += $name }
  }
  Write-Output ('::notice title=Forge metadata parity::COMMON=' + $pairs + ' WHOLE_SHA_DIFFERENT=' + $wholeDifferent +
    ' MODS_TOML_DIFFERENT=' + $tomlDifferent.Count + ' ACCESS_TRANSFORMER_DIFFERENT=' + $atDifferent.Count +
    ' MANIFEST_DIFFERENT=' + $manifestDifferent.Count + '; READ_ONLY=true; HANDSHAKE_NOT_TESTED=true')
  Write-Output ('::notice title=Forge metadata differing approved names::' + $(if ($tomlDifferent.Count) { $tomlDifferent -join ',' } else { 'none' }))
  exit 0
} catch {
  Write-Output ('::notice title=Forge metadata parity::AUDIT_UNAVAILABLE TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_RAW_JAR_OUTPUT=true')
  exit 2
}
