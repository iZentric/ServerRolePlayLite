# Create a dedicated SSH client identity on the owner's PC (self-hosted runner).
# Output ONLY the public key. The private key is never uploaded or logged.
$ErrorActionPreference = 'Stop'
$created = $false
try {
    if (-not $env:USERPROFILE -or -not $env:RUNNER_TEMP) { throw 'NOT_A_PC_RUNNER' }
    if ($env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE') -or
        $env:USERPROFILE -match '^(?i:C:\\Windows\\)') { throw 'RUNNER_IS_SERVICE_ACCOUNT' }
    $keygen = (Get-Command 'ssh-keygen.exe' -ErrorAction Stop).Source
    $dir = Join-Path $env:USERPROFILE '.ssh'
    if (Test-Path -LiteralPath $dir) {
        $item = Get-Item -LiteralPath $dir -Force
        if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'SSH_DIRECTORY_NOT_PLAIN'
        }
    } else {
        [void](New-Item -ItemType Directory -Path $dir -ErrorAction Stop)
    }
    # Do not overwrite or reuse the earlier identity exposed in chat.
    # Generate a fresh, distinct local identity; reruns validate this same pair.
    $private = Join-Path $dir 'funcity_hidencloud_ed25519_rotated'
    $public = $private + '.pub'
    $hasPrivate = Test-Path -LiteralPath $private
    $hasPublic = Test-Path -LiteralPath $public
    if ($hasPrivate -ne $hasPublic) { throw 'PARTIAL_KEY_PAIR_REFUSE_OVERWRITE' }
    if (-not $hasPrivate) {
        # Validate native empty-passphrase quoting on this exact PowerShell/SSH build,
        # without exposing a persistent credential if ssh-keygen fails.
        $probe = Join-Path $env:RUNNER_TEMP ('fc-ssh-quote-test-' + $env:GITHUB_RUN_ID)
        if ((Test-Path -LiteralPath $probe) -or (Test-Path -LiteralPath ($probe + '.pub'))) {
            throw 'PROBE_PATH_ALREADY_EXISTS'
        }
        try {
            & $keygen -q -t ed25519 -a 100 -f $probe -N '""' -C 'fc-ssh-probe' 2>$null
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath ($probe + '.pub'))) {
                throw 'SSH_KEYGEN_PROBE_FAILED'
            }
            # A valid unencrypted probe must be usable non-interactively.
            & $keygen -y -P '""' -f $probe 1>$null 2>$null
            if ($LASTEXITCODE -ne 0) { throw 'SSH_KEYGEN_EMPTY_PASSPHRASE_FAILED' }
        } finally {
            Remove-Item -LiteralPath $probe, ($probe + '.pub') -Force -ErrorAction SilentlyContinue
        }
        $created = $true
        & $keygen -q -t ed25519 -a 100 -f $private -N '""' -C 'funcity-hidencloud-2026-10-22' 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'SSH_KEYGEN_FAILED' }
    }
    foreach ($file in @($private, $public)) {
        $item = Get-Item -LiteralPath $file -Force -ErrorAction Stop
        if (-not $item.PSIsContainer -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) { continue }
        throw 'KEY_FILE_NOT_PLAIN'
    }
    # Only the Windows identity executing the runner can read the private key.
    $principal = (whoami.exe).Trim()
    & icacls.exe $private '/inheritance:r' '/grant:r' ("${principal}:(F)") 1>$null
    if ($LASTEXITCODE -ne 0) { throw 'PRIVATE_KEY_ACL_FAILED' }
    $publicLine = (Get-Content -LiteralPath $public -Raw -Encoding ASCII).Trim()
    if ($publicLine -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+ funcity-hidencloud-2026-10-22$') {
        throw 'PUBLIC_KEY_INVALID'
    }
    # The original PC identity was exposed in chat. Never report it as usable;
    # keep it on disk for deliberate owner-controlled revocation and rotation.
    $exposedPublicKey = 'AAAAC3NzaC1lZDI1NTE5AAAAIM25Ri3sNCuYzBIPpErBs3rwDSdDM3BWn5qUcgQRMfJy'
    if (($publicLine -split ' ')[1] -eq $exposedPublicKey) {
        Write-Output '::error title=SSH key generation::EXPOSED_KEY_ROTATION_REQUIRED; old PC key NOT usable'
        exit 2
    }
    $derived = (& $keygen -y -P '""' -f $private 2>$null)
    if ($LASTEXITCODE -ne 0 -or ($derived -split ' ')[1] -ne ($publicLine -split ' ')[1]) {
        throw 'PRIVATE_PUBLIC_MISMATCH'
    }
    Write-Output ('::notice title=HidenCloud SSH public key ONLY::' + $publicLine)
    Write-Output 'PASS: keypair restricted on PC; private key NOT printed, uploaded, or committed'
    exit 0
} catch {
    if ($created) {
        Remove-Item -LiteralPath $private, $public -Force -ErrorAction SilentlyContinue
    }
    Write-Output '::error title=SSH key generation::FAILED; do not add a public key to HidenCloud until verified'
    exit 2
}
