# Fișă: Starlight (port Forge 1.16.5)

- **Problemă**: luminozitatea (sky/block light) din vanilla recalculează agresiv la
  modificări de terain; orașele RP care se construiesc non-stop = ore pierdute în
  light updates (la Mohist, se propagă și prin puntea Bukkit).
- **Mecanism**: motor de lumină rescris (algoritmi de tip BFS cu lazy update), înlocuiește
  integral vanilla light engine. Originea: PaperMC/Starlight.
- **Sursă**: github.com/PaperMC/Starlight (consultat 2026-10-13; ultimul push 2024-03).
  Portul Forge pentru 1.16.5 NU apare ca repository github verificabil prin API —
  distribuția e pe CurseForge/Modrinth („Starlight (Forge)" de Spotted/similar).
- **Licență**: PaperMC/Starlight = „NOASSERTION" pe API (fișier LICENSE propriu — de citit
  înainte de orice utilizare; Paper folosește de regulă licență permisivă, dar NU afirm
  fără să văd fișierul). Portul Forge: licență de revăzut la sursa distribuirii.
- **Compatibil**: teoretic Forge 1.16.5; pe Mohist e zona cea mai periculoasă — puntea
  Bukkit expune BlockLight/hărțile de lumină către pluginuri; orice diferență de hard-light
  se vede în WorldGuard flags/Lights.
- **Risc**: mare la prioritatea 1: lumina greșită = chunk-uri salvate cu date de lumină
  corupte (persistent!). DE ACEEA: rulează DOAR în mediu izolat cu copie de world,
  niciodată direct pe box cu lumea reală (regula §proces).
- **Experiment**: W5 (generare de chunk + lluminare la load) pe lume de test + comparare
  nib-by-byte a regiunilor salvate (anvil diff) cu si fara.
- **Rezultat**: în așteptarea măsurătorii (și a clarificării licenței).
- **Decizie**: **neconfirmat** — nu intră în niciun profil până nu rezolvă: (1) citire
  LICENSE, (2) identitate de autor portului, (3) anvil-diff curat. Dacă rămâne opac,
  rescriem noi algoritmul BFS în FunCity (fără a fura codul).
