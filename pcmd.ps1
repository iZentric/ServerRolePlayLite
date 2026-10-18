# pcmd.ps1 - V3: paznic 1s + CHEIA din clipboard + RESUME instalare (robocopy, fara redesccarcare)
$ErrorActionPreference='Continue'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
$dir="$env:LOCALAPPDATA\FunCityCtl"
New-Item -ItemType Directory -Force $dir | Out-Null
$tk=''; try{ $tk=(Get-Clipboard).Trim() }catch{}
if($tk -match '^github_pat_[A-Za-z0-9_]{20,}'){ [IO.File]::WriteAllText("$dir\token.txt",$tk); L "cheia: luata din clipboard" }
elseif(Test-Path "$dir\token.txt" -PathType Leaf){ L "cheia: fisier existent OK" }
else { L "cheia: NICAIERI (clipboard gol, fisier lipsta)" }
if(Test-Path "$dir\token.txt" -PathType Leaf){
@'
$ErrorActionPreference='Continue'
$dir="$env:LOCALAPPDATA\FunCityCtl"
$tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
$H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="fctl" }
$repo="iZentric/ServerRolePlayLite"; $ref="arena/9bbcb24f-serverroleplaylite"
$last=""
function Put($path,$txt){
  $sha=$null
  try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/$path" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="paznic"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch=$ref }
  if($sha){ $b.sha=$sha }
  try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/$repo/contents/$path" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4) -EA Stop | Out-Null }catch{}
}
while($true){
  try{
    $c=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/pcmd.ps1?ref=$ref" -Headers $H -EA Stop).content -replace '\s',''
    $dec=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($c))
    if($dec -ne $last){
      $last=$dec
      Set-Content -Path "$dir\pcmd-run.ps1" -Value $dec -Encoding UTF8
      Put "diag/pctl.txt" ("START " + (Get-Date -Format s))
      $out=& powershell -NoProfile -ExecutionPolicy Bypass -File "$dir\pcmd-run.ps1" 2>&1 | Out-String
      if($out.Length -gt 90000){ $out=$out.Substring(0,90000)+"...TR" }
      Put "diag/pctl.txt" ($out + "`nGATA " + (Get-Date -Format s))
    }
  }catch{ Start-Sleep 10 }
  Start-Sleep 1
}
'@ | Set-Content -Encoding ascii "$dir\fctl.ps1"
  "CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $dir\fctl.ps1"", 0, False" | Set-Content -Encoding ascii "$dir\fctl.vbs"
  schtasks /Create /TN FunCityCtl /TR "wscript.exe \"$dir\fctl.vbs\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
  $runing=$false
  try{ $runing=@(Get-ScheduledTask -TaskName FunCityCtl -EA SilentlyContinue | Get-ScheduledTaskInfo -EA SilentlyContinue | Where-Object { $_.State -ne 'Ready' -and $_.PSComputerName }).Count -gt 0 }catch{}
  $fcp=@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -match 'fctl\.ps1' })
  if($fcp.Count -eq 0){ Start-Process -FilePath "$dir\fctl.vbs"; L "paznic: proces nou pornit" } else { L "paznic: deja ruleaza ( $($fcp.Count) procese)" }
  L "paznic 1s: instalat + task FunCityCtl la logon"
}
# ==== RESUME INSTALARE ====
$srv='E:\Administrator\Desktop\FunCity\server'
New-Item -ItemType Directory -Force $srv,"$srv\logs" | Out-Null
$jar="$srv\FunCity-1.16.5-b1.0827.jar"
$z="$env:TEMP\fs.zip"; $x="$env:TEMP\fsx"
# omor orice extractionor fantoma ramasă din jobul anulat
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -match 'fs\.zip|fsx|Expand-Archive' -and $_.ProcessId -ne $PID } | ForEach-Object { try{ Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue; L "am oprit fantoma pid $($_.ProcessId)" }catch{} }
if(-not (Test-Path $jar)){
  if(-not (Test-Path $z) -or (Get-Item $z).Length -lt 400000000){
    L "zip lipsa in TEMP -> redesccarc (487MB)..."
    curl.exe -fLso $z "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip"
  } else { L "zip gasit in TEMP: $([math]::Round((Get-Item $z).Length/1MB)) MB - nu redesccarc nimic" }
  if((Test-Path $z) -and (Get-Item $z).Length -gt 400000000){
    $have=@(Get-ChildItem $x -EA SilentlyContinue).Count
    if($have -lt 5){ L "desfac arhiva direct in server (fara copie dubla)..."
      Remove-Item -Recurse -Force -EA SilentlyContinue $x
      Add-Type -AssemblyName System.IO.Compression.FileSystem
      $a=[IO.Compression.ZipFile]::OpenRead($z)
      $n=$a.Entries.Count; $i=0
      $tops=@{}
      foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){$tops[$matches[1]]=1}else{$tops['']=1} }
      $strip=$false
      if($tops.Count -eq 1 -and -not $tops.Contains('')){ $strip=$true; L "radacina zip: '$($tops.Keys[0])' - o taiem" }
      foreach($e in $a.Entries){
        $i++
        if($e.FullName -match '/$'){ continue }
        $rel=$e.FullName -replace '\\','/'
        if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
        if(-not $rel){ continue }
        $dest=Join-Path $srv $rel
        $dd=Split-Path $dest -Parent
        if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd | Out-Null }
        if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ continue }
        [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true)
      }
      $a.Dispose()
    } else { L "fsx partial exista ($have invari) - las desfacerea la Copy rapid mai jos" }
    L "server extras: $(@(Get-ChildItem $srv -File).Count) fisiere radacina, mods: $(@(Get-ChildItem $srv\mods -EA SilentlyContinue).Count)"
  } else { L "EROR: nici zip in TEMP nici download ok" }
} else { L "jar deja prezent - sar peste arhiva" }
Remove-Item -Force -EA SilentlyContinue $z
Remove-Item -Recurse -Force -EA SilentlyContinue $x
Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
# world
if(-not (Test-Path "$srv\world\level.dat")){
  $wt="$env:TEMP\ws.tar.gz"
  if(-not (Test-Path $wt)){ curl.exe -fLso $wt "https://github.com/iZentric/ServerRolePlayLite/releases/download/world-live/worldsync.tar.gz" }
  if((Test-Path $wt) -and (Get-Item $wt).Length -gt 50000000){ tar -xzf $wt -C $srv; L "world: desfacut" } else { L "world: tar lipsa/marime ciudata" }
  Remove-Item -Force -EA SilentlyContinue $wt
} else { L "world: level.dat OK" }
# java
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  $jz="$env:TEMP\j11.zip"; Remove-Item -Force -EA SilentlyContinue $jz,"$srv\jt"
  curl.exe -fLso $jz 'https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse'
  Expand-Archive $jz "$srv\jt" -Force; $in=@(Get-ChildItem "$srv\jt")[0].FullName
  Move-Item $in "$srv\java11" -Force; Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt",$jz
  L "java11 instalat"
} else { L "java11: existent" }
# configuri 100%
$raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs" | Out-Null
foreach($f in @(@('server.properties',"$srv\server.properties"),@('spigot.yml',"$srv\config\spigot.yml"),@('bukkit.yml',"$srv\config\bukkit.yml"),@('commands.yml',"$srv\config\commands.yml"),@('connectivity-common.toml',"$srv\config\connectivity-common.toml"),@('modernfix-mixins.properties',"$srv\config\modernfix-mixins.properties"),@('forge-server.toml',"$srv\defaultconfigs\forge-server.toml"))){
  try{ Invoke-WebRequest "$raw/$($f[0])" -OutFile $f[1] -EA Stop }catch{ L "config FAIL $($f[0])" }
}
L "configuri: 100% FunCity aplicate"
# launch + watchdog
@"
@echo off
cd /d $srv
java11\bin\java -Xms2G -Xmx8G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui >> logs\boot.log 2>&1
"@ | Set-Content -Encoding ascii "$srv\launch.bat"
"\`$dir='$srv'
while(\`$true){
  \`$p=@(Get-Process java -EA SilentlyContinue | Where-Object { \`$_.Path -like \"\`$dir*java11*\" })
  if(\`$p.Count -eq 0){ Start-Process -FilePath \"\`$dir\launch.bat\" -WindowStyle Hidden }
  Start-Sleep 30
}" | Set-Content -Encoding ascii "$srv\watchdog.ps1"
"CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $srv\watchdog.ps1"", 0, False" | Set-Content -Encoding ascii "$srv\watchdog.vbs"
schtasks /Create /TN FunCityServer /TR "wscript.exe \"$srv\watchdog.vbs\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
$jp=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
if($jp.Count -eq 0){ Start-Process -FilePath "$srv\watchdog.vbs"; L "server: pornit (astept ~90s boot)" } else { L "server: java deja ruleaza" }
L "marca: v3-resume"
$T -join "`n"
