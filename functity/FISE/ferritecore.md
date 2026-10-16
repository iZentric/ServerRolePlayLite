# Fișă: FerriteCore

- **Problemă**: memoria RAM dominată de structuri de date duplicabile (mesh-uri de
  modele, tabele de biomi, stringuri interenate de registru) — la server cu 36 de moduri
  crește presiunea pe GC și riscul de swap pe boxul de producție.
- **Mecanism**: interning + deduplicare la nivel de obiect (model store, biome container,
  registry) fără a schimba semantica de joc; acționează asupra datelor, nu a fluxului de tick.
- **Sursă**: github.com/malte0811/FerriteCore (consultat 2026-10-13 prin API GitHub);
  versiune 1.16.5: 2.1.0 (publicații CurseForge/Modrinth — de verificat SHA la instalare).
- **Licență**: MIT (SPDX confirm din repo, 2026-10-13). Repo activ (ultima împingere 2026-03).
- **Compatibil**: Forge 1.16.5 oficial; pe Mohist = mod Forge de partea serverului, fără
  componente Bukkit — risc de interferență mic, dar de testat obligatoriu cu puntea
  Bukkit→Forge (dedup-ul la registry nu trebuie să atingă CraftInventory — nu îl atinge).
- **Risc**: scăzut ca semantică (nu schimbă tick), dar dedup-ul greșit poate strica
  persistența (partajare accidentală de obiecte mutabile). Attenuare: verificare NBT round-trip
  pe banca noastră (orase RP cu cufere/mașini pe dropper).
- **Experiment**: W3 (memorie/GC) + soak 30 min pe banca de test; comparare ramheap +
  evenimente GC cu si fara.
- **Rezultat**: în așteptarea măsurătorii.
- **Decizie**: **reuse** (pornire din codul oficial, fără fork), condiționat de W3.
