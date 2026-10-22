# Compare installed client and server JAR bytes read-only. No account/config/world access.
$ErrorActionPreference = 'Stop'
function PlainDir([string]$path) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) { return $false }
    $item = Get-Item -LiteralPath $path -Force
    return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0)
}
function Jars([string]$path) {
    if (-not (PlainDir $path)) { return @() }
    $files = @(Get-ChildItem -LiteralPath $path -File -Filter '*.jar' -ErrorAction Stop)
    if (@($files | Where-Object { $_.Length -le 0 -or ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count -gt 0) {
        throw 'INVALID_JAR_ENTRY'
    }
    return $files
}
function Mods([string]$profile) {
    $mc = Join-Path $profile '.minecraft'
    if (-not (PlainDir $mc)) { $mc = Join-Path $profile 'minecraft' }
    return @(Jars (Join-Path $mc 'mods'))
}
function MapFiles($files) {
    $map = @{}
    foreach ($file in $files) {
        if ($map.ContainsKey($file.Name)) { throw 'DUPLICATE_CASE_INSENSITIVE_NAME' }
        $map[$file.Name] = $file
    }
    return $map
}
function ExactNames($map, $expected) {
    if ($map.Count -ne $expected.Count) { return $false }
    foreach ($name in $expected) { if (-not $map.ContainsKey($name)) { return $false } }
    return $true
}
try {
    $original = Get-Content -LiteralPath 'agent/FREEROAM-LISTA-DECLARATA.json' -Encoding UTF8 -Raw | ConvertFrom-Json
    $lite = Get-Content -LiteralPath 'agent/FUNCITY-RP-LITE-SELECTIE.json' -Encoding UTF8 -Raw | ConvertFrom-Json
    $target = Get-Content -LiteralPath 'agent/FUNCITY-SERVER-TARGET-28.json' -Encoding UTF8 -Raw | ConvertFrom-Json
    if (@($original.jar_names).Count -ne 28 -or @($lite.retained_in_future_target).Count -ne 22 -or @($target.mods).Count -ne 28 -or $lite.ready_for_release) { throw 'MANIFEST_DRIFT' }

    $roots = @('C:\Users\Administrator\AppData\Roaming\PrismLauncher')
    if ($env:APPDATA) { $roots += Join-Path $env:APPDATA 'PrismLauncher' }
    $profiles = @()
    foreach ($root in @($roots | Select-Object -Unique)) {
        foreach ($section in @('instances', 'Arena-Archived-Instances')) {
            $p = Join-Path $root $section
            if (-not (PlainDir $p)) { continue }
            foreach ($dir in @(Get-ChildItem -LiteralPath $p -Directory -ErrorAction Stop | Select-Object -First 80)) {
                if (($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
                $profiles += $dir.FullName
                if ($section -eq 'Arena-Archived-Instances') {
                    $profiles += @(Get-ChildItem -LiteralPath $dir.FullName -Directory -ErrorAction Stop |
                        Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0 } |
                        Select-Object -First 80 | ForEach-Object { $_.FullName })
                }
            }
        }
    }
    $profiles = @($profiles | Select-Object -Unique)
    $originalCandidates = @($profiles | Where-Object { (Split-Path $_ -Leaf) -eq 'Freeroam 1.0.0' })
    $clientCandidates = @($profiles | Where-Object { (Split-Path $_ -Leaf) -in @('FunCity RP Lite','FunCity-Lite-LowSpec-LAB-1.16.5') })
    $chosenOriginal = $null; $originalMap = $null
    foreach ($profile in $originalCandidates) {
        $files = @(Mods $profile)
        $map = MapFiles $files
        if (ExactNames $map @($original.jar_names)) { $chosenOriginal=$profile; $originalMap=$map; break }
    }
    if (-not $chosenOriginal) { throw 'ORIGINAL_28_NOT_EXACT' }
    $chosenLite = $null; $liteMap = $null; $category = 'NONE'
    foreach ($label in @('FunCity RP Lite','FunCity-Lite-LowSpec-LAB-1.16.5')) {
        foreach ($profile in $clientCandidates) {
            if ((Split-Path $profile -Leaf) -ne $label) { continue }
            $map = MapFiles @(Mods $profile)
            if (ExactNames $map @($lite.retained_in_future_target)) {
                $chosenLite=$profile; $liteMap=$map
                if ($label -eq 'FunCity RP Lite') { $category='LITE_PROFILE' } else { $category='LAB_PROFILE' }
                break
            }
        }
        if ($chosenLite) { break }
    }
    if (-not $chosenLite) { throw 'LITE_22_NOT_EXACT' }

    $same = 0; $different = 0
    foreach ($name in @($lite.retained_in_future_target)) {
        if (-not $originalMap.ContainsKey($name)) { throw 'SELECTED_NOT_IN_ORIGINAL' }
        $a = (Get-FileHash -LiteralPath $originalMap[$name].FullName -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath $liteMap[$name].FullName -Algorithm SHA256).Hash
        if ($a -eq $b) { $same++ } else { $different++ }
    }
    Write-Output ('::notice title=Original versus Lite bytes read only::original=28 lite=22 same_sha256=' + $same + ' changed_sha256=' + $different + ' lite_source=' + $category + ' profiles_modified=0 JARs_uploaded=0')

    $server = 'C:\Users\Administrator\Desktop\FunCityLocal\server'
    if (-not (PlainDir $server)) { throw 'SERVER_DIRECTORY_MISSING' }
    $serverMods = MapFiles @(Jars (Join-Path $server 'mods'))
    $plugins = MapFiles @(Jars (Join-Path $server 'plugins'))
    if ($serverMods.Count -ne 34 -or $plugins.Count -ne 13) { throw 'SERVER_34_13_DRIFT' }
    $targetCount = 0
    foreach ($name in @($target.mods)) { if ($serverMods.ContainsKey($name)) { $targetCount++ } }
    $serverClientMatching = 0; $serverClientDifferent = 0
    $differentNames = @()
    foreach ($name in @($lite.retained_in_future_target)) {
        if ($serverMods.ContainsKey($name)) {
            $a = (Get-FileHash -LiteralPath $serverMods[$name].FullName -Algorithm SHA256).Hash
            $b = (Get-FileHash -LiteralPath $liteMap[$name].FullName -Algorithm SHA256).Hash
            if ($a -eq $b) { $serverClientMatching++ } else {
                $serverClientDifferent++
                # Only names already present in the published 22-name manifest.
                $differentNames += ($name -replace '[^A-Za-z0-9 ._()+-]', '_')
            }
        }
    }
    Write-Output ('::notice title=Installed server inventory read only::mods=34 plugins=13 lab_target_name_overlap=' + $targetCount + '/28 shared_client_same_sha256=' + $serverClientMatching + ' shared_client_different_sha256=' + $serverClientDifferent + ' world_opened=0 files_copied=0 process_changed=0')
    if ($differentNames.Count -gt 0) {
        Write-Output ('::notice title=Shared client-server JARs with different SHA256::' + ($differentNames -join ' | '))
    }
    if ($env:GITHUB_STEP_SUMMARY) {
        @(
            '## Read-only PC parity (not a gameplay or release test)',
            "- Freeroam 28 vs Lite 22: $same matching SHA-256, $different different; source: $category.",
            "- Server: $($serverMods.Count) mod JARs / $($plugins.Count) plugin JARs; lab target name overlap $targetCount/28.",
            "- Shared server/client JARs: $serverClientMatching same SHA-256, $serverClientDifferent different.",
            '- No world, private config, account, mod binary, process or profile changed/uploaded.'
        ) | Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY -Encoding UTF8
    }
    if ($different -gt 0 -or $category -ne 'LITE_PROFILE') { throw 'CLIENT_PARITY_OR_RELEASE_PROFILE_UNVERIFIED' }
    Write-Output 'PASS: read-only file-byte parity; no boot, login or player capacity tested'
    exit 0
} catch {
    Write-Output '::error title=PC release parity gate::FAILED_OR_UNVERIFIED; see sanitized counts above; no private paths, JARs or logs published'
    exit 2
}
