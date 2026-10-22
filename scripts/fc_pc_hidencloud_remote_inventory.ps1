# Private read-only SFTP root inventory. Never log remote file names/paths,
# contents, SFTP stdout, private key, or account secrets. No remote writes.
$ErrorActionPreference = 'Stop'
$hostName = 'olivia.hidencloud.com'
$port = 2022
$login = 'izentric-150380.6ddc2b7d'
$expectedClient = 'AAAAC3NzaC1lZDI1NTE5AAAAILm8LdLcmC0AO9bHH5poxjEu7IS8Sa5KA7gx8kqetuGl'
# Seen twice on the PC; TOFU only, NOT independently verified with HidenCloud.
$expectedServerFingerprint = 'SHA256:8B88Xl+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4'
if (-not $env:USERPROFILE -or -not $env:RUNNER_TEMP -or
    $env:USERNAME -in @('SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE') -or
    -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') {
    Write-Output '::error title=Remote inventory::NOT_OWNER_PC_RUNNER'
    exit 2
}
$key = Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
$pub = $key + '.pub'
foreach ($file in @($key, $pub)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf) -or
        ((Get-Item -LiteralPath $file -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Output '::error title=Remote inventory::ROTATED_PC_KEY_MISSING_OR_UNSAFE'
        exit 2
    }
}
$line = (Get-Content -LiteralPath $pub -Raw -Encoding ASCII).Trim()
if ($line -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+(?: .*)?$' -or
    ($line -split ' ')[1] -ne $expectedClient) {
    Write-Output '::error title=Remote inventory::ROTATED_KEY_IDENTITY_MISMATCH'
    exit 2
}
try {
    $sftp = (Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen = (Get-Command ssh-keygen.exe -ErrorAction Stop).Source
} catch {
    Write-Output '::error title=Remote inventory::OPENSSH_CLIENT_UNAVAILABLE'
    exit 2
}
$dir = Join-Path $env:RUNNER_TEMP ('fc-remote-inventory-' + $env:GITHUB_RUN_ID)
if (Test-Path -LiteralPath $dir) {
    Write-Output '::error title=Remote inventory::TEMP_PATH_EXISTS'
    exit 2
}
$ok = $false
try {
    [void](New-Item -ItemType Directory -Path $dir -ErrorAction Stop)
    $batch = Join-Path $dir 'read-only.txt'
    $known = Join-Path $dir 'known_hosts'
    $listing = Join-Path $dir 'private-listing.txt'
    [IO.File]::WriteAllText($batch, "ls -1`nbye`n", [Text.Encoding]::ASCII)
    $args = @(
        '-q', '-b', $batch, '-P', [string]$port, '-i', $key,
        '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
        '-o', 'PreferredAuthentications=publickey', '-o', 'PasswordAuthentication=no',
        '-o', 'KbdInteractiveAuthentication=no',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', ('UserKnownHostsFile=' + $known), '-o', 'ConnectTimeout=12',
        "${login}@${hostName}"
    )
    & $sftp @args 1>$listing 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) {
        throw 'SFTP_LIST_FAILED'
    }
    $fingerprints = @(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or
        @($fingerprints | Where-Object { $_ -match [regex]::Escape($expectedServerFingerprint) }).Count -ne 1) {
        throw 'SERVER_HOST_KEY_CHANGED_FROM_PREVIOUS_TOFU'
    }
    $entries = @(Get-Content -LiteralPath $listing -ErrorAction Stop | Where-Object { $_.Trim() })
    $names = @($entries | ForEach-Object { $_.Trim() })
    # SFTP output remains private; only counts and known generic categories escape.
    $labels = @('mods', 'plugins', 'world', 'server.properties', 'libraries', 'logs', 'eula.txt')
    $flags = @($labels | ForEach-Object {
        $label = $_
        $found = @($names | Where-Object { $_ -ieq $label }).Count -gt 0
        ($label.Replace('.', '_') + '=' + $found)
    })
    Write-Output ('::notice title=HidenCloud SFTP root inventory::ROOT_ENTRIES=' + $names.Count + ' ' + ($flags -join ' ') + ' HOSTKEY_SAME_AS_PREVIOUS_TOFU=true SERVER_DATA_NOT_BACKED_UP=true READ_ONLY=true')
    $ok = $true
} catch {
    Write-Output '::error title=HidenCloud SFTP root inventory::REMOTE_READ_ONLY_INVENTORY_UNVERIFIED; READ_ONLY=true'
} finally {
    Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
}
if (-not $ok) { exit 2 }
