# Fișă: AI Improvements

- **Problemă**: IA vanilla (pathfinding, sensing) e costisitoare pe server cu multe
  entități — fiecare entitate vie din orașul RP plătește tick de pathfinding și sensing.
- **Mecanism**: înlocuiește pașii de pathfinding cu variante optimizate (cache,
  throttling pe distanță). SCHIMBĂ comportamentul observabil al mob-ilor (diferențe față de vanilla în
  rutină) — de aceea e doar Experimental, niciodată în Compatibility.
- **Sursă**: github.com/BuiltBrokenModding/AI-Improvements (consultat 2026-10-13);
  repo activ (push 2026-10), linia de versiuni pentru 1.16.5: 1.1.2/1.2 — de fixat
  exact la instalare.
- **Licență**: MIT.
- **Compatibil**: Forge 1.16.5; pe Mohist, mob-urile atinse de pluginuri (Clear lag,
  stack de entity de la mod RP) pot intra în conflict cu cache-ul de pathfinding.
- **Risc**: RIDICAT pentru prioritatea 1 (integritatea lumii) — comportamentul diferit
  al AI nu corupe world-ul, dar schimbă gameplay-ul RP (un cal care se blochează altfel
  satele reacționează diferit la hoarde). Activabil DOAR cu acordul explicit al lui marius
  și doar după test de joc, nu doar de cifre.
- **Experiment**: W4 (entity spam) + test de joc manual (comportare observabilă) +
  comparare video 60s pe aceleași entități, seed identic.
- **Rezultat**: în așteptarea măsurătorii.
- **Decizie**: **Experimental** — opt-in, cu documentație de trade-off gameplay în
  panoul de profil.
