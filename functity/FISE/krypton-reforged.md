# Fișă: Krypton-Reforged

- **Problemă**: rețeaua (packet batching + flush) arde CPU pe tick-ul de rețea când sunt
  mulți jucători în același orase — fluxul vanilla trimite pachete mici nefragmentate.
- **Mecanism**: înlocuiește attention la flush + batching la nivel de packet buffer
  (port al lui Krypton de la Fabric la Forge, adaptat la netty din 1.16). Nu atinge
  logicoa de joc, doar transportul.
- **Sursă**: github.com/txnimc/KryptonReforged (consultat 2026-10-13, API GitHub);
  ultima împingere 2023-06-24, ramura 1.16.5.
- **Licență**: MIT (SPDX din repo).
- **Compatibil**: Forge 1.16.5. PE MOHIST ATENȚIE: Mohist are propriul lui attention
  patch la rețea (Bukkit eventuri pe packet); suprapunerea Krypton + puntea Mohist poate
  speri event-urile de rețea ale pluginurilor (ex. AuthMe, protocol handshake) — de
  verificat în carantină cu login complet, inclusiv auth.
- **Risc**: mediu — netty patch greșit = corupție de flux/deconectări. Nu schimbă-world
  data, deci world-ul nu e în pericol (prioritatea 1 respectată).
- **Experiment**: W1 (TPS/MSPT) + W2 (multiplayer burst 20 fake players — suport pentru
  fakeplayers e în lista de engine-* din deploy) + soak deconectări; comparare cu
  profilul fără.
- **Rezultat**: în așteptarea măsurătorii.
- **Decizie**: **adaptare** (păstrăm idea de batching, dar dacă patch-ul nu coexistă cu
  puntea Mohist, rescriem noi partea de flush în FunCity — licența MIT permite amândouă).
