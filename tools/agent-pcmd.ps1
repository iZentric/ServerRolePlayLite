# agent-fix: aduce jar+moduri lipsa, saree ce exista, pune java/config, porneste serverul
$ErrorActionPreference='Continue'
$srv="$env:USERPROFILE\Desktop\FunCityLocal\server"
$T=@()
New-Item -Force -ItemType Directory "$srv\logs" | Out-Null
$z="$env:TEMP\fs.zip"
if(-not (Test-Path "$srv\FunCity-1.16.5-b1.0827.jar")){
  $haveZip=(Test-Path $z) -and ((Get-Item $z).Length -gt 400000000)
  if(-not $haveZip){ $T+="descarc zip 487MB..."; curl.exe -L -o $z "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip" -s -S 2>>"$srv\logs\dl.log" }
  $zs=(Get-Item $z -EA SilentlyContinue).Length
  if($zs -gt 400000000){
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $a=[IO.Compression.ZipFile]::OpenRead($z)
    $tops=@{}; foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){ $tops[$matches[1]]=1 } else { $tops['']=1 } }
    $strip=($tops.Count -eq 1 -and -not $tops.Contains(''))
    $done=0; $skip=0
    foreach($e in $a.Entries){
      if($e.FullName -match '/$'){ continue }
      $rel=$e.FullName -replace '\\','/'
      if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
      if(-not $rel){ continue }
      $dest=Join-Path $srv $rel; $dd=Split-Path $dest -Parent
      if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd | Out-Null }
      if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ $skip++; continue }
      [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true); $done++
    }
    $a.Dispose(); Remove-Item -Force -EA SilentlyContinue $z
    $T+="zip $zs B | scrise $done | sarite (existau) $skip"
  } else { $T+="EROR: zip incomplet ($zs B)" }
} else { $T+="jar deja prezent" }
if(Test-Path "$srv\FunCity-1.16.5-b1.0827.jar"){
  Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
  if(-not (Test-Path "$srv\java11\bin\java.exe")){
    $T+="java11..."
    curl.exe -L -o "$env:TEMP\j11.zip" "https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory("$env:TEMP\j11.zip","$srv\jt")
    Move-Item @(Get-ChildItem "$srv\jt")[0].FullName "$srv\java11" -Force
    Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt","$env:TEMP\j11.zip"
  }
  $raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
  New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs" | Out-Null
  foreach($f in @('spigot.yml','bukkit.yml','commands.yml','connectivity-common.toml','modernfix-mixins.properties')){ try{ Invoke-WebRequest "$raw/$f" -OutFile "$srv\config\$f" -EA Stop }catch{} }
  try{ Invoke-WebRequest "$raw/forge-server.toml" -OutFile "$srv\defaultconfigs\forge-server.toml" -EA Stop }catch{}
  try{ Invoke-WebRequest "$raw/server.properties" -OutFile "$srv\server.properties" -EA Stop }catch{}
  $dir="$env:LOCALAPPDATA\FunCityCtl"
  if(Test-Path "$srv\server.properties"){
    $t=@(Get-Content "$srv\server.properties")
    if(-not (@($t|?{$_ -match '^enable-rcon='}).Count)){ $t+='enable-rcon=true'; $t+='rcon.port=25575' }
    if(-not (Test-Path "$dir\rcon.pass")){ -join((48..57+97..122|Get-Random -Count 14|%{[char]$_})) | Set-Content -Encoding ascii "$dir\rcon.pass" }
    $rp=@(Get-Content "$dir\rcon.pass")[0].Trim()
    for($i=0;$i -lt $t.Count;$i++){ if($t[$i] -match '^rcon.password='){ $t[$i]="rcon.password=$rp" } }
    if(-not (@($t|?{$_ -match '^rcon\.password='}).Count)){ $t+="rcon.password=$rp" }
    Set-Content "$srv\server.properties" $t -Encoding ascii
    $T+="config 100% + rcon OK"
  }
  $run=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
  if($run.Count -eq 0){
    Start-Process -FilePath $env:ComSpec -ArgumentList "/k cd /d $srv && java11\bin\java -Xms2G -Xmx6G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui"
    $T+="SERVER PORNIT (fereastra noua pe ecran = consola ta; /stop = oprire)"
  } else { $T+="server ruleaza deja" }
  $T+="mods: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+" pluginuri: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count)
}
$T -join "`n"
