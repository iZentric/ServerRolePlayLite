# Decizia executabilă: FunCity 1.16.5, pluginuri întâi

19.10.2026. **Aleg motorul FunCity b1.0827 hibrid** (JAR SHA256 `d6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd`) **pentru copia de laborator**, nu CatServer-ul găsit lângă `FunCityEngine.jar` pe PC, nu un build nou și nu Paper-only. Motiv: motorul ales deja pentru proiect suportă atât pluginuri, cât și posibile moduri de conținut proprii; îi avem binarul istoric cu SHA verificabil, iar schimbarea motorului simultan cu schimbarea conținutului ar distruge comparația. Nu afirmăm că e motorul cu consumul cel mai mic ori că JAR-ul de pe PC este același.

## Modurile rămase *în această etapă nouă*

**Zero JAR-uri în `mods/` pe server, zero moduri cerute pe client**, nu pentru că toate optimizările sunt inutile, ci fiindcă proprietarul nu vrea module terțe nedemonstrate. Nici Pizzaland, ModernXL, CFM, armele/vehiculele terțe, bibliotecile lor, nici Clumps/Rubidium/Oculus/FerriteCore/ModernFix/Radon/LazyDFU/RoadRunner/Ksyxis/FastSuite/Placebo nu primesc o derogare din vechiul pack. Un mod de conținut al proprietarului revine numai când este identificat exact și autorizat; o optimizare numai după hotspot și A/B pozitiv pe server sau client. **Aceasta este o copie nouă, nu operație de ștergere pe PC/lumea existentă.** `agent/PLUGIN-FIRST.json` este poarta; numărul zero este selecția inițială de *test de bază*, nu un pack RP gata.

## Pluginuri în copia închisă (6 JAR-uri, cu SHA de intrare verificat)

| Plugin | Motiv și limită |
|---|---|
| EssentialsX + EssentialsXChat + EssentialsXSpawn, din vechiul ZIP cu SHA pinuit | Comenzi, chat, spawn/economie de bază. **Nu înseamnă** joburi sau mafii implementate. |
| LuckPerms din același ZIP | Permisiuni și roluri; nu înseamnă că regulile RP au fost configurate. |
| Vault din același ZIP | Punte de economie pentru viitoare pluginuri; poate fi reevaluat dacă nu are dependent. |
| CoreProtect 21.2, binar oficial cu SHA pinuit | Jurnal și rollback administrativ, nu protecție preventivă; logarea modurilor proprii și restaurarea nu sunt probate. |

**Fără** claimchunk, WorldGuard, EssentialsXAntiBuild/Protect, WorldEdit permanent, Chunky permanent, ProtocolLib, SkinsRestorer, Cuantic-Brand sau mod de voce implicit. Le reintroducem numai pentru o cerință și o dependență probate. Pluginul de autentificare **nu este încă pinuit**: în stadiul actual serverul de laborator ascultă doar pe `127.0.0.1`, cu `online-mode=true` și `white-list=true`. Asta nu este configurația de publicare pentru comunitatea cu login prin plugin. Vocea RP rămâne cerință deschisă; un plugin pe server nu o furnizează automat clientului.

## Ce am pregătit efectiv

`scripts/fc_plugin_first_stage.py` verifică SHA pentru motor, vechiul ZIP de pluginuri și CoreProtect; acceptă numai cele cinci JAR-uri istorice de mai sus plus CoreProtect, scrie un **folder nou** cu `mods/` gol, `plugins/` cu exact 6, `server.properties` închis și un raport fără lume/conturi/config vechi. Refuză destinația existentă, modificări de hash și dependeți `plugin.yml` lipsă. Fixture-ul `scripts/fc_plugin_first_stage_test.py` verifică aceste refuzuri. Workflow-ul `.github/workflows/plugin-first-stage.yml` rulează exclusiv pe GitHub-hosted, descarcă sursele oficiale pinuit(e), face stage temporar și încearcă un boot/stop **numai pe loopback**; nu urcă arhiva, nu accesează runnerul Windows/hostingul și nu creează release. Rezultatul real de boot trebuie consemnat după run, nu presupus aici.

## Primul boot a descoperit o dependență a motorului, nu un „mod de performanță”

[Runurile 39311668685 și 39312131848](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39312131848) au făcut stage cu **0 mods / 6 plugins**, dar motorul b1.0827 nealterat **nu a atins `Done`**. Installerul descarcă `libraries/com/google/guava/guava/20.0/guava-20.0.jar`; apoi Minecraft eșuează cu `NoSuchMethodError: ImmutableMap.toImmutableMap(...)`. Nu este dovadă că lipsesc moduri RP sau că un optimizer e necesar; e o incompatibilitate de bibliotecă la pornire. [Guava 21.0 oficial](https://github.com/google/guava/releases/tag/v21.0) are metoda, JAR SHA256 `972139718abc8a4893fa78cba8cf7b2c903f35c97aaf44fa3031b0669948b480`. [Runul 39312631544](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39312631544) **SUCCESS**: motorul a atins `Done`, a activat cel puțin CoreProtect, Essentials, LuckPerms și Vault și s-a oprit curat cu **zero moduri**, într-o copie loopback cu Guava21 preîncărcat prin JVM. Este **o singură probă de boot cu override de laborator**, nu o demonstrație că toate cele șase pluginuri sunt active, că intră jucători, că pluginurile RP funcționează sau că avem remediu aprobat pentru producție. Nu modifică motorul ori bibliotecile de pe PC. Următorul test cere activarea nominală a **tuturor celor șase** pluginuri; fixul durabil trebuie implementat în bootstrapul/sursa motorului, cu dependență/compatibilitate verificate.

**Ce lipsește pentru „serverul e gata”:** boot valid fără workaround temporar, confirmarea modurilor proprii, implementarea joburilor/mafiilor/vehiculelor în pluginuri ori justificarea unor excepții, voce compatibilă, pluginul de autentificare pinuit și testat, backup/restaurare, test client și scenarii RP, apoi comparație de consum pe PC și hosting. Nu pune `online-mode=false` pe un server public fără autentificare funcțională.
