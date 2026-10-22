# Transfer the existing PC-only SSH identity into a GitHub Actions repository
# secret IF the PC already has authorized GitHub CLI access. Never echo the key.
$ErrorActionPreference = 'Stop'
$repo = 'iZentric/ServerRolePlayLite'
$name = 'FUNCITY_HIDENCLOUD_SSH_KEY'
try {
    $gh = Get-Command 'gh.exe' -ErrorAction SilentlyContinue
    if (-not $gh) {
        Write-Output '::notice title=HidenCloud GitHub secret::NOT_STORED_GH_CLI_NOT_INSTALLED_ON_PC'
        exit 0
    }
    $env:GH_PROMPT_DISABLED = '1'
    try {
        & $gh.Source api ("repos/$repo/actions/secrets/public-key") --jq '.key_id' 1>$null 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Output '::notice title=HidenCloud GitHub secret::NOT_STORED_PC_GH_AUTH_LACKS_SECRETS_ACCESS'
            exit 0
        }
    } catch {
        Write-Output '::notice title=HidenCloud GitHub secret::NOT_STORED_PC_GH_AUTH_LACKS_SECRETS_ACCESS'
        exit 0
    }
    $private = Join-Path (Join-Path $env:USERPROFILE '.ssh') 'funcity_hidencloud_ed25519'
    $public = $private + '.pub'
    foreach ($file in @($private, $public)) {
        $item = Get-Item -LiteralPath $file -Force -ErrorAction Stop
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'KEY_NOT_A_PLAIN_FILE'
        }
    }
    $firstLine = Get-Content -LiteralPath $private -Encoding ASCII -TotalCount 1
    if ($firstLine -ne '-----BEGIN OPENSSH PRIVATE KEY-----') { throw 'PRIVATE_KEY_FORMAT_INVALID' }
    $publicLine = (Get-Content -LiteralPath $public -Encoding ASCII -Raw).Trim()
    if ($publicLine -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+ funcity-hidencloud-2026-10-22$') {
        throw 'PUBLIC_KEY_FORMAT_INVALID'
    }
    # Do not overwrite an existing, unreadable secret whose key we cannot compare.
    try {
        & $gh.Source api ("repos/$repo/actions/secrets/$name") --jq '.name' 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Output '::notice title=HidenCloud GitHub secret::ALREADY_EXISTS_NOT_OVERWRITTEN_OR_VERIFIED'
            exit 0
        }
    } catch { }
    # stdin only: GitHub CLI encrypts with the repository public key before upload.
    # Never pass the private key as an argument, workflow output, artifact or file in Git.
    Get-Content -LiteralPath $private -Encoding ASCII -Raw |
        & $gh.Source secret set $name --repo $repo --app actions 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'SECRET_WRITE_FAILED' }
    & $gh.Source api ("repos/$repo/actions/secrets/$name") --jq '.name' 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'SECRET_NOT_VERIFIABLE' }
    Write-Output '::notice title=HidenCloud GitHub secret::STORED_AND_VERIFIED_NAME_ONLY; no private bytes logged'
    exit 0
} catch {
    Write-Output '::error title=HidenCloud GitHub secret::NOT_CONFIRMED; private key remains only on PC'
    exit 2
}
