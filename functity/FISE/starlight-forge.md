# Fișă: Starlight (port Forge 1.16.5)

- **Problemă**: luminozitatea (sky/block light) din vanilla recalculează agresiv la
  modificări de terain; orașele RP care se construiesc non-stop = ore pierdute în
  light updates (la Mohist, se propagă și prin puntea Bukkit).
- **Mecanism**: motor de lumină rescris (algoritmi de tip BFS cu lazy update), înlocuiește
  integral vanilla light engine. Originea: PaperMC/Starlight.
- **Sursă**: github.com/PaperMC/Starlight (consultat 2026-10-13; ultimul push 2024-03).
  Portul Forge pentru 1.16.5 NU apare ca repository github verificabil prin API —
  distribuția circulă pe CurseForge/Modrinth („Starlight (Forge)" de Spotted/similar).
- **Licență**: PaperMC/Starlight = „NOASSERTION" pe API (fișier LICENSE propriu — de citit
  înainte de orice utilizare; Paper folosește de regulă licență permisivă, dar NU afirm
  fără să văd fișierul). Portul Forge: licență de revăzut la sursa distribuirii.
- **Compatibil**: teoretic Forge 1.16.5; pe Mohist e zona cea mai periculoasă — puntea
  Bukkit expune BlockLight/hărțile de lumină către pluginuri; orice diferență de luminozitate
  se propagă în pluginurile care cită lumina (WorldGuard, restricții de build).
- **Risc**: mare la prioritatea 1: lumina greșită = chunk-uri salvate cu date de lumină
  corupte (persistent!). DE ACEEA: rulează DOAR în mediu izolat cu copie de world,
  niciodată direct pe box cu lumea reală (regula §proces).
- **Experiment**: W5 (generare de chunk + luminare la încărcare) pe lume de test + comparare
  bit-cu-bit a regiunilor salvate (anvil diff) cu și fără.
- **Rezultat**: în așteptarea măsurătorii (și a clarificării licenței).
- **Decizie**: **neconfirmat** — nu intră în niciun profil până nu rezolvă: (1) citirea LICENSE, (2) identificarea autorului portului, (3) anvil-diff curat. Dacă rămâne opac,
  rescriem noi algoritmul de lumină în FunCity, pe cont propriu.
