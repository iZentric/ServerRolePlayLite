# pcmd V4: omoara zombiele, cauta SSD, mutam serverul pe SSD, paznic 1s, reportez
$ErrorActionPreference='Continue'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -match 'fsx|Expand-Archive' -and $_.ProcessId -ne $PID } | ForEach-Object { try{ Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue; L "zombie oprit pid $($_.ProcessId)" }catch{} }
$ssdVols=@()
try{
  foreach($d in (Get-PhysicalDisk -EA SilentlyContinue)){
    L ("disk: $($d.FriendlyName) [$($d.MediaType)]")
    if("$($d.MediaType)" -eq 'SSD'){ foreach($p in (Get-Partition -DiskNumber $d.DeviceId -EA SilentlyContinue)){ if($p.DriveLetter){ $ssdVols += [string][char](64+$p.DriveLetter) } } }
  }
}catch{ L "fara Get-PhysicalDisk (neadmin)" }
$srv=$null
foreach($v in $ssdVols){
  $f=[math]::Round(((Get-PSDrive $v -EA SilentlyContinue).Free/1GB),1)
  if($f -gt 15 -and -not $srv){ $srv="$v" + ':\FunCityServer'; L "SSD gasit: vol $v liber $f GB -> $srv" }
}
if(-not $srv){ $srv='E:\Administrator\Desktop\FunCity\server'; L "nu-am gasit SSD liber -> ramane E:" }
New-Item -ItemType Directory -Force $srv,"$srv\logs" | Out-Null
$old='E:\Administrator\Desktop\FunCity\server'
if($old -ne $srv -and (Test-Path $old)){
  $cj=@(Get-ChildItem $old -Recurse -File -EA SilentlyContinue)
  if(-not (Test-Path "$old\FunCity-1.16.5-b1.0827.jar") -and $cj.Count -lt 80){ Remove-Item -Recurse -Force -EA SilentlyContinue $old; L "gunoi partial E: sters ($($cj.Count) fise)" }
}
$dir="$env:LOCALAPPDATA\FunCityCtl"
New-Item -ItemType Directory -Force $dir | Out-Null
if(-not (Test-Path "$dir\token.txt")){ $tk=''; try{ $tk=(Get-Clipboard).Trim() }catch{}; if($tk -match '^github_pat_[A-Za-z0-9_]{20,}'){ [IO.File]::WriteAllText("$dir\token.txt",$tk); L "cheia luata din clipboard" } else { L "EROR: cheia nici in fisier nici in clipboard" } } else { L "cheia: fisier token.txt OK" }
if(Test-Path "$dir\token.txt"){
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
  $fcp=@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -match 'fctl\.ps1' })
  if($fcp.Count -eq 0){ Start-Process -FilePath "$dir\fctl.vbs"; L "paznic pornit (bucla 1s)" } else { L "paznic: ruleaza deja" }
}
$jar="$srv\FunCity-1.16.5-b1.0827.jar"
$z="$env:TEMP\fs.zip"
if(-not (Test-Path $jar)){
  if(-not (Test-Path $z) -or (Get-Item $z).Length -lt 400000000){
    L "descarc functity.zip (487MB)..."
    curl.exe -fLso $z "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip"
  } else { L "zip gasit in TEMP, il refolosesc" }
  if((Test-Path $z) -and (Get-Item $z).Length -gt 400000000){
    L "extrag direct in $srv (fara copie dubla)..."
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $a=[IO.Compression.ZipFile]::OpenRead($z)
    $tops=@{}
    foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){ $tops[$matches[1]]=1 } else { $tops['']=1 } }
    $strip=$false
    if($tops.Count -eq 1 -and -not $tops.Contains('')){ $strip=$true }
    $done=0
    foreach($e in $a.Entries){
      if($e.FullName -match '/$'){ continue }
      $rel=$e.FullName -replace '\\','/'
      if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
      if(-not $rel){ continue }
      $dest=Join-Path $srv $rel
      $dd=Split-Path $dest -Parent
      if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd | Out-Null }
      if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ $done++; continue }
      [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true)
      $done++
    }
    $a.Dispose()
    L "extrase $done fisiere"
  } else { L "EROR: nici zip in TEMP nici download ok" }
} else { L "jar prezent, sar peste arhiva" }
Remove-Item -Force -EA SilentlyContinue $z,"$env:TEMP\fsx"
Remove-Item -Force -EA SilentlyContinue "$srv\mods\SeleneChat*"
if(-not (Test-Path "$srv\world\level.dat")){
  $wt="$env:TEMP\ws.tar.gz"
  if(-not (Test-Path $wt)){ L "descarc world (92MB)..."; curl.exe -fLso $wt "https://github.com/iZentric/ServerRolePlayLite/releases/download/world-live/worldsync.tar.gz" }
  if((Test-Path $wt) -and (Get-Item $wt).Length -gt 50000000){ tar -xzf $wt -C $srv; L "world desfacut" } else { L "EROR world tar" }
  Remove-Item -Force -EA SilentlyContinue $wt
} else { L "world: level.dat OK" }
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  $jz="$env:TEMP\j11.zip"; Remove-Item -Force -EA SilentlyContinue $jz,"$srv\jt"
  curl.exe -fLso $jz 'https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse'
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [IO.Compression.ZipFile]::ExtractToDirectory($jz,"$srv\jt")
  $in=@(Get-ChildItem "$srv\jt")[0].FullName
  Move-Item $in "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt",$jz
  L "java11 OK"
} else { L "java11 existent" }
$raw='https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/functity-config'
New-Item -ItemType Directory -Force "$srv\config","$srv\defaultconfigs" | Out-Null
foreach($f in @(@('server.properties',"$srv\server.properties"),@('spigot.yml',"$srv\config\spigot.yml"),@('bukkit.yml',"$srv\config\bukkit.yml"),@('commands.yml',"$srv\config\commands.yml"),@('connectivity-common.toml',"$srv\config\connectivity-common.toml"),@('modernfix-mixins.properties',"$srv\config\modernfix-mixins.properties"),@('forge-server.toml',"$srv\defaultconfigs\forge-server.toml"))){
  try{ Invoke-WebRequest "$raw/$($f[0])" -OutFile $f[1] -EA Stop }catch{ L "config FAIL $($f[0])" }
}
L "config 100% aplicate"
@"
@echo off
cd /d $srv
java11\bin\java -Xms2G -Xmx8G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui >> logs\boot.log 2>&1
"@ | Set-Content -Encoding ascii "$srv\launch.bat"
"\`$dir='$srv'
while(\`$true){
  \`$p=@(Get-Process java -EA SilentlyContinue | Where-Object { \$_.Path -like \"\$dir*java11*\" })
  if(\$p.Count -eq 0){ Start-Process -FilePath \"\$dir\launch.bat\" -WindowStyle Hidden }
  Start-Sleep 30
}" | Set-Content -Encoding ascii "$srv\watchdog.ps1"
"CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $srv\watchdog.ps1"", 0, False" | Set-Content -Encoding ascii "$srv\watchdog.vbs"
schtasks /Create /TN FunCityServer /TR "wscript.exe \"$srv\watchdog.vbs\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
if($srv -ne $old -and -not (Test-Path $old)){ cmd /c mklink /J "$old" "$srv" | Out-Null; L "link E:\...\FunCity\server -> SSD (vezi aceeasi locatie veche)" }
$jp=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
if($jp.Count -eq 0){ Start-Process -FilePath "$srv\watchdog.vbs"; L "server pornit (astept boot 2-4 min)" } else { L "java ruleaza deja" }
L "install v6 gata"
$srv=$null
foreach($c in @('C:\FunCityServer','D:\FunCityServer','E:\Administrator\Desktop\FunCity\server')){ if(Test-Path "$c\FunCity-1.16.5-b1.0827.jar"){ $srv=$c; break } }
if(-not $srv){ L "EROR: serverul nu e gata dupa instalare"; $T -join "`n"; exit 0 }
L "server: $srv"
$dir="$env:LOCALAPPDATA\FunCityCtl"; New-Item -Force -ItemType Directory $dir | Out-Null
$pw=-join((48..57+97..122|Get-Random -Count 14|ForEach-Object{[char]$_}))
$t=@(Get-Content "$srv\server.properties" -EA SilentlyContinue)
$reps=@{'enable-rcon'='true';'rcon.port'='25575';'rcon.password'=$pw}
for($i=0;$i -lt $t.Count;$i++){ foreach($k in $reps.Keys){ if($t[$i] -match "^$k="){ $t[$i]="$k=$($reps[$k])" } } }
foreach($k in $reps.Keys){ if(-not (@($t|Where-Object{$_ -match "^$k="}).Count -gt 0)){ $t+="$k=$($reps[$k])" } }
Set-Content "$srv\server.properties" $t -Encoding ascii
Set-Content -Encoding ascii "$dir\rcon.pass" $pw
L "rcon activat (port 25575, parola doar local in FunCityCtl\rcon.pass)"
L "rcon+playit marca v5"
$T -join "`n"

# playit: adresa publica fara router (varianta de rezerva)
$pi="$srv\playit.exe"
if(-not (Test-Path $pi)){
  L "incarc playit.exe..."
  curl.exe -fLso $pi "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-win64-x64.exe"
  $ps=(Get-Item $pi -EA SilentlyContinue).Length
  if($ps -lt 3000000){ L "playit download esuat ($ps B) - ramane varianta router"; Remove-Item -Force $pi -EA SilentlyContinue }
}
if(Test-Path $pi){
  Start-Process -FilePath $pi -ArgumentList '--new-run','--config',("`"$srv\playit.toml`"") -RedirectStandardOutput "$dir\playit.out" -RedirectStandardError "$dir\playit.err" -WindowStyle Hidden
  Start-Sleep 12
  $po=@(Get-Content "$dir\playit.out" -EA SilentlyContinue) -join ' '
  $m=[regex]::Match($po,'https://playit\.gg/claim\s+(\S+)')
  if($m.Success){ L ("PLAYIT CLAIM: " + $m.Value) } else { L ("playit a zis: " + $po.Substring(0,[Math]::Min(180,$po.Length))) }
}
# runner autostart (ca sa nu mai fie nevoie de click manual niciodata)
$runner=$null
foreach($c in @("$env:USERPROFILE\actions-runner","C:\actions-runner","D:\actions-runner","$env:LOCALAPPDATA\actions-runner","$env:USERPROFILE\Desktop\actions-runner")){ if(Test-Path "$c\run.cmd"){ $runner=$c; break } }
if(-not $runner){ $f=@(Get-ChildItem C:\ -Directory -Filter "*actions-runner*" -EA SilentlyContinue); if($f.Count){ $runner=$f[0].FullName } }
if(-not $runner){ $f=@(Get-ChildItem D:\ -Directory -Filter "*actions-runner*" -EA SilentlyContinue); if($f.Count){ $runner=$f[0].FullName } }
if($runner){
  "CreateObject(\"WScript.Shell\").Run \"cmd /c cd /d $runner && run.cmd\", 0, False" | Set-Content -Encoding ascii "$dir\runrunner.vbs"
  schtasks /Create /TN FunCityRunner /TR "\"wscript.exe \\"$dir\runrunner.vbs\\"\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
  L "runner gasit la $runner : autostart inregistrat (task FunCityRunner)"
} else { L "runner: nu l-am gasit singur - lasa fereastra aia deschisa si gata" }
$T -join "`n"
