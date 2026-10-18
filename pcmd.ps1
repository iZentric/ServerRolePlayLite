# V9: omoara extractorii-fantoma care fură CPU (v7 vechi/Expand-Archive), apoi continuă
$ErrorActionPreference='Continue'
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { ($_.CommandLine -match 'fs\.zip|fsx|Expand-Archive|ZipFile') -and ($_.ProcessId -ne $PID) } | ForEach-Object { try{ Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }catch{} }
Get-Process curl,git,java -EA SilentlyContinue | Where-Object { $_.Id -ne $PID } | ForEach-Object { try{ Stop-Process -Id $_.Id -Force -EA SilentlyContinue }catch{} }
Remove-Item -Recurse -Force -EA SilentlyContinue "$env:TEMP\fsx"
# pcmd V8: doctor + paznic fortat + status complet (ruleaza automat dupa v7)
$ErrorActionPreference='Continue'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
$dir="$env:LOCALAPPDATA\FunCityCtl"
New-Item -ItemType Directory -Force $dir | Out-Null
# 1) cheia - fortam existenta
if(-not (Test-Path "$dir\token.txt")){
  $tk=''; try{ $tk=(Get-Clipboard).Trim() }catch{}
  if($tk -match '^github_pat_[A-Za-z0-9_]{20,}'){ [IO.File]::WriteAllText("$dir\token.txt",$tk); L "cheia: din clipboard" } else { L "cheia: NICAIRI" }
} else { L "cheia: fisier OK" }
# 2) paznicul - mereu reinstall (idempotent)
$tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
if($tok -match '^github_pat_'){
@'
$ErrorActionPreference='Continue'
$dir="$env:LOCALAPPDATA\FunCityCtl"
$tok=@(Get-Content "$dir\token.txt" -EA SilentlyContinue)[0].Trim()
$H=@{ Authorization="token $tok"; Accept="application/vnd.github+json"; "User-Agent"="fctl" }
$repo="iZentric/ServerRolePlayLite"; $ref="arena/9bbcb24f-serverroleplaylite"
$last=""
try{ $last=((Invoke-RestMethod "https://api.github.com/repos/$repo/contents/pcmd.ps1?ref=$ref" -Headers $H -EA Stop).content -replace "\s","") }catch{}
function Put($path,$txt){
  $sha=$null
  try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/$path" -Headers $H -EA Stop).sha }catch{}
  $b=@{ message="paznic"; content=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($txt)); branch=$ref }
  if($sha){ $b.sha=$sha }
  for($k=0;$k -lt 3;$k++){
    try{ Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/$repo/contents/$path" -Headers $H -ContentType "application/json" -Body ($b|ConvertTo-Json -Compress -Depth 4) -EA Stop | Out-Null; return }catch{ Start-Sleep 2; try{ $sha=(Invoke-RestMethod "https://api.github.com/repos/$repo/contents/$path" -Headers $H -EA Stop).sha; $b.sha=$sha }catch{} }
  }
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
  }catch{ Start-Sleep 5 }
  Start-Sleep 1
}
'@ | Set-Content -Encoding ascii "$dir\fctl.ps1"
  "CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $dir\fctl.ps1"", 0, False" | Set-Content -Encoding ascii "$dir\fctl.vbs"
  schtasks /Create /TN FunCityCtl /TR "wscript.exe \`"$dir\fctl.vbs\`"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
  $fcp=@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -EA SilentlyContinue | Where-Object { $_.CommandLine -match 'fctl\.ps1' })
  if($fcp.Count -eq 0){ Start-Process -FilePath "$dir\fctl.vbs"; L "paznic 1s: PORNIT ACUM" } else { L "paznic: traia deja" }
}
# 3) stare server
$srv=$null
foreach($c in @('C:\FunCityServer','D:\FunCityServer','E:\Administrator\Desktop\FunCity\server')){ if(Test-Path "$c\FunCity-1.16.5-b1.0827.jar"){ $srv=$c; break } }
if($srv){
  L "server la: $srv"
  L ("moduri: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+" pluginuri: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count))
  if(Test-Path "$srv\world\level.dat"){ L "world: OK" } else { L "world: LIPSA" }
  $jp=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
  if($jp.Count -gt 0){ L "java: RULEAZA pid $($jp[0].Id)" } else { L "java: nu ruleaza -> il pornesc"; Start-Process -FilePath "$srv\watchdog.vbs" -EA SilentlyContinue }
  try{ $tcp=New-Object Net.Sockets.TcpClient; $tcp.Connect('127.0.0.1',25565); L "port 25565: DESCHIS"; $tcp.Close() }catch{ L "port 25565: inchis (incă boot?)" }
  L ("boot.log: " + ((Get-Content "$srv\logs\boot.log" -Tail 1 -EA SilentlyContinue)))
  if(Test-Path "$srv\playit.exe"){ L "playit: prezent" } else { L "playit: absent" }
  if(Test-Path "$dir\rcon.pass"){ L "rcon: setat" }
} else { L "server: JAR LIPSA - v7 n-a terminat (vezi raportul lui)" }
L "v8 gata"
$T -join "`n"
