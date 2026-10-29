# Ce motor rămâne pentru FunCity RP Lite? Tabel verificat

**Verdict la 20.10.2026:** **FunCity b1.0827 rămâne singurul motor de referință pentru *candidatul de laborator***, nu un motor final „100%”. Este un **derivat hibrid Mohist/Tenet**, nu un motor original scris independent de la zero și nu poate fi prezentat drept imun la problemele Mohist sau ale altor hibrizi. Motorul existent și lumea live nu au fost înlocuite. SHA256 al binarului testat: `d6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd`.

**De ce îl păstrăm ca bază, deocamdată:** același JAR a pornit în copii închise cu conținutul RP ales și șase pluginuri; suportă arhitectura cerută (moduri Forge + pluginuri Bukkit) fără a schimba simultan motorul și modpackul. Nu l-am ales pentru un avantaj MSPT/RAM demonstrat. La boot fără override, motorul a eșuat cu **Guava 20 / `NoSuchMethodError`**; numai laboratorul a pornit cu Guava 21 injectat prin JVM. Aceasta este **o problemă reală nerezolvată în binarul final**, nu dovada unui motor perfect.

## Test nou în paralel pe **același conținut Lite** (20.10.2026)

[Run 39424486961](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39424486961), **reconfirmat cu exit JVM = 0 și verificare după oprire în [run 39431729563](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39431729563)**: cinci joburi independente pe runner-e GitHub-hosted, fiecare cu **aceleași 15 JAR-uri de conținut/dependențe și șase pluginuri**, surse/JAR-uri SHA256 verificate, lume temporară proprie, port `127.0.0.1`, whitelist activă, oprire după boot; zero date live. Java 11 pentru FunCity/Mist; Java 17 pentru CatServer/Arclight. Job `SUCCESS` înseamnă că preflightul s-a executat; verdictul real este în adnotarea `status=`.

| Motor concret | Java | Rezultat nou cu 15/6 | Limita probei |
|---|---:|---|---|
| FunCity b1.0827 | 11 | **Boot + 6 pluginuri OK**, oprire curată; necesită încă override Guava 21. | Fără client join sau test de API plugin+mod în gameplay. |
| CatServer vechi CUANTIC, JAR SHA `96f82479…` | 17 | **Boot + 6 pluginuri OK**, oprire curată. | Nu dovedește aceeași lume funcțională sau câștig de performanță. |
| CatServer oficial 1.16.5, JAR SHA `8edea98c…` | 17 | **Boot + 6 pluginuri OK**, oprire curată. | Nu există test cu client sau clasament nou de MSPT/RAM. |
| Arclight Forge 1.0.25, JAR SHA `f7615ceb…` | 17 | **Boot + 6 pluginuri OK**, oprire curată. | **Schimbare importantă față de packul vechi 36/14 unde eșua**: rezultatul depinde de pack; nu îl numim „perfect”. |
| Mist 1.16.5-33, JAR SHA `1c5554d5…` | 11 | **Nu a ajuns la `Done` în acest stage.** | Motivul exact nu este publicat ca log brut și nu îl atribuim fără diagnostic. |

**Nu sunt linii de performanță pentru acest test:** joburile rulează pe runner-e diferite și JDK-uri diferite; durata bootstrapului, RSS și tickul nu sunt comparabile. Graficele 15/6 de pe site provin din prima rundă A/B pe un singur runner, iar cele 36/14 din vechiul benchmark CatServer/CUANTIC; sunt marcate distinct. Un boot reușit nu dovedește că un client Forge se poate conecta sau că modurile și pluginurile interacționează corect.

## A/B Lite, pe **aceeași mașină** și noul conținut 15/6

**Runda 3, cea curentă și verificată mai strict:** [run 39434450455](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39434450455) SUCCESS, același protocol A/B/B/A/A/B, pe runner unic / Java 11 / lume generată resetată / 15 JAR-uri + 6 pluginuri / 40 zombie confirmați. De această dată toate cele șase probe au trecut și poarta de **cod de ieșire JVM = 0 și lipsa marcatorilor critici până după oprire**. Măsurile de mai jos sunt publicate abia după validarea întregii serii.

| Măsură, fereastră 30 s | FunCity A1 / A2 / A3 | CatServer B1 / B2 / B3 | Mediană A / B |
|---|---|---|---|
| CPU JVM, secunde | 10,51 / 10,82 / 10,54 | 7,64 / 8,03 / 7,85 | **10,54 / 7,85** |
| RSS JVM, MiB | 3317,99 / 3184,38 / 3254,81 | 3226,41 / 3281,08 / 3346,91 | **3254,81 / 3281,08** |

În ambele runde complete CatServer a consumat mai puțin CPU **numai** în fereastra sintetică de 30 s; RSS-ul se suprapune între motoare și diferențele dintre runde sunt mari. Runda intermediară nu a fost completă. Aceste observații **nu** măsoară MSPT, FPS sau compatibilitatea cu clientul RP și nu aleg un motor de live.

**Istoric: runda 1 și rerularea eșuată:**  [run 39425133030](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39425133030) SUCCESS cu verificarea de oprire din acea versiune (fără cod de ieșire și fără căutarea erorilor critice de după sarcină): FunCity b1.0827 (**A**) vs CatServer vechi SHA `96f82479…` (**B**), pe **același runner și Java 11**, aceeași lume **generată** și resetată din snapshot la fiecare probă, aceleași 15 JAR-uri de conținut/dependențe și șase pluginuri. Ordine A/B/B/A/A/B, trei probe valide/braț; 40 de zombie confirmați prin consola serverului în fiecare probă și 30 s fereastră de observație după pornire. Nu au fost jucători, vehicule sau client Forge conectat; nu s-a măsurat MSPT/TPS. Nu este lumea reală.

**Runda 2, rerulare cu verificare mai strictă:** [run 39431729723](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39431729723) FAILED: primele cinci probe (A/B/B/A/A) au trecut, ultimul B **nu a ajuns la `Done`**; nu au fost publicate metrici și nu a fost confirmat un nou A/B complet. Cauza exactă nu este încă identificată. Valorile de mai jos rămân **istoricul rundei 1**; runda 2 nu le reconfirmă, iar runda 3 a încheiat o serie nouă cu valori diferite. Nu pretindem stabilitatea CatServer sau un avantaj live.

| Măsură, fereastră 30 s | FunCity A1 / A2 / A3 | CatServer B1 / B2 / B3 | Mediană A / B |
|---|---|---|---|
| CPU JVM, secunde | 13,51 / 14,34 / 12,60 | 10,48 / 9,51 / 10,46 | **13,51 / 10,46** |
| RSS JVM, MiB | 3057,84 / 2979,90 / 3068,69 | 2962,99 / 3051,09 / 2935,07 | **3057,84 / 2962,99** |

**Lectură corectă pentru runda 1:** CatServer a folosit mai puțin CPU în **acest** scenariu sintetic repetat. Valorile RSS se suprapun între probe; nu există încă un câștig RAM stabil demonstrat, iar CPU pe 30 s fără MSPT, login modat/vehicule și lumea RP nu stabilește care motor va fi mai bun pentru jucători. Nu promovăm automat CatServer și nu numim FunCity „perfect”; următorul experiment trebuie să includă clientul, funcțiile RP și MSPT cu sarcină reprezentativă. [Pagina cu liniile și axele pornind de la zero](../site/index.html#motoare).

## Motoarele și fork-urile pentru care există probe

| Candidat | Pe ce pack și ce s-a testat efectiv | Rezultat și ce **nu** dovedește | Decizie pentru noul Lite |
|---|---|---|---|
| **FunCity b1.0827**, derivat Mohist/Tenet | Pe stage nou: 0 moduri/6 pluginuri, apoi 15 JAR-uri de conținut/dependențe/6 pluginuri și, separat, 18 JAR-uri incluzând trei optimizări. Boot/oprit pe runner și PC, numai loopback. [15 pe PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39333730944) · [18 pe PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39336314432). | `Done` și activarea pluginurilor **cu Guava 21 prin override**; [fără el nu pornește corect](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39312131848). Fără intrare de client LowSpec cu 21 JAR-uri, login prin plugin, funcții RP, backup/restaurare sau A/B sub sarcină. | **Păstrat ca bază de test, nu aprobat pentru release/live.** Repară bootstrapul Guava într-un build auditabil și testează cap-coadă. |
| **CUANTIC / CatServer 1.7.7 istoric** | Packul istoric diferit: 36 moduri + 14 pluginuri; a trecut boot izolat și exista evidență de status live istoric. [Comparația veche](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-DECISION.md). | Nu e noul pack cu 15/21 și nu dovedește că poate înlocui FunCity b1.0827; istoricul live nu este test de login nou sau garanție de capacitate. | Reper istoric, **nu înlocuitor automat**. |
| **CatServer oficial 1.16.5-1d8d6313** | Comparație cu CUANTIC vechi 36/14 pe același runner: 2 probe/variantă, fără jucători/vehicule. [Raportul A/B](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-NATIVE-RESULT.md). | Ambele au pornit; medianele RSS 2328,55 vs 2330,60 MiB, MSPT p95 1,2 ms în ambele brațe. Diferența RAM era mult sub variația dintre probe. | Niciun avantaj convingător; **nu promova pe baza acestor cifre**. |
| **CatServer upstream 2024 și fork-uri proprii experimentale (hotpath, hopper, tickete)** | Teste de boot și comparații sintetice pe packul vechi 36/14. [Decizie upstream](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-DECISION.md) · [fork-uri reale și limite](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-FORK-STATUS.md). | Au existat porniri reușite, dar nu un câștig stabil simultan CPU/MSPT față de baseline; probele nu includ perechea LowSpec actuală sau gameplay RP. | Nu le declarăm „motorul nostru perfect” și nu le instalăm live. |
| **Arclight Forge 1.16.5-1.0.25** | O probă **istorică** de boot cu vechiul pack identic 36/14. [Raport](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-FAMILY-RESULT.md). | **Nu a ajuns la `Done`** (eroare mixin); 0 pluginuri activate. Nu a existat benchmark de performanță sau test pe noul pack. | Respins pentru *acea* combinație; **a trecut noul smoke 15/6 de mai sus**. Nu există încă gameplay ori avantaj măsurat. |
| **Mist 1.16.5-33** | Test pe același pack 36/14; Java 17 a lovit acces intern JDK, [retentativa pe Java 11](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-MIST-J11-RESULT.md) nu a ajuns nici ea la `Done`. | Nu a trecut poarta de pornire a packului istoric; nu avem cifre valide de MSPT. | Nu e înlocuitor probat pentru FunCity. |
| **Mohist upstream / motorul din backup HYPECITY** | Există configurații istorice Mohist în backup, **nu** o probă comparativă validă cu cele 15 JAR-uri + LowSpec și aceleași pluginuri. [Limita capturii](AUDIT-SERVERE-REFERINTA.md). | Prezența unui config sau reputația unui fork **nu** dovedesc că a mers fără probleme ori că e mai rapid în FunCity. | Neselectat; moștenirea Mohist/Tenet din b1.0827 se auditează, nu se ascunde. |
| **Magma, LoliServer, alte hibriduri noi** | Nu avem un boot comparabil și repetat cu packul Lite actual din acest branch; unele încercări istorice au fost limitate de surse/JAR-uri inaccesibile. | **NETESTATE pentru noul Lite**. Nu le numim nici mai bune, nici mai proaste. | Fără concluzie; nu promitem că „le-am testat pe toate”. |
| **Paper/Purpur/Vanilla fără Forge** | Nicio probă echivalentă cu conținutul RP Forge + pluginurile cerute. | Comparația numerică fără aceleași moduri ar schimba jocul, nu doar motorul. | Nu le substituim automat pentru un server modat. |

**Atenție:** benchmarkurile CatServer/Arclight/Mist au folosit **packul CUANTIC 36/14**, pe când FunCity Lite a folosit **15 JAR-uri de conținut/dependențe + 6 pluginuri**, apoi 18 în trial. Rezultatele nu formează un clasament comun. Tabelul nu spune că am testat toate motoarele vechi și noi, nici că versiunea din PC sau de pe hosting este identică cu JAR-ul SHA de laborator.

## Ce înseamnă, în mod verificabil, „motorul nostru”

Putem menține **un fork FunCity personalizat**, cu modificări proprii și teste, dar originea Mohist/Tenet și licențele trebuie declarate. Un nume/branding nou nu repară incompatibilitățile. Pentru a-l putea numi motor de release: (1) build reproductibil din sursa corespunzătoare și licențe/atribuiri corecte; (2) fix real al incompatibilității Guava fără override de laborator; (3) 15 moduri conținut + pluginurile RP/login pe copie, cu clientul LowSpec complet conectat și funcții RP verificate; (4) restart, backup/restaurare și rollback; (5) profilare/optimizări A/B reprezentative. **Niciun motor nu este 100% fără probleme**, iar aceste porți nu sunt încă trecute.
