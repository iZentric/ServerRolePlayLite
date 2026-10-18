# pcmd.ps1 - comanda curenta a canalului rapid (ruleaza PC-ul tau la ~10s distanta)
# Versia 1: INSTALARE functity in E:\Administrator\Desktop\FunCity
$ErrorActionPreference='Continue'
$root='E:\Administrator\Desktop\FunCity'
$raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
$rel='https://github.com/iZentric/ServerRolePlayLite/releases/download'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
New-Item -ItemType Directory -Force $root | Out-Null
$dv=($root -split '\\')[0]
try{ $free=[math]::Round((Get-PSDrive $dv).Free/1GB,1) }catch{ $free=-1 }
L "radacina: $root | disk liber: $free GB"
if($free -ge 0 -and $free -lt 6){ L "EROR: spatiu insuficient pe $dv"; $T -join "`n"; exit 0 }
$srv="$root\server"
New-Item -ItemType Directory -Force $srv | Out-Null
# 1) server pack (ZIP cu tot: motor+moduri+pluginuri+CoreProtect) - doar daca lipseste jar-ul
if(-not (Test-Path "$srv\FunCity-1.16.5-b1.0827.jar")){
  $z="$env:TEMP\fs.zip"; Remove-Item -Force -EA SilentlyContinue $z
  L "descarc FUNCTITY-SERVER.zip..."
  curl.exe -fLso $z "$rel/funcity/FUNCTITY-SERVER.zip"
  $zs=(Get-Item $z -EA SilentlyContinue).Length
  if($zs -lt 400000000){ L "EROR zip mic: $zs"; $T -join "`n"; exit 0 }
  L "zip: $zs B, dezarhivez..."
  $x="$env:TEMP\fsx"; Remove-Item -Recurse -Force -EA SilentlyContinue $x
  Expand-Archive $z $x -Force
  $src=$x
  $inner=@(Get-ChildItem $x -Directory)
  if((@(Get-ChildItem $x -File).Count -eq 0) -and $inner.Count -eq 1){ $src=$inner[0].FullName }
  Copy-Item "$src\*" $srv -Recurse -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue $x,$z
  L "server dezarhivat: $(@(Get-ChildItem $srv -File).Count) fisiere radacina, $(@(Get-ChildItem $srv\mods -EA SilentlyContinue).Count) moduri"
} else { L "jar existent, sar peste zip" }
Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
# 2) lumea din backup (worldsync.tar.gz = world cu tot cu claims+CoreProtect loguri)
if(-not (Test-Path "$srv\world\level.dat")){
  $wt="$env:TEMP\ws.tar.gz"; Remove-Item -Force -EA SilentlyContinue $wt
  L "descarc world-ul (92MB)..."
  curl.exe -fLso $wt "$rel/world-live/worldsync.tar.gz"
  L "tar: $((Get-Item $wt -EA SilentlyContinue).Length) B"
  tar -xzf $wt -C $srv
  Remove-Item -Force -EA SilentlyContinue $wt
} else { L "world existent" }
if(Test-Path "$srv\world\level.dat"){ L "level.dat: OK" } else { L "ATENTIE: fara level.dat" }
# 3) Java 11 Temurin
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  L "descarc Java 11..."
  $jz="$env:TEMP\j11.zip"; Remove-Item -Force -EA SilentlyContinue $jz,"$srv\jt"
  curl.exe -fLso $jz 'https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse'
  Expand-Archive $jz "$srv\jt" -Force
  $in=@(Get-ChildItem "$srv\jt")[0].FullName
  Move-Item $in "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt",$jz
  L "java11 OK"
} else { L "java11 existent" }
# 4) configuri 100% peste ce e in zip
New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs","$srv\logs" | Out-Null
foreach($f in @(@('server.properties',"$srv\server.properties"),@('spigot.yml',"$srv\config\spigot.yml"),@('bukkit.yml',"$srv\config\bukkit.yml"),@('commands.yml',"$srv\config\commands.yml"),@('connectivity-common.toml',"$srv\config\connectivity-common.toml"),@('modernfix-mixins.properties',"$srv\config\modernfix-mixins.properties"),@('forge-server.toml',"$srv\defaultconfigs\forge-server.toml"))){
  try{ Invoke-WebRequest "$raw/$($f[0])" -OutFile $f[1] -EA Stop; }catch{ L "config FAIL $($f[0])" }
}
L "configuri 100% aplicate"
# 5) launch.bat + watchdog + task la logon
@"
@echo off
cd /d $srv
java11\bin\java -Xms2G -Xmx8G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui >> logs\boot.log 2>&1
"@ | Set-Content -Encoding ascii "$srv\launch.bat"
"\`$dir='$srv'
while(`$true){
  \$p=@(Get-Process java -EA SilentlyContinue | Where-Object { \$_.Path -like "\$dir*java11*" })
  if(\$p.Count -eq 0){ Start-Process -FilePath "\$dir\launch.bat" -WindowStyle Hidden }
  Start-Sleep 30
}" | Set-Content -Encoding ascii "$srv\watchdog.ps1"
"CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $srv\watchdog.ps1"", 0, False" | Set-Content -Encoding ascii "$srv\watchdog.vbs"
schtasks /Create /TN FunCityServer /TR "wscript.exe \"$srv\watchdog.vbs\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
L "task FunCityServer la logon: inregistrat"
# 6) pornire acum (daca nu cumva deja merge)
$run=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
if($run.Count -eq 0){ Start-Process -FilePath "$srv\watchdog.vbs"; L "watchdog pornit ACUM" } else { L "java deja ruleaza (pid $($run[0].Id))" }
# 7) astept primul boot si masor
for($i=0;$i -lt 60;$i++){
  Start-Sleep 5
  if(Test-Path "$srv\logs\boot.log"){
    if((Get-Content "$srv\logs\boot.log" -Tail 5 -EA SilentlyContinue) -join ' ' -match 'Done \('){ L "server PORNIT"; break }
  }
}
$log=@(Get-Content "$srv\logs\boot.log" -EA SilentlyContinue)
L ("boot.log linii: $($log.Count); "+(($log | Select-String -Pattern 'Done \(' | Select-Object -Last 1)))
try{ $tcp=New-Object Net.Sockets.TcpClient; $tcp.Connect('127.0.0.1',25565); L "PORT 25565: DESCHIS"; $tcp.Close() }catch{ L "port inchis inca" }
L "gata. fisier marcatori: instalat-v1"
$T -join "`n"
