$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-lite-lowfps-' + [guid]::NewGuid().ToString('N'))
$profile=Join-Path (Join-Path $root 'PrismLauncher/instances') 'FunCity RP Lite'
try {
  New-Item -ItemType Directory -Path (Join-Path $profile '.minecraft') -Force | Out-Null
  $options=Join-Path $profile '.minecraft/options.txt'
  $original="renderDistance:12`ngraphicsMode:1`nparticles:0`nmipmapLevels:4`nentityShadows:true`nusername:PRIVATE_ACCOUNT`n"
  [IO.File]::WriteAllText($options,$original,[Text.UTF8Encoding]::new($false))
  $env:GITHUB_RUN_ID='985731'
  $result=& (Join-Path $PSScriptRoot 'fc_lite_lowfps_options.ps1') -Profile $profile -Synthetic
  if ($LASTEXITCODE -ne 0 -or -not ($result -match 'CLIENT_RENDER=5 GRAPHICS=FAST')) { throw 'Synthetic options update failed' }
  $after=[IO.File]::ReadAllText($options)
  foreach ($line in @('renderDistance:5','graphicsMode:0','particles:1','mipmapLevels:0','entityShadows:false','username:PRIVATE_ACCOUNT')) {
    if (-not $after.Contains($line)) { throw 'Missing expected value/private value altered' }
  }
  $backup=Join-Path $root 'PrismLauncher/Arena-Private-Settings-Backups/lite-lowfps-985731/original-options.txt'
  if (-not (Test-Path -LiteralPath $backup) -or [IO.File]::ReadAllText($backup) -cne $original -or
      $result -match 'PRIVATE_ACCOUNT|fc-lite-lowfps') { throw 'Private backup or redaction failed' }
  Write-Output 'PASS: exact low-end options only, private backup/restore rehearsal, no account output'
} finally {
  Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
