# Benchmark motoare CUANTIC — 12 octombrie 2026

**Verdict:** cel mai bun JAR **validat pentru pack-ul actual** rămâne CatServer-ul CUANTIC aflat deja pe server, SHA-256 `96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c`. „Validat” înseamnă că pornește cu exact 36 moduri + 14 pluginuri, are probe pe live cu jucător și nu a pierdut funcționalitatea cunoscută; **nu** înseamnă cel mai rapid motor din lume sau că rulează fără lag pe orice laptop. Niciun fork nou nu a demonstrat simultan câștig repetabil la CPU și p95 plus conectare cu clientul modat și vehicule. Nu am schimbat JAR-ul producției.

## Benchmark comparabil: același pack, GitHub-hosted, A/B/B/A

A = binarul exact din serverul live; B = JAR-ul sursă CatServer 2023 compilat cu patch-ul nostru. Două porniri independente pentru fiecare, pe aceeași mașină în cadrul fiecărui run, Java și seed identice în interiorul runului. Valorile sunt **mediane ale celor două probe per variantă**. **Nu compara numeric rânduri cu sarcini diferite**.

| Candidat B / sarcină | p95 MSPT A → B | CPU A → B | Verdict |
|---|---:|---:|---|
| [Patch nostru, hopper plin, 256/256 NBT confirmat](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38126700415) | **0,45 → 0,75 ms** | **8,87 → 9,66 s** | Pierde ambele. |
| [Patch nostru, 256 hoppers goale](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38127922977) | **3,75 → 3,95 ms** | **9,62 → 9,79 s** | Pierde ambele. |
| [JAR-ul nostru cu scanare optimizată a ticketelor, 64 chunk-uri forțate, incluzând încărcarea inițială](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38175428475) | **5,90 → 4,85 ms** | **19,30 → 19,42 s** | p95 mai mic, CPU nu. A trecut smoke cu 36/14. |
| [Același JAR, aceiași 64 chunk-uri, doar 75 s stabile după 55 s de încălzire](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38176647079) | **1,20 → 1,25 ms** | **3,875 → 3,595 s** | CPU mai mic (~7%), p95 nu; RSS 2140,8 → 2164,0 MiB. Diferențe mici, două probe/variantă. **Nu e upgrade demonstrat.** |

[Patch-ul CatServer upstream 2024](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38125287933) a obținut p95 **1,9 ms** vs **2,9 ms** fără patch pe acel upstream, dar **0,7 ms** pentru binarul live în același test cu hoppers plini. Și acela a pierdut contra live-ului. Nu combinăm rezultate din experimente diferite ca și cum ar fi o cursă unică. Surse/rețete și loguri: [statusul fork-urilor](ENGINE-FORK-STATUS.md), [testul ticket inițial](ENGINE-TICKET-RESULT.md), [testul ticket stabil](ENGINE-TICKET-STEADY-RESULT.md).

## Alte familii de JAR, **aceleași fișiere** de moduri și pluginuri

[Runul de compatibilitate](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178055825) a verificat SHA-256 pentru inventarul celor **36 de moduri și 14 pluginuri**: în copiile izolate s-a înlocuit **doar motorul**, fără tăierea modpack-ului. Nu are sens să afișăm TPS pentru un JAR care nu ajunge la `Done`.

| Motor | Java / rezultat la boot | Este eligibil pentru comparație de performanță cu pack-ul complet? |
|---|---|---|
| CatServer live (2023) | Java 17: `Done`, **14/14 pluginuri** | **Da**, referința. |
| CatServer cu patch-ul nostru de ticket | Java 17: `Done`, **14/14 pluginuri**; [compilare + smoke](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38175428475) | Da pentru teste izolate, **nu** pentru instalare: benchmarkul de mai sus nu validează un câștig complet. |
| Arclight Forge 1.16.5 / 1.0.25 | Java 17: **nu pornește** cu pack-ul complet. [Diagnostic](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178448453): injecția obligatorie `BreakBlockGoalMixin.arclight$mobGriefing` a eșuat `(0/1)` | **Nu**, nu scoatem moduri doar pentru un scor. Nu afirmăm că Arclight nu poate porni cu *alte* pack-uri. |
| Mist 1.16.5-33 | Java 17: `IllegalAccessError`; Java 8: launcherul cere Java 11–15; [Java 11](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178847794): `NoSuchMethodError` în `ManifestEntryVerifier`, fără `Done`. Referința CatServer pe Java 11 a pornit cu **14/14**. | **Nu** cu acest binar și acest pack/JVM; nu raportăm A/B fictiv. |

Paper/Purpur/Pufferfish și Forge simplu nu pot fi candidați echivalenți **cu ambele** 36 moduri și 14 pluginuri Bukkit; comparația lor TPS ar însemna alt joc. Mohist/Magma/LoliServer nu au fost măsurate în această rundă cu un binar verificat pentru aceeași combinație de versiuni; „toate motoarele din lume” nu pot fi declarate învinse fără acele probe.

## Proba pe serverul real și ce primești acum

[Baza reală](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38174649414): CatServer-ul neschimbat, jucător prezent la cele trei citiri; p95 pe 10 s **2,8 / 2,3 / 2,1 ms**, pe 1 min **4,7 / 2,6 / 2,3 ms**. [Profilul CPU](ENGINE-PROFILE-ANALYSIS.md) a ghidat patch-ul de ticket, dar metadatele Spark indică `playerCount: 0` în timp ce consola indica 1 la capetele probei: nu e dovadă de sarcină constantă cu vehicule. Nu am oprit, repornit sau schimbat producția pentru testele noi.

**JAR recomandat acum:** [descărcare directă CUANTIC-Engine-Validated-Live-1.16.5.jar](https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/CUANTIC-Engine-Validated-Live-1.16.5.jar) ([proveniență și SHA verificate în CI](ENGINE-WINNER-JAR.md)). Acesta este **identic bit-cu-bit**, nu o optimizare nouă, cu JAR-ul din arhiva [release-ului `lite`](https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite) `CUANTIC-Server-CatServer-1.7.7.zip` (`CatServer-1.16.5-1d8d6313-server.jar`). Descărcarea directă conține doar motorul; pentru funcționare ai nevoie de pack-ul complet și de numele JAR folosit de scripturile de pornire. **JAR-ul propriu experimental** este doar în [artifactul runului 38175428475](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38175428475) (`cuantic-engine-ticket-EXPERIMENTAL`, disponibil temporar); nu îl recomand drept upgrade. Nu pretind că am construit un motor mai rapid decât câștigătorul curent doar schimbându-i numele. Site-ul nu trebuie să anunțe un motor nou până când unul trece benchmarkul și testul cu client Forge, jucători și vehicule.
