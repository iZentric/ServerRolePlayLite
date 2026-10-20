# Hosted fixture only: 22->23 on isolated new Prism profile, original+server intact.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID) { throw 'CI fixture only' }
$root = Join-Path $env:RUNNER_TEMP ('fc-clumps-fixture-' + $env:GITHUB_RUN_ID)
$instances = Join-Path $root 'PrismLauncher/instances'
$original = Join-Path $instances 'Freeroam 1.0.0/.minecraft/mods'
$profile = Join-Path $instances 'FunCity RP Lite'
$lite = Join-Path $profile '.minecraft/mods'
$server = Join-Path $root 'FunCityLocal/server'
$serverMods = Join-Path $server 'mods'
if (Test-Path -LiteralPath $root) { throw 'Fixture exists' }
try {
  foreach ($dir in @($original,$lite,$serverMods)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  $declared = Get-Content -LiteralPath agent/FREEROAM-LISTA-DECLARATA.json -Raw | ConvertFrom-Json
  $selection = Get-Content -LiteralPath agent/FUNCITY-RP-LITE-SELECTIE.json -Raw | ConvertFrom-Json
  foreach ($name in $declared.jar_names) { [IO.File]::WriteAllText((Join-Path $original $name),('original:' + $name)) }
  foreach ($name in $selection.retained_in_future_target) {
    Copy-Item -LiteralPath (Join-Path $original $name) -Destination (Join-Path $lite $name)
  }
  $clumps = Join-Path $serverMods 'Clumps-6.0.0.28.jar'
  try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
  $zip = [IO.Compression.ZipFile]::Open($clumps,[IO.Compression.ZipArchiveMode]::Create)
  try {
    $entry = $zip.CreateEntry('META-INF/mods.toml')
    $writer = [IO.StreamWriter]::new($entry.Open())
    try { $writer.Write("[[mods]]`nmodId=`"clumps`"`n") } finally { $writer.Dispose() }
  } finally { $zip.Dispose() }
  $sourceHash = (Get-FileHash -LiteralPath $clumps -Algorithm SHA256).Hash
  & ./scripts/fc_lite_add_clumps.ps1 -Profile $profile -Server $server
  if ($LASTEXITCODE -ne 0) { throw 'Clumps fixture apply failed' }
  if (@(Get-ChildItem -LiteralPath $original -Filter '*.jar').Count -ne 28 -or
      @(Get-ChildItem -LiteralPath $lite -Filter '*.jar').Count -ne 23 -or
      (Get-FileHash -LiteralPath (Join-Path $lite 'Clumps-6.0.0.28.jar') -Algorithm SHA256).Hash -ne $sourceHash -or
      (Get-FileHash -LiteralPath $clumps -Algorithm SHA256).Hash -ne $sourceHash) { throw 'Fixture inventory or hash mismatch' }
  foreach ($name in $selection.retained_in_future_target) {
    if ((Get-FileHash -LiteralPath (Join-Path $lite $name) -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath (Join-Path $original $name) -Algorithm SHA256).Hash) { throw 'Original mod changed' }
  }
  Write-Output 'PASS: fixture isolated Lite 22->23 with Clumps, original 28 and server intact'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
