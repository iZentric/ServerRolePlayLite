# FunCity Engine

Motor de Minecraft 1.16.5 (Forge+ Bukkit prin Mohist, derivat GPL-3.0 — atribuit la [MohistMC](https://github.com/MohistMC/Mohist)) cu
setup-ul verificat de pe server: 36 moduri client/server + 14 pluginuri RP, rulat non-stop pe 2 core ARM.

## Ce e aici
- `functity/` — sursele + pachetul de moduri (fise in `functity/FISE/`) + supervisorul JVM (`functity/ci/`)
- `scripts/functity-stage.sh` — kitul de pe server: backup, montare, test, snapshot, restart (mode prin marcaj)
- `scripts/fc_bench.py` — bancul de incercare care a ales motorul (masuratoare, nu promisiuni)
- `aichat/` — FunCityAI, plugin de asistent in chat
- `site/` — pagina publica

## Live
`92.5.171.150:25565` — FunCity b1.0827, 3G heap, JDK 11, world salvat zilnic pe release-ul `world-live`.
