# Synthetic local fixtures only; never connects to HidenCloud.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'fc_pc_restart_readiness_lib.ps1')
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-restart-fixture-' + [guid]::NewGuid().ToString('N'))
$scriptListed=$true
function Assert-FcState {
    param([bool]$Expected, [string]$Case)
    $actual=Get-FcRestartReadiness -Root $root -StartScriptListed $scriptListed
    if ($actual.StaticPreconditionsMet -ne $Expected) {
        throw ('UNEXPECTED_STATIC_STATUS_' + $Case)
    }
    if ($actual.PSObject.Properties.Name -contains 'RestartWorks') {
        throw 'UNSAFE_RESTART_SUCCESS_CLAIM'
    }
}
try {
    if (Test-FcRootEntryListed -Names @(' start.sh','start.sh ') -Expected 'start.sh') {
        throw 'TRIMMED_REMOTE_NAME_FALSE_POSITIVE'
    }
    if (-not (Test-FcRootEntryListed -Names @('start.sh') -Expected 'start.sh')) {
        throw 'EXACT_REMOTE_NAME_REJECTED'
    }
    [void](New-Item -ItemType Directory -Path $root -ErrorAction Stop)
    Set-Content -LiteralPath (Join-Path $root 'server.properties') -Value 'enable-rcon=false' -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: ./start.sh', 'world-settings:', '  default: {}') -Encoding UTF8
    Assert-FcState $true 'basic'

    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  timeout-time: 60') -Encoding UTF8
    $default=Get-FcRestartReadiness -Root $root -StartScriptListed $true
    if (-not $default.RestartScriptDefaulted -or -not $default.StaticPreconditionsMet) { throw 'DEFAULT_NOT_RECOGNIZED' }
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: "./start.sh"') -Encoding UTF8
    Assert-FcState $true 'quoted'
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '    restart-script: /other.sh') -Encoding UTF8
    Assert-FcState $false 'unexpected-indent-path'
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: ../start.sh') -Encoding UTF8
    Assert-FcState $false 'path-escape'
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: ./start.sh', '  restart-script: ./start.sh') -Encoding UTF8
    Assert-FcState $false 'duplicate-restart-key'
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: ./start.sh', 'settings:', '  restart-script: ./start.sh') -Encoding UTF8
    Assert-FcState $false 'duplicate-settings'
    Set-Content -LiteralPath (Join-Path $root 'spigot.yml') -Value @('settings:', '  restart-script: ./start.sh') -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $root 'server.properties') -Value @('enable-rcon=false','enable-rcon=true') -Encoding UTF8
    Assert-FcState $false 'duplicate-rcon'
    Set-Content -LiteralPath (Join-Path $root 'server.properties') -Value 'enable-rcon=true' -Encoding UTF8
    Assert-FcState $false 'rcon-enabled'
    Set-Content -LiteralPath (Join-Path $root 'server.properties') -Value 'enable-rcon=false # not a Java properties comment' -Encoding UTF8
    Assert-FcState $false 'invalid-inline-comment'
    Set-Content -LiteralPath (Join-Path $root 'server.properties') -Value 'enable-rcon=false' -Encoding UTF8
    $scriptListed=$false
    Assert-FcState $false 'missing-script-from-listing'
    $scriptListed=$true
    Remove-Item -LiteralPath (Join-Path $root 'spigot.yml') -Force
    Assert-FcState $false 'missing-spigot'
    Write-Output 'FC_RESTART_STATIC_FIXTURES_PASS'
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
