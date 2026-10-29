# Read-only SFTP inventory of restart prerequisites. NEVER issues /restart,
# changes host files, exposes settings or turns RCON on. Not a live restart test.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'fc_pc_restart_readiness_lib.ps1')
$work=$null
try {
    if (-not $env:USERPROFILE -or -not $env:RUNNER_TEMP -or -not $env:GITHUB_RUN_ID -or
        $env:GITHUB_RUN_ID -notmatch '^\d+$' -or
        $env:USERNAME -in @('SYSTEM','LOCAL SERVICE','NETWORK SERVICE')) { throw 'NOT_OWNER_PC_RUNNER' }
    $key=Join-Path $env:USERPROFILE '.ssh\funcity_hidencloud_ed25519_rotated'
    $pub=$key + '.pub'
    foreach ($path in @($key,$pub)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
            ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'ROTATED_PC_KEY_MISSING_OR_UNSAFE'
        }
    }
    $expectedClient='AAAAC3NzaC1lZDI1NTE5AAAAILm8LdLcmC0AO9bHH5poxjEu7IS8Sa5KA7gx8kqetuGl'
    $line=(Get-Content -LiteralPath $pub -Raw -Encoding ASCII).Trim()
    if ($line -notmatch '^ssh-ed25519 [A-Za-z0-9+/=]+(?: .*)?$' -or
        ($line -split ' ')[1] -cne $expectedClient) { throw 'ROTATED_KEY_IDENTITY_MISMATCH' }
    $sftp=(Get-Command sftp.exe -ErrorAction Stop).Source
    $keygen=(Get-Command ssh-keygen.exe -ErrorAction Stop).Source
    $work=Join-Path $env:RUNNER_TEMP ('fc-restart-readonly-' + $env:GITHUB_RUN_ID)
    if (Test-Path -LiteralPath $work) { throw 'TEMP_PATH_EXISTS' }
    [void](New-Item -ItemType Directory -Path $work -ErrorAction Stop)
    $batch=Join-Path $work 'commands.txt'
    $known=Join-Path $work 'known_hosts'
    $privateOutput=Join-Path $work 'sftp-output.txt'
    $destination='izentric-150380.6ddc2b7d@olivia.hidencloud.com'
    $args=@('-q','-b',$batch,'-P','2022','-i',$key,
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
        '-o',('UserKnownHostsFile=' + $known),'-o','ConnectTimeout=12',
        '-o','ServerAliveInterval=20','-o','ServerAliveCountMax=2')
    [IO.File]::WriteAllText($batch,"ls -1a`nbye`n",[Text.Encoding]::ASCII)
    & $sftp @args -o 'StrictHostKeyChecking=accept-new' $destination 1>$privateOutput 2>$null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $known -PathType Leaf)) { throw 'SFTP_LIST_FAILED' }
    $fps=@(& $keygen -lf $known 2>$null)
    if ($LASTEXITCODE -ne 0 -or $fps.Count -ne 1 -or
        $fps[0] -notmatch '\sSHA256:8B88Xl\+b19yzYinbJ9bZxwc79nW1sBZrF0XvGiCqdd4\s') {
        throw 'SFTP_HOST_KEY_CHANGED_FROM_PREVIOUS_TOFU'
    }
    # Fixed allowlist: no remote configuration value is ever used in an SFTP
    # command. Root listing remains private; only aggregate booleans escape.
    $names=@(Get-Content -LiteralPath $privateOutput -ErrorAction Stop | Where-Object { $_.Length -gt 0 })
    $commands=[Collections.Generic.List[string]]::new()
    foreach ($name in @('server.properties','spigot.yml')) {
        if (Test-FcRootEntryListed -Names $names -Expected $name) {
            $target=(Join-Path $work $name).Replace([char]92,[char]47)
            if ($target.Contains('"') -or $target.Contains("`n")) { throw 'UNSAFE_PC_TEMP_PATH' }
            $commands.Add('get "' + $name + '" "' + $target + '"')
        }
    }
    if ($commands.Count -gt 0) {
        $commands.Add('bye')
        [IO.File]::WriteAllLines($batch,$commands,[Text.Encoding]::ASCII)
        & $sftp @args -o 'StrictHostKeyChecking=yes' $destination 1>$privateOutput 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'SFTP_FIXED_FILES_READ_FAILED' }
    }
    $state=Get-FcRestartReadiness -Root $work -StartScriptListed (Test-FcRootEntryListed -Names $names -Expected 'start.sh')
    $bool={ param([bool]$value) if ($value) { 'true' } else { 'false' } }
    Write-Output ('::notice title=Restart static preflight::RCON_DISABLED=' + (& $bool $state.RconDisabled) +
        ' SPIGOT_PRESENT=' + (& $bool $state.SpigotPresent) +
        ' START_SH_LISTED=' + (& $bool $state.StartScriptListed) +
        ' RESTART_REFERENCES_ROOT_START_SH=' + (& $bool $state.RestartReferencesRootScript) +
        ' RESTART_SCRIPT_DEFAULTED=' + (& $bool $state.RestartScriptDefaulted) +
        ' STATIC_PRECONDITIONS_MET=' + (& $bool $state.StaticPreconditionsMet) +
        ' RUNTIME_RESTART_TESTED=false CONSOLE_ACCESS_VERIFIED=false READ_ONLY=true HOSTKEY_PREVIOUS_TOFU_ONLY=true')
} catch {
    Write-Output '::error title=Restart static preflight::READ_ONLY_PROBE_FAILED; no server writes; no restart attempted'
    exit 2
} finally {
    if ($work -and (Test-Path -LiteralPath $work)) {
        Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
    }
}
