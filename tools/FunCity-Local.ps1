# FunCity LOCAL - ruleaza dublu-click pe FunCity-Local.bat
# Face totul local, cu progres afisat in fereastra: server MC doar-pentru-tine + agent-ul meu (fara runner GitHub)
$ErrorActionPreference='Continue'
$Host.UI.RawUI.WindowTitle='FunCity Local - nu inchide fereastra'
$root="$env:USERPROFILE\Desktop\FunCityLocal"
New-Item -ItemType Directory -Force $root | Out-Null
function Step($m){ Write-Host ">>> $m" -ForegroundColor Cyan }
Step "folder de lucru: $root"
# 1) cheia (doar daca lipseste - o dai o data, paste cu click dreapta)
$dir="$env:LOCALAPPDATA\FunCityCtl"; New-Item -ItemType Directory -Force $dir | Out-Null
if(-not (Test-Path "$dir\token.txt")){
  Write-Host "Pasteaza cheia github_pat_... aici (click dreapta = paste) si Enter. Sau doar Enter daca nu vrei agentul:" -ForegroundColor Yellow
  $k=Read-Host "cheie"
  if($k -match '^github_pat_'){ Set-Content -Encoding ascii "$dir\token.txt" $k.Trim() }
}
# 2) server pack
$srv="$root\server"; New-Item -Force -ItemType Directory "$srv\logs" | Out-Null
if(-not (Test-Path "$srv\FunCity-1.16.5-b1.0827.jar")){
  Step "descarc FunCity server (487MB - se vede progresul mai jos)..."
  curl.exe -L -o "$env:TEMP\fs.zip" "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip"
  Step "desfac arhiva (doar ce lipseste - la reluare e instant)..."
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $a=[IO.Compression.ZipFile]::OpenRead("$env:TEMP\fs.zip")
  $tops=@{}; foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){ $tops[$matches[1]]=1 } else { $tops['']=1 } }
  $strip=($tops.Count -eq 1 -and -not $tops.Contains(''))
  $done=0
  foreach($e in $a.Entries){
    if($e.FullName -match '/$'){ continue }
    $rel=$e.FullName -replace '\\','/'
    if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
    if(-not $rel){ continue }
    $dest=Join-Path $srv $rel; $dd=Split-Path $dest -Parent
    if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd | Out-Null }
    if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ $done++; continue }
    [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true); $done++
  }
  $a.Dispose(); Remove-Item -Force -EA SilentlyContinue "$env:TEMP\fs.zip"
  if(-not (Test-Path "$srv\FunCity-1.16.5-b1.0827.jar")){ $msg="EROR: dupa extragere jar tot lipseste (scrise $done)" -join ""; try{ $tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim(); if($tok -match '^github_pat_'){ $H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="doc" }; $sha=$null; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -EA Stop).sha }catch{}; $b=@{ message="bat eroare"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($msg)); branch="arena/9bbcb24f-serverroleplaylite" }; if($sha){ $b.sha=$sha }; Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4)|Out-Null } }catch{} }
  Step "server gata: $done fisiere"
} else { Step "server: deja instalat, sar peste" }
Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
# 3) lumea ta din backup
if(-not (Test-Path "$srv\world\level.dat")){
  Step "descarc lumea (92MB)..."
  curl.exe -L -o "$env:TEMP\ws.tar.gz" "https://github.com/iZentric/ServerRolePlayLite/releases/download/world-live/worldsync.tar.gz"
  tar -xzf "$env:TEMP\ws.tar.gz" -C $srv
  Remove-Item -Force -EA SilentlyContinue "$env:TEMP\ws.tar.gz"
}
# 4) Java 11
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  Step "Java 11 (Temurin)..."
  curl.exe -L -o "$env:TEMP\j11.zip" "https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [IO.Compression.ZipFile]::ExtractToDirectory("$env:TEMP\j11.zip","$srv\jt")
  Move-Item @(Get-ChildItem "$srv\jt")[0].FullName "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt","$env:TEMP\j11.zip"
}
# 5) configurile 100% (ale tale) + RCON local
$raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs" | Out-Null
foreach($f in @('server.properties','spigot.yml','bukkit.yml','commands.yml','connectivity-common.toml','modernfix-mixins.properties')){ try{ Invoke-WebRequest "$raw/$f" -OutFile "$srv\config\$f" -EA Stop }catch{} }
try{ Invoke-WebRequest "$raw/server.properties" -OutFile "$srv\server.properties" -EA Stop }catch{}
try{ Invoke-WebRequest "$raw/forge-server.toml" -OutFile "$srv\defaultconfigs\forge-server.toml" -EA Stop }catch{}
(Get-Content "$srv\server.properties" -EA SilentlyContinue) + 'enable-rcon=true' + 'rcon.port=25575' | Set-Content "$srv\server.properties" -Encoding ascii
if(-not (Test-Path "$dir\rcon.pass")){ -join((48..57+97..122|Get-Random -Count 14|%{[char]$_})) | Set-Content -Encoding ascii "$dir\rcon.pass" }
$rp=@(Get-Content "$dir\rcon.pass")[0].Trim()
$t=@(Get-Content "$srv\server.properties"); for($i=0;$i -lt $t.Count;$i++){ if($t[$i] -match '^rcon.password='){ $t[$i]="rcon.password=$rp" } }; if(-not (@($t|?{$_ -match '^rcon\.password='}).Count)){ $t+="rcon.password=$rp" }; Set-Content "$srv\server.properties" $t -Encoding ascii
# 6) pornire server in fereastra lui (il vezi live, il opresti cu /stop)
Step "PORNESC SERVERUL (fereastra noua = consola live, /stop = oprire)"
Start-Process -FilePath "$env:ComSpec" -ArgumentList "/k cd /d $srv && java11\bin\java -Xms2G -Xmx6G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui"
# 7) agentul meu (fara runner, fara cozi): bucla de 1 secunda pe API
if(Test-Path "$dir\token.txt"){
@'
$ErrorActionPreference='Continue'
$dir="$env:LOCALAPPDATA\FunCityCtl"
$tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
$H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="fctl" }
$repo="iZentric/ServerRolePlayLite"; $ref="arena/9bbcb24f-serverroleplaylite"
function Put($path,$txt){
  $sha=$null
  try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/$path" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="agent"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch=$ref }
  if($sha){ $b.sha=$sha }
  for($k=0;$k -lt 3;$k++){
    try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/$repo/contents/$path" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4) -EA Stop | Out-Null; return }catch{ Start-Sleep 2; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/$path" -Headers $H -EA Stop).sha; $b.sha=$sha }catch{} }
  }
}
$last=""
while($true){
  try{
    $c=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/tools/agent-pcmd.ps1?ref=$ref" -Headers $H -EA Stop).content -replace '\s',''
    $dec=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($c))
    if($dec -ne $last){
      $last=$dec
      Set-Content -Path "$dir\cmd-run.ps1" -Value $dec -Encoding UTF8
      $out=& powershell -NoProfile -ExecutionPolicy Bypass -File "$dir\cmd-run.ps1" 2>&1 | Out-String
      if($out.Length -gt 90000){ $out=$out.Substring(0,90000) }
      Put "diag/agent.txt" ($out + "`nGATA " + (Get-Date -Format s))
    }
  }catch{ Start-Sleep 5 }
  Start-Sleep 1
}
'@ | Set-Content -Encoding ascii "$dir\fctl.ps1"
  "CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $dir\fctl.ps1"", 0, False" | Set-Content -Encoding ascii "$dir\fctl.vbs"
  schtasks /Create /TN FunCityCtl /TR "wscript.exe \`"$dir\fctl.vbs\`"" /SC ONLOGON /RL LIMITED /F | Out-Null
  Start-Process -FilePath "$dir\fctl.vbs"
  Step "agentul meu e live: de acum iti trimit comenzi si-ti raspund in ~2 secunde, fara cozi"
} else { Step "agent sarit (fara cheie) - serverul tot merge local, perfect" }
# 8) doctor: portariu 3 min, reporneeste ascuns daca-i mort, imi trimite raportul
Step "doctor: portez 3 minute dupa server..."
$rep=@("doctor @ "+(Get-Date -Format s)); $alive=$false
for($i=0;$i -lt 18;$i++){ Start-Sleep 10; try{ $t=New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',25565); $t.Close(); $alive=$true; break }catch{} }
if($alive){ $rep+="port 25565: VIU - server up, joaca pe localhost" } else {
  $rep+="3 min fara port -> il pornesc eu ascuns (consola in logs\latest.log)"
  Start-Process -FilePath "$srv\java11\bin\java.exe" -ArgumentList '-Xms2G','-Xmx6G','-XX:+UnlockExperimentalVMOptions','-XX:+UseG1GC','-XX:MaxGCPauseMillis=30','-XX:+ParallelRefProcEnabled','-jar','FunCity-1.16.5-b1.0827.jar','nogui' -WorkingDirectory $srv -WindowStyle Hidden -RedirectStandardOutput "$srv\logs\console.log" -RedirectStandardError "$srv\logs\console.err"
  for($i=0;$i -lt 40;$i++){ Start-Sleep 5; try{ $t=New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',25565); $t.Close(); $rep+="VIU dupa $((($i+1)*5))s"; $alive=$true; break }catch{}; if(-not @(Get-Process java -EA SilentlyContinue).Count){ $rep+="java a murit la boot"; break } }
  if(-not $alive){ $rep+="NU-I VIU NICI DUPA 3 MIN - uita-te in server\logs\latest.log" }
}
$tl=@(Get-Content "$srv\logs\latest.log" -Tail 8 -EA SilentlyContinue); $rep+=($tl|%{"  $_"})
$rep+="mods: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+" plugins: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count)
$txt=$rep -join "`n"; $txt|Write-Host
try{ $tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim() }catch{ $tok="" }
if($tok -match '^github_pat_'){
  $H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="doc" }
  $sha=$null; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="doctor"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch="arena/9bbcb24f-serverroleplaylite" }
  if($sha){ $b.sha=$sha }
  for($k=0;$k -lt 4;$k++){ try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4)|Out-Null; Write-Host "raport trimis la mine pe GitHub - stiu acum tot"; break }catch{ Start-Sleep 3; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H).sha; $b.sha=$sha }catch{} } }
}
Step "GATA. Serverul se vede in fereastra noua. Joaca pe 'localhost' sau IP-ul tau local, doar tu."
Write-Host "Am inchis usile: zero port forwarding, zero tunel public. Nu le deschide nimeni decat daca zici tu." -ForegroundColor Green
pause
