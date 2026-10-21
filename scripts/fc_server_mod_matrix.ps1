# Read-only exact-name comparison. Never opens any JAR, world, config or account.
param(
    [Parameter(Mandatory=$true)][string]$Server,
    [string]$Manifest = (Join-Path (Split-Path $PSScriptRoot -Parent) 'agent/FUNCITY-SERVER-TARGET-28.json')
)
$ErrorActionPreference='Stop'
function Is-PlainDirectory([string]$p) {
    if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw 'EXPECTED_DIRECTORY_MISSING' }
    $entry=Get-Item -LiteralPath $p -Force
    if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_POINT_REJECTED' }
}
try {
    Is-PlainDirectory $Server
    $mods=Join-Path $Server 'mods'
    $plugins=Join-Path $Server 'plugins'
    Is-PlainDirectory $mods
    Is-PlainDirectory $plugins
    $plan=Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $target=@($plan.mods)
    $archive=@($plan.historical_names)
    $uniqueTarget=@($target | Sort-Object -Unique)
    if ($plan.schema -ne 1 -or $plan.status -ne 'PROPOSED_CLIENT_ALIGNED_SERVER_TEST_ONLY_NOT_LIVE' -or
        $target.Count -ne 28 -or $archive.Count -ne 36 -or
        $plan.explicitly_excluded_from_historical_29 -in $target -or
        $uniqueTarget.Count -ne 28) {
        throw 'MANIFEST_INVENTORY_CHANGED'
    }
    $modFiles=@(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar' -ErrorAction Stop)
    $pluginFiles=@(Get-ChildItem -LiteralPath $plugins -File -Filter '*.jar' -ErrorAction Stop)
    $modReparse=@($modFiles | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 })
    $pluginReparse=@($pluginFiles | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 })
    if ($modReparse.Count -gt 0 -or $pluginReparse.Count -gt 0) {
        throw 'REPARSE_POINT_JAR_REJECTED'
    }
    $actual=@($modFiles | ForEach-Object Name)
    $missing=@($target | Where-Object { $_ -notin $actual })
    $extras=@($actual | Where-Object { $_ -notin $target })
    $known=@($actual | Where-Object { $_ -in $archive })
    $road='RoadRunner-mc1.16.5-1.5.2.jar' -in $actual
    $perfMatches=@($actual | Where-Object { $_ -like 'performant-*.jar' })
    $perf=$perfMatches.Count -gt 0
    if ($road -and $perf) { throw 'INCOMPATIBLE_OPTIMIZERS_PRESENT' }
    $voice='voicechat-forge-1.16.5-2.3.23.jar' -in $actual
    Write-Output ('::notice title=PC server mod inventory READ ONLY::SERVER_JARS=' + $actual.Count +
        ' PLUGIN_JARS=' + $pluginFiles.Count + ' TARGET_28_PRESENT=' + ($target.Count - $missing.Count) +
        ' TARGET_28_MISSING=' + $missing.Count + ' EXTRA_TO_TARGET=' + $extras.Count +
        ' ARCHIVED_36_NAME_OVERLAP=' + $known.Count + ' ROADRUNNER=' + $road +
        ' PERFORMANT=' + $perf + ' VOICE=' + $voice + ' CLIENT_OR_WORLD_TEST=NO')
    exit 0
} catch {
    Write-Output '::error title=PC server mod inventory rejected::READ_ONLY_PRECHECK_FAILED; no private paths or names uploaded'
    exit 2
}
