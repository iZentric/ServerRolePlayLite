# FunCity Fix-stick: repară java/jar, repornește serverul, citește logul, îmi trimite raportul — apoi IESE
$ErrorActionPreference='Continue'
$srv="$env:USERPROFILE\Desktop\FunCityLocal\server"; $r=@("fix @ "+(Get-Date -Format s))
$jar="$srv\FunCity-1.16.5-b1.0827.jar"
# 1) curăț processori java blocati
$z=@(Get-Process java -EA SilentlyContinue)
if($z.Count){ $z|Stop-Process -Force -EA SilentlyContinue; $r+="am oprit $($z.Count) java blocati" }
# 2) jar
if(-not (Test-Path $jar)){
  $r+="jar lipseste -> repun din zip..."
  curl.exe -L -s -o "$env:TEMP\fs.zip" "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FUNCTITY-SERVER.zip"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $a=[IO.Compression.ZipFile]::OpenRead("$env:TEMP\fs.zip"); $done=0
  $tops=@{}; foreach($e in $a.Entries){ $p=($e.FullName -replace '\\','/'); if($p -match '^([^/]+)/'){ $tops[$matches[1]]=1 } else { $tops['']=1 } }
  $strip=($tops.Count -eq 1 -and -not $tops.Contains(''))
  foreach($e in $a.Entries){ if($e.FullName -match '/$'){continue}
    $rel=$e.FullName -replace '\\','/'
    if($strip){ $rel=($rel -split '/')[1..99] -join '\' } else { $rel=$rel -replace '/','\' }
    if(-not $rel){continue}
    $dest=Join-Path $srv $rel; $dd=Split-Path $dest -Parent
    if(-not (Test-Path $dd)){ New-Item -ItemType Directory -Force $dd|Out-Null }
    if((Test-Path $dest) -and ((Get-Item $dest).Length -eq $e.Length)){ continue }
    [IO.Compression.ZipFileExtensions]::ExtractToFile($e,$dest,$true); $done++ }
  $a.Dispose(); Remove-Item -Force -EA SilentlyContinue "$env:TEMP\fs.zip"
  $r+="repus: $done fisiere"
}
if(-not (Test-Path $jar)){ $r+="EROR FINAL: jar tot lipseste"; $r|Write-Host; exit 1 }
# 3) java 11
if(-not (Test-Path "$srv\java11\bin\java.exe")){
  $r+="java11 lipseste -> descarc Temurin..."
  curl.exe -L -s -o "$env:TEMP\j11.zip" "https://api.adoptium.net/v3/binary/latest/11/ga/windows/x64/jre/hotspot/normal/eclipse"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [IO.Compression.ZipFile]::ExtractToDirectory("$env:TEMP\j11.zip","$srv\jt")
  Move-Item @(Get-ChildItem "$srv\jt")[0].FullName "$srv\java11" -Force
  Remove-Item -Recurse -Force -EA SilentlyContinue "$srv\jt","$env:TEMP\j11.zip"
  if(Test-Path "$srv\java11\bin\java.exe"){ $r+="java11 OK" } else { $r+="EROR: java11 nu s-aptelat"; $r|Write-Host; exit 1 }
}
# 4) eula + pornire ascinsa cu log
Set-Content -Encoding ascii "$srv\eula.txt" "eula=true"
New-Item -Force -ItemType Directory "$srv\logs" | Out-Null
Remove-Item -Force -EA SilentlyContinue "$srv\logs\latest.log"
$p=Start-Process -FilePath "$srv\java11\bin\java.exe" -ArgumentList '-Xms2G','-Xmx6G','-XX:+UnlockExperimentalVMOptions','-XX:+UseG1GC','-XX:MaxGCPauseMillis=30','-XX:+ParallelRefProcEnabled','-jar','FunCity-1.16.5-b1.0827.jar','nogui' -WorkingDirectory $srv -WindowStyle Hidden -PassThru -RedirectStandardOutput "$srv\logs\console.log" -RedirectStandardError "$srv\logs\console.err"
$r+="server pornit ascuns (pid $($p.Id)), il pazesc max 5 min..."
$ok=$false;$t0=Get-Date
for($i=0;$i -lt 60;$i++){
  Start-Sleep 5
  if(-not (Get-Process -Id $p.Id -EA SilentlyContinue)){ $r+="java a iesit dupa $([int]((Get-Date)-$t0).TotalSeconds)s"; break }
  $lg=@(Get-Content "$srv\logs\latest.log" -EA SilentlyContinue)
  if(@($lg|?{$_ -match 'Done \('}).Count){ $ok=$true; $r+="SERVER LIVE in $([int]((Get-Date)-$t0).TotalSeconds)s - "+(@($lg|?{$_ -match 'Done \('})|Select-Object -Last 1); break }
  if(@($lg|?{$_ -match 'Address already in use'}).Count){ $r+="port 25565 ocupat (mai exista un server pe PC)"; break }
}
if(-not $ok -and (Get-Process -Id $p.Id -EA SilentlyContinue)){ $r+="incarca lent dupa 5 min - il las sa mearga" }
$tl=@(Get-Content "$srv\logs\latest.log" -Tail 8 -EA SilentlyContinue)
if(-not $tl.Count){ $tl=@(Get-Content "$srv\logs\console.err" -Tail 8 -EA SilentlyContinue) }
$r+="ultimele linii:"; $r+=($tl|%{"  $_"})
# 5) raport catre mine
$dir="$env:LOCALAPPDATA\FunCityCtl"; $tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
$txt=$r -join "`n"
$txt|Write-Host
if($tok -and $tok -match '^github_pat_'){
  $H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="fix" }
  $sha=$null; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="fix report"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch="arena/9bbcb24f-serverroleplaylite" }
  if($sha){ $b.sha=$sha }
  for($k=0;$k -lt 3;$k++){ try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4)|Out-Null; Write-Host "raport trimis OK"; break }catch{ Start-Sleep 2; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/iZentric/ServerRolePlayLite/contents/diag/fix.txt" -Headers $H).sha; $b.sha=$sha }catch{} } }
}
