# Read-only Forge JAR metadata comparison. Never opens worlds, account data or logs.
# Reports sanitized mod IDs, not paths, filenames, user data or raw TOML contents.
param([Parameter(Mandatory=$true)][string]$ClientMods,
      [Parameter(Mandatory=$true)][string]$ServerMods,
      [switch]$SyntheticDiagnostics,
      [switch]$DiagnosticTypeOnly)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
function Inspect-Mods([string]$Folder) {
  $dir = [IO.DirectoryInfo]::new($Folder)
  if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe folder' }
  # Non-JAR notes/subfolders in server/mods are unrelated to the Forge mod list.
  $jars = @(Get-ChildItem -LiteralPath $Folder -File -Filter '*.jar' -Force -ErrorAction Stop)
  if ($jars.Count -gt 80) { throw 'Too many files' }
  $ids = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  $unknown = 0
  $clumpsFile = $null
  foreach ($jar in $jars) {
    if ($jar.PSIsContainer -or ($jar.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $jar.Length -gt 300000000 -or $jar.Extension -ine '.jar') { throw 'Unsafe JAR' }
    $zip = [IO.Compression.ZipFile]::OpenRead($jar.FullName)
    try {
      $entry = $zip.GetEntry('META-INF/mods.toml')
      if ($null -eq $entry -or $entry.Length -gt 1048576) { $unknown++; continue }
      $reader = [IO.StreamReader]::new($entry.Open(),[Text.Encoding]::UTF8)
      try { $toml = $reader.ReadToEnd() } finally { $reader.Dispose() }
      $sections = [regex]::Matches($toml, '(?ms)^\s*\[\[mods\]\]\s*(.*?)(?=^\s*\[\[|\z)')
      $found = $false
      foreach ($section in $sections) {
        $id = [regex]::Match($section.Groups[1].Value, '(?m)^\s*modId\s*=\s*["'']([A-Za-z0-9_.-]{2,80})["'']')
        if ($id.Success) {
          $null = $ids.Add($id.Groups[1].Value.ToLowerInvariant())
          $found = $true
          if ($id.Groups[1].Value -ieq 'clumps') {
            if ($clumpsFile -or $jar.Name -notmatch '^[A-Za-z0-9 _.()+-]{1,160}\.jar$') { throw 'Ambiguous Clumps file' }
            $clumpsFile = $jar.Name
          }
        }
      }
      if (-not $found) { $unknown++ }
    } finally { $zip.Dispose() }
  }
  return @{ ids=$ids; jars=$jars.Count; unknown=$unknown; clumpsFile=$clumpsFile }
}
try {
  $client = Inspect-Mods $ClientMods
  $server = Inspect-Mods $ServerMods
  $onlyServer = @($server.ids | Where-Object { -not $client.ids.Contains($_) } | Sort-Object)
  $onlyClient = @($client.ids | Where-Object { -not $server.ids.Contains($_) } | Sort-Object)
  $common = @($client.ids | Where-Object { $server.ids.Contains($_) })
  # Mod IDs are public identifiers; never mistake set difference for required dependencies.
  $serverText = if ($onlyServer.Count) { $onlyServer -join ',' } else { 'none' }
  $clientText = if ($onlyClient.Count) { $onlyClient -join ',' } else { 'none' }
  Write-Output ('::notice title=Forge metadata mismatch candidates::CLIENT_JARS=' + $client.jars + ' SERVER_JARS=' + $server.jars + ' COMMON_IDS=' + $common.Count + ' SERVER_ONLY_IDS=' + $onlyServer.Count + ' CLIENT_ONLY_IDS=' + $onlyClient.Count + ' CLIENT_UNREADABLE_JARS=' + $client.unknown + ' SERVER_UNREADABLE_JARS=' + $server.unknown + ' CLUMPS_SERVER_JAR=' + $server.clumpsFile + ' CLUMPS_CLIENT_PRESENT=' + [bool]$client.clumpsFile + '; READ_ONLY=true; NOT_A_HANDSHAKE_PROOF=true')
  Write-Output ('::notice title=Forge server-only mod IDs::' + $serverText)
  Write-Output ('::notice title=Forge client-only mod IDs::' + $clientText)
  exit 0
} catch {
  # An exception can carry private paths or JAR metadata; never print it on a PC runner.
  if ($DiagnosticTypeOnly -or ($SyntheticDiagnostics -and [Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT)) {
    Write-Output ('::notice title=Forge parser diagnostics::LINE=' + $_.InvocationInfo.ScriptLineNumber + ' TYPE=' + $_.Exception.GetType().Name)
  }
  Write-Output '::notice title=Forge metadata mismatch candidates::AUDIT_UNAVAILABLE; READ_ONLY=true'
  exit 2
}
