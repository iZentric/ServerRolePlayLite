$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-matrix-fixture-'+[guid]::NewGuid().ToString('N'))
try {
    $srv=Join-Path $root 'test-server'
    $mods=Join-Path $srv 'mods'
    $plugins=Join-Path $srv 'plugins'
    $null=New-Item -ItemType Directory -Path $mods,$plugins -Force
    $plan=Get-Content -LiteralPath (Join-Path $PSScriptRoot '../agent/FUNCITY-SERVER-TARGET-28.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($name in @($plan.mods)) {
        [IO.File]::WriteAllBytes((Join-Path $mods $name),[byte[]]@(0))
    }
    [IO.File]::WriteAllBytes((Join-Path $plugins 'Fake-plugin.jar'),[byte[]]@(0))
    $run=@(& pwsh -NoProfile -File (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 0 -or $run.Count -ne 1 -or $run[0] -notmatch 'TARGET_28_MISSING=0 EXTRA_TO_TARGET=0') {
        throw 'matched inventory not identified'
    }
    [IO.File]::WriteAllBytes((Join-Path $mods 'extra-test.jar'),[byte[]]@(0))
    $run=@(& pwsh -NoProfile -File (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 0 -or $run[0] -notmatch 'EXTRA_TO_TARGET=1') { throw 'extra mod not detected' }
    [IO.File]::WriteAllBytes((Join-Path $mods 'performant-fake.jar'),[byte[]]@(0))
    $run=@(& pwsh -NoProfile -File (Join-Path $PSScriptRoot 'fc_server_mod_matrix.ps1') -Server $srv)
    if ($LASTEXITCODE -ne 2 -or $run[0] -notmatch 'READ_ONLY_PRECHECK_FAILED') {
        throw 'incompatible server optimizers not rejected'
    }
    Write-Output 'PASS: exact 28, extra mod and incompatible optimizers all classified without reading JARs'
} catch {
    Write-Output ('::error title=Synthetic mod matrix failed::' + $_.Exception.GetType().Name + ': ' + $_.Exception.Message)
    throw
} finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
