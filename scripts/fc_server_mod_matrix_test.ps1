$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-matrix-fixture-'+[guid]::NewGuid().ToString('N'))
try {
    $srv=Join-Path $root 'test-server'
    $mods=Join-Path $srv 'mods'
    $plugins=Join-Path $srv 'plugins'
    $null=New-Item -ItemType Directory -Path $mods,$plugins -Force
    $source=Get-Content -LiteralPath (Join-Path $PSScriptRoot '../agent/DECIZII.md') -Raw -Encoding UTF8
    $section=$source.Split(@('## Server —'),[StringSplitOptions]::None)[1].Split(@('## Pluginurile'),[StringSplitOptions]::None)[0]
    $rows=@([regex]::Matches($section, '(?m)^\| S\d\d \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS(?: din runtime normal)?) \|'))
    foreach ($m in $rows) {
        if ($m.Groups[2].Value -eq 'PĂSTRAT') {
            [IO.File]::WriteAllBytes((Join-Path $mods $m.Groups[1].Value),[byte[]]@(0))
        }
    }
    [IO.File]::WriteAllBytes((Join-Path $plugins 'Fake-plugin.jar'),[byte[]]@(0))
    $run=@(& (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 0 -or $run.Count -ne 1 -or $run[0] -notmatch 'TARGET_29_MISSING=0 EXTRA_TO_TARGET=0') {
        throw 'matched inventory not identified'
    }
    [IO.File]::WriteAllBytes((Join-Path $mods 'extra-test.jar'),[byte[]]@(0))
    $run=@(& (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 0 -or $run[0] -notmatch 'EXTRA_TO_TARGET=1') { throw 'extra mod not detected' }
    [IO.File]::WriteAllBytes((Join-Path $mods 'performant-fake.jar'),[byte[]]@(0))
    $run=@(& (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 2 -or $run[0] -notmatch 'READ_ONLY_PRECHECK_FAILED') {
        throw 'incompatible server optimizers not rejected'
    }
    Write-Output 'PASS: exact 29, extra mod and incompatible optimizers all classified without reading JARs'
} finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
