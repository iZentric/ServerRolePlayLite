# Read-only inventory of user-provided E:\Administrator\Desktop\FunCity.
# SHA/name/type inventory stays in private PC backup folder. Never upload JARs,
# configs or paths to GitHub. Static ZIP metadata only, no Java execution.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try {
    if (-not $env:USERPROFILE -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $root='E:\Administrator\Desktop\FunCity'
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        Write-Output '::notice title=E FunCity private JAR inventory::E_ROOT_PRESENT=false JARS_TESTED=0 NO_PC_OR_HOST_WRITES=true'
        exit 0
    }
    $origin=Get-Item -LiteralPath $root -Force -ErrorAction Stop
    if (($origin.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'E_ROOT_REPARSE' }
    $privateDir=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups'
    $private=Get-Item -LiteralPath $privateDir -Force -ErrorAction Stop
    if (($private.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'PRIVATE_DIR_REPARSE' }
    $output=Join-Path $privateDir ('e-funcity-jar-inventory-' + $env:GITHUB_RUN_ID + '.json')
    if (Test-Path -LiteralPath $output) { throw 'INVENTORY_ALREADY_EXISTS' }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $queue=[Collections.Generic.Queue[string]]::new()
    $queue.Enqueue($origin.FullName)
    $jars=[Collections.Generic.List[object]]::new()
    $counts=[ordered]@{ files=0; directories=0; skipped_links=0; jars=0; launchers=0;
        mods=0; plugins=0; dual_metadata=0; other_jars=0; invalid_zip=0; bytes=0L }
    while ($queue.Count -gt 0) {
        $directory=$queue.Dequeue()
        foreach ($item in @(Get-ChildItem -LiteralPath $directory -Force -ErrorAction Stop)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                $counts.skipped_links++
                continue
            }
            if ($item.PSIsContainer) {
                $counts.directories++
                if ($counts.directories -gt 30000) { throw 'TREE_TOO_LARGE' }
                $queue.Enqueue($item.FullName)
                continue
            }
            $counts.files++
            $counts.bytes += [long]$item.Length
            if ($counts.files -gt 200000 -or $counts.bytes -gt 200000000000L) { throw 'TREE_TOO_LARGE' }
            if ($item.Extension -ine '.jar') { continue }
            $counts.jars++
            if ($counts.jars -gt 3000 -or $item.Length -gt 1073741824L) { throw 'JAR_INVENTORY_UNSAFE_SIZE' }
            $type='OTHER'
            $zip=$null
            try {
                $zip=[IO.Compression.ZipFile]::OpenRead($item.FullName)
                $plugin=$null -ne $zip.GetEntry('plugin.yml')
                $mod=$null -ne $zip.GetEntry('META-INF/mods.toml')
                $manifest=$zip.GetEntry('META-INF/MANIFEST.MF')
                $launcher=$false
                if ($null -ne $manifest -and $manifest.Length -le 1048576L) {
                    $stream=$manifest.Open()
                    try {
                        $reader=[IO.StreamReader]::new($stream)
                        try { $content=$reader.ReadToEnd() } finally { $reader.Dispose() }
                    } finally { $stream.Dispose() }
                    $launcher=($content -match '(?im)^Main-Class\s*:')
                }
                if ($plugin -and $mod) { $type='DUAL_METADATA'; $counts.dual_metadata++ }
                elseif ($plugin) { $type='PLUGIN'; $counts.plugins++ }
                elseif ($mod) { $type='MOD'; $counts.mods++ }
                elseif ($launcher) { $type='LAUNCHER_CANDIDATE'; $counts.launchers++ }
                else { $counts.other_jars++ }
            } catch {
                $type='INVALID_ZIP'
                $counts.invalid_zip++
            } finally {
                if ($null -ne $zip) { $zip.Dispose() }
            }
            $relative=$item.FullName.Substring($origin.FullName.TrimEnd([char[]]@([char]92,[char]47)).Length).TrimStart([char[]]@([char]92,[char]47))
            if (-not $relative -or $relative.StartsWith('..') -or [IO.Path]::IsPathRooted($relative)) { throw 'UNSAFE_RELATIVE_PATH' }
            $jars.Add([pscustomobject]@{ relative_path=$relative; bytes=[long]$item.Length;
                sha256=(Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256 -ErrorAction Stop).Hash; kind=$type })
        }
    }
    $manifest=[pscustomobject]@{ source='E drive supplied by owner'; complete=$true;
        counts=[pscustomobject]$counts; jars=@($jars.ToArray()) }
    $manifest | ConvertTo-Json -Depth 6 -Compress | Set-Content -LiteralPath $output -Encoding UTF8 -ErrorAction Stop
    $readback=Get-Content -LiteralPath $output -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($readback.complete -ne $true -or @($readback.jars).Count -ne $counts.jars) { throw 'INVENTORY_READBACK_FAILED' }
    Write-Output ('::notice title=E FunCity private JAR inventory::E_ROOT_PRESENT=true STATIC_JARS_SHA_VERIFIED=' + $counts.jars +
        ' LAUNCHER_CANDIDATES=' + $counts.launchers + ' MOD_JARS=' + $counts.mods +
        ' PLUGIN_JARS=' + $counts.plugins + ' DUAL_METADATA=' + $counts.dual_metadata +
        ' OTHER_JARS=' + $counts.other_jars + ' INVALID_ZIP=' + $counts.invalid_zip +
        ' SKIPPED_LINKS=' + $counts.skipped_links + ' PRIVATE_MANIFEST_PC_ONLY=true JARS_NOT_EXECUTED=true HOST_UNCHANGED=true')
} catch {
    Write-Output '::error title=E FunCity private JAR inventory::INVENTORY_UNVERIFIED; no private filenames, hashes or content printed'
    exit 2
}
