#_MUTARE PE ALT GITHUB — ghid complet_

Acest repo conține TOT ce există acum: cod, site, workflow-uri, kit de operare,
**toate build-urile FunCity** (branch `functity-out`, 900+ fișiere) și arhivele de producție.

## Varianta A (recomandată): Transfer oficial GitHub
1. **Settings → Danger Zone → Transfer repository** → noua gazdă (cont sau org).
2. Pastă **tot**: branchuri (`main`, arena, `functity-out` cu jare), **releases** (arhiva live +
   world), Pages (site-ul), **runners self-hosted** (boxa + KERNELOS-PC), workflow-urile programate.
3. Singura schimbare manuală după transfer: numele `iZentric/ServerRolePlayLite` apare
   hardcoded în 3 locuri — le actualizezi cu:
   `grep -rl iZentric/ServerRolePlayLite scripts deploy .github site | xargs sed -i 's|iZentric/ServerRolePlayLite|NOUL/REPO|g'`
   (nu uita și link-ul de download din site dacă e pe nume vechi — GitHub face redirect
   temporar de la numele vechi, deci de fapt merge și fără nimic).

## Varianta B: repo nou, push mirror
```bash
git clone --mirror https://github.com/iZentric/ServerRolePlayLite.git
cd ServerRolePlayLite.git
git remote set-url --push origin https://github.com/NUME-NOU/REPO.git
git push --mirror            # duci TOATE branchurile, inclusiv functity-out cu jare
```
**Releases NU se copiază prin git** (sunt pe API) — se mută cu:
```bash
gh repo edit NUME-NOU/REPO  # apoi, pentru arhive, pur și simplu le descarci de aici și le urci acolo:
gh release download world-live -R iZentric/ServerRolePlayLite -p '*.tar.gz' -D ./arhive
gh release create  world-live ./arhive/*.tar.gz -R NUME-NOU/REPO --title "FunCity world snapshots"
```

## Ce conține fiecare bucată
| Unde | Ce |
|---|---|
| branch `functity-out` : `builds/` | toate build-urile FunCity.jar (b1.0600 → b1.2323), fiecare 8.5 MB |
| branch `functity-out` : `pack/` | **CUANTIC-Server-CatServer-1.7.7.zip** (48 MB — serverul vechi complet) + NOTES/SHA256SUMS |
| release `world-live` | `functity-live.tar.gz` (serverul LIVE: jar + 36 moduri + 14 pluginuri + configuri) și `worldsync.tar.gz` (world-ul, când încap pe disc) — create de modul `migpack` |
| `scripts/functity-stage.sh` | kitul întreg de operare pe boxă (backup/tune/bootcheck/tuneprod/packtest/packpromote/inbox/migpack/stats…) |
| `.github/workflows/` | relay boxă (self-hosted), build CI, site + deploy automat, cron cifre reale |
| `site/` + Pages | pagina publică cu benchmark-urile măsurate |
| `functity-stage` reports (`analysis/`) | istoria completă a testelor, cu sonde externe |

## După mutare
- Runners: la **Transfer** rămân atașați de repo. La **repo nou** trebuie re-atasați:
  pe boxă și pe PC rulezi din nou `config.cmd/sh` cu noul URL + `run.sh`/`run.cmd` ca serviciu.
- Verificare rapidă ca totul e viu: marker `migpack x x` pe noul branch → trebuie raport + arhive pe release.
