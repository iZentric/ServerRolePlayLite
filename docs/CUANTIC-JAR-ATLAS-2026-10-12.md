# CUANTIC · Atlasul JAR-urilor și ținta 10×

**12 octombrie 2026 · cercetare + probe locale, NU clasament de marketing.** Ținta produsului rămâne Roleplay Lite + survival complet cu clientul **non-premium, Forge 1.16.5 modat**, 36 moduri și 14 pluginuri. Nu modificăm pack-ul doar pentru a câștiga un concurs sintetic. „Toate JAR-urile” în sens literal nu poate fi garantat: apar fork-uri private și proiecte noi; tabelul acoperă familiile și candidații identificați în această rundă, nu fiecare fork de pe internet. Am făcut >30 interogări adaptive (descoperire → surse primare → versiune exactă/compatibilitate → concurenți moderni); am citit direct documentația CatServer, Arclight, Folia, Cardboard, Sponge, EssentialsX și lista de hybrid-uri din docker-minecraft-server. Serverul Magma GitLab a răspuns **522**, iar URL-ul încercat pentru LoliServer a dat **404**; sursele secundare nu le certifică drept build-uri compatibile. Nu am instalat sau benchmarkuit noi JAR-uri în această sesiune.

**Legendă:** `D` = dovadă locală cu 36/14; `S` = există sursă/release pentru versiune, dar **nu** avem smoke cu pack-ul exact; `N` = alt loader/API/versiune, deci nu este adversar echivalent fără portarea clientului/conținutului. „Nu pornește” nu înseamnă „mai lent”. Pentru orice afirmație din căutarea web, sursa apare în același rând; rezultatele noastre sunt legate de raportul brut local.

## A. Duel echivalent posibil: Forge 1.16.5 + Bukkit, pack-ul nostru intact

| JAR/familie | Versiune, proveniență și stare | Cuantic 36/14 | Verdict strategic, fără TPS inventat |
| --- | --- | --- | --- |
| **CUANTIC live**, CatServer adaptat | 1.16.5, Java 17, SHA `96f82479…7789c`; codul JAR diferă de upstream în două intrări, inclusiv `data/forge-1.16.5-36.2.39-universal.jar` ([A/B brut](ENGINE-NATIVE-RESULT.md)). | **D**: `Done`, 14 pluginuri; proba cu 1 jucător nu acoperă încă trafic/vehicule ([smoke](ENGINE-FAMILY-RESULT.md), [jucător](ENGINE-PLAYER-RESULT.md)). | Referință funcțională; **nu 10×** și nu un motor original complet. |
| **CatServer oficial** | Forge+Bukkit/Spigot 1.16.5; documentația recomandă Java 8/11, spune că 17 poate avea probleme cu unele moduri/pluginuri, licență LGPL-3.0 [2](https://github.com/Luohuayu/CatServer/blob/1.16.5/docs/README_EN.md) [4](https://github.com/Luohuayu/CatServer). | **D**: în testul nostru 1.16.5-1d8d6313 a pornit cu 36/14; A/B/B/A pe Java 17, fără jucători ([date](ENGINE-NATIVE-RESULT.md)). | Principalul adversar comparabil; rezultatele CUANTIC ↔ oficial sunt amestecate, fără câștig repetabil. |
| **CUANTIC patch SortedArraySet** | Cod compilat diferit, SHA `b0817358…215ee3` ([metodă](ENGINE-STRICT-RESULT.md)). | **D**: 6 smoke-uri, dar fără clienți modati/vehicule. | **Respins:** pornirea externă mai bună într-o rundă, dar CPU/p95/RSS/Done nu trec simultan pragul strict. |
| **Arclight Forge** | Arhitectură Bukkit prin Mixin, branch vechi 1.16.x, proiectul dezvoltă și linii noi; GPL-3.0 [3](https://github.com/IzzelAliz/Arclight/tree/1.16) [4](https://github.com/IzzelAliz/Arclight). | **D**: `1.16.5-1.0.25` nu a ajuns la `Done` cu 36/14: mixin `BreakBlockGoalMixin` obligatoriu eșuat ([diagnostic](BENCHMARK-MOTOARE-CUANTIC-2026-10-12.md)). | Candidat numai după patch izolat și retest; nu are scor MSPT echivalent. |
| **Mist** | Fork Mohist 1.16.5, repo arhivat în 2021, GPL-3.0 [4](https://github.com/MinecraftMist/Mist). | **D**: Java 17 `IllegalAccessError`; Java 11 `NoSuchMethodError`, fără `Done` ([run](ENGINE-MIST-J11-RESULT.md)). | Nu îl lansăm; fără A/B valid. |
| **Mohist 1.16.5** | Forge+Bukkit; binare istorice 1.16.5-1237 în Maven, GPL-3.0 [5](https://search.maven.org/artifact/com.mohistmc/mohist) [3](https://github.com/MohistMC-Archives/Mohist). Producătorul EssentialsX avertizează că nu îl suportă [1](https://essentialsx.net/downloads). | **S**, nu am boot/login 36/14. | Test în sandbox numai cu fișiere oficiale și SHA; validează pluginurile/atribuirile înainte de benchmark. |
| **LoliServer 1.16.5** | Hybrid Forge+Bukkit derivat din Mohist; fork vizibil GPL-3.0 [1](https://github.com/Sam-Chai/LoliServer), oglindă Gitee indică LGPL-3.0 [3](https://gitee.com/kotori0629/LoliServer1.16): **licența exactă a candidatului trebuie verificată înainte de reutilizare**. Relația istorică cu CatServer este descrisă de CatServer [2](https://github.com/Luohuayu/CatServer/blob/1.16.5/docs/README_EN.md). | **S**, niciun binar exact testat; URL-ul încercat `Loli-Server/LoliServer1.16` a răspuns 404. | Prioritate de descoperire a sursei/release-ului autentic, apoi smoke; fără punctaj până atunci. |
| **Magma 1.16.5** | Release 1.16.5/Forge 36.2.35 indexat [1](https://git.magmafoundation.org/magmafoundation/Magma-1-16-x/-/releases/c6d2f4f8), proiectul 1.16.x marcat arhivat [4](https://git.magmafoundation.org/magmafoundation/Magma-1-16-x); ghidul docker spune că Magma original a fost terminat [1](https://github.com/itzg/docker-minecraft-server/blob/master/docs/types-and-platforms/server-types/hybrids.md). Pagina primară GitLab a dat 522 la verificare. | **S**, fără SHA/verificare 36/14. | Nu pretinde compatibilitate sau licență verificată; dacă reapare binarul oficial, smoke numai izolat. |

**Valorile într-adevăr comparabile CUANTIC live / CatServer oficial** (două repetări, pack identic, Java 17, 64 chunkuri forțate + 40 zombies, 55 s încălzire + 75 s stabil, fără jucători): CPU **3,32/2,86 vs 3,32/3,43 s**; p95 **1,3/1,1 vs 1,2/1,2 ms**; RSS **2205/2452 vs 2186/2476 MiB**. Alternanța rezultatelor nu susține superioritate overall ([raport brut](ENGINE-NATIVE-RESULT.md)).

## B. Celelalte JAR-uri/implementări descoperite — *nu* în aceeași cursă 36/14

| JAR/familie | Ce rulează / unde are sens | De ce nu primește „pierde contra CUANTIC” |
| --- | --- | --- |
| **Minecraft vanilla** | Serverul oficial, referință de mecanici de bază. | Nu încarcă 36 moduri Forge și 14 pluginuri Bukkit; alt produs. |
| **Forge 1.16.5** | Loader pentru modurile clientului; bază de control pentru costul layer-ului hibrid [1](https://github.com/minecraftforge/minecraftforge). | Nu încarcă nativ pluginurile Bukkit; comparație separată, cu funcțiile lipsă raportate. |
| **SpongeForge 1.16.5** | Forge + **pluginuri Sponge**, nu Bukkit; documentație oficială API 8.2.0 și Java 11 recomandat [3](https://docs.spongepowered.org/stable/en/plugin/api-versions.html) [4](https://docs.spongepowered.org/stable/en/server/quickstart.html). | Cele 14 pluginuri Bukkit necesită alternative/portare; nu e drop-in. |
| **SpongeVanilla** | Sponge API peste vanilla [4](https://docs.spongepowered.org/stable/en/server/quickstart.html). | Nu oferă același Forge+Bukkit. |
| **CraftBukkit / Spigot** | API Bukkit, bază istorică a familiei Paper [1](https://github.com/papermc/paper). | Fără modurile Forge în aceeași lume. |
| **Paper** | Server Bukkit/Paper, inclusiv build-uri istorice 1.16.5; proiect activ pe versiuni noi [1](https://github.com/papermc/paper). | Nu este hybrid Forge; performanța Paper cu 0 moduri nu este duel echivalent. |
| **Purpur** | Fork Paper/Pufferfish orientat pe configurare; istoricul include 1.16.5 [3](https://geocities.purpurmc.org/docs/) [5](https://minecraftversion.net/purpur/). | Fără 36 moduri; modificările de mecanici nu sunt bonus gratuit. |
| **Pufferfish** | Fork Paper pentru servere mari, patch-uri GPL-3.0 [2](https://github.com/pufferfish-gg/Pufferfish). | Fără Forge în JAR; doar idei/patch-uri analizate individual după versiune/licență. |
| **Gale** | Fork Paper fără schimbări comportamentale revendicate de autor [1](https://github.com/GaleMC/Gale). | Afirmația de viteză de pe README nu este benchmark pentru modpack-ul nostru. |
| **Leaf** | Fork Paper/Purpur, versiune modernă 26.2 pe site-ul oficial [5](https://www.leafmc.one/en). | Fără Forge; nu migrează conținutul 1.16.5. |
| **Leaves** | Fork Paper orientat spre mecanici vanilla; index GitHub [3](https://github.com/topics/minecraft-performance?o=desc&s=stars). | Nu poate încărca pack-ul Forge direct. |
| **DivineMC** | Fork Purpur, GPL-3.0 [1](https://github.com/BX-Team/DivineMC). | API Bukkit fără Forge; alte versiuni nu echivalează clientul actual. |
| **Folia** | Paper cu regiuni tick-uite paralel, necesită pluginuri adaptate; însuși README avertizează că multe pluginuri se vor rupe [1](https://github.com/PaperMC/Folia). | Nici Forge 1.16.5, nici compatibilitate gratuită cu 14 pluginuri; ideea de paralelism necesită proof-of-concept sigur, nu transplant orb. |
| **Tuinity** | Fork Paper istoric, idei integrate ulterior în Paper (catalogul comunitar necesită revalidare) [3](https://anythingmc.xyz/server/info/lists/server_software/). | Fără Forge; nu instala un JAR vechi pentru nostalgie. |
| **Airplane / Purplane** | Fork-uri Paper istorice pentru servere mari; informație de catalog, nu benchmark pentru noi [3](https://anythingmc.xyz/server/info/lists/server_software/). | Fără Forge; versiunile/buildurile de interes necesită verificare primară. |
| **Yatopia** | Fork 1.16.5 arhivat în 2021; autorii enumeră multe optimizări preluate [1](https://github.com/YatopiaMC/Yatopia). | Fără Forge; amestecul de patch-uri nu justifică portarea automată. |
| **Canvas / SparklyPaper / Vine** | Fork-uri Paper/Folia orientate spre multi-threading descoperite în indexul GitHub [5](https://github.com/topics/paper-fork). | Nu am citit încă sursa, licența și versiunea fiecărui patch relevant; fără pack Forge. |
| **Fabric / Quilt** | Alte loadere de moduri, nu suport direct pentru modurile Forge 1.16.5 [3](https://gdlauncher.com/docs/mod-loaders-compared/). | Ar cere portarea celor 36 de moduri și a clientului, nu un swap de JAR. |
| **Cardboard / Bukkit4Fabric** | API Bukkit peste Fabric, GPL-3.0 [1](https://github.com/CardboardPowered/cardboard) [4](https://github.com/ThatGamerBlue/bukkit4fabric); wiki Cardboard marchează **≤1.16.5 nesuportat** [5](https://github.com/CardboardPowered/cardboard/wiki/Supported-Versions). | Nu încarcă Forge; fără migrare completă a pack-ului. |
| **Banner** | API Bukkit peste Fabric, sursa arhivată indică GPL-3.0 [2](https://github.com/AutoArchives/mohistmc-banner). | Nu este Forge 1.16.5; fără pack echivalent. |
| **NeoForge / Youer** | NeoForge este loader distinct de Forge 1.16.5 [3](https://gdlauncher.com/docs/mod-loaders-compared/); Youer promite integrare Bukkit pe NeoForge [4](https://mohistmc.com/software/youer). | Viitor cu portarea tuturor modurilor/clientului; promisiunile vendor nu certifică gameplay-ul. |
| **Ketting / Magma Maintained** | Documentația de operare indică Ketting pentru 1.20.1+ și Magma Maintained pentru alte versiuni, fără 1.16.5 în lista de acolo [1](https://github.com/itzg/docker-minecraft-server/blob/master/docs/types-and-platforms/server-types/hybrids.md). | Nu corespund baseline-ului; păstrăm în radar pentru migrare planificată, nu schimbare live. |
| **Minestom** | Framework pentru servere custom; reimplementarea oficială a survival-ului este limitată și arhivată în 2026 [1](https://github.com/Minestom/VanillaReimplementation). | Nu e înlocuitor drop-in pentru survival + Forge + Bukkit; ar cere construcția jocului și a protocolului modat. |
| **Feather (Rust)** | Implementare experimentală, multe funcții lipsesc; Apache-2.0 în forkul inspectat [1](https://github.com/lineCode/feather-1). | Nu livrează conținutul și API-urile cerute; cercetare de arhitectură, nu JAR de producție. |
| **Crucible / Thermos / Kettle vechi** | Familie istorică de hybrid-uri pentru alte versiuni, Kettle marcat depreciat din 2021 [4](https://github.com/KettleFoundation/Kettle) [1](https://github.com/Shawiizz/minecraft-hybrids). | Nu sunt candidați 1.16.5 în aceleași condiții. |
| **Proxy-uri Velocity / BungeeCord / Waterfall** | Rutare între servere, nu implementări de lume Minecraft [1](https://winternode.com/help/games/minecraft-java/setup/server-types). | Nu sunt JAR-uri de joc comparabile; nu le numărăm ca motoare învinse. |

**Limită de cercetare:** Nu am revizuit fiecare issue, release și licență pentru fiecare rând B; acestea sunt *radar*, nu decizii de portare. Un catalog comunitar din 2023 poate contrazice documentația primară curentă — de exemplu a listat CatServer numai pentru 1.12.2, în timp ce README oficial și build-ul nostru confirmă 1.16.5 [1](https://github.com/Shawiizz/minecraft-hybrids) [2](https://github.com/Luohuayu/CatServer/blob/1.16.5/docs/README_EN.md). Pentru adoptarea unui patch verificăm tag, commit, licență și testul 36/14, nu doar numele.

## Ce înseamnă 10× pentru Overlord

**Nu 10× TPS**: jocul obișnuit țintește 20 TPS; la idle baseline-ul are deja p95 circa 1–1,3 ms. 10× în p95 față de 1,2 ms ar cere ≤0,12 ms sub *aceeași* sarcină; 10× RAM față de ~2,2 GiB ar cere ~0,22 GiB RSS cu întregul pack, ceea ce nu este demonstrat. Nu voi înlocui jucătorii cu 0 ca să obțin „10×” pe hârtie.

**Ținta cu potențial de sens:** jucători *efectiv conectați și activi* per vCPU și per GiB la ≥19,5 TPS, p95 ≤50 ms și fără crash ori pierdere de funcții; separat CPU, RSS, p95/p99, startup și latență la același număr de jucători. Dacă baseline-ul suportă doar N în workload-ul definit, 10× înseamnă ≥10N pe același host/pack/seed/setări și cu clientul modat funcțional, repetat. **N este momentan necunoscut**; 0/25 din Curtain nu este baseline. Nu există încă **niciun** 10× demonstrat împotriva vreunui motor, cu atât mai puțin împotriva tuturor.

### Planul de atac, în ordinea avantajului posibil

1. **Calificare înainte de viteză:** obține build-uri 1.16.5 autentice pentru Mohist/LoliServer/Magma, notează SHA și licență; smoke 36/14 în sandbox. Reia Arclight doar dacă poți izola incompatibilitatea mixin-ului fără a pierde funcții. JAR-urile care nu pornesc rămân „incompatibile”.
2. **Măsoară plafonul real:** cu client Forge autorizat, vehicule, oraș, chunks, survival și pluginuri, măsoară 1, 5, 10 și 25 doar dacă fiecare prag ține; repetiții și loguri. Scrie o bază proprie reproductibilă; niciun număr de capacitate până când jucătorii nu apar în `/list`.
3. **Identifică hotspot-ul:** Spark flamegraph + GC/proc/disk pe aceeași lume; avertismentul de mixin ModernFix↔RoadRunner din CHK este o **ipoteză de verificat**, nu cauza demonstrată de lag. Alege o singură schimbare per experiment (optimizație native/JAR sau config care păstrează funcțiile), apoi A/B/B/A.
4. **Cuantic Engine propriu incremental:** sursă, licențe și atribuire upstream; adaptor Forge/Bukkit menținut, modul propriu pentru hotspot-ul măsurat. Pentru release, startup/CPU/p95/RAM strict mai bune, fără regresie client/vehicul/survival; verifică efectiv `/version`. Dacă un modul nu câștigă, nu îl promovăm.
5. **Regula verdictului:** `scripts/cuantic_tenx_gate.py` respinge probe fără amprente identice, minimum trei repetări distincte, hash-uri de loguri și număr de clienți Forge declarat; cu date valide declarate produce cel mult `10X_PRELIMINAR`, **nu dovadă automată**. Logurile trebuie inspectate independent înaintea oricărei afirmații publice; fără probe afișează `NEMASURAT`.

Totul de mai sus rămâne cercetare și cod local. Niciun JAR nou, benchmark cu boți validați sau publicare live nu a fost realizat în acest tur.

## Tier list — cum se citește clasamentul de pe site

Site-ul nu are un al doilea adevăr: `site/jar_tier.py` citește **acest document** și repartizează fiecare rând într-un tier folosind legenda `D`/`S`/`N` de mai sus, prin categoriile deja stabilite în `site/jar_atlas.py`. Niciun tier nu este scris manual și nicio poziție nu poate fi „promovată" fără o probă nouă în acest fișier.

| Tier | Regulă mecanică | Ce înseamnă | Ce NU înseamnă |
| --- | --- | --- | --- |
| **S** | `D` + a ajuns la `Done` cu 36/14 | A pornit cu pack-ul intact și a fost măsurat | **Nu** „cel mai rapid". Sunt doi candidați și sunt la egalitate în limita zgomotului |
| **A** | `D` + măsurat + respins la pragul strict | A intrat în bancul de probe și a pierdut pe CPU/p95/RSS/boot simultan | Nu „aproape bun". Pragul este tot sau nimic |
| **B** | `D` + nu a ajuns la `Done` | Incompatibil cu pack-ul nostru | **Nu** „mai lent". Un JAR care nu pornește nu are scor comparabil |
| **C** | `S` | Există sursă/release pentru versiunea corectă | Nu este evaluat. Fără punctaj până la smoke 36/14 |
| **D** | `N` | Alt loader, alt API de pluginuri sau altă versiune | Nu este un motor învins; ar cere portarea conținutului |

Repartizarea actuală, derivată din tabelele de mai sus: **S 2 · A 1 · B 2 · C 3 · D 26 = 34 de rânduri**.

### Consumul: de ce verdictul este NECONCLUDENT, nu un câștigător

Tabelul de consum de pe site citește valorile **verbatim** din [ENGINE-NATIVE-RESULT.md](ENGINE-NATIVE-RESULT.md) — nu le reformatează din float, ca să nu derive niciodată față de raportul brut. Verdictul fiecărei măsuri folosește aceeași regulă ca `scripts/cuantic_tenx_gate.py`:

- sub `MIN_TRIALS = 3` repetări reale pe braț → **NECONCLUDENT**;
- cu date valide → cel mult **PRELIMINAR**, niciodată dovadă automată; logurile se inspectează independent.

Astăzi avem **2 probe pe braț** pentru singurii doi candidați echivalenți, deci fiecare măsură este NECONCLUDENT. Diferența dintre medianele RSS este **2,05 MiB** față de variații interne de **246,9 și 290,0 MiB**: un raport de peste 100 de ori. A declara „cel mai mic consum" din aceste date ar fi zgomot prezentat ca rezultat.

**Răspunsul la „care e cel mai performant JAR cu cel mai mic consum" este, onest: NEDECIS.** Tier list-ul arată cine poate fi comparat și cine nu, nu cine a câștigat.

## Scara CUANTIC — cum urcă un motor din C în S (și ce nu se poate fură)

Secțiunea de față este singura parte a atlasului care poate schimba tier list-ul de pe site.
Tooling: `scripts/cuantic_ladder.py` + workflow-ul `CUANTIC LADDER` (`.github/workflows/cuantic-ladder.yml`),
care publică [CUANTIC-LADDER-RESULT.md](CUANTIC-LADDER-RESULT.md). Site-ul citește acel fișier și
adaută automat rândurile candidaților; dacă fișierul lipsește, rândurile rămân **NEAVĂGAT**.

Treapta se parcurge într-o singură direcție și fiecare eșec se raportează, nu se ascunde:

| Treaptă | Ce se întâmplă | Ce se publică | Ce NU se publică |
|---|---|---|---|
| 1 · Identitate | build 1.16.5 luat din sursa oficială, SHA-256 consemnat, licență notată | URL, SHA, licență | „cea mai bună variantă” fără SHA |
| 2 · Fum 36/14 | pack identic, înlocuit **doar** motorul, căutare de `Done` | `Done` sau linia de eroare | scor MSPT pentru un motor care nu a pornit |
| 3 · A/B | minim **3 probe valide pe braț**, aceeași mașină, același seed, 55 s încălzire + 75 s stabil | mediane + plaja din interiorul brațului | procent de câștig sub plaja de zgomot |
| 4 · Poarta | `scripts/cuantic_tenx_gate.py` cere clienți Forge confirmați în `/list`, vehicule, survival, pluginuri | `10X_PRELIMINAR` sau `SUB_ȚINTĂ` sau `NEMĂSURAT` | orice afirmație de 10×/„cel mai bun” |

De ce e nevoie de un runner: `repo1.maven.org` și `objects.githubusercontent.com` nu sunt accesibile
din sandbox-ul agentului (căutarea Mohist/LoliServer a dat 404, pagina Magma a dat 522). Rulează
**numai** pe `ubuntu-latest`, niciodată pe gazda live și niciodată ca pas automat al unui deploy.

Când un candidat trece treapta 2, el nu „a câștigat”: a devenit comparabil. Când trece și treapta 3,
cel mult devine `PARITATE_OBSERVATĂ` sau `RESPINS` — niciodată „câștigător”, pentru că proba e sintetică
(fără jucători, fără vehicule, fără client Forge). Titlul live-ului se schimbă doar la treapta 4.

## Surse verificate pe scară (12 oct 2026, runner GitHub)

| Motor | URL oficial încercat | Rezultat |
|---|---|---|
| Mohist 1.16.5-1237 | `repo1.maven.org/maven2/com/mohistmc/mohist/1.16.5-1237/mohist-1.16.5-1237-server.jar` (8.697.940 octeți, sha256 `17d08ed544aab50f0c9c0281507a44d765cfeb371289a10d47e2143146255bff`) | accesibil din browser; primul runner l-a căutat cu numele greșit (`mohist-1.16.5-1237.jar`, fără classifier) și a primit 404 |
| Magma 1.16.5-36.2.39-c1c5a946 | `git.magmafoundation.org/api/v4/projects/8/packages/maven/.../Magma-1.16.5-36.2.39-c1c5a946-server.jar` | `HTTP 522` din runner, la fel și pe pagina principală a proiectului — gazda e căzută, nu candidat mai lent |
| LoliServer 1.16.5 | `github.com/Loli-Server/LoliServer` | `404` pe API-ul releases: repository stins; nu luăm binare de pe oglinzi neoficiale |

Niciunul nu are încăfum pe pack-ul 36/14 înseamnă **NEAVĂGAT**, nu „mai slab”.
