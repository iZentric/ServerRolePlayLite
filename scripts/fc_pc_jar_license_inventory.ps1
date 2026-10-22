# Read-only metadata inventory of exact server target and installed plugins.
# JAR names, contents, configs, logs, worlds and accounts are never uploaded.
$ErrorActionPreference = 'Stop'
function PlainDir([string]$p) {
    if (-not (Test-Path -LiteralPath $p -PathType Container)) { return $false }
    $item=Get-Item -LiteralPath $p -Force
    return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0)
}
function Metadata($jar) {
    $result=@{ label='UNDECLARED'; licenseFile=$false; metadata=$false }
    $zip=[IO.Compression.ZipFile]::OpenRead($jar.FullName)
    try {
        foreach ($entry in $zip.Entries) {
            if ($entry.FullName -match '^(?i)(LICENSE|LICENCE|COPYING|NOTICE)(\.[^/]*)?$' -or
                $entry.FullName -match '^(?i)META-INF/(LICENSE|LICENCE|COPYING|NOTICE)(\.[^/]*)?$') {
                $result.licenseFile=$true
            }
            if ($entry.FullName -ieq 'META-INF/mods.toml' -and $entry.Length -le 131072) {
                $result.metadata=$true
                $reader=[IO.StreamReader]::new($entry.Open())
                try {
                    $text=$reader.ReadToEnd()
                    if ($text -match '(?m)^\s*license\s*=\s*["'']([^"''\r\n]+)["'']') {
                        $result.label=($matches[1] -replace '[^A-Za-z0-9 ._+()/:-]','_').Substring(0,[Math]::Min(90,$matches[1].Length))
                    }
                } finally { $reader.Dispose() }
            }
        }
    } finally { $zip.Dispose() }
    return $result
}
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $target=Get-Content -LiteralPath 'agent/FUNCITY-SERVER-TARGET-28.json' -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($target.schema -ne 1 -or @($target.mods).Count -ne 28) { throw 'TARGET_DRIFT' }
    $server='C:\Users\Administrator\Desktop\FunCityLocal\server'
    $modsDir=Join-Path $server 'mods'; $pluginsDir=Join-Path $server 'plugins'
    if (-not (PlainDir $modsDir) -or -not (PlainDir $pluginsDir)) { throw 'SERVER_MISSING' }
    $mods=@(Get-ChildItem -LiteralPath $modsDir -File -Filter '*.jar' -ErrorAction Stop)
    $plugins=@(Get-ChildItem -LiteralPath $pluginsDir -File -Filter '*.jar' -ErrorAction Stop)
    if ($mods.Count -ne 34 -or $plugins.Count -ne 13) { throw 'SERVER_INVENTORY_DRIFT' }
    $byName=@{}
    foreach ($file in $mods) {
        if ($file.Length -le 0 -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'INVALID_MOD_ENTRY' }
        if ($byName.ContainsKey($file.Name)) { throw 'DUPLICATE_NAME' }
        $byName[$file.Name]=$file
    }
    $labels=@{}; $licenseFileCount=0; $missing=@()
    foreach ($name in @($target.mods)) {
        if (-not $byName.ContainsKey($name)) { throw 'TARGET_FILE_NOT_ON_PC' }
        $info=Metadata $byName[$name]
        if (-not $labels.ContainsKey($info.label)) { $labels[$info.label]=0 }
        $labels[$info.label]++
        if ($info.licenseFile) { $licenseFileCount++ }
        if ($info.label -eq 'UNDECLARED') { $missing += ($name -replace '[^A-Za-z0-9 ._()+-]','_') }
    }
    $pluginLicenseFiles=0; $pluginMetadata=0
    foreach ($file in $plugins) {
        if ($file.Length -le 0 -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'INVALID_PLUGIN_ENTRY' }
        $info=Metadata $file
        if ($info.licenseFile) { $pluginLicenseFiles++ }
        if ($info.metadata) { $pluginMetadata++ }
    }
    $classes=@($labels.GetEnumerator() | Sort-Object Key | ForEach-Object { $_.Key + ':' + $_.Value }) -join '|'
    Write-Output ('::notice title=Server target JAR license metadata read only::target_mods=28 classes=' + $classes + ' license_file_in_jar=' + $licenseFileCount + '/28; metadata_is_NOT_redistribution_permission=true')
    Write-Output ('::notice title=Installed plugin JAR license metadata read only::plugins=13 license_file_in_jar=' + $pluginLicenseFiles + '/13 forge_metadata=' + $pluginMetadata + '/13; no_plugin_names_or_bytes_published=true')
    if ($missing.Count -gt 0) { Write-Output ('::notice title=Target JARs without Forge license field::' + ($missing -join ' | ')) }
    Write-Output 'PASS: metadata inventory complete, no file copied, no release or live change'
    exit 0
} catch {
    Write-Output '::error title=License metadata inventory::FAILED_OR_UNVERIFIED; no private filenames or JARs published'
    exit 2
}
