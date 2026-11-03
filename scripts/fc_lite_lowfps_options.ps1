# Conservative low-end graphics preset for the existing Lite profile only.
# Never closes Prism/game, touches mods/accounts/worlds, or uploads private data.
param([Parameter(Mandatory=$true)][string]$Profile,[switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$phase='PREFLIGHT'
$temp=$null
$swap=$null
$changed=$false
try {
  if ((Split-Path -Leaf $Profile) -cne 'FunCity RP Lite' -or
      (Split-Path -Leaf (Split-Path -Parent $Profile)) -cne 'instances' -or
      -not $env:GITHUB_RUN_ID -or $env:GITHUB_RUN_ID -notmatch '^\d+$') { throw 'Wrong instance or run id' }
  $games=@(@('.minecraft','minecraft') | Where-Object { Test-Path -LiteralPath (Join-Path $Profile $_) -PathType Container })
  if ($games.Count -ne 1) { throw 'Ambiguous game folder' }
  $game=Join-Path $Profile $games[0]
  $options=Join-Path $game 'options.txt'
  foreach ($path in @($Profile,$game)) {
    $dir=[IO.DirectoryInfo]::new($path)
    if (-not $dir.Exists -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe folder' }
  }
  $item=Get-Item -LiteralPath $options -ErrorAction Stop
  if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      $item.Length -gt 1000000) { throw 'Unsafe options' }
  if (-not $Synthetic) {
    if (@(Get-Process -Name 'prismlauncher' -ErrorAction SilentlyContinue).Count -gt 0) {
      throw 'Prism active; user must close normally'
    }
    $gameJava=@(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
      $_.CommandLine -and $_.CommandLine.IndexOf($Profile,[StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    if ($gameJava.Count -gt 0) { throw 'Client game active' }
  }
  $phase='VERIFY_CURRENT_VALUES'
  $text=[IO.File]::ReadAllText($options,[Text.Encoding]::UTF8)
  $changes=[ordered]@{
    'renderDistance'=@('12','5')
    'graphicsMode'=@('1','0')
    'particles'=@('0','1')
    'mipmapLevels'=@('4','0')
    'entityShadows'=@('true','false')
  }
  $newText=$text
  foreach ($key in $changes.Keys) {
    $pattern='(?m)^' + [regex]::Escape($key) + ':([^\r\n]*)(\r?)$'
    $found=[regex]::Matches($newText,$pattern)
    if ($found.Count -ne 1 -or $found[0].Groups[1].Value -cne $changes[$key][0]) {
      throw 'Options changed since read-only audit'
    }
    $replacement=$key + ':' + $changes[$key][1] + '$2'
    $newText=[regex]::Replace($newText,$pattern,$replacement)
  }
  $parent=Split-Path -Parent (Split-Path -Parent $Profile)
  $backupRoot=Join-Path $parent 'Arena-Private-Settings-Backups'
  if (Test-Path -LiteralPath $backupRoot) {
    $existing=[IO.DirectoryInfo]::new($backupRoot)
    if (-not $existing.Exists -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe backup folder' }
  }
  $backup=Join-Path $backupRoot ('lite-lowfps-' + $env:GITHUB_RUN_ID)
  if (Test-Path -LiteralPath $backup) { throw 'Existing settings backup' }
  $phase='PRIVATE_BACKUP_AND_RESTORE_REHEARSAL'
  New-Item -ItemType Directory -Path $backup -Force -ErrorAction Stop | Out-Null
  $backupFile=Join-Path $backup 'original-options.txt'
  Copy-Item -LiteralPath $options -Destination $backupFile -ErrorAction Stop
  $oldHash=(Get-FileHash -LiteralPath $options -Algorithm SHA256 -ErrorAction Stop).Hash
  if ((Get-FileHash -LiteralPath $backupFile -Algorithm SHA256).Hash -cne $oldHash) { throw 'Backup digest mismatch' }
  $rehearsal=Join-Path $backup 'restore-rehearsal.txt'
  Copy-Item -LiteralPath $backupFile -Destination $rehearsal -ErrorAction Stop
  if ((Get-FileHash -LiteralPath $rehearsal -Algorithm SHA256).Hash -cne $oldHash) { throw 'Restore rehearsal mismatch' }
  Remove-Item -LiteralPath $rehearsal -Force -ErrorAction Stop
  $phase='ATOMIC_OPTIONS_REPLACE'
  $temp=Join-Path $game ('options.txt.arena-' + $env:GITHUB_RUN_ID + '.new')
  $swap=Join-Path $backup 'atomic-original-options.txt'
  if ((Test-Path -LiteralPath $temp) -or (Test-Path -LiteralPath $swap)) { throw 'Existing temporary file' }
  [IO.File]::WriteAllText($temp,$newText,[Text.UTF8Encoding]::new($false))
  [IO.File]::Replace($temp,$options,$swap)
  $changed=$true
  if ((Get-FileHash -LiteralPath $swap -Algorithm SHA256).Hash -cne $oldHash -or
      [IO.File]::ReadAllText($options,[Text.Encoding]::UTF8) -cne $newText) { throw 'Atomic replacement mismatch' }
  Write-Output '::notice title=Lite low-end graphics::CLIENT_RENDER=5 GRAPHICS=FAST PARTICLES=DECREASED MIPMAP=0 ENTITY_SHADOWS=OFF PRIVATE_BACKUP=true RESTORE_REHEARSED=true; MODS_UNCHANGED=true FPS_NOT_MEASURED=true SERVER_UNCHANGED=true'
  exit 0
} catch {
  Write-Output ('::notice title=Lite low-end graphics::APPLY_BLOCKED PHASE=' + $phase + ' TYPE=' + $_.Exception.GetType().Name + ' LINE=' + $_.InvocationInfo.ScriptLineNumber + '; NO_FORCED_PROCESS=true')
  if ($changed -and $swap -and (Test-Path -LiteralPath $swap) -and $options) {
    try { [IO.File]::Replace($swap,$options,$null) } catch { }
  }
  exit 2
} finally {
  if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }
}
