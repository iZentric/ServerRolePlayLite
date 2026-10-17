# Fișă: RandomPatches

- **Problemă**: zeci de micro-fixuri vanilla/perf care nu au case separat (hopper cu
  entity-inventar, chunk GC, reducere spam log, chestii de rețea minore).
- **Mecanism**: colecție de peticuri individuale, fiecare comutabil din config
  (randompatches.toml). Valoarea lui = granularitatea, nu „totul deodată".
- **Sursă**: github.com/TheRandomLabs/RandomPatches (consultat 2026-10-13);
  versiune 1.16.5: 2.4.4 (din publicațiile oficiale CurseForge — de revăzut SHA la
  instalare). Ultimul push 2021-10 — întreținere înghețată, codul e stabil.
- **Licență**: MIT.
- **Compatibil**: Forge 1.16.5; pe Mohist, peticurile care ating tile entity logic
  (hopper/dropper) se suprapun cu VanillaInventoryCodeHooks — fix P1 al nostru!
  Regula: nicio suprapunere tăcută — dacă activăm patch-ul de hopper din RandomPatches,
  testingul P1 trebuie refăcut împreună.
- **Risc**: mediu din cauza combinărilor; fiecare petic activat individual + testat
  individual (regula „nu orbi din start").
- **Experiment**: activare doar: reduceLoggingSpam, peticurile de hopper/tick (lista exactă a lui 2.4.4 se verifică la instalare), peticurile strict de client se ignoră. Fiecare
  pornit/oprit prin W1+W3.
- **Rezultat**: în așteptarea măsurătorii.
- **Decizie**: **reuse parțial** — doar peticuri selectate, niciodată cu configul implicit
  „totul pornit".
