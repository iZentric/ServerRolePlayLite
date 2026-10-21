# Read-only exact-name comparison. Never opens any JAR, world, config or account.
param(
    [Parameter(Mandatory=$true)][string]$Server,
    [string]$Decisions = (Join-Path (Split-Path $PSScriptRoot -Parent) 'agent/DECIZII.md')
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
    $text=Get-Content -LiteralPath $Decisions -Raw -Encoding UTF8
    $section=$text.Split(@('## Server —'),[StringSplitOptions]::None)
    if ($section.Count -ne 2) { throw 'SERVER_MANIFEST_NOT_UNIQUE' }
    $table=$section[1].Split(@('## Pluginurile'),[StringSplitOptions]::None)[0]
    $rows=@([regex]::Matches($table, '(?m)^\| S\d\d \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS(?: din runtime normal)?) \|'))
    $historicalTarget=@($rows | Where-Object { $_.Groups[2].Value -eq 'PĂSTRAT' } | ForEach-Object { $_.Groups[1].Value })
    # Historical 29 includes Clumps; current Lite/client and server excluded it.
    $target=@($historicalTarget | Where-Object { $_ -ne 'Clumps-6.0.0.28.jar' })
    $archive=@($rows | ForEach-Object { $_.Groups[1].Value })
    if ($archive.Count -ne 36 -or $historicalTarget.Count -ne 29 -or $target.Count -ne 28 -or @($archive | Sort-Object -Unique).Count -ne 36) {
        throw 'MANIFEST_INVENTORY_CHANGED'
    }
    $modFiles=@(Get-ChildItem -LiteralPath $mods -File -Filter '*.jar' -ErrorAction Stop)
    $pluginFiles=@(Get-ChildItem -LiteralPath $plugins -File -Filter '*.jar' -ErrorAction Stop)
    if (@($modFiles | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count -gt 0 -or
        @($pluginFiles | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count -gt 0) {
        throw 'REPARSE_POINT_JAR_REJECTED'
    }
    $actual=@($modFiles | ForEach-Object Name)
    $missing=@($target | Where-Object { $_ -notin $actual })
    $extras=@($actual | Where-Object { $_ -notin $target })
    $known=@($actual | Where-Object { $_ -in $archive })
    $road='RoadRunner-mc1.16.5-1.5.2.jar' -in $actual
    $perf=@($actual | Where-Object { $_ -like 'performant-*.jar' }).Count -gt 0
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
