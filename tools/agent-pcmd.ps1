# agent-pcmd - prima comanda: status complet (se rescrie de la mine cand vreau actiuni)
$ErrorActionPreference='Continue'
$root="$env:USERPROFILE\Desktop\FunCityLocal"; $srv="$root\server"
$r=@()
if(Test-Path "$srv\FunCity-1.16.5-b1.0827.jar"){ $r+="jar: OK" } else { $r+="jar: LIPSA (instaleaza cu FunCity-Local.bat)" }
$r+="mods: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+" pluginuri: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count)
if(Test-Path "$srv\world\level.dat"){ $r+="world: OK" } else { $r+="world: LIPSA" }
$jp=@(Get-Process java -EA SilentlyContinue|?{$_.Path -like "$srv*"})
if($jp.Count){ $r+="server: RULEAZA (memorie $([math]::Round($jp[0].WorkingSet64/1MB))MB)" } else { $r+="server: oprit (ruleaza bat din nou)" }
try{ $t=New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',25565); $r+="port 25565: DESCHIS (doar local)"; $t.Close() }catch{ $r+="port 25565: inchis" }
$r+="agent: PAZNIC 1s LIVE - scrie-mi si raspund in 2 secunde"
$r -join "`n"
