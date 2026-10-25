$ErrorActionPreference = 'Stop'
$Runtime = Join-Path $PSScriptRoot 'runtime'
$Jar = Join-Path $Runtime 'paper.jar'
$Eula = Join-Path $Runtime 'eula.txt'

if (-not (Test-Path -LiteralPath $Jar -PathType Leaf)) {
    throw "Missing $Jar. Run: py `"$PSScriptRoot\download_paper.py`""
}
if (-not (Test-Path -LiteralPath $Eula -PathType Leaf) -or -not (Select-String -LiteralPath $Eula -Pattern '^eula\s*=\s*true\s*$' -Quiet)) {
    throw "EULA not accepted. Read $Eula and set eula=true only if you agree."
}
$Java = Get-Command java -ErrorAction SilentlyContinue
if (-not $Java) {
    throw 'Java 25 is required for Paper 26.2; install it and put java on PATH.'
}
$JavaVersion = (& java -version 2>&1 | Select-Object -First 1) -join ''
$VersionMatch = [regex]::Match($JavaVersion, 'version "([^"]+)"')
$JavaMajorText = if ($VersionMatch.Success) { ($VersionMatch.Groups[1].Value -split '[.+-]')[0] } else { '' }
$JavaMajor = 0
if (-not [int]::TryParse($JavaMajorText, [ref]$JavaMajor) -or $JavaMajor -lt 25) {
    throw "Paper 26.2 requires Java 25 or newer. Detected: $JavaVersion"
}

$TotalBytes = [double](Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$TotalGiB = [math]::Floor($TotalBytes / 1GB)
if ($env:PAPER_HEAP_GB) {
    $HeapGiB = [int]$env:PAPER_HEAP_GB
} else {
    $HeapGiB = [int]($TotalGiB - 2)
}
if ($HeapGiB -lt 1) {
    throw "Detected $TotalGiB GiB RAM; total RAM minus 2 GiB leaves no usable heap. Set PAPER_HEAP_GB only if you understand the host memory limit."
}
Write-Host "Paper heap: $HeapGiB GiB (detected RAM: $TotalGiB GiB; reserve target: 2 GiB)"

$JvmArgs = @(
    "-Xms${HeapGiB}G", "-Xmx${HeapGiB}G",
    '-XX:+UseG1GC',
    '-XX:+ParallelRefProcEnabled',
    '-XX:MaxGCPauseMillis=200',
    '-XX:+UnlockExperimentalVMOptions',
    '-XX:+DisableExplicitGC',
    '-XX:+AlwaysPreTouch',
    '-XX:G1NewSizePercent=30',
    '-XX:G1MaxNewSizePercent=40',
    '-XX:G1HeapRegionSize=8M',
    '-XX:G1ReservePercent=20',
    '-XX:G1HeapWastePercent=5',
    '-XX:G1MixedGCCountTarget=4',
    '-XX:InitiatingHeapOccupancyPercent=15',
    '-XX:G1MixedGCLiveThresholdPercent=90',
    '-XX:G1RSetUpdatingPauseTimePercent=5',
    '-XX:SurvivorRatio=32',
    '-XX:+PerfDisableSharedMem',
    '-XX:MaxTenuringThreshold=1'
)

Push-Location $Runtime
try {
    while ($true) {
        & java @JvmArgs -jar $Jar '--nogui'
        $ExitCode = $LASTEXITCODE
        if ($ExitCode -eq 0) { break }
        Write-Warning "Paper exited with status $ExitCode; auto-restarting in 15 seconds. Press Ctrl+C to cancel."
        Start-Sleep -Seconds 15
    }
} finally {
    Pop-Location
}
