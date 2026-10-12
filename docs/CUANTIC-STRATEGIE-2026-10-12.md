# Cuantic — strategie de construcție Roleplay Lite

**Decizie de produs:** serverul rămâne **non-premium** și clientul rămâne **modat Forge 1.16.5**. Sistemul `/login` se adaugă **la finalul dezvoltării serverului**, nu este condiție pentru experimentele curente. Cost maxim: 0. Acest plan este local; nu schimbă serverul, pack-ul sau JAR-ul.

## Ce știm, ce nu știm

- Release-ul verificat prin SHA conține [36 de moduri și 14 pluginuri](ENGINE-PACK-AUDIT.md); clientul și conținutul RP/survival trebuie păstrate. FerriteCore, ModernFix și RoadRunner sunt deja prezente; încă un mod de optimizare nu este automat o îmbunătățire.
- În [CHK la 09:54 UTC](../analysis/chk.md), Java, supervisorul, tunelul și portul Minecraft local au pornit, dar cele trei verificări externe au întors `online:false` / `Unknown problem with returned server data`. Nu avem acolo probă de conectare modată de afară și nu deducem starea actuală a serverului dintr-un log vechi.
- [A/B/B/A CUANTIC vs CatServer oficial](ENGINE-NATIVE-RESULT.md) nu a arătat avantaj repetabil; [patch-ul SortedArraySet](ENGINE-STRICT-RESULT.md) nu a trecut criteriul strict. [Încercarea cu fake players](ENGINE-FAKEPLAYERS-RESULT.md) a lăsat `/list` la 0/25. Nu avem încă probă de capacitate la 5, 10 sau 25 jucători reali.

## Ordinea de lucru — fără muncă de dragul muncii

| Etapă | Ce implementăm/testăm | Când o considerăm trecută |
| --- | --- | --- |
| 1. Conectare și gameplay | Verificăm traseul port local → tunel → status public → client Forge normal în lume; testăm vehicule, inventar, chat, survival, mobs și salvare/reconectare. Investigăm pe copie avertismentul de mixin ModernFix/RoadRunner din CHK. | Clientul modat intră, funcțiile cerute sunt utilizabile, logurile nu indică erori noi; fără restart experimental peste jucători. |
| 2. Măsurare reală | Fixăm lumea, seed-ul, Java, versiunile și distanțele. Profilăm Spark, CPU, RSS și GC la repaus și cu activitate RP/vehicule, apoi găsim hotspot-ul. | Raport datat cu hardware, număr real de jucători, MSPT p95/p99 și logurile corespunzătoare; nu combinăm probe din scenarii diferite. |
| 3. Load pe staging | Găsim/creăm harness cu handshake Forge validat; verificăm prezența efectivă în `/list`, apoi testăm 1 → 5 → 10 → 25 clienți numai dacă pragul anterior a trecut. Mișcare, chunkuri, entități, reconnect și soak, nu doar status-ping. | Fiecare prag este repetat; raportăm doar jucătorii conectați efectiv. Dacă botul nu poate intra, rezultatul este „netestat”, nu „25 suportați”. |
| 4. Candidat Cuantic izolat | Alegem **un singur** hotspot dovedit; implementăm patch în copia sursei, păstrăm atribuiri și facem build reproductibil. Comparăm A/B/B/A cu baseline-ul pe același pack/client/lume. | Startup, CPU, p95 și RAM strict mai bune, repetabil, plus compatibilitate RP/survival/vehicule; altfel candidatul este respins, iar JAR-ul live rămâne neschimbat. |
| 5. Profil Lite și funcții finale | Optimizăm pentru host modest fără a elimina pe ascuns conținutul. Comparăm clientul normal cu OptiFine separat de orice variantă alternativă pe laptop slab în oraș. Finalizăm abia apoi experiența de onboarding și sistemul `/login` pentru non-premium. | Țintă de test: cel puțin 19,5 TPS susținut, p95 MSPT ≤ 50 ms după încălzire, fără crash și cu funcțiile păstrate; hardware-ul minim și numărul de jucători se publică numai dacă sunt măsurate. |

**Strategia mea:** gameplay coerent și accesibil întâi, capacitate măsurată apoi, un motor Cuantic cu patch-uri proprii numai când poate depăși baseline-ul fără regresii. Nu declarăm 1000×, „zero lag” sau un JAR superior dintr-un boot gol. `/version` și proveniența upstream trebuie verificate pe build-ul real înainte de un release nou.

În acest tur am corectat doar strategia locală după decizia proprietarului. Nu s-a construit/deployat un JAR și nu s-a rulat un test nou cu jucători.
