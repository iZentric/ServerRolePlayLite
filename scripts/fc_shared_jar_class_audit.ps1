# Compare class bytecode of same-named client/server JARs without uploading binaries.
# A resource-only SHA difference is not automatically a Forge incompatibility.
param([Parameter(Mandatory=$true)][string]$ClientMods,
      [Parameter(Mandatory=$true)][string]$ServerMods,
      [string]$Manifest = '',
      [switch]$SyntheticDiagnostics)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
function Class-Fingerprint([string]$JarPath) {
  $archive = [IO.Compression.ZipFile]::OpenRead($JarPath)
  $sha = [Security.Cryptography.SHA256]::Create()
  try {
    $classes = [System.Collections.Generic.SortedDictionary[string,string]]::new([StringComparer]::Ordinal)
    if ($archive.Entries.Count -gt 60000) { throw 'Too many archive entries' }
    foreach ($entry in $archive.Entries) {
      if (-not $entry.FullName.EndsWith('.class',[StringComparison]::Ordinal)) { continue }
      if ($entry.Length -gt 50000000 -or $classes.ContainsKey($entry.FullName)) { throw 'Unsafe archive entry' }
      $stream = $entry.Open()
      try { $digest = [Convert]::ToBase64String($sha.ComputeHash($stream)) }
      finally { $stream.Dispose() }
      $classes.Add($entry.FullName,$digest)
    }
    return $classes
  } finally { $archive.Dispose(); $sha.Dispose() }
}
try {
  foreach ($dir in @($ClientMods,$ServerMods)) {
    $entry = [IO.DirectoryInfo]::new($dir)
    if (-not $entry.Exists -or ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe mods directory' }
  }
  if ($Manifest) {
    $names = @((Get-Content -LiteralPath $Manifest -Raw -ErrorAction Stop | ConvertFrom-Json).retained_in_future_target)
  } else {
    $names = @(Get-ChildItem -LiteralPath $ClientMods -File -Filter '*.jar' | ForEach-Object { $_.Name })
  }
  if ($names.Count -gt 80) { throw 'Too many JARs' }
  $common = 0
  $different = 0
  $codeDifferent = @()
  $resourceOnly = @()
  foreach ($name in $names) {
    if (-not [regex]::IsMatch($name,'^[A-Za-z0-9 _().+\-]{1,160}\.jar$',[Text.RegularExpressions.RegexOptions]::IgnoreCase)) { throw 'Unsafe JAR name' }
    $client = Join-Path $ClientMods $name
    $server = Join-Path $ServerMods $name
    if (-not (Test-Path -LiteralPath $server -PathType Leaf)) { continue }
    foreach ($file in @($client,$server)) {
      $entry = Get-Item -LiteralPath $file -ErrorAction Stop
      if ($entry.PSIsContainer -or ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $entry.Length -gt 300000000) { throw 'Unsafe JAR' }
    }
    $common++
    if ((Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash -eq
        (Get-FileHash -LiteralPath $server -Algorithm SHA256).Hash) { continue }
    $different++
    $a = Class-Fingerprint $client
    $b = Class-Fingerprint $server
    $same = ($a.Count -eq $b.Count)
    if ($same) {
      foreach ($key in $a.Keys) {
        if (-not $b.ContainsKey($key) -or $a[$key] -cne $b[$key]) { $same = $false; break }
      }
    }
    if ($same) { $resourceOnly += $name } else { $codeDifferent += $name }
  }
  Write-Output ('::notice title=Forge class-level audit::COMMON_FILENAME_JARS=' + $common + ' WHOLE_JAR_SHA_DIFF=' + $different + ' CLASS_DIFF=' + $codeDifferent.Count + ' SAME_CLASSES_OTHER_BYTES_DIFF=' + $resourceOnly.Count + '; READ_ONLY=true; NOT_A_JOIN_TEST=true')
  Write-Output ('::notice title=Forge class-different approved names::' + $(if ($codeDifferent.Count) { $codeDifferent -join ',' } else { 'none' }))
  exit 0
} catch {
  if ($SyntheticDiagnostics -and [Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    Write-Output ('::error title=Forge synthetic class audit::LINE=' + $_.InvocationInfo.ScriptLineNumber + ' TYPE=' + $_.Exception.GetType().Name)
  }
  Write-Output '::notice title=Forge class-level audit::AUDIT_UNAVAILABLE; READ_ONLY=true'
  exit 2
}
