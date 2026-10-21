# Add the exact Lite voicechat Forge JAR only to the private no-Clumps server copy.
# Original server, Prism and verified backup are read-only; no server is started.
param([Parameter(Mandatory=$true)][string]$Profile,
      [Parameter(Mandatory=$true)][string]$Server,
      [Parameter(Mandatory=$true)][ValidatePattern('^\d+$')][string]$CopyRunId,
      [switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
$phase='VALIDATE'
$destination=$null
$copied=$false
$finished=$false
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances' -or
      (Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Wrong profile/server' }
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous game folder' }
  $clientMods=Join-Path (Join-Path $Profile $games[0]) 'mods'
  $stage=Join-Path (Join-Path (Split-Path -Parent $Server) 'Arena-CompatStages') ('bootable-no-clumps-' + $CopyRunId)
  $copyServer=Join-Path $stage 'server'
  $copyMods=Join-Path $copyServer 'mods'
  foreach ($dir in @($clientMods,$stage,$copyServer,$copyMods)) {
    $item=[IO.DirectoryInfo]::new($dir)
    if (-not $item.Exists -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe folder' }
  }
  $manifest=Get-Content -LiteralPath (Join-Path $stage 'private-copy-manifest.json') -Raw -ErrorAction Stop | ConvertFrom-Json
  if ($manifest.schema -ne 1 -or $manifest.source_verified_offline -ne $true -or
      $manifest.copy_hash_verified -ne $true -or $manifest.removed_from_runnable_copy -cne 'Clumps-6.0.0.28.jar' -or
      $manifest.test_server_started -ne $false) { throw 'Unverified copy' }
  $stageMods=@(Get-ChildItem -LiteralPath $copyMods -File -Filter '*.jar' -Force -ErrorAction Stop)
  if ($stageMods.Count -ne 33 -or (Test-Path -LiteralPath (Join-Path $copyMods 'Clumps-6.0.0.28.jar'))) {
    throw 'Stage mod inventory changed'
  }
  if (Test-Path -LiteralPath (Join-Path $stage 'private-voicechat-trial.json')) { throw 'Already staged' }
  $stageProcs = @()
  if (-not $Synthetic) {
    $stageProcs=@(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
      $_.CommandLine -and $_.CommandLine.IndexOf($copyServer,[StringComparison]::OrdinalIgnoreCase) -ge 0
    })
  }
  if ($stageProcs.Count -ne 0) { throw 'Test server running' }
  $phase='FIND_EXACT_MOD'
  $clientJars=@(Get-ChildItem -LiteralPath $clientMods -File -Filter '*.jar' -Force -ErrorAction Stop)
  $expected=if ($Synthetic) { 2 } else { 22 }
  if ($clientJars.Count -ne $expected) { throw 'Client inventory changed' }
  $candidates=@()
  foreach ($jar in $clientJars) {
    if (($jar.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $jar.Length -gt 300000000 -or
        -not [regex]::IsMatch($jar.Name,'^[A-Za-z0-9 _().+\-]{1,160}\.jar$',[Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
      throw 'Unsafe client jar'
    }
    $zip=[IO.Compression.ZipFile]::OpenRead($jar.FullName)
    try {
      $entry=$zip.GetEntry('META-INF/mods.toml')
      if (-not $entry -or $entry.Length -gt 1048576) { continue }
      $reader=[IO.StreamReader]::new($entry.Open(),[Text.Encoding]::UTF8)
      try { $toml=$reader.ReadToEnd() } finally { $reader.Dispose() }
      if ($toml -match '(?m)^\s*modId\s*=\s*["'']voicechat["'']') { $candidates += $jar }
    } finally { $zip.Dispose() }
  }
  if ($candidates.Count -ne 1) { throw 'Voicechat Forge mod not unique' }
  $source=$candidates[0]
  $destination=Join-Path $copyMods $source.Name
  if (Test-Path -LiteralPath $destination) { throw 'Destination exists' }
  if (@(Get-ChildItem -LiteralPath (Join-Path $Server 'mods') -File -Filter '*.jar' -ErrorAction Stop | Where-Object { $_.Name -ceq $source.Name }).Count -ne 0) {
    throw 'Voicechat already on original server'
  }
  $phase='COPY_VERIFY'
  $sha=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256 -ErrorAction Stop).Hash
  Copy-Item -LiteralPath $source.FullName -Destination $destination -ErrorAction Stop
  $copied=$true
  if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256 -ErrorAction Stop).Hash -ne $sha -or
      (Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256 -ErrorAction Stop).Hash -ne $sha -or
      @(Get-ChildItem -LiteralPath $copyMods -File -Filter '*.jar' -Force).Count -ne 34) { throw 'Copy verification failed' }
  $phase='FINALIZE'
  @{ schema=1; base_copy=$CopyRunId; client_voicechat_sha256=$sha;
     voicechat_added_to_private_copy=$true; clumps_removed_from_private_copy=$true;
     live_server_unchanged=$true; client_unchanged=$true; boot_tested=$false; join_tested=$false } |
     ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $stage 'private-voicechat-trial.json') -Encoding UTF8 -ErrorAction Stop
  $finished=$true
  Write-Output '::notice title=Private Forge candidate::NO_CLUMPS=true VOICECHAT_FROM_LITE=true COPY_MODS=34 SHA_VERIFIED=true ORIGINAL_SERVER_UNCHANGED=true LITE_UNCHANGED=true SERVER_NOT_STARTED=true JOIN_NOT_TESTED=true'
  exit 0
} catch {
  Write-Output ('::error title=Private Forge candidate::STAGE_BLOCKED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; ORIGINAL_SERVER_UNCHANGED=true')
  exit 2
} finally {
  if ($copied -and -not $finished -and $destination -and (Test-Path -LiteralPath $destination)) {
    Remove-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
  }
}
