$srv="$env:USERPROFILE\Desktop\FunCityLocal\server"; $r=@()
$jp=@(Get-Process java -EA SilentlyContinue | Where-Object { $_.Path -like "*FunCityLocal*" })
if($jp.Count){ $r+="server: VIU | procese java: $($jp.Count) | memorie: $([math]::Round(($jp|Measure-Object WorkingSet64 -Sum).Sum/1MB))MB" } else { $r+="server: NU RULEAZA" }
try{ $t=New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',25565); $r+="port 25565: DESCHIS"; $t.Close() }catch{ $r+="port 25565: inchis" }
$log="$srv\logs\latest.log"
if(Test-Path $log){ $tail=@(Get-Content $log -Tail 6); $r+="log:"; $r+=($tail|ForEach-Object{ "  "+$_ }) } else { $r+="log: lipseste (nu a apucat sa scrie)" }
$r+="mods: "+(@(Get-ChildItem "$srv\mods" -Filter *.jar -EA SilentlyContinue).Count)+" | pluginuri: "+(@(Get-ChildItem "$srv\plugins" -Filter *.jar -EA SilentlyContinue).Count)+" | world: $(Test-Path "$srv\world\level.dat")"
$r -join "`n"
