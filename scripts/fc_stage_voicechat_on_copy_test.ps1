$ErrorActionPreference='Stop'
try { Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop } catch { }
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-voice-trial-' + [guid]::NewGuid().ToString('N'))
$project=Join-Path $root 'FunCityLocal'
$server=Join-Path $project 'server'
$profile=Join-Path (Join-Path $root 'instances') 'FunCity RP Lite'
$client=Join-Path $profile '.minecraft/mods'
$stage=Join-Path $project 'Arena-CompatStages/bootable-no-clumps-777'
try {
  foreach ($dir in @($server,$client,(Join-Path $stage 'server/mods'),(Join-Path $stage 'excluded-backup'))) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
  }
  [IO.File]::WriteAllBytes((Join-Path $server 'mods-source-placeholder.txt'),[byte[]](1))
  New-Item -ItemType Directory -Path (Join-Path $server 'mods') | Out-Null
  [IO.File]::WriteAllBytes((Join-Path $server 'mods/Clumps-6.0.0.28.jar'),[byte[]](1))
  foreach ($n in 1..33) { [IO.File]::WriteAllBytes((Join-Path $stage ('server/mods/mod' + $n + '.jar')),[byte[]]($n)) }
  [IO.File]::WriteAllBytes((Join-Path $stage 'excluded-backup/Clumps-6.0.0.28.jar'),[byte[]](1))
  @{schema=1;source_verified_offline=$true;copy_hash_verified=$true;removed_from_runnable_copy='Clumps-6.0.0.28.jar';test_server_started=$false} |
    ConvertTo-Json | Set-Content (Join-Path $stage 'private-copy-manifest.json')
  foreach ($pair in @(@('voice.jar','voicechat'),@('other.jar','othermod'))) {
    $file=Join-Path $client $pair[0]
    $zip=[IO.Compression.ZipFile]::Open($file,[IO.Compression.ZipArchiveMode]::Create)
    try {
      $entry=$zip.CreateEntry('META-INF/mods.toml')
      $writer=[IO.StreamWriter]::new($entry.Open())
      try { $writer.WriteLine('[[mods]]'); $writer.WriteLine('modId="' + $pair[1] + '"') }
      finally { $writer.Dispose() }
    } finally { $zip.Dispose() }
  }
  $result=& (Join-Path $PSScriptRoot 'fc_stage_voicechat_on_copy.ps1') -Profile $profile -Server $server -CopyRunId '777' -Synthetic
  if ($LASTEXITCODE -ne 0 -or -not ($result -match 'VOICECHAT_FROM_LITE=true') -or
      @(Get-ChildItem (Join-Path $stage 'server/mods') -Filter '*.jar').Count -ne 34 -or
      -not (Test-Path (Join-Path $stage 'server/mods/voice.jar')) -or
      @(Get-ChildItem (Join-Path $server 'mods') -Filter '*.jar').Count -ne 1) { throw 'Voicechat stage fixture failed' }
  Write-Output 'PASS: voicechat added only to private no-Clumps copy, original and Lite unchanged'
} finally {
  Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
