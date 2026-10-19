# FunCity Lite — baseline istoric pentru validare, NU pachetul lean final (19.10.2026)

> Actualizare V2: `agent/DECIZII.md` este alegerea în vigoare; ținta client are 23/25 moduri istorice plus Voice Chat Forge (24 total); acesta este doar baseline-ul vechi.

**Corecție:** după comparația cu motoarele/configurile de pe PC și prioritatea explicită „fără moduri degeaba”, cele 25 de JAR-uri de mai jos reprezintă numai copia A pentru A/B, **nu lista aleasă pentru publicare**. Ținta este cea mai mică combinație cu RP funcțional și beneficiu real; `agent/alegere-motor-lean.md` definește motorul și poarta de eliminare. Primul A/B client este Out of Sight, separat de Entity Culling. Niciun pack instalat nu a fost schimbat.

**Ce am comparat:** arhiva publică CUANTIC 1.7.7 avea **36 moduri pe server și 14 pluginuri**, nu un client cu 36 JAR-uri (`git show b1ec20c:docs/ENGINE-PACK-AUDIT.md`). Captura făcută de runner din `E:\Administrator\Desktop\FunCity` (`diag/oldcfg-report.txt`) arată în HYPECITY BK configurații pentru CGM, CFM, FerriteCore, AI Improvements, Performant, PlasmoVoice, Aquaculture, Tough As Nails, UsefulBackpacks, XLFoodMod. Prezența configurațiilor este dovadă despre proiect, **nu** că orice mod era încărcat ori că avea FPS bun. CUANTIC avea view 4, broadcast 60%, compresie 512 (`agent/comparatie-proiecte-vechi.md`). Nu există un clasament verificabil al popularității proiectelor sau FPS comparabil de pe laptopurile lor.

**Copia client A pentru comparație:** exact cele **25 de nume** din cele două inventare istorice identice `diag/pc-client.txt`, organizate după rol, fără JAR-uri server-only; prezența în A nu dovedește necesitate în clientul Lite final:

| Rol | Moduri alese (numele complete ale fișierelor sunt în inventarul istoric) |
|---|---|
| Conținut RP (11) | Additional Guns, CFM, CGM, Emotecraft, Modern Life, ModernXL, Pam's Food Core, Pizzaland, Road Stuff, Supplementaries, Vehicle Mod |
| Biblioteci ale conținutului (4) | Mapper Base, Obfuscate, Player Animation Lib, Selene/Moonlight |
| Pornire/RAM/randare (6) | Entity Collision FPS Fix, FerriteCore, LazyDFU, ModernFix, Radon, Rubidium |
| Vizibilitate (3) | Entity Culling, Oculus, Out of Sight |
| Compatibilitate XP (1) | Clumps — pe ambele părți ale conexiunii Forge 1.16.5 |

**De ce nu copiez tot din HYPECITY:** adăugarea Aquaculture, PFM, Tough As Nails, UsefulBackpacks, XLFoodMod sau PlasmoVoice ar încărca clientul și/sau ar schimba gameplay-ul fără probă de necesitate în lumea FunCity. Performant nu se adaugă lângă RoadRunner-ul serverului doar pe baza numelui. În schimb păstrez mobilierul, vehiculele, armele și mâncarea existente; clientul nu primește AI Improvements, Ksyxis sau celelalte optimizări strict server. Vocea RP apare în vechiul HYPECITY și pe serverul CUANTIC (`voicechat`), dar inventarul istoric al clientului FunCity nu confirmă un mod de voce: **nu promit voice chat funcțional și nu adaug o dependență incompatibilă pe nevăzute.**

**Preset ales:** shaders oprite, render 5, Fast Graphics, AO off, particule minime, mipmap 0, umbre entități off, VSync off; nu impun Xmx universal. Este o țintă de import unic în launcher, nu instrucțiune de rescriere a profilului instalat. Serverul rămâne la b1.0827 și packul actual; nu scoatem moduri de pe server din numărul din arhiva veche. Pentru CPU/rețea pe laptopuri slabe, view 4 și broadcast 60% sunt **candidați A/B individuali**, nu setări copiate pe live.

**Poarta binară — NU E TRECUTĂ:** `gh api` raportează pentru assetul `FunCity-1.2.5.mrpack` 135.786.860 B și SHA256 `cd9c8ddeaff2e02e009934d7a35eba14b1b5a2bc919797ad7a0ab2a92bc5fb47`; atât `gh release download`, cât și alternativa API pentru asset au dat EOF pe hostul de assets. Nu am putut deschide/verifica ZIP-ul; `diag/curate.log` arată că o versiune anterioară scotea Oculus/LazyDFU, iar `diag/pc-client.txt` arată Clumps adus ulterior din server. Numele celor 25 instalate **nu garantează** că release-ul 1.2.5 le instalează. Pentru un `.mrpack` final, trebuie manifest cu hashuri reale, import curat + reinstalare, login Forge cu registry compatibil, verificare RP și A/B FPS/RAM pe laptop vechi, backup și rollback testat. `scripts/fc_mrpack_audit.py` poate verifica structura când binarul devine disponibil. **Nu fabricăm un `.mrpack` din nume fără binare/hashuri și nu publicăm un release fals.**

**Verdict:** baseline-ul primului test este inventariat, dar **selecția lean finală NU este decisă** fără A/B; pachetul instalabil final, performanța pe „orice OLX” și audio/voce rămân NEMĂSURATE. La eșec de login sau gameplay, nu reducem conținutul în orb: investigăm dependența/registrul, refacem testul și revenim la packul funcțional.
