# FISE — registrul candidaților (formatul §2 din ARHITECTURA.md)

O carte per proiect extern evaluat. Regulile jocului:
- **sursă** = URL + data consultării; orice neconfirmat poartă marcaj explicit.
- **licență** = SPDX confirmat din repository, nu din descriere.
- **risc** include și starea de întreținere (ultima împingere).
- **experiment** = cum măsurăm pe bancă (W1–W5 din ARHITECTURA §5), înainte de orice decizie.
- **decizie** = reuse / adaptare / rescriere / incompatibil / neconfirmat.

Stare la 2026-10-13: toate sunt „în așteptarea măsurătorii" — niciun candidat nu intră în
serverul de producție fără card complet + rezultat măsurat. Binarele fără cod sursă
verificabil rulează DOAR în mediu izolat, niciodată pe box cu lumea reală (regula §proces).

## Index

| Card | Verdict provizoriu | Profil țintă |
|---|---|---|
| [ferritecore.md](ferritecore.md) | reuse (așteaptă măsurătoare) | Compatibility+ |
| [krypton-reforged.md](krypton-reforged.md) | adaptare (așteaptă măsurătoare) | Performance |
| [randompatches.md](randompatches.md) | reuse parțial (peticuri selectate) | Balanced+ |
| [ai-improvements.md](ai-improvements.md) | Experimental (schimbă comportamentul AI) | Experimental |
| [starlight-forge.md](starlight-forge.md) | neconfirmat (licență + originea portului) | Experimental, doar izolat |
