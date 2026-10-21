try {
# Hosted-only syntax and synthetic byte-preservation/rollback fixture.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$source = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'fc_server_live_view5.ps1'))
$tokens = $null; $errors = $null
[void][System.Management.Automation.Language.Parser]::ParseInput($source,[ref]$tokens,[ref]$errors)
if ($errors.Count) { throw 'Live maintenance script failed PowerShell syntax check' }
foreach ($fragment in @('Check-Zero','save-all flush','-Command stop','fc_server_offline_backup.ps1',
    'RESTORE_COPY_VERIFIED=true','[IO.File]::Replace($temp,$cfg,$swap)','Start-ScheduledTask',
    'VIEW_FIVE_ACTIVE=')) {
  if (-not $source.Contains($fragment)) { throw 'Missing required guard' }
}
if ($source.Contains('Stop-Process') -or $source.Contains('taskkill')) { throw 'Forced stop is forbidden' }
$stop = $source.IndexOf('-Command stop',[StringComparison]::Ordinal)
$backup = $source.IndexOf('fc_server_offline_backup.ps1',[StringComparison]::Ordinal)
$change = $source.IndexOf('[IO.File]::Replace($temp,$cfg,$swap)',[StringComparison]::Ordinal)
$restart = $source.IndexOf('Start-ScheduledTask',[StringComparison]::Ordinal)
if ($stop -lt 0 -or $backup -le $stop -or $change -le $backup -or $restart -le $change) {
  throw 'Maintenance order is unsafe'
}
$root = Join-Path ([IO.Path]::GetTempPath()) ('view-five-fixture-' + [guid]::NewGuid().ToString('N'))
try {
  [void][IO.Directory]::CreateDirectory($root)
  $cfg = Join-Path $root 'server.properties'
  $temp = Join-Path $root 'new.properties'
  $swap = Join-Path $root 'old.properties'
  $encoding = [Text.Encoding]::GetEncoding(28591)
  $initial = [byte[]]@(35,233,13,10) + $encoding.GetBytes("view-distance=6`r`nsecret=untouched`r`n")
  [IO.File]::WriteAllBytes($cfg,$initial)
  $originalHash=(Get-FileHash $cfg -Algorithm SHA256).Hash
  $oldText=[IO.File]::ReadAllText($cfg,$encoding)
  $pattern='(?m)^view-distance=6(\r?)$'
  if ([regex]::Matches($oldText,'(?m)^view-distance=[^\r\n]*\r?$').Count -ne 1 -or
      [regex]::Matches($oldText,$pattern).Count -ne 1) { throw 'Fixture guard failed' }
  $newText=[regex]::Replace($oldText,$pattern,'view-distance=5$1')
  [IO.File]::WriteAllText($temp,$newText,$encoding)
  [IO.File]::Replace($temp,$cfg,$swap)
  if ((Get-FileHash $swap -Algorithm SHA256).Hash -cne $originalHash -or
      ([IO.File]::ReadAllBytes($cfg))[1] -ne [byte]233 -or
      $newText -cne [IO.File]::ReadAllText($cfg,$encoding)) { throw 'Byte-preserving view change failed' }
  [IO.File]::WriteAllText($temp,[IO.File]::ReadAllText($swap,$encoding),$encoding)
  [IO.File]::Replace($temp,$cfg,$null)
  if ((Get-FileHash $cfg -Algorithm SHA256).Hash -cne $originalHash) { throw 'Rollback failed' }
  $unexpected=$oldText.Replace('view-distance=6','view-distance=5')
  if ([regex]::Matches($unexpected,$pattern).Count -ne 0) { throw 'Already-five fixture guard failed' }
  Write-Output 'VIEW_FIVE_SYNTAX_OK=true GUARD_ORDER_OK=true SYNTHETIC_BYTE_PRESERVATION=true ROLLBACK_OK=true LIVE_SERVER_UNTOUCHED=true'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

} catch {
  Write-Output ("::error title=Five-chunk fixture::TYPE=" + $_.Exception.GetType().Name + " LINE=" + $_.InvocationInfo.ScriptLineNumber + " MESSAGE=" + $_.Exception.Message)
  exit 2
}
