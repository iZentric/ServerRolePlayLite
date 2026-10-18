# pcmd V5: RCON + playit (adresa publica) + verificare — ruleaza paznicul dupa v4
$ErrorActionPreference='Continue'
$T=@(); $sw=[Diagnostics.Stopwatch]::StartNew()
function L($m){ $script:T += ("[{0:n0}s] {1}" -f $sw.Elapsed.TotalSeconds,$m) }
$srv=$null
foreach($c in @('C:\FunCityServer','D:\FunCityServer','E:\Administrator\Desktop\FunCity\server')){ if(Test-Path "$c\FunCity-1.16.5-b1.0827.jar"){ $srv=$c; break } }
if(-not $srv){ L "EROR: nici un server cu jar complet gasit (v4 mai lucreaza?)"; $T -join "`n"; exit 0 }
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
