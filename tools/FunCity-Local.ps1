# FunCity Local v4 (watch): raport LIVE pe GitHub la fiecare pas, server ascuns, zicand "gata" eu vad tot
$ErrorActionPreference='Continue'
$srv="$env:USERPROFILE\Desktop\FunCityLocal\server"
$dir="$env:LOCALAPPDATA\FunCityCtl"
New-Item -ItemType Directory -Force $dir,"$srv\logs" | Out-Null
$global:REP=@()
function Rep($m){
  $global:REP += "[$(Get-Date -Format 'HH:mm:ss')] $m"
  Write-Host $m -ForegroundColor Cyan
  if($global:REP.Count -gt 60){ $global:REP=@($global:REP[-60..-1]) }
  $tok=$env:GH_TOKEN
  if(-not $tok){ $saved=@(Get-Content "$dir\token.txt" -EA SilentlyContinue); if($saved.Count){ $tok=$saved[0].Trim() } }
  if(-not $tok){ return }
  $H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="watch" }
  $sha=$null; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt?ref=arena/9bbcb24f-serverroleplaylite" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="v4"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($global:REP -join "`n"))); branch="arena/9bbcb24f-serverroleplaylite" }
  if($sha){ $b.sha=$sha }
  for($k=0;$k -lt 2;$k++){ try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4)|Out-Null; break }catch{ Start-Sleep 2; try{ $b.sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt?ref=arena/9bbcb24f-serverroleplaylite" -Headers $H).sha }catch{} } }
}
Rep "v4: START, tintea $srv"
$jar="$srv\FunCityEngine.jar"
# 0) unfold: daca totul a nimerit intr-un subfolder
if(-not (Test-Path $jar)){
  $nest=@(Get-ChildItem $srv -Directory -EA SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName "FunCityEngine.jar") })
  if($nest.Count){
    Rep "jar gasit NEST in $($nest[0].Name) -> urc totul sus"
    robocopy $nest[0].FullName $srv /E /MOVE /NFL /NDL /NJH /NJS /NP | Out-Null
  }
}
# 1) jar direct din tar (132MB)
if(-not (Test-Path $jar)){
  Rep "jar lipseste -> iau functity-jare-toate.tar.gz (132MB)..."
  curl.exe -L -s -o "$env:TEMP\jare.tar.gz" "https://github.com/iZentric/ServerRolePlayLite/releases/download/jars-20261017-0952/functity-jare-toate.tar.gz"
  $tl=(Get-Item "$env:TEMP\jare.tar.gz" -EA SilentlyContinue).Length
  if($tl -gt 100000000){
    New-Item -ItemType Directory -Force "$env:TEMP\jare" | Out-Null
    tar -xzf "$env:TEMP\jare.tar.gz" -C "$env:TEMP\jare"
    # release-jars redenumeste buildul b1.0827 in FunCity-b1.0827.jar
    $f=@(Get-ChildItem "$env:TEMP\jare" -Recurse -File -Filter "FunCity-b1.0827.jar" -EA SilentlyContinue | Where-Object { $_.Length -gt 5MB })
    if(-not $f.Count){ Rep "EROR: buildul b1.0827 nu apare in tar; refuz alt build netestat" }
    if($f.Count){ Copy-Item $f[0].FullName $jar -Force; Rep ("jar asezat din "+$f[0].Name+" ("+[math]::Round((Get-Item $jar).Length/1MB)+"MB)") } else { Rep "EROR: nici un jar in tar" }
  } else { Rep "EROR: tar descarcat incomplet ($tl B)" }
  Remove-Item -Recurse -Force -EA SilentlyContinue "$env:TEMP\jare","$env:TEMP\jare.tar.gz"
} else { Rep "jar: deja prezent" }
# 2) mods din zip mare - doar ce lipsesc, cu progres live
$mc=@(Get-ChildItem "$srv\mods" -File -Filter *.jar -EA SilentlyContinue).Count
Rep "mods prezenti: $mc"
# Arhiva FunCity pune jarele in mods/mods-pre-fr, nu direct in mods.
if($mc -lt 25){
  $folders=@(Get-ChildItem "$srv\mods" -Directory -EA SilentlyContinue | ForEach-Object {
    [pscustomobject]@{ Path=$_.FullName; Name=$_.Name; Count=@(Get-ChildItem $_.FullName -File -Filter '*.jar' -EA SilentlyContinue).Count }
  } | Sort-Object Count -Descending)
  Rep ("subfoldere mods: " + (($folders | ForEach-Object { $_.Name+'='+$_.Count }) -join ', '))
  $source=@($folders | Where-Object { $_.Count -ge 20 -and $_.Name -notmatch '(?i)backup|disabled|old' })
  if($source.Count){
    $chosen=$source[0]
    Rep "mut $($chosen.Count) moduri din $($chosen.Name) in mods/"
    foreach($mod in @(Get-ChildItem $chosen.Path -File -Filter '*.jar')){ Copy-Item $mod.FullName "$srv\mods\$($mod.Name)" -Force }
    $mc=@(Get-ChildItem "$srv\mods" -File -Filter '*.jar' -EA SilentlyContinue).Count
    Rep "mods acum: $mc"
  }
}
if($mc -lt 25){
  Rep "trag FUNCTITY-SERVER.zip (464MB) pentru rest..."
  $z="$env:TEMP\fs.zip"
  if(-not ((Test-Path $z) -and (Get-Item $z).Length -gt 400000000)){ curl.exe -L -s -o $z "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip" }
  $zlen=(Get-Item $z -EA SilentlyContinue).Length
  Rep "zip $zlen B - desfac"
  if($zlen -gt 400000000){
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $a=[IO.Compression.ZipFile]::OpenRead($z)
    $tops=@{}; foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){ $tops[$matches[1]]=1 } else { $tops['']=1 } }
    $strip=($tops.Count -eq 1 -and -not $tops.Contains(''))
    $zm=@($a.Entries|?{ $_.FullName -match '(?i)^mods/[^/]+\.jar$' }); $rj=@($a.Entries|?{ $_.FullName -match '(?i)^[^/]+\.jar$' })
    Rep ("in zip: mods="+$zm.Count+" | root-jar-uri: ["+((($rj|%{$_.Name+" "+[math]::Round($_.Length/1MB)+"MB"}) -join ' '))+"]")
    Rep "structura zip: tops=[$($tops.Keys -join ',')] strip=$strip total=$($a.Entries.Count) intrari"
    Rep ("exemple mods: "+(($a.Entries|Where-Object{$_.FullName -match '(?i)mods/'}|Select-Object -First 6|ForEach-Object{$_.FullName}) -join ','))
    $done=0;$skip=0;$i=0
    foreach($e in $a.Entries){ $i++
      if($e.FullName -match '/$'){ continue }
      $rel=$e.FullName -replace '\\','/'
      if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
      if(-not $rel){ continue }
      $dest=Join-Path $srv $rel
      if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ $skip++; continue }
      $dd=Split-Path $dest -Parent
      if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd | Out-Null }
      [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true); $done++
      if(($done+$skip) % 400 -eq 0){ Rep "progres: $i/$($a.Entries.Count) scrise=$done sarite=$skip" }
    }
    $a.Dispose(); Remove-Item -Force -EA SilentlyContinue $z
    Rep "zip: +$done scrise, $skip existau"
    if(-not (Test-Path $jar)){
      $nest=@(Get-ChildItem $srv -Directory -EA SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName "FunCityEngine.jar") })
      if($nest.Count){ Rep "nest post-zip -> urc sus"; robocopy $nest[0].FullName $srv /E /MOVE /NFL /NDL /NJH /NJS /NP | Out-Null }
    }
  } else { Rep "EROR: zip incomplet - mods raman $mc" }
}
Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
# 3) lume
if(-not (Test-Path "$srv\world\level.dat")){
  Rep "world lipseste -> 92MB..."
  curl.exe -L -s -o "$env:TEMP\ws.tar.gz" "https://github.com/iZentric/ServerRolePlayLite/releases/download/world-live/worldsync.tar.gz"
  tar -xzf "$env:TEMP\ws.tar.gz" -C $srv
  Remove-Item -Force -EA SilentlyContinue "$env:TEMP\ws.tar.gz"
  Rep "world OK"
} else { Rep "world: OK" }
# 4) java
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  Rep "java11 -> Temurin..."
  curl.exe -L -s -o "$env:TEMP\j11.zip" "https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [IO.Compression.ZipFile]::ExtractToDirectory("$env:TEMP\j11.zip","$srv\jt")
  Move-Item @(Get-ChildItem "$srv\jt")[0].FullName "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt","$env:TEMP\j11.zip"
}
Rep "java: $(Test-Path "$srv\java11\bin\java.exe")"
# 5) configurile 100% + rcon
$raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs" | Out-Null
foreach($f in @('spigot.yml','bukkit.yml','commands.yml','connectivity-common.toml','modernfix-mixins.properties')){ try{ Invoke-WebRequest "$raw/$f" -OutFile "$srv\config\$f" -EA Stop }catch{} }
try{ Invoke-WebRequest "$raw/server.properties" -OutFile "$srv\server.properties" -EA Stop }catch{}
try{ Invoke-WebRequest "$raw/forge-server.toml" -OutFile "$srv\defaultconfigs\forge-server.toml" -EA Stop }catch{}
Set-Content -Encoding ascii "$srv\eula.txt" "eula=true"
if(Test-Path "$srv\server.properties"){
  $t=@(Get-Content "$srv\server.properties")
  if(-not (Test-Path "$dir\rcon.pass")){ -join((48..57+97..122|Get-Random -Count 14|%{[char]$_})) | Set-Content -Encoding ascii "$dir\rcon.pass" }
  $rp=@(Get-Content "$dir\rcon.pass")[0].Trim()
  $t=$t|?{$_ -notmatch '^(enable-rcon|rcon\.)'}
  $t=@($t|Where-Object{$_ -notmatch '^server-ip='})+'server-ip=127.0.0.1'+'enable-rcon=true'+'rcon.port=25575'+"rcon.password=$rp"
  Set-Content "$srv\server.properties" $t -Encoding ascii
  Rep "config+eula+rcon: puse"
}
# 6) server ascuns + doctor
if(-not (Test-Path $jar)){
  $c=@(Get-ChildItem $srv -Filter 'FunCity-1.16.5-b1.0827.jar' -EA SilentlyContinue|?{$_.Length -gt 5MB})
  if($c.Count){ Copy-Item $c[0].FullName $jar -Force; Rep "jar b1.0827 gasit la root -> FunCityEngine.jar" }
}
if(-not (Test-Path $jar)){ Rep 'OPRIT: motorul b1.0827 lipseste; nu pornesc alt jar'; return }
$mcBefore=@(Get-ChildItem "$srv\mods" -File -Filter '*.jar' -EA SilentlyContinue).Count
if($mcBefore -lt 20){ Rep "OPRIT: doar $mcBefore mods; serverul cu toate modurile NU e gata"; return }
function ServerProc {
  @(Get-CimInstance Win32_Process -Filter "Name='java.exe' OR Name='javaw.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -like '*FunCityEngine.jar*' })
}
function LocalPort {
  $tcp=New-Object Net.Sockets.TcpClient
  try { $a=$tcp.BeginConnect('127.0.0.1',25565,$null,$null); if(-not $a.AsyncWaitHandle.WaitOne(1500)){ return $false }; $tcp.EndConnect($a); return $true }
  catch { return $false } finally { $tcp.Close() }
}
$run=@(ServerProc)
if($run.Count){ Rep "proces server gasit (pid $($run[0].ProcessId)); port local=$(LocalPort)" } else {
  Rep "pornesc serverul ascuns..."
  Remove-Item -Force -EA SilentlyContinue "$srv\logs\latest.log"
  $scheduled=$false; $p=$null
  if($env:GITHUB_ACTIONS -eq 'true'){
    try {
      $uid=[Security.Principal.WindowsIdentity]::GetCurrent().Name
      $javaw="$srv\java11\bin\javaw.exe"
      if(-not (Test-Path $javaw)){ $javaw="$srv\java11\bin\java.exe" }
      $action=New-ScheduledTaskAction -Execute $javaw -Argument '-Xms2G -Xmx6G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -jar FunCityEngine.jar nogui' -WorkingDirectory $srv
      if($uid -eq 'NT AUTHORITY\SYSTEM'){
        $principal=New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount
      }else{
        $principal=New-ScheduledTaskPrincipal -UserId $uid -LogonType Interactive -RunLevel Limited
      }
      $trigger=New-ScheduledTaskTrigger -AtLogOn
      Register-ScheduledTask -TaskName 'FunCityLocalServer' -Action $action -Principal $principal -Trigger $trigger -Force -EA Stop | Out-Null
      Start-ScheduledTask -TaskName 'FunCityLocalServer' -EA Stop
      $scheduled=$true
      Rep 'server lansat separat prin Task Scheduler (supravietuieste jobului PC)'
    }catch{ Rep "Task Scheduler esuat: $($_.Exception.Message)" }
  }
  if(-not $scheduled){
    $env:RUNNER_TRACKING_ID=''
    $p=Start-Process -FilePath "$srv\java11\bin\java.exe" -ArgumentList '-Xms2G','-Xmx6G','-XX:+UnlockExperimentalVMOptions','-XX:+UseG1GC','-XX:MaxGCPauseMillis=30','-XX:+ParallelRefProcEnabled','-jar','FunCityEngine.jar','nogui' -WorkingDirectory $srv -WindowStyle Hidden -PassThru -RedirectStandardOutput "$srv\logs\console.log" -RedirectStandardError "$srv\logs\console.err"
  }
  $ok=$false;$t0=Get-Date
  for($i=0;$i -lt 72;$i++){
    Start-Sleep 5
    $alive=if($scheduled){ @(ServerProc).Count -gt 0 }else{ [bool](Get-Process -Id $p.Id -EA SilentlyContinue) }
    if(-not $alive){ Rep "java a iesit dupa $([int]((Get-Date)-$t0).TotalSeconds)s - trag log"; break }
    $lg=@(Get-Content "$srv\logs\latest.log" -EA SilentlyContinue)
    if(@($lg|Where-Object {$_ -match 'Done \('}).Count -and (LocalPort)){
      $ok=$true; Rep "SERVER LIVE pe 127.0.0.1:25565 in $([int]((Get-Date)-$t0).TotalSeconds)s"; break
    }
    if($i % 12 -eq 11){ Rep "incarca... $([int]((Get-Date)-$t0).TotalSeconds)s port=$(LocalPort)" }
  }
  if(-not $ok){ $tl=@(Get-Content "$srv\logs\latest.log" -Tail 10 -EA SilentlyContinue); if(-not @($tl).Count){ $tl=@(Get-Content "$srv\logs\console.err" -Tail 10 -EA SilentlyContinue) }; Rep "NU LIVE. log tail:"; $tl|%{ Rep "  $_" } }
}
$mc2=@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count
$pc2=@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count
Rep "STARE FINALA: jar=$(Test-Path $jar) mods=$mc2 plugins=$pc2 world=$(Test-Path "$srv\world\level.dat") java=$(Test-Path "$srv\java11\bin\java.exe")"
# Nu pornim agenti/runner separat. Raportul din aceasta rulare e suficient.
Rep "GATA V4 - verificati SERVER LIVE mai sus; altfel serverul NU e pornit"
Write-Host "Daca zice SERVER LIVE: intra in Minecraft -> Multiplayer -> localhost. Gata." -ForegroundColor Green
