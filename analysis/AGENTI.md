# FunCity — arhitectura de agenți (decizie finală, 2026-10-16)

## Ce e activ acum
- **Dispatcher unic:** sesiunea Arena pe branch-ul `arena/9bbcb24f-serverroleplaylite`. Tu vorbești doar cu el.
- **Worker #1 (gazda ta):** self-hosted GitHub runner → joburi din `functity-stage.yml` (mod: host-info/backup/assemble/test/up/down/restart/status/expose/install/prune). Fiecare job face checkout proaspăt = "update pe runner" e automat.
- **Worker #2 (runnerii găzduiți GitHub):** `functity-build.yml` (compilă motorul), `site.yml` (publică pagina), `functity-hostinfo.yml`. Rulează cu cota GitHub gratuită, nu pe PC-ul tău.
- **Reguli care nu se negociază:** accesul la cont = NU se dă nimănui (nici unui "agent" care cere parola); secret-e nu se pun în repo; producția nu se atinge fără aprobare explicită în chat.

## Când mai adăugăm un agent
Doar când avem două fluxuri care nu pot aștepta (ex: dezvoltare plugin FunCityAI în paralel cu operațiuni de server). Formă corectă: a doua sesiune Arena pe ACELAȘI repo, dar pe alt branch + markere de handoff în `deploy/`. Niciodată doi agenți pe același branch.

## Ce NU e "subagent"
- OmniRoute/Atomic/Kilo/Jules: tool-uri de cod externe; nu aduc valoare până nu există volum (vezi analysis/FUNCTITY-* pentru ce fac deja joburile noastre).
- Un bot pe PC-ul tău: PC-ul = client de joc, nu loc de muncă. Serverul lucrează deja.
