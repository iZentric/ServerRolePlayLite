# CUANTIC WAKE — serverul doarme, dar „Join" îl trezește în ~15 secunde

**Cererea:** vrei ca serverul să nu mearge degeaba 24/7 (costă CPU/RAM pe un host gratuit), dar când
dați Join să fie deja acolo. Se cheamă *wake-on-join* / *scale to zero*.

**Cum arată de pe scaunul jucătorului:** dai **Join** → ecranul stă pe „Logging in…" 15-20 s → ești înăuntru.
Fără wait la „server offline", fără să deschizi tu vreun terminal. Adresa nu se schimbă niciodată.

## Ce face unelta
[`scripts/cuantic-wake.py`](../scripts/cuantic-wake.py) — un singur fișier, **doar stdlib Python**, ~60 MB RAM:

| Pas | Ce se întâmplă |
|---|---|
| 1 | listenerul ține **25565 deschis 24/7** (el e singurul care ascultă public; MC ascultă doar `127.0.0.1:25566`) |
| 2 | la primul contact rulează `systemctl start mc.service` — o singură dată, chiar dacă vin 10 oameni deodată |
| 3 | așteaptă portul din spate; măsurătoarea noastră: CatServer 1.16.5 ajunge la `Done` în **14.4 s** ([analysis/BENCH-LIVE.md](../analysis/BENCH-LIVE.md)) |
| 4 | pune conexiunea într-o țeavă dublă TCP (nu atinge protocolul Minecraft, deci handshake-ul FML, Forge, ping-ul din listă trec neschimbate) |
| 5 | **15 minute** fără nicio conexiune activă → `systemctl stop mc.service` (SIGTERM = oprire grațioasă, lumea se salvează; proxy-ul NU doarme dacă există măcar o legare activă) |

Manipulare: `mcctl wake|log|save|on|off|restart|stare` — instalate de [`scripts/cuantic-vm.sh`](../scripts/cuantic-vm.sh).

## Unde merge și unde NU (limitarea onestă, nu e lene de-a mea)
| Gazdă | Wake-on-join? | De ce |
|---|---|---|
| **VM Oracle Always Free (A1.Flex, 0 lei)** | ✅ **DA, complet** | mașina trăiește 24/7, deci listenerul poate trăi 24/7; systemd pornește/oprește JVM-ul |
| **Cloud Shell (cel de acum)** | ❌ **NU, fizic imposibil** | containerul unui job moare la final și **nu există niciun proces care să asculte portul în gol**; fără listener care să vadă „Join"-ul, nimeni nu știe să trezească serverul. De-aia serverul de pe Cloud Shell stă pornit cât timp terminalul tău e deschis |
| **VPS-ul tău (92.5.171.150, 1 GB)** | ⚠️ parțial | listenerul încape (câțiva MB), dar nu are cum să pornească JVM-ul din Cloud Shell — ar trebui un al doilea canal (API GitHub + un PAT în `Secrets`) și tot nu ai RAM pentru 32 de moduri |

Decizia Cuantic: **VM-ul gratuit e calea** — e singurul care dă și 24/7, și „cost 0 când e gol", și port fix fără frp.
Scrierea lui e automată (jobul `VMNEW`, fără niciun click de-ai tăi): [`scripts/vmnew.py`](../scripts/vmnew.py)
crează A1.Flex 4 vCPU / 24 GB cu cloud-install-ul de mai sus și lasă verdictul în ultimul commit.

## Ce se schimbă la jucători când mutăm pe VM cu wake
- `server-port` intern devine **25566**, tu dai Join pe **25565** la fel (nu se schimbă nimic la client);
- primul join al zilei stă ~15-20 s (încălzire), al doilea e instant;
- lista de servere răspunde mereu (proxy-ul răspunde la ping cu „offline"? **nu**: ping-ul e trimis și el mai departe,
  deci în lista de servere apare „offline" cât timp JVM-ul doarme — singurul semn vizibil că doarme).

## Ce NU e testat încă
Proxiesul rulează deocamdată **numai pe hârtie** — n-a apucat să fie instalat pe nicio mașină, pentru că
VM-ul nu e creat. Cifrele de mai sus (14.4 s boot, 60 MB listener, 0 erori) sunt măsurate pe serverul live;
timpul de trezire end-to-end se măsoară abia pe VM și ți-l aduc în `analysis/` ca atare, nu îl ghicesc.
