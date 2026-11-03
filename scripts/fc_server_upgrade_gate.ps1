# Read-only server backup/stop readiness. Enumerates file metadata only;
# never prints paths, filenames, addresses, passwords, logs or player identities.
param([Parameter(Mandatory=$true)][string]$Server, [switch]$Synthetic)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try {
  if ((Split-Path -Leaf $Server) -cne 'server' -or
      (Split-Path -Leaf (Split-Path -Parent $Server)) -cne 'FunCityLocal') { throw 'Wrong server' }
  $root = [IO.DirectoryInfo]::new($Server)
  if (-not $root.Exists -or ($root.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe server root' }
  $queue = [System.Collections.Generic.Queue[string]]::new()
  $queue.Enqueue($Server)
  $files = 0
  $bytes = 0L
  while ($queue.Count -gt 0) {
    $dir = $queue.Dequeue()
    foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop)) {
      if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point in server tree' }
      if ($item.PSIsContainer) { $queue.Enqueue($item.FullName) }
      else { $files++; $bytes += $item.Length }
      if ($files -gt 200000 -or $bytes -gt 200000000000L) { throw 'Backup size beyond gate' }
    }
  }
  $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($Server))
  if (-not $drive.IsReady) { throw 'Drive unavailable' }
  $spaceOk = $drive.AvailableFreeSpace -gt ($bytes * 2 + 1073741824L)
  $props = Join-Path $Server 'server.properties'
  $prop = Get-Item -LiteralPath $props -ErrorAction Stop
  if ($prop.PSIsContainer -or ($prop.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Unsafe config' }
  $settings = @(Get-Content -LiteralPath $props -ErrorAction Stop)
  $rconEnabled = @($settings | Where-Object { $_ -match '^enable-rcon=true$' }).Count -eq 1
  $rconPassPresent = @($settings | Where-Object { $_ -match '^rcon\.password=.+$' }).Count -eq 1
  $portLine = @($settings | Where-Object { $_ -match '^rcon\.port=\d+$' })
  $rconPort = 0
  if ($portLine.Count -eq 1) { $rconPort = [int](($portLine[0] -split '=', 2)[1]) }
  $ownedListener = $false
  $serverProc = $false
  $restartTaskMatches = $false
  if (-not $Synthetic -and [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
    $task = Get-ScheduledTask -TaskName 'FunCityLocalServer' -ErrorAction SilentlyContinue
    if ($task -and $task.State -ne 'Disabled') {
      $actions = @($task.Actions)
      if ($actions.Count -eq 1 -and $actions[0].Execute -and $actions[0].WorkingDirectory -and
          $actions[0].WorkingDirectory.TrimEnd([char[]]@([char]92,[char]47)).Equals($Server.TrimEnd([char[]]@([char]92,[char]47)),[StringComparison]::OrdinalIgnoreCase) -and
          $actions[0].Arguments -match '(?i)-jar\s+FunCityEngine\.jar') { $restartTaskMatches = $true }
    }
  }
  if (-not $Synthetic -and $rconEnabled -and $rconPassPresent -and $rconPort -gt 0 -and $rconPort -le 65535) {
    $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'java.exe' OR Name = 'javaw.exe'" -ErrorAction Stop | Where-Object {
      $_.CommandLine -and $_.CommandLine.IndexOf($Server, [StringComparison]::OrdinalIgnoreCase) -ge 0
    })
    $serverProc = $processes.Count -eq 1
    if ($serverProc) {
      $serverPid = $processes[0].ProcessId
      $ownedListener = @(Get-NetTCPConnection -State Listen -LocalPort $rconPort -ErrorAction SilentlyContinue |
        Where-Object { $_.OwningProcess -eq $serverPid -and ($_.LocalAddress -eq '127.0.0.1' -or $_.LocalAddress -eq '::1') }).Count -gt 0
    }
  }
  Write-Output ('::notice title=Server backup readiness::SOURCE_FILES=' + $files + ' SOURCE_BYTES_BUCKET_GIB=' + [math]::Ceiling($bytes / 1GB) + ' FREE_SPACE_FOR_2X_BACKUP=' + $spaceOk + ' RCON_CONFIGURED=' + ($rconEnabled -and $rconPassPresent -and $rconPort -gt 0 -and $rconPort -le 65535) + ' SERVER_PROCESS_UNIQUE=' + $serverProc + ' RCON_LOOPBACK_OWNED_BY_SERVER=' + $ownedListener + ' RESTART_TASK_MATCHES_SERVER=' + $restartTaskMatches + '; READ_ONLY=true; BACKUP_CREATED=false')
  exit 0
} catch {
  Write-Output '::notice title=Server backup readiness::GATE_UNAVAILABLE; READ_ONLY=true; BACKUP_CREATED=false'
  exit 2
}
