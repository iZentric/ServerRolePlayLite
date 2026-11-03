# FunCity RP Lite — publicare responsabilă

**Stare la 20.10.2026:** depozitul GitHub și PR-ul de lucru sunt deja publice. Prezentarea proiectului poate fi publicată ca **proiect în dezvoltare**. Noul modpack, motorul derivat și serverul accesibil jucătorilor **nu sunt lansate**. Release-urile istorice ale repo-ului nu trebuie prezentate drept noul Lite.

## 1. Cod și pagină GitHub — public, fără informații private

- README și pagina statică explică proiectul, motivele pentru a-l urmări și stadiul probat, nu un FPS, număr de jucători sau server „online” inventat.
- Publicăm doar cod și documentație auditate. Fără lume, inventare ale jucătorilor, conturi, adrese neaprobate, loguri brute, parole, tokenuri, backupuri sau configurații private.
- PR-ul de lucru este vizibil public, dar nu înseamnă că schimbările sale sunt pe `main` sau că GitHub Pages a publicat noua pagină. Verifică separat integrarea și site-ul după rezolvarea conflictelor PR.
- Fișierul JAR istoric deja urmărit la `aichat/FunCityAI-1.16.5-1.0.0.jar` trebuie auditat la proveniență/licență; nu îl considera aprobat pentru noul pachet doar pentru că se află deja în repo.

## 2. Modpack public — blocat până la probe și drepturi

- Pentru **fiecare** JAR de motor/mod/plugin: identifică titlul, versiunea, sursa, autorul, licența și condițiile de redistribuire; verifică SHA256 al binarului exact și dependențele. Dacă licența nu permite bundling, folosește un mecanism autorizat de distribuție sau lasă binarul în afara release-ului. Nu atribui automat proprietatea utilizatorului.
- Motorul derivat din Mohist/Tenet cere verificarea cerințelor GPL-3.0, atribuire și sursa corespunzătoare binarului efectiv distribuit. Nu aplica o licență globală pentru cod, moduri și asseturi diferite fără audit.
- Testează **clientul LowSpec de 21 JAR-uri** pornit în Prism și conectat la **serverul complet de conținut de 15 JAR-uri** pe instanță închisă. Verifică handshake Forge, emote, vehicule, mobilier, hrană și toate funcțiile RP cerute. Numărul de fișiere sau `Done` nu este o probă de gameplay.
- Optimizează serverul doar dacă RoadRunner / FerriteCore / ModernFix dau câștig relevant și stabil la A/B pe copie, fără regresii; testul actual cu 18 JAR-uri este exclusiv de boot.
- După probe, pregătește manifest cu SHA256, instrucțiuni clare de import și reinstalare, licențe/atribuiri și test de descărcare. Nu eticheta vechile release-uri drept Lite.

## 3. Server accesibil jucătorilor — blocat până la siguranță

- Alege și testează pluginul de autentificare cu cont nou, reconnect și permisiuni; nu dezactiva autentificarea online pentru public fără control funcțional al identității.
- Probează vocea cu client și server, rolurile/economia, CoreProtect (inclusiv rollback), lumea/modurile și conectarea reală a clientului complet.
- Fă backup în afara locației publice, restaurează-l pe o copie și verifică rezultatul; definește rollback și responsabilul pentru incident.
- Măsoară sub sarcină reprezentativă MSPT p95, CPU, RSS/GC și erori. Nu deduce numărul maxim de jucători din sloturi, RAM nominal sau bootul izolat.
- Publică o adresă de intrare numai după testele de mai sus și acordul explicit pentru configurația live, fără a urca fișiere de cont/lume pe GitHub.

**Criteriu de închidere:** un release verificat separat de vechile arhive, documentația corespondentă, client importat și conectat, backup/restaurare probate, permisiuni de distribuire confirmate și aprobarea proprietarului pentru publicarea serverului. Până atunci folosim eticheta **„în laborator”**.
