# INVENTAR MUTARE — ce conține repo-ul, măsurat acum

Repo pe GitHub: ~154 MB (toate branchurile, cu tot cu istorie)

## Binare pe branchul functity-out (se cloneaza odata cu repo-ul)
- **90 build-uri FunCity-1.16.5.jar** (252 MB) — versiuni: b.0600 1.0732 1.0827 1.1115 1.2105 1.2118 1.2140 1.2222 1.2223 1.2235 1.2256 1.2258 1.2322 1.2323 1.2326
- **pack/CUANTIC-Server-CatServer-1.7.7.zip** (48.7 MB) — serverul vechi 1.7.10 complet (jar+mods+configs+launch)

```
fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15  CUANTIC-Server-CatServer-1.7.7.zip
```
- bench-v4/, bench/, smoke36/ — datele brute ale testelor de pe boxa (5.9 MB)

## Cod + operatiuni (branchul arena / main)
- scripts/functity-stage.sh — kitul complet: backup, tune, bootcheck, tuneprod, packtest, packpromote, inbox, migpack, unclog, stats
- .github/workflows/ — relay boxa (self-hosted), pack-build CI, site + deploy Pages, site-auto cron, runner-probe (test PC Windows)
- site/index.html — pagina publica cu benchmark-urile masurate (se redeployeaza automat din main)
- analysis/FUNCTITY-STAGE.md — istoria rapoartelor + sonde externe ale portului 25565
- deploy/funcity-stage.txt — markerii de comanda catre boxa (format: MODE port jar)

## Ce NU e in repo (temporar, pana revine runnerul de pe boxa)
- setul LIVE de pe server: 36 moduri + 14 pluginuri exacte, configurile curente, lume 1.16.5, libraries/versions
- ele vin in release-ul `world-live` prin \`migpack\` (functity-live.tar.gz + worldsync.tar.gz cu sha in label)
- cat时间在: rulez markerul cum revine runnerul (ai comanda de diagnostic data); FARA runner, FunCity ramane neatinis si in continuare ruleaza

## Cum muti (alegi UNA)
1. **Transfer GitHub** (recomandat): Settings → Danger Zone → Transfer → pastă branchuri + releases + runners + Pages + redirect. Zero mutari de maina.
2. **Repo nou + mirror** (doar git, NU si releases):
   ```
   git clone --mirror https://github.com/iZentric/ServerRolePlayLite.git && cd ServerRolePlayLite.git
   git remote set-url --push origin https://github.com/NOU/REPO.git && git push --mirror
   ```
3. **Mi-l dai pe cel nou** (creat gol, cu acces la contul tau) — fac mirror + recreez release-urile cu `gh`, zero miscari de la tine.
