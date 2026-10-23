# Static private triage of all launchers in the owner's E-drive inventory.
# Do not execute or copy any JAR to GitHub or change active PC/host servers.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try {
    if (-not $env:USERPROFILE -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'NOT_PC_RUNNER' }
    $backup=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups'
    $inventory=Join-Path $backup 'e-funcity-jar-inventory-39988539852.json'
    $root='E:\Administrator\Desktop\FunCity'
    if (-not (Test-Path -LiteralPath $inventory -PathType Leaf) -or
        -not (Test-Path -LiteralPath $root -PathType Container)) { throw 'INVENTORY_OR_E_ROOT_MISSING' }
    foreach ($path in @($inventory,$root)) {
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_SOURCE' }
    }
    $data=Get-Content -LiteralPath $inventory -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($data.complete -ne $true -or [int]$data.counts.jars -ne 1830 -or
        @($data.jars).Count -ne 1830) { throw 'INVENTORY_CHANGED' }
    $launchers=@($data.jars | Where-Object { $_.kind -eq 'LAUNCHER_CANDIDATE' })
    if ($launchers.Count -ne 115) { throw 'LAUNCHER_INVENTORY_CHANGED' }
    $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $counts=[ordered]@{ all_launchers=$launchers.Count; duplicate_sha=0; unique_launcher_sha=0;
        catserver=0; mohist=0; arclight=0; magma=0; mist=0; forge=0;
        bukkit_paper=0; vanilla=0; other=0; missing_main=0 }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    foreach ($record in $launchers) {
        if ($record.relative_path -match '^\s*$|(^|[\\/])\.\.?([\\/]|$)' -or
            [IO.Path]::IsPathRooted([string]$record.relative_path)) { throw 'UNSAFE_PRIVATE_RELATIVE_PATH' }
        $path=Join-Path $root ([string]$record.relative_path)
        $file=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256 -ErrorAction Stop).Hash -cne $record.sha256) {
            throw 'LAUNCHER_SHA_CHANGED'
        }
        if (-not $seen.Add([string]$record.sha256)) { $counts.duplicate_sha++; continue }
        $counts.unique_launcher_sha++
        $zip=[IO.Compression.ZipFile]::OpenRead($path)
        try {
            $entry=$zip.GetEntry('META-INF/MANIFEST.MF')
            if ($null -eq $entry -or $entry.Length -gt 1048576L) { $counts.missing_main++; continue }
            $stream=$entry.Open()
            try {
                $reader=[IO.StreamReader]::new($stream)
                try { $text=$reader.ReadToEnd() } finally { $reader.Dispose() }
            } finally { $stream.Dispose() }
            $main=''
            foreach ($line in $text -split "`r?`n") {
                if ($line -match '^Main-Class:\s*(\S+)') { $main=$Matches[1]; break }
            }
            if (-not $main) { $counts.missing_main++; continue }
            switch -Regex ($main) {
                '(?i)catserver' { $counts.catserver++; break }
                '(?i)mohist' { $counts.mohist++; break }
                '(?i)arclight' { $counts.arclight++; break }
                '(?i)magma' { $counts.magma++; break }
                '(?i)mist' { $counts.mist++; break }
                '(?i)forge' { $counts.forge++; break }
                '(?i)paper|bukkit|spigot' { $counts.bukkit_paper++; break }
                '(?i)minecraft\.server' { $counts.vanilla++; break }
                default { $counts.other++; break }
            }
        } finally { $zip.Dispose() }
    }
    $working=Join-Path $backup 'offline-39843776626\server\FunCityEngine.jar'
    $workingHash=(Get-FileHash -LiteralPath $working -Algorithm SHA256 -ErrorAction Stop).Hash
    $currentFound=($seen.Contains($workingHash))
    $officialFound=($seen.Contains('8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0'))
    if ($counts.unique_launcher_sha + $counts.duplicate_sha -ne $counts.all_launchers) { throw 'COUNT_INCONSISTENT' }
    Write-Output ('::notice title=E FunCity server launcher triage::LAUNCHERS=' + $counts.all_launchers +
        ' DISTINCT_SHA=' + $counts.unique_launcher_sha + ' DUPLICATES=' + $counts.duplicate_sha +
        ' CATSERVER=' + $counts.catserver + ' MOHIST=' + $counts.mohist +
        ' ARCLIGHT=' + $counts.arclight + ' MAGMA=' + $counts.magma + ' MIST=' + $counts.mist +
        ' FORGE=' + $counts.forge + ' BUKKIT_PAPER=' + $counts.bukkit_paper +
        ' VANILLA=' + $counts.vanilla + ' OTHER=' + $counts.other +
        ' MISSING_MAIN=' + $counts.missing_main + ' WORKING_PC_ENGINE_PRESENT=' + $currentFound +
        ' OFFICIAL_CATSERVER_PRESENT=' + $officialFound +
        ' JARS_NOT_EXECUTED=true PRIVATE_PATHS_NOT_LOGGED=true HOST_UNCHANGED=true')
} catch {
    Write-Output '::error title=E FunCity server launcher triage::CHECK_FAILED; no private names/paths or JARs published'
    exit 2
}
