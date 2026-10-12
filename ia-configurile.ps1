# Colecteaza config-urile serverelor de RP, ca sa le pot citi fara sa-mi dai date de jucatori.
# Ce face: intr-un singur configuri-rp.tar.gz pune doar config-urile (properties/yml/toml/conf/json/txt),
# un inventar de JAR-uri (nume + marime + hash, NU binarele) si logurile CURATATE de IP-uri, UUID-uri
# si nume de jucatori. Excluziile sunt hard: world*/level.dat (acolo e seed-ul), usercache/ops/whitelist/bans,
# server.log, backup-uri, resourcepacks.
#
#   python3 colecteaza-configuri.py
# sau, pe o lista de servere:
#   python3 colecteaza-configuri.py server1 server2 server3
#
# Iesii: configuri-rp.tar.gz in folderul curent. Daca trece de 25 MB, il imparte el in bucati de
# 20 MB (configuri-rp.tar.gz.part-aa, -ab, ...) pe care le trimiți pe rand.
$ErrorActionPreference = "Stop"
$py = (Get-Command python -ErrorAction SilentlyContinue), (Get-Command py -ErrorAction SilentlyContinue) |
      Where-Object { $_ } | Select-Object -First 1
if (-not $py) { Write-Host "Nu gasesc Python. instaleaza din python.org sau Trimite-mi folderele direct."; exit 1 }
& $py.Source -c "print('ok')" 2>$null | Out-Null
$tmp = Join-Path $env:TEMP "colecteaza-configuri.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/9bbcb24f-serverroleplaylite/colecteaza-configuri.py" -OutFile $tmp
& $py.Source $tmp @args
