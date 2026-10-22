# FunCity RP (mafii, oraș, mașini) — cost real vs. „mod degeaba” (22.10.2026)

**Nu există test al „întregului internet” sau benchmark de jucători reali aici.** Comparația este delimitată de Minecraft/Forge 1.16.5, inventarul public al celor [28 moduri țintă](FUNCITY-SERVER-TARGET-28.json), [34 moduri/13 pluginuri numărate pe PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39696088517) (șase moduri suplimentare încă neidentificate în raportul agregat), versiuni originale și compatibilitate RP. Nu schimbăm live, profil, client, lume, JAR-uri ori pluginuri private. Nu numim „degeaba” un mod care păstrează obiecte, mașini, arme, economie, voice, ID-uri în salvare sau dependențe.

## Probe executabile, cu limite declarate

- [Canary Chunk Sending](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39704706580): un JAR server-only eligibil (Forge 1.16.5, file ID 4583202, SHA pin) a pornit de două ori cu 29 moduri/6 pluginuri pe CatServer oficial; **niciun client/packet throughput**, deci nu s-a adăugat serverului.
- [Ablation AI/rețete/spawn](../.github/workflows/rp-mod-cost-ab.yml): aceeași mașină GitHub, Java 17, motor oficial și cele 28 JAR-uri istorice cu SHA verificat; 6 pluginuri; ordine **A/I/R/K/K/R/I/A**, pe copii ale aceleiași lumi generate, 80 zombie. A=28 intact, I=minus AI Improvements, R=minus FastSuite + FastWorkbench + Placebo *împreună* (dependențe), K=minus Ksyxis. Două repetări per braț, CPU 30 s, RSS mediană, timpul pornirii, media `forge tps`; numerice numai dacă trec toate. Acest test nu exercită crafting real, NPC de mafie, mașini, voice, jucători sau lumea pregenerată RP; **nu poate valida eliminarea rețetelor sau capacitatea**. Fără TPS p95/p99 din fiecare tick.
- [Test de entități mașină](../.github/workflows/parked-vehicle-ab.yml): pe copie, 16 entități modate `vehicle:smart_car` **staționare**, confirmate numeric de comanda de scor după summon; brațe R/N/N/R, RoadRunner cu/fără, aceeași lume/platformă generată și 6 pluginuri. Niciun șofer, traficul unui client, coliziuni în oraș sau pachete către clienți: nu confundăm mașinile parcate cu 16 jucători la volan. [Sursa autorului 1.16.X, `ModEntities`](https://github.com/MrCrayfish/MrCrayfishVehicleMod/blob/1.16.X/src/main/java/com/mrcrayfish/vehicle/init/ModEntities.java) declară `smart_car`; [VehicleUtil](https://github.com/MrCrayfish/MrCrayfishVehicleMod/blob/1.16.X/src/main/java/com/mrcrayfish/vehicle/util/VehicleUtil.java) setează tracking 256/update interval 1 pentru tipurile de vehicule în acea ramură. Valoarea exactă din JAR-ul istoric trebuie confirmată separat; **fără clienți, costul efectiv al rețelei nu poate fi măsurat**.

### Statistici primite: [rularea 39706471206](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39706471206) — **PASS**, 8/8 brațe

Unități: boot secunde până la `Done`; CPU = secunde de CPU consumate în fereastra de ~30 secunde după 80 zombie; RSS MiB mediană în fereastră; tick = **medie** `forge tps` ms, nu distribuția tickurilor. Valorile sunt cele două observații brute, nu promisiuni pe lumea FunCity.

| Braț și JAR-uri excluse numai din copia temporară | Boot s | CPU s/~30 s | RSS MiB | tick mediu ms |
|---|---|---|---|---|
| A, 28 intact | 30,30 / 28,81 | 1,40 / 1,24 | 1829 / 1910 | 0,34 / 0,37 |
| I, −AI Improvements | 28,55 / 30,55 | 1,35 / 1,46 | 1855 / 2039 | 0,33 / 0,45 |
| R, −FastSuite, FastWorkbench, Placebo | 30,81 / 31,05 | 1,12 / 1,37 | 1764 / 1402 | 0,27 / 0,53 |
| K, −Ksyxis | 42,07 / 42,57 | 3,00 / 2,62 | 2096 / 1828 | 1,18 / 1,00 |

**Interpretare limitată:** Ksyxis arată un **semnal repetat de beneficiu** în această lume generată fără jucători (boot cu ~12–14 s mai rapid și tick mediu mai mic când e prezent). Nu scoatem Ksyxis din ținta de test. Dacă centrul orașului este spawnul activ, efectul poate fi diferit: trebuie confirmat pe copie cu client și pluginuri complete. AI Improvements și triada de rețete au probe suprapuse/inconsecvente în sarcina *fără NPC modat sau crafting*; niciun verdict de „inutil” sau de ștergere. RSS de la grupul R oscilează mult chiar între două rulări. Nu avem p95/p99 ori consumul raportat per JAR.

### Statistici mașini parcate: [rularea 39707192281](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39707192281) — **PASS**, 4/4 brațe

16 entități `vehicle:smart_car` confirmate în fiecare probă, pe aceeași platformă/lume generată, șase pluginuri. Fără șoferi sau pachete de poziție spre clienți:

| Braț | Boot s | CPU s/~30 s | RSS MiB | tick mediu ms |
|---|---|---|---|---|
| R, 28 cu RoadRunner | 25,80 / 27,80 | 0,89 / 0,85 | 1990 / 1622 | 0,34 / 0,33 |
| N, 27 fără RoadRunner | 27,04 / 27,05 | 1,07 / 0,98 | 1802 / 2337 | 0,57 / 0,45 |

**Interpretare:** RoadRunner are CPU și tick mediu mai mici în **ambele** observații cu vehicule *nemişcate*, deci nu îl scoatem doar pentru a scădea numărul de JAR-uri. RSS are variație mare, nu acordăm câștig RAM. Mișcarea, condusul, coliziunile, traficul de rețea, lumea cu clădiri și mafii și celelalte șapte pluginuri rămân netestate; cifrele de mai sus **nu** dau plafon de jucători.

**Regulă de interpretare:** două probe de 30 s și o medie `forge tps` arată doar comportamentul laboratorului; diferența poate fi zgomot de JVM/GC, ordine, configurația din template sau lumea sintetică. Nu scoatem automat moduri când rezultatele sunt apropiate, nici nu promovăm un mod pentru un singur număr bun. Datele care *pot* conduce la o decizie: profil al hotspotului pe copia privată a lumii pregenerate, inventar exact al celor șase JAR-uri extra și al celor 13 pluginuri, două sesiuni cu clienți Forge reali conduși prin oraș, cu p95/p99 tick, FPS p5, CPU thread principal, RSS/GC, disc, upload/UDP, număr de vehicule și interacțiuni mafie/economie. Protocolul cu praguri: [capacitate RP](CAPACITATE-FUNCITY-RP.md).

## Prioritizare pentru oraș, mafii și trafic

| Componentă | Dovezi și acțiune sigură |
|---|---|
| Mașini, arme, voice, mobilier, drumuri, economia orașului | Conținut/funcții RP; păstrăm perechile client-server și bibliotecile obligatorii. Asseturile mari sau 0 acțiuni în idle **nu** sunt dovadă că pot fi șterse din lumea sau inventarele existente. Prioritare: coliziuni și pachete la condus, update-uri de mobilier/block entities, proiectile, pluginuri economie și voice UDP. |
| AI Improvements | [Fișierul exact 1.16.5](https://www.curseforge.com/minecraft/mc-mods/ai-improvements/files/3798940) există; relevanța depinde de AI/NPC și mobj. Testul de zombie poate măsura o pistă AI vanilla, nu justifică generalizarea la NPC/plugin ori vehicule. |
| FastSuite / FastWorkbench / Placebo | [FastSuite](https://www.curseforge.com/minecraft/mc-mods/fastsuite) vizează rețete, [FastWorkbench](https://github.com/Shadows-of-Fire/FastWorkbench) vizează crafturile în masă. *Placebo este dependență declarată* a ambelor JAR-uri istorice: numai îndepărtarea întregului grup este experimentul sigur pentru comparație; o lume fără crafting nu poate proba utilitatea lor în economia RP. Nu schimbăm unilateral rețete/book/advancements. |
| Ksyxis | [Autorul](https://github.com/VidTu/Ksyxis) vizează spawn chunks nefolosite, nu traficul de mașini. Dacă spawnul este centrul orașului, reducerile de încărcare pot altera mecanici acolo; comparăm timpul de boot și comportamentul spawn pe copie, fără a schimba simultan `keep-spawn-loaded`. Pregen elimină worldgen, **nu** menținerea chunkurilor deja încărcate. |
| RoadRunner | Baza de test până la proba cu mașini și clienți; NU îl stivuim cu Performant. Comparația de 16 vehicule parcate, dacă reușește, nu spune nimic despre condus la 60 persoane; verificăm fizica, coliziunile, login/handshake, și tickul cu trafic real. |
| FerriteCore / ModernFix | Păstrate provizoriu pentru heap/memorie/compatibilitate; nu confundăm RAM cu TPS și nu le atribuim un număr de jucători. Au nevoie de test lung cu aceeași lume și după GC înainte de scoatere. |
| Connectivity, InControl, drop-merge | Nu declarăm „boost” gratuit: login/rețea, reguli spawn și dropurile au implicații RP/anti-abuz. Configul repo nu e dovada configului live; A/B numai după inventar privat și teste de siguranță/corectitudine. |
| LazyDFU și extra 6 necunoscute | LazyDFU vizează pornirea, nu traficul; fără identificarea exactă a celor șase extra nu putem spune care mod consumă degeaba. Întâi inventar privat, apoi test câte o variabilă. |

**Verdict actual:** nu putem certifica „cele mai bune moduri de pe net” nici capacitatea cu mafii și mașini. 28 este ținta de test, **nu** recomandare de ștergere a celor șase sau o nouă lansare. Un rezultat CI este o probă îngustă, nu înlocuiește testarea serverului privat cu 34/13 și clienți reali.
