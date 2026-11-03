# Read-only SFTP authentication probe from the owner's Windows runner.
# The rotated private key stays on that PC. Never print it, server file names,
# remote paths, or the SFTP client's output. No server writes or shell commands.
$ErrorActionPreference = 'Stop'
$server = 'olivia.hidencloud.com'
$port = 2022
$login = 'izentric-150380.6ddc2b7d'
$expectedPublic = 'AAAAC3NzaC1lZDI1NTE5AAAAILm8LdLcmC0AO9bHH5poxjEu7IS8Sa5KA7gx8kqetuGl'

if (-not $env:RUNNER_TEMP -or -not $env:USERPROFILE -or
    $env:USERNAME -in @('SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE')) {
    Write-Output '::error title=HidenCloud SFTP::NOT_OWNER_PC_RUNNER'
    exit 2
}
$key = Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
$public = $key + '.pub'
foreach ($path in @($key, $public)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Write-Output '::error title=HidenCloud SFTP::ROTATED_KEY_NOT_ON_THIS_PC_ACCOUNT'
        exit 2
    }
    if (((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Output '::error title=HidenCloud SFTP::KEY_PATH_IS_REPARSE_POINT'
        exit 2
    }
}
$publicLine = (Get-Content -LiteralPath $public -Raw -Encoding ASCII).Trim()
if ($publicLine -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+(?: .*)?$' -or
    ($publicLine -split ' ')[1] -ne $expectedPublic) {
    Write-Output '::error title=HidenCloud SFTP::ROTATED_KEY_IDENTITY_MISMATCH'
    exit 2
}

try { $sftp = (Get-Command 'sftp.exe' -ErrorAction Stop).Source }
catch {
    Write-Output '::error title=HidenCloud SFTP::SFTP_CLIENT_NOT_INSTALLED_ON_PC'
    exit 2
}
$tcp = [Net.Sockets.TcpClient]::new()
try {
    $connection = $tcp.ConnectAsync($server, $port)
    if (-not $connection.Wait(12000) -or -not $tcp.Connected) {
        Write-Output '::error title=HidenCloud SFTP::TCP_CONNECT_TIMEOUT_OR_REFUSED'
        exit 2
    }
    Write-Output 'TCP_PORT_REACHABLE'
} catch {
    Write-Output '::error title=HidenCloud SFTP::TCP_CONNECT_FAILED'
    exit 2
} finally {
    $tcp.Dispose()
}

# Isolated first-use host key (TOFU): not independently authenticated by provider.
# Do not pollute the owner's known_hosts. Record only its public fingerprint.
$probeDir = Join-Path $env:RUNNER_TEMP ('funcity-sftp-probe-' + $env:GITHUB_RUN_ID)
if (Test-Path -LiteralPath $probeDir) {
    Write-Output '::error title=HidenCloud SFTP::TEMP_PATH_ALREADY_EXISTS'
    exit 2
}
$result = 'SFTP_AUTH_OR_PROTOCOL_FAILED'
try {
    [void](New-Item -ItemType Directory -Path $probeDir -ErrorAction Stop)
    $knownHosts = Join-Path $probeDir 'known_hosts'
    $batch = Join-Path $probeDir 'read-only-batch.txt'
    [IO.File]::WriteAllText($batch, "pwd`nbye`n", [Text.Encoding]::ASCII)
    $arguments = @(
        '-q', '-b', $batch, '-P', [string]$port, '-i', $key,
        '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
        '-o', 'PreferredAuthentications=publickey',
        '-o', 'PasswordAuthentication=no', '-o', 'KbdInteractiveAuthentication=no',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', ('UserKnownHostsFile=' + $knownHosts),
        '-o', 'ConnectTimeout=12',
        "${login}@${server}"
    )
    & $sftp @arguments 1>$null 2>$null
    $sftpExit = $LASTEXITCODE
    if (Test-Path -LiteralPath $knownHosts) {
        $keygen = (Get-Command 'ssh-keygen.exe' -ErrorAction SilentlyContinue).Source
        if ($keygen) {
            $fingerprints = & $keygen -lf $knownHosts 2>$null
            foreach ($line in @($fingerprints)) {
                if ($line -match 'SHA256:[A-Za-z0-9+/=]+') {
                    Write-Output ('::notice title=HidenCloud server host key fingerprint (TOFU)::' + $Matches[0] + '; verify independently with provider before relying on it')
                    break
                }
            }
        }
    }
    if ($sftpExit -eq 0) { $result = 'SFTP_READ_ONLY_AUTH_OK' }
} catch {
    $result = 'SFTP_CLIENT_PROBE_ERROR'
} finally {
    Remove-Item -LiteralPath $probeDir -Recurse -Force -ErrorAction SilentlyContinue
}
if ($result -ne 'SFTP_READ_ONLY_AUTH_OK') {
    Write-Output ('::error title=HidenCloud SFTP::' + $result + '; no remote files modified')
    exit 2
}
Write-Output '::notice title=HidenCloud SFTP::SFTP_READ_ONLY_AUTH_OK; no remote files modified; server host key not independently verified'
