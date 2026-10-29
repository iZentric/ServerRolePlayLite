# Read-only, conservative interpretation of local copies of three fixed host files.
# This does NOT prove that /restart works: a panel may terminate a shell-launched
# child, and a script may be empty, unsafe, or incompatible with the panel.
Set-StrictMode -Version Latest

function Test-FcRegularSmallFile {
    param([string]$Path, [long]$Limit)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $item=Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0 -and
        $item.Length -gt 0 -and $item.Length -le $Limit)
}

function Get-FcRestartReadiness {
    param([Parameter(Mandatory=$true)][string]$Root,
          [bool]$StartScriptListed=$false)
    if (-not (Test-Path -LiteralPath $Root -PathType Container) -or
        ((Get-Item -LiteralPath $Root -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'UNSAFE_LOCAL_ROOT'
    }
    $properties=Join-Path $Root 'server.properties'
    $spigot=Join-Path $Root 'spigot.yml'
    $rconDisabled=$false
    $spigotPresent=Test-FcRegularSmallFile $spigot 131072
    # A listing cannot distinguish a regular script from a symlink or prove
    # safe content. Never download or run the remotely named start.sh.
    $scriptListed=$StartScriptListed
    $scriptIsRoot=$false
    $scriptDefaulted=$false

    if (Test-FcRegularSmallFile $properties 131072) {
        # Repeated keys are ambiguous across Java properties readers: fail closed.
        $rconLines=@(Get-Content -LiteralPath $properties -Encoding UTF8 -ErrorAction Stop |
            Where-Object { $_ -match '^\s*enable-rcon\s*[:=]' })
        # Java .properties has whole-line comments, not trailing comments.
        $rconDisabled=($rconLines.Count -eq 1 -and
            $rconLines[0] -match '^\s*enable-rcon\s*[:=]\s*false\s*$')
    }
    if ($spigotPresent) {
        $lines=@(Get-Content -LiteralPath $spigot -Encoding UTF8 -ErrorAction Stop)
        $settingsCount=0
        $restartValues=[Collections.Generic.List[string]]::new()
        $inside=$false
        foreach ($line in $lines) {
            if ($line -match '^settings:\s*(?:#.*)?$') {
                $settingsCount++
                $inside=$true
                continue
            }
            if ($line -match '^[^\s#][^:]*:\s*') { $inside=$false }
            if ($inside -and $line -match '^ +restart-script:\s*(.*?)\s*$') {
                $value=$Matches[1]
                # If indentation is not the direct child form we recognize,
                # reject rather than silently assume CatServer's default.
                if ($line -match '^  restart-script:') {
                    $restartValues.Add($value)
                } else {
                    $restartValues.Add('INVALID_INDENT')
                }
            }
        }
        if ($settingsCount -eq 1 -and $restartValues.Count -eq 0) {
            # CatServer's pinned SpigotConfig default is ./start.sh.
            $scriptIsRoot=$true
            $scriptDefaulted=$true
        } elseif ($settingsCount -eq 1 -and $restartValues.Count -eq 1) {
            $value=$restartValues[0]
            # Whitelist only root-relative start.sh. No paths or shell syntax
            # from host config are ever executed or interpolated into SFTP.
            $scriptIsRoot=(@('./start.sh','start.sh','"./start.sh"','"start.sh"',
                "'./start.sh'","'start.sh'") -ccontains $value)
        }
    }
    return [pscustomobject]@{
        RconDisabled=[bool]$rconDisabled
        SpigotPresent=[bool]$spigotPresent
        StartScriptListed=[bool]$scriptListed
        RestartReferencesRootScript=[bool]$scriptIsRoot
        RestartScriptDefaulted=[bool]$scriptDefaulted
        StaticPreconditionsMet=[bool]($rconDisabled -and $spigotPresent -and $scriptListed -and $scriptIsRoot)
    }
}
