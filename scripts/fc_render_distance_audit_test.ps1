$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-render-audit-' + [guid]::NewGuid().ToString('N'))
$profile=Join-Path (Join-Path $root 'instances') 'FunCity RP Lite'
$server=Join-Path (Join-Path $root 'FunCityLocal') 'server'
try {
  New-Item -ItemType Directory -Path (Join-Path $profile '.minecraft') -Force | Out-Null
  New-Item -ItemType Directory -Path $server -Force | Out-Null
  "view-distance=6`nsecret=PRIVATE_TOKEN" | Set-Content (Join-Path $server 'server.properties')
  "renderDistance:9`ngraphicsMode:1`nparticles:2`nmipmapLevels:4`nentityShadows:true`nusername:SECRET_NAME" | Set-Content (Join-Path $profile '.minecraft/options.txt')
  $result=& (Join-Path $PSScriptRoot 'fc_render_distance_audit.ps1') -Profile $profile -Server $server
  if ($LASTEXITCODE -ne 0 -or @($result | Where-Object {
    $_ -match 'SERVER_VIEW_DISTANCE=6' -and $_ -match 'CLIENT_RENDER_DISTANCE=9' -and $_ -match 'FPS_NOT_MEASURED=true'
  }).Count -ne 1 -or $result -match 'PRIVATE_TOKEN|SECRET_NAME|fc-render-audit') {
    throw 'Synthetic render audit failed or leaked private values'
  }
  Write-Output 'PASS: read-only graphics audit reports bounded values, not usernames or private paths'
} finally {
  Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
