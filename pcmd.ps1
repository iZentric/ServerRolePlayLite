$ErrorActionPreference='Continue'
$srv="$env:USERPROFILE\Desktop\FunCityLocal\server"
$dir="$env:LOCALAPPDATA\FunCityCtl"
$r=@("v10 @ "+(Get-Date -Format s))
function Rep{
  $tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
  $txt=$script:r -join "`n"
  if($tok -match '^github_pat_'){
    $H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="v10" }
    $sha=$null; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/pctl.txt" -Headers $H -EA Stop).sha }catch{}
    $b=@{ message="v10"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch="arena/9bbcb24f-serverroleplaylite" }
    if($sha){ $b.sha=$sha }
    for($k=0;$k -lt 4;$k++){ try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/pctl.txt" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4)|Out-Null; break }catch{ Start-Sleep 3; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/pctl.txt" -Headers $H).sha; $b.sha=$sha }catch{} } }
  }
  Write-Output $txt
}
try{ $t=New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',25565); $t.Close()
  $r+="SERVER DEJA VIU pe 25565 - nu ma ating de nimic"
  $tl=@(Get-Content "$srv\logs\latest.log" -Tail 3 -EA SilentlyContinue); $r+=($tl|%{"  $_"})
  Rep; exit 0
}catch{ $r+="port 25565 inchis - pornesc eu" }
$jar="$srv\FunCity-1.16.5-b1.0827.jar"
if(-not (Test-Path $jar)){ $r+="EROR: jar lipseste in $srv"; Rep; exit 0 }
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  $r+="java11 lipseste -> iau de pe adoptium"
  curl.exe -L -s -o "$env:TEMP\j11.zip" "https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [IO.Compression.ZipFile]::ExtractToDirectory("$env:TEMP\j11.zip","$srv\jt")
  Move-Item @(Get-ChildItem "$srv\jt")[0].FullName "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt","$env:TEMP\j11.zip"
}
if(-not (Test-Path "$srv\java11\bin\java.exe")){ $r+="EROR: java11 tot lipseste"; Rep; exit 0 }
Set-Content -Encoding ascii "$srv\eula.txt" "eula=true"
New-Item -Force -ItemType Directory "$srv\logs" | Out-Null
Remove-Item -Force -EA SilentlyContinue "$srv\logs\latest.log"
$p=Start-Process -FilePath "$srv\java11\bin\java.exe" -ArgumentList '-Xms2G','-Xmx6G','-XX:+UnlockExperimentalVMOptions','-XX:+UseG1GC','-XX:MaxGCPauseMillis=30','-XX:+ParallelRefProcEnabled','-jar','FunCity-1.16.5-b1.0827.jar','nogui' -WorkingDirectory $srv -WindowStyle Hidden -PassThru -RedirectStandardOutput "$srv\logs\console.log" -RedirectStandardError "$srv\logs\console.err"
$r+="pornit pid $($p.Id), astept Done..."
$ok=$false;$t0=Get-Date
for($i=0;$i -lt 72;$i++){
  Start-Sleep 5
  if(-not (Get-Process -Id $p.Id -EA SilentlyContinue)){ $r+="java a iesit dupa $([int]((Get-Date)-$t0).TotalSeconds)s"; break }
  $lg=@(Get-Content "$srv\logs\latest.log" -EA SilentlyContinue)
  if(@($lg|?{$_ -match 'Done \('}).Count){ $ok=$true; $r+="SERVER LIVE in $([int]((Get-Date)-$t0).TotalSeconds)s"; break }
}
$tl=@(Get-Content "$srv\logs\latest.log" -Tail 10 -EA SilentlyContinue)
if(-not @($tl).Count){ $tl=@(Get-Content "$srv\logs\console.err" -Tail 10 -EA SilentlyContinue) }
$r+="log:"; $r+=($tl|%{"  $_"})
Rep
Start-Sleep 1800
