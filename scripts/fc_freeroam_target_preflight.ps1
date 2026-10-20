# Read-only Freeroam PC gate. No profile write, world access, account access or raw paths in output.
param([Parameter(Mandatory=$true)][string]$Profile, [switch]$Quiet, [switch]$SyntheticDiagnostics)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
  if ((Split-Path -Path $Profile -Leaf) -cne 'Freeroam 1.0.0') { throw 'Wrong profile' }
  $base = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
  $declared = @((Get-Content -LiteralPath (Join-Path $base 'agent/FREEROAM-LISTA-DECLARATA.json') -Raw | ConvertFrom-Json).jar_names)
  $selection = Get-Content -LiteralPath (Join-Path $base 'agent/FUNCITY-RP-LITE-SELECTIE.json') -Raw | ConvertFrom-Json
  $removed = @($selection.removed_from_future_target)
  $kept = @($selection.retained_in_future_target)
  $approved = @(
    'CTM-MC1.16.1-1.1.2.6.jar',
    'DynamicSurroundings-1.16.5-4.0.5.0.jar',
    'InGameAccountSwitcher-Forge-1.16-8.0.1.jar',
    'lightfallclient-1.0.0.jar',
    'notenoughanimations-1.2.4.jar',
    'TRansliterationLib-1.0.4.jar'
  )
  $declaredSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
  $approvedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
  $removedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
  $keptSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
  foreach ($name in $declared) { if (-not $declaredSet.Add([string]$name)) { throw 'Duplicate declaration' } }
  foreach ($name in $approved) { if (-not $approvedSet.Add($name)) { throw 'Duplicate approved name' } }
  foreach ($name in $removed) { if (-not $removedSet.Add([string]$name)) { throw 'Duplicate exclusion' } }
  foreach ($name in $kept) { if (-not $keptSet.Add([string]$name)) { throw 'Duplicate kept name' } }
  if ($declared.Count -ne 28 -or $approved.Count -ne 6 -or
      $removed.Count -ne 6 -or $kept.Count -ne 22 -or
      -not $removedSet.SetEquals($approvedSet) -or
      -not $declaredSet.IsSupersetOf($keptSet) -or
      -not $declaredSet.IsSupersetOf($approvedSet) -or
      $selection.ready_for_release -ne $false) { throw 'Manifest mismatch' }
  foreach ($name in $declaredSet) {
    if ($removedSet.Contains($name) -eq $keptSet.Contains($name)) { throw 'Incomplete selection' }
  }
  $profileItem = Get-Item -LiteralPath $Profile -ErrorAction Stop
  if (-not $profileItem.PSIsContainer -or ($profileItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe profile' }
  $choices = @()
  foreach ($folder in @('.minecraft', 'minecraft')) {
    $path = Join-Path $Profile $folder
    if (Test-Path -LiteralPath $path) { $choices += $path }
  }
  if ($choices.Count -ne 1) { throw 'Minecraft folder missing or ambiguous' }
  $game = [IO.DirectoryInfo]::new([string]($choices[0]))
  $mods = [IO.DirectoryInfo]::new((Join-Path $game.FullName 'mods'))
  if (-not $game.Exists -or -not $mods.Exists -or
      ($game.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      ($mods.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe mods folder' }
  $jars = @(Get-ChildItem -LiteralPath $mods.FullName -Force | Where-Object { $_.Name -match '\.jar$' })
  if ($jars.Count -gt 128) { throw 'Unexpected count' }
  $diskNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
  $diskFolded = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
  foreach ($jar in $jars) {
    if ($jar.PSIsContainer -or ($jar.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $jar.Length -gt 300000000 -or
        -not [regex]::IsMatch($jar.Name, '^[A-Za-z0-9 _().+\-]{1,160}\.jar$', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase) -or
        -not $diskFolded.Add($jar.Name) -or -not $diskNames.Add($jar.Name)) { throw 'Unsafe JAR' }
    # Compute locally for readability/integrity, but no reference hashes exist yet.
    $null = Get-FileHash -LiteralPath $jar.FullName -Algorithm SHA256
  }
  $missing = @($declaredSet | Where-Object { -not $diskNames.Contains($_) })
  $extra = @($diskNames | Where-Object { -not $declaredSet.Contains($_) })
  if ($missing.Count -gt 0 -or $extra.Count -gt 0) {
    if (-not $Quiet) { Write-Output ('::error title=Freeroam PC gate::INVENTORY_MISMATCH original=' + $diskNames.Count + ' missing=' + $missing.Count + ' unexpected=' + $extra.Count + '; READ_ONLY=true INSTALLATION=false') }
    exit 1
  }
  if (-not $Quiet) { Write-Output ('::notice title=Freeroam PC gate::INVENTORY_MATCH original=' + $diskNames.Count + ' target_declared=22; READ_ONLY=true INSTALLATION=false') }
  exit 0
} catch {
  # Only synthetic hosted fixtures may publish type and script line; never PC paths or exception text.
  if ($Quiet -and $SyntheticDiagnostics) {
    Write-Output ('::error title=Freeroam synthetic gate::LINE=' + $_.InvocationInfo.ScriptLineNumber + ' TYPE=' + $_.Exception.GetType().Name)
  }
  if (-not $Quiet) { Write-Output '::error title=Freeroam PC gate::PROFILE_UNSAFE_OR_UNREADABLE; READ_ONLY=true INSTALLATION=false' }
  exit 2
}
