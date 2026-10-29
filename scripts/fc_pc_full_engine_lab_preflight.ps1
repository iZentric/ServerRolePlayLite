# Read-only gate for a full-content A/B on a THROWAWAY PC copy, not the live PC/host.
# Do not copy/boot the real world until network isolation and resources are proven.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
try {
    if (-not $env:USERPROFILE -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $backup=Join-Path $env:USERPROFILE 'Desktop\FunCityLocal\Arena-Private-Backups\offline-39843776626'
    $root=Join-Path $backup 'server'
    $manifestFile=Join-Path $backup 'private-manifest.json'
    foreach ($path in @($backup,$root,$manifestFile,(Join-Path $root 'mods'),(Join-Path $root 'plugins'),(Join-Path $root 'world'))) {
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_SOURCE' }
    }
    $manifest=Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
    if ($manifest.consistent_offline_snapshot -ne $true -or $manifest.independent_restore_copy_verified -ne $true -or
        [int]$manifest.files -ne 3994 -or [long]$manifest.bytes -ne 852735002L) { throw 'OFFLINE_BACKUP_CHANGED' }
    $mods=@(Get-ChildItem -LiteralPath (Join-Path $root 'mods') -File -Force -Filter '*.jar' -ErrorAction Stop)
    $plugins=@(Get-ChildItem -LiteralPath (Join-Path $root 'plugins') -File -Force -Filter '*.jar' -ErrorAction Stop)
    if ($mods.Count -ne 34 -or $plugins.Count -ne 13) { throw 'CONTENT_INVENTORY_CHANGED' }
    if (@(Get-ChildItem -LiteralPath (Join-Path $root 'world') -Force -ErrorAction Stop).Count -eq 0) {
        throw 'WORLD_MISSING'
    }
    $engine=Join-Path $root 'FunCityEngine.jar'
    $property=$manifest.sha256.PSObject.Properties['FunCityEngine.jar']
    if ($null -eq $property -or (Get-FileHash -LiteralPath $engine -Algorithm SHA256).Hash -cne $property.Value) {
        throw 'WORKING_ENGINE_SHA_CHANGED'
    }
    # Hash only the actual 47 private JARs against the original offline manifest.
    foreach ($item in @($mods)+@($plugins)) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_JAR' }
        $group=if ($item.Directory.Name -eq 'mods') { 'mods' } else { 'plugins' }
        $forward=$group+'/'+$item.Name
        $backward=$group+'\'+$item.Name
        $expected=$manifest.sha256.PSObject.Properties[$forward]
        if ($null -eq $expected) { $expected=$manifest.sha256.PSObject.Properties[$backward] }
        if ($null -eq $expected -or (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash -cne $expected.Value) {
            throw 'CONTENT_JAR_SHA_CHANGED'
        }
    }
    $os=Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $freeRam=[long]$os.FreePhysicalMemory * 1024L
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($env:RUNNER_TEMP))
    $spaceOkay=($drive.IsReady -and $drive.AvailableFreeSpace -ge (2L*[long]$manifest.bytes+4294967296L))
    $memoryOkay=($freeRam -ge 4294967296L)
    $dockerPresent=($null -ne (Get-Command docker.exe -ErrorAction SilentlyContinue))
    # An installed CLI is not proof of a working network-isolated VM/container.
    Write-Output ('::notice title=Full RP engine A/B feasibility::BACKUP_VERIFIED=true MOD_JARS_SHA_VERIFIED=' + $mods.Count +
        ' PLUGIN_JARS_SHA_VERIFIED=' + $plugins.Count + ' REAL_WORLD_PRESENT=true' +
        ' FREE_DISK_FOR_TWO_THROWAWAY_COPIES=' + $spaceOkay +
        ' FREE_RAM_FOR_ISOLATED_LAB=' + $memoryOkay + ' DOCKER_CLI_PRESENT=' + $dockerPresent +
        ' SAFE_NETWORK_ISOLATION_NOT_VERIFIED=true NO_WORLD_BOOT=true PC_AND_HOST_LIVE_UNTOUCHED=true')
} catch {
    Write-Output '::error title=Full RP engine A/B feasibility::PREFLIGHT_FAILED; no private paths/data printed; no live changes'
    exit 2
}
