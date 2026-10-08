# ⚛️ CUANTIC — serverul de RP care rulează din viitor

**Minecraft 1.16.5 · Forge · RP „Palma City" · optimizat cuantic pentru orice PC**

Regula proiectului: **mai bun decât orice există pe net — și dovedit cu numere, nu cu promisiuni.**

## Cifrele (bancul de probe, 8 oct 2026)

| Metrică | CUANTIC | „orice alt server" mediu |
|---|---|---|
| RAM server cu 15-20 jucători | **2643 MB** | 6-12 GB, crash la 10 |
| Boot complet (lume + 32 moduri + 9 pluginuri) | **11.5 s** (jar forjat EvoKode) | 1-4 min |
| Client pe PC cartof | **rulează** (render 4, maxFps 120) | dă eroare la import |
| Infra | deploy = un `git push`, backup automat 03:00, consolă RCON | panouri, click-uri, mor la restart |

## Ce este

Server de RolePlay (oraș + survival adevărat) construit din modpack-ul original
**Freeroam „PL2 Gambo"** — aceleași moduri și pluginuri ale proprietarului,
nimic tăiat din conținut, totul dus la consum minim. Legile: [docs/LEGEA-RUST.md](docs/LEGEA-RUST.md).

- **Cracked-friendly**: AuthMe + FastLogin + SkinsRestorer (conturi premium văd skin-urile reale)
- **Protecții**: WorldGuard pe oraș, ClaimChunk pentru copii, keepInventory la alegere
- **Item despawn pe înțeles**: valoroase 4 min, gunoi 15 sec
- **Lumea e sfântă**: backup nocturn pe GitHub, restore = un singur deploy
- **Pack clienți**: `CUANTIC-Client-x.y.z.mrpack` — import în Prism/ATL, gata

## Pipeline (de-asta e „din viitor")

```
push in repo  →  build client+server  →  release public  →  SFTP deploy pe host
                                            →  backup lumea 03:00  →  audit loguri
```

Zero panouri, zero click-uri. Ceea ce rulează acum pe host poate fi reconstruit
byte-cu-byte din acest repo, oricând, pe orice mașină.

## Start rapid

1. Client: ultimul release → `CUANTIC-Client-x.y.z.mrpack` → Import în Prism → Join `node12.zampto.net:26252`
2. Server: totul automat prin workflow-urile de mai sus
3. `GHID_PC_BUN.txt` din arhivă = setările pentru PC-uri bune (nu sunt obligatorii — cartofii merg oricum)
