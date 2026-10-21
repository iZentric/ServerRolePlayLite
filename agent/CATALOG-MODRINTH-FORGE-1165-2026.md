# Catalog extins de alternative pentru FunCity RP Lite — Forge **Minecraft 1.16.5**

22 octombrie 2026. Răspuns la cererea de a căuta și **alte moduri care există pe Modrinth**, nu doar cele 22 deja instalate. [Auditul celor 22 din Lite](AUDIT-PERFORMANTA-FORGE-1165-2026.md) rămâne inventarul de plecare: Rubidium + ModernFix + FerriteCore + LazyDFU + Oculus + TexTrue și conținutul/dependențele RP; Embeddium e numai în TEST. Serverul live are view-distance 5. **Nu** s-au instalat/șters JAR-uri, nu s-au schimbat lumea ori serverul.

**Metodă și limită:** am inventariat toate **53 de intrări** din secțiunea Forge 1.16.x a [UsefulMods](https://github.com/TheUsefulLists/UsefulMods/blob/main/Performance/Performance116.md) (52 de nume deoarece sunt două proiecte *Entity Culling* diferite), apoi am căutat pe Modrinth ediții exacte *game version=1.16.5* **și** *loader=Forge*, inclusiv ediții apărute ulterior listei. Pentru proiectele absente ori fără fișiere pe Modrinth am confruntat paginile autorilor de pe CurseForge/GitHub. Lista UsefulMods este **sursă de descoperire istorică**, nu test de compatibilitate în lumea FunCity. Interfața publică de descoperire Modrinth nu ne-a furnizat un export exhaustiv filtrat; nu pretind că am verificat fiecare mod încărcat vreodată acolo. În tabele, «există» înseamnă **fișierul exact indicat** pentru 1.16.5/Forge, NU compatibilitate demonstrată cu toate modurile Lite ori FPS măsurat.

## A. Renderere — se alege **unul**, nu se pun în paralel

| Proiect / ediție verificată | Ce este de fapt | Verdict pentru Lite |
|---|---|---|
| [Rubidium 0.2.13](https://modrinth.com/mod/rubidium/version/0.2.13) | Port renderer Sodium, Forge 1.16.5. Este deja în Lite, iar [changelogul](https://www.curseforge.com/minecraft/mc-mods/rubidium/files/4743730) enumeră corecții ale construirii chunkurilor, scurgerilor RenderTypes și particulelor. | **Rămâne alegerea funcțională.** Nu dubla rendererul. |
| [Embeddium 0.3.18](https://github.com/FiniteReality/embeddium/wiki/Changelog#0318) | Ultima versiune cu suport 1.16.5, fork al aceleiași familii; deja în TEST, **în locul** Rubidium + TexTrue Rubidium Options, cu propria pereche de opțiuni. | Unicul concurent de randare deja pregătit; TEST 5/Fast față de Lite 12/Fancy la ultima citire, deci fără verdict FPS. |
| [Magnesium 1.5](https://www.curseforge.com/minecraft/mc-mods/sodium-reforged/files/all), [Chlorine 0.0.1.3](https://www.curseforge.com/minecraft/mc-mods/chlorine/files/3199916) | Porturi Forge 1.16.5 mai vechi de Sodium, nu complemente ale Rubidium. | Nu au argument demonstrat pentru a schimba clientul funcțional; scoți Rubidium pentru test, nu le adaugi. |
| [Halogen / sodium-forge-2.9.10](https://www.curseforge.com/minecraft/mc-mods/halogen) | **Omisiune importantă din prima căutare:** există port Forge 1.16.5 care a încercat să îmbine Sodium, Lithium și Phosphor. Autorul marchează explicit proiectul **nemaiîntreținut**; în descriere a tăiat Lithium/Phosphor, explicând că optimizările AI și unele funcții de iluminare sunt dezactivate implicit din cauza incompatibilităților. Declară conflicte cu alte forkuri de renderer/OptiFine/Performant. | Nu este un înlocuitor «totul într-un singur JAR» sigur pentru Rubidium, ModernFix, FerriteCore, Oculus și RP; **nu îl instalez**. |
| [Xenon](https://www.curseforge.com/minecraft/mc-mods/xenon/files/all) | Renderer + opțiuni integrate, dar pagina autorului arată **numai Minecraft 1.20.1**. | Exclus 1.16.5. |
| [Sodium](https://modrinth.com/mod/sodium) / [Nvidium Forge pack](https://modrinth.com/modpack/nvidium-forge) / [Celeritas](https://github.com/GTNewHorizons/Celeritas) | Pagina Sodium are game-version 1.16.5, dar **nu** un JAR original Forge 1.16.5; Nvidium Forge pack este pentru 1.20.1 și cere mai multe piese; mirrorul Celeritas avertizează că nu există binare oficiale disponibile pentru descărcare. | Nu se confundă eticheta generală a proiectului cu ediția potrivită loaderului. Nu luăm JAR-uri neoficiale. |

## B. Alte moduri client găsite — compatibile pe hârtie, dar **nu** înlocuiesc rendererul

| Fișier/versiune și sursă exactă | Rol și suprapunere în Lite | Decizie |
|---|---|---|
| [Oculus 1.4.8](https://www.curseforge.com/minecraft/mc-mods/oculus/files/5194273) | Stratul de shaders/compatibilitate peste Rubidium/Embeddium; Lite are 1.4.7. Actualizarea rezolvă probleme vizuale, nu FPS dovedit. | Păstrează 1.4.7 fără test RP al actualizării. |
| [Rubidium/Embeddium Extra 0.4.18 build 107](https://modrinth.com/mod/rubidium-extra/version/lRzQatbE) | Forge 1.16.x: comutatoare particule/animații/cer etc.; **ediția build 107 listează Rubidium ca dependență obligatorie**, deci nu o mutăm automat peste Embeddium TEST; se suprapune cu opțiuni grafice și cu alte add-onuri. | JAR în plus; nu pentru FPS garantat, poate strica vizualul RP. |
| [Embeddium Extras 1.12.5](https://www.curseforge.com/minecraft/mc-mods/embeddium-extras/files/all) | Add-on Forge 1.16.5 publicat pe CurseForge în 2025; [pagina Modrinth a proiectului](https://modrinth.com/mod/embeddium-extras/versions) afișa chiar «No versions in project». **Prezența unui proiect Modrinth nu implică fișiere acolo.** | Nu este renderer autonom; nu adăugăm în TEST peste alt Extra fără verificare de compatibilitate. |
| [Entity Culling 1.16.5-2.1.7](https://modrinth.com/mod/entity-culling/version/1.16.5-2.1.7) și separat [tr7zw 1.5.2](https://modrinth.com/mod/entityculling/version/1.5.2-forge-1.16) | **Două proiecte diferite**, ambele cu build Forge. Ascund entități ocluzate; pot introduce cost suplimentar de culling și pot afecta afișarea NPC/entităților RP. Autorul tr7zw [marchează 1.16.5 drept linie nesusținută](https://modrinth.com/mod/entityculling). | Nu punem ambele și nici unul preventiv înainte de un test cu NPC-urile și utilizarea CPU/GPU pe PC-ul slab. |
| [Better FPS Render Distance 1.1](https://www.curseforge.com/minecraft/mc-mods/better-fps-render-distance/files/3543461) | Forge 1.16.5; reduce secțiunile de chunk randate prin schimbarea formei distanței (poate ascunde vizual zone/peșteri). Nu este o nouă limită server și nici înlocuitor Rubidium. | Cu server view 5 / client dorit 5, risc de pop-in; doar test vizual/FPS pe copie dacă apare scenă specifică. |
| [Dynamic FPS 3.4.3 Forge 1.16.5](https://modrinth.com/mod/dynamic-fps/version/nGi7w36N) și [FPS Reducer 1.16.5-1.24](https://modrinth.com/mod/fps-reducer/version/1.16.5-1.24) | Ambele reduc consumul mai ales când jocul este inactiv/în fundal, **nu** fac orașul să ruleze mai rapid la fereastră activă. Ediții mai noi ale proiectului Dynamic FPS 1.16.5 pot fi *Fabric*, nu Forge. | Nu adăugăm două soluții pentru aceeași țintă care nu e problema cerută. |
| [Distant Horizons 3.3.2-1.16.5](https://modrinth.com/mod/distanthorizons/version/3.3.2-1.16.5) | **Da, există ediție publicată în septembrie 2026 pentru Fabric/Forge 1.16.5.** Randare de teren LOD foarte depărtat; propriile baze de date/generare/CPU/RAM, nu simplifică mobilierul/texture packul și nu înlocuiește rendererul. | Pentru view 5 și PC slab, adăugarea acestuia nu este soluția FPS; nu instalăm doar fiindcă e nou. Compatibilitatea exactă cu Oculus/Rubidium și serverul nostru rămâne netestată. |
| [FastQuit-Forge 3.0.1](https://modrinth.com/mod/fastquit-forge/version/3.0.1+1.16.5forge) | Există pentru 1.16.5; permite revenirea rapidă din «Save and Quit», nu FPS de gameplay. | Nu e necesar pentru cererea actuală. |
| [Mobs Optimized Render](https://modrinth.com/mod/mobs-optimized) | Proiect nou ce declară Forge 1.16.5 și cifre FPS proprii într-o scenă cu 100+ mobi. Nu am confirmat într-o pagină de versiune exactă JAR-ul, dependențele sau A/B pe FunCity; aceeași idee ca Entity Culling. | **Pistă nevalidată**, nu adoptăm marketingul ori benchmarkul autorului pentru serverul nostru. |

## C. Memorie / lansare / server — mai multe moduri există, dar țintesc alte costuri

| Ediție verificată | Ce schimbă; relația cu instalarea | Decizie |
|---|---|---|
| [ModernFix 5.18.0 Forge 1.16.5](https://modrinth.com/mod/modernfix/version/Cc0b1kXl), [FerriteCore 2.1.1](https://modrinth.com/mod/ferrite-core/version/2.1.1-forge), [LazyDFU 0.1.3](https://www.curseforge.com/minecraft/mc-mods/lazy-dfu-forge/files/3249059) | **Deja în Lite**: pornire/bugfixuri/memorie, structuri memorie, respectiv inițializare DFU. Există suprapunere de obiectiv, nu probă că un JAR îl poate înlocui fără pierdere. | Nu adăugăm copie/versiune de alt joc. |
| [Saturn mc1.16.5-0.0.3](https://modrinth.com/mod/saturn/version/mc1.16.5-0.0.3), [Memory Leak Fix 1.1.5](https://modrinth.com/mod/memoryleakfix/version/xYL9nIiR), [Helium 1.0](https://www.curseforge.com/minecraft/mc-mods/hydrogen-reforged/files/3526014) | Builduri Forge 1.16.5; obiective RAM/leaks care pot suprapune ModernFix/FerriteCore. Helium este un port vechi (nu noul proiect Fabric omonim). Autorul Memory Leak Fix menționează preferința pentru versiunea 1.1.2 în unele versiuni vechi. | Fără măsurare RAM/GC și o scurgere diagnosticată nu suprapunem optimizatoare. |
| [Lightspeed 1.16.5-1.1.0](https://modrinth.com/mod/lightspeed/version/1.16.5-1.1.0), [Smooth Boot](https://www.curseforge.com/minecraft/mc-mods/smooth-boot-forge), [DataFixerSlayer](https://www.curseforge.com/minecraft/mc-mods/datafixerslayer) | Pornire/CPU/DFU; pot suprapune ModernFix/LazyDFU, nu FPS în scene RP. | Fără măsurarea timpului de pornire și compatibilității, nu adăugăm. |
| [Structure Layout Optimizer 1.0.7+1.16.5-forge](https://modrinth.com/mod/structure-layout-optimizer/version/1.0.7+1.16.5-forge) | Server/singleplayer, optimizează *generarea structurilor Jigsaw/NBT*, nu FPS client într-un oraș deja generat. Versiunea este din 2025, nu trebuie confundată cu alte versiuni ale proiectului. | Nu are motiv să intre în live fără hotspot de worldgen. |
| [Krypton Reforged 1.0.0](https://www.curseforge.com/minecraft/mc-mods/krypton-reforged/files/3534475) | Forge 1.16.5, stack de rețea client+server; nu e substitut pentru voice chat/renderer. Compatibilitatea cu motorul și pluginurile live nu e testată. | Nu adăugăm pe serverul live doar pentru numărul de jucători din alt server. |
| [AI Improvements 0.5.0](https://modrinth.com/mod/ai-improvements/version/0.5.0) | Forge 1.16.5, AI server; este distinct de FPS client. Alte moduri server (RoadRunner, FastSuite/FastWorkbench + Placebo etc.) au fost deja analizate în [auditul istoric](AUDIT-COST-MODURI.md). | MSPT/profilare, nu stack suplimentar preventiv. |
| [Ksyxis 1.1](https://modrinth.com/mod/ksyxis/versions) | În lista de versiuni există ediția *Ksyxis-Forge1.14thru1.16.5-1.1*; vizează generarea spawn chunks/pornirea lumii, nu FPS în centru. | Nu schimbăm încărcarea lumii live doar pentru pornire mai rapidă. |
| [Clumps 6.0.0.28](https://modrinth.com/mod/clumps/version/6.0.0.28) | Există Forge 1.16.5, dar autorul spune explicit că sub Minecraft 1.17 este necesar **client+server**; registrul `clumps:xp_orb_big` a fost motiv de precauție. Clumps a fost scos din server cu rollback privat, și **nu** e în Lite. | Nu îl adăugăm; nu tratăm drept fix doar pe server. |
| [ChunkLimiter 1.2.0](https://modrinth.com/mod/chunklimiter/version/1.2.0) | Nume înșelător: limitează **numărul de blocuri per chunk**, nu render/view-distance! | Nu-l folosim pentru a limita view-ul. |
| [Load My Chunks](https://modrinth.com/mod/load-my-chunks/version/zvXzZOHh) / [Chunk Loaders](https://modrinth.com/mod/chunk-loaders/version/1.2.8a-forge-mc1.16) / [Chunky](https://modrinth.com/mod/chunky) | Primele două **mențin** chunkuri încărcate, invers scopului de limitare; Chunky pregenerează lumea doar printr-o operație controlată. Autorul Load My Chunks [a renunțat ulterior la Forge 1.16.5 din cauza crashurilor fără diagnostic](https://modrinth.com/mod/load-my-chunks/version/1.2.3). | Nu adăugăm în live. |
| [Starlight (Forge)](https://modrinth.com/mod/starlight-forge/versions) / [Starlight x Create](https://www.curseforge.com/minecraft/mc-mods/starlight-x-create) / [Radon 0.8.0a](https://modrinth.com/mod/radon/version/0.8.0a) / [Sulfuric](https://www.curseforge.com/minecraft/mc-mods/phosphor-reforged) | **Starlight oficial de pe Modrinth NU listează 1.16.5** (minim 1.17.1); varianta Starlight x Create este un fork distinct. Radon/Sulfuric sunt alte schimbări ale iluminării, cu interacțiuni și risc la lumea Forge. | Nu punem două motoare de lumină peste serverul funcțional fără probă pe copie. |
| [Observable 0.2.1](https://modrinth.com/mod/observable/version/Pg3uqzyX) | Modrinth are ediție **Forge 1.16.5** pentru diagnosticarea costului entităților/tile entities; nu reduce singur sarcina. | Candidat de profilare pe copie, nu un optimizer de adăugat tuturor. |
| [spark 1.9.1-forge1165](https://modrinth.com/mod/spark/version/9NSIbttL) | Profiler temporar de diagnostic, nu optimizer ce trebuie să rămână în clientul tuturor. | Folositor pentru a găsi un hotspot, nu un înlocuitor de mod RP. |

### Proiecte cu nume atractiv, dar filtru greșit

- [ImmediatelyFast Backport pentru 1.16.5](https://www.curseforge.com/minecraft/mc-mods/immediatelyfast-backport/files/8119275) este **Fabric**; [BadOptimizations](https://modrinth.com/mod/badoptimizations/versions) nu listează 1.16.5; [Exordium](https://github.com/tr7zw/Exordium/blob/main/Curseforge.md) spune că nu plănuiește backport; [Cull Leaves 2.1.0 1.16.5](https://modrinth.com/mod/cull-leaves/version/NfeMW5mF) este **Fabric**. Eticheta de ansamblu a proiectului («Forge/Fabric, 1.16.5») nu înseamnă aceeași ediție le combină pe amândouă.
- [Forge Optimized 1.16.5](https://modrinth.com/modpack/forge-optimised/version/1.16.5), [Optimized FPS](https://modrinth.com/modpack/optimized-fps/version/1.9.1) și pachete similare sunt **modpack-uri, nu un JAR magic**: dependențele lor ar adăuga multe moduri/posibile suprapuneri și ar putea schimba RP. Nu înlocuiesc packul FunCity doar pentru că sunt marcate «optimized».
- Proiectele de **conținut** de pe Modrinth (mobilier, drumuri, vehicule, arme, mâncare, chat etc.) nu sunt candidați de *înlocuire de performanță* doar pentru că arată asemănător. Registrul/lumea și dependențele vechilor moduri trebuie migrate; tabela celor 22 păstrează acest lucru explicit.

## Inventarul complet al listei de pornire (53 intrări)

Tabelul următor arată **fiecare nume** din secțiunea Forge 1.16.x a UsefulMods. «Rol listat» reproduce categoria listei; **nu** este o confirmare individuală de build 1.16.5 pe Modrinth sau o recomandare de instalare. Cele două linii Entity Culling sunt proiecte distincte. Pentru cele cu analiză aprofundată și fișier confirmat, vezi tabelele A–C de mai sus.

| Proiect publicat (link sursă) | Rol listat | Notă rapidă pentru FunCity |
|---|---|---|
| [AI Improvements](https://www.curseforge.com/minecraft/mc-mods/ai-improvements) | Server | AI server; doar dacă profilarea indică. |
| [APTweaks](https://www.curseforge.com/minecraft/mc-mods/adaptive-performance-tweaks) | Server | Spawn/tick adaptiv; schimbă gameplay, nu client FPS. |
| [Better Biome Blend](https://www.curseforge.com/minecraft/mc-mods/better-biome-blend) | Client | Culori biome; poate suprapune rendererul. |
| [Better Fps - Render Distance](https://www.curseforge.com/minecraft/mc-mods/better-fps-render-distance) | Client | Formă distanță: efect vizual posibil. |
| [Connectivity](https://www.curseforge.com/minecraft/mc-mods/connectivity) | Both | Rețea; nu rezolvă FPS client. |
| [Chunk-Pregenerator](https://www.curseforge.com/minecraft/mc-mods/chunkpregenerator) | Both | Operație de pregen, nu JAR FPS. |
| [Chunky](https://www.curseforge.com/minecraft/mc-mods/chunky-pregenerator-forge) | Both | Pregen controlat, nu FPS la joc. |
| [Chunk Sending](https://www.curseforge.com/minecraft/mc-mods/chunk-sending-forge-fabric) | Server | Ritmul de trimis chunkuri server. |
| [Client Crafting](https://www.curseforge.com/minecraft/mc-mods/client-crafting) | Client | UI crafting, nu randarea orașului. |
| [Clumps](https://www.curseforge.com/minecraft/mc-mods/clumps) | Server | 1.16.5 cere ambele părți; eliminat deja. |
| [Cull Particles](https://www.curseforge.com/minecraft/mc-mods/cull-particles) | Client | Barat în listă; nu candidat. |
| [DataFixerSlayer](https://www.curseforge.com/minecraft/mc-mods/datafixerslayer) | Both | DFU/start; verifică overlap LazyDFU. |
| [Does It Tick?](https://www.curseforge.com/minecraft/mc-mods/does-it-tick) | Server | Diagnostic server, nu optimizer FPS. |
| [DrawerFPS](https://www.curseforge.com/minecraft/mc-mods/drawerfps) | Client | Sertare/cutii; nu înlocuitor renderer. |
| [Dynamic View](https://www.curseforge.com/minecraft/mc-mods/dynamic-view) | Server | Distanță dinamică server; deja view=5. |
| [Embeddium](https://www.curseforge.com/minecraft/mc-mods/embeddium) | Client | În TEST separat; A/B corect necesar. |
| [Entity Culling](https://www.curseforge.com/minecraft/mc-mods/entity-culling) | Client | Alt proiect culling; ID autor separat. |
| [Entity Culling](https://modrinth.com/mod/entityculling) | Client | Proiect tr7zw; Forge vechi, nesusținut. |
| [Entity Collision FPS Fix](https://modrinth.com/mod/entity-collision-fps-fix) | Client | Mod istorico/archived; exclus din Lite. |
| [Fast Async World Save](https://www.curseforge.com/minecraft/mc-mods/fast-async-world-save-forge-fabric) | Server | Salvări server; risc I/O/world, test copie. |
| [FastFurnace](https://www.curseforge.com/minecraft/mc-mods/fastfurnace) | Server | Rețete cuptoare; scenă RP relevantă? |
| [FastSuite](https://www.curseforge.com/minecraft/mc-mods/fastsuite) | Server | Rețete; Placebo obligatoriu în candidatul vechi. |
| [FastWorkbench](https://www.curseforge.com/minecraft/mc-mods/fastworkbench) | Server | Crafting; Placebo obligatoriu în candidatul vechi. |
| [FerriteCore](https://www.curseforge.com/minecraft/mc-mods/ferritecore) | Both | Instalat; memorie, nu renderer. |
| [ForgetMeChunk](https://modrinth.com/mod/forgetmechunk) | Client | Versiune Forge 1.16.5 neverificată individual. |
| [Get It Together, Drops!](https://www.curseforge.com/minecraft/mc-mods/get-it-together-drops) | Server | Grupează dropuri; schimbări server. |
| [Halogen⁶](https://www.curseforge.com/minecraft/mc-mods/halogen) | Client | Proiect abandonat, AI/lighting implicit off. |
| [Helium](https://www.curseforge.com/minecraft/mc-mods/hydrogen-reforged) | Both | Port memorie vechi; poate suprapune FerriteCore. |
| [Krypton Reforged](https://www.curseforge.com/minecraft/mc-mods/krypton-reforged) | Both | Net client/server; impact în FunCity netestat. |
| [Ksyxis](https://www.curseforge.com/minecraft/mc-mods/ksyxis) | Both | Spawn chunks; world/server, nu FPS GPU. |
| [LazyDFU](https://www.curseforge.com/minecraft/mc-mods/lazy-dfu-forge) | Both | Instalat; pornire, nu FPS. |
| [Let Me Despawn](https://modrinth.com/plugin/lmd) | Server | Despawn; afectează lumea/gameplay. |
| [Lightspeed](https://modrinth.com/mod/lightspeed) | Client | Pornire; nu FPS în oraș. |
| [Limited Chunkloading](https://www.curseforge.com/minecraft/mc-mods/limited-chunkloading) | Both | Limite de încărcare; nu confunda cu view. |
| [Log Begone](https://www.curseforge.com/minecraft/mc-mods/log-begone) | Server | Suprimă loguri; poate ascunde diagnostice. |
| [MCMT](https://www.curseforge.com/minecraft/mc-mods/mcmt-multithreading) | Server | Multithreading risc corupere (lista); nu live. |
| [Magnesium](https://www.curseforge.com/minecraft/mc-mods/sodium-reforged) | Client | Alt renderer vechi, exclusiv Rubidium. |
| [Magnesium/Rubidium Extras](https://www.curseforge.com/minecraft/mc-mods/magnesium-extras) | Client | Add-on, JAR în plus, nu renderer. |
| [ModernFix](https://www.curseforge.com/minecraft/mc-mods/modernfix) | Both | Instalat, multi-rol. |
| [Observable](https://modrinth.com/mod/observable) | Server | Profiler (tile entities), nu fix automat. |
| [Out of Sight](https://www.curseforge.com/minecraft/mc-mods/out-of-sight) | Client | Poate ascunde decorul RP. |
| [Overworld Two](https://www.curseforge.com/minecraft/mc-mods/overworld-two-forge) | Server | Generare lume diferită; nu copia live. |
| [Performant](https://www.curseforge.com/minecraft/mc-mods/performant) | Server | Poate interfera RoadRunner/AI. |
| [RoadRunner](https://www.curseforge.com/minecraft/mc-mods/roadrunner) | Server | Tick server, nu FPS client. |
| [Rubidium](https://www.curseforge.com/minecraft/mc-mods/rubidium) | Client | Instalat ca renderer. |
| [Saturn](https://www.curseforge.com/minecraft/mc-mods/saturn) | Both | RAM; fără benchmark nu adăuga. |
| [Smooth Boot](https://www.curseforge.com/minecraft/mc-mods/smooth-boot-forge) | Both | CPU în faza de lansare. |
| [Smooth Chunk Save](https://www.curseforge.com/minecraft/mc-mods/smooth-chunk-save) | Server | I/O salvări server, măsurare înainte. |
| [Spawner Bug Fix](https://www.curseforge.com/minecraft/mc-mods/spawner-fix) | Client | Fix vizual/client în listă, nu server TPS. |
| [Starlight](https://www.curseforge.com/minecraft/mc-mods/starlight-forge) | Server | Oficial Modrinth nu are 1.16.5. |
| [Starlight x Create](https://www.curseforge.com/minecraft/mc-mods/starlight-x-create) | Both | Fork diferit; nu confunda cu Starlight oficial. |
| [Sulfuric](https://www.curseforge.com/minecraft/mc-mods/phosphor-reforged) | Both | Motor de lumină; nu stivui cu Radon. |
| [Radon](https://www.curseforge.com/minecraft/mc-mods/radon) | Both | Motor de lumină; nu stivui cu Sulfuric. |

**Decizie:** rămâne profilul `FunCity RP Lite` cu 22 JAR-uri și Rubidium, server view 5, fără alt mod client. **Cele mai importante noutăți reale** sunt Halogen (nu mai este întreținut, cu componente dezactivate), Distant Horizons 3.3.2 Forge 1.16.5 (funcție LOD care adaugă sarcină, nu rezolvă PC-ul slab), Structure Layout Optimizer (doar worldgen), Dynamic FPS/FPS Reducer (fereastră inactivă), și două proiecte Entity Culling (nu sunt același mod). Pentru comparație validă Rubidium/Embeddium, egalizăm **opțiunile grafice** în cele două profile și măsurăm aceeași scenă/1% low/consumul memoriei; nu riscăm instalarea live ori obiectele RP ca experiment necontrolat. Nu afirmăm că vreunul e automat mai rapid pe PC-ul proprietarului.
