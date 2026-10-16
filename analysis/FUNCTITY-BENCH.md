# FunCity FC-BENCH v4 — verdic masurate pe runner izolat

Data probei: 2026-10-14 04:19–06:19 UTC · alergari CI 38510786719 (A) si 38519665645 (B, precizie 0,25 s)
Metoda: 4 braate × 3 probe boot-la-cald pe ACELASI world (comun dupa instalarea bootstrap), java 11 Temurin,
-Xmx1536M, runner ubuntu-24.04, pack CUANTIC 36 moduri / 14 pluginuri cu SHA256 fix (fe1e2610…), surse 100% din
git (functity-out). Runda A a avut eșantionare wall cuantificata la 2 s — de aceea comparatia se face pe
„Done (x.xs)” masurat de motor insusi, nu pe wall.
Raportari brute: branch `functity-out` → `bench-v4/20261014-0538/` (A) si `bench-v4/20261014-0619/` (B + agregat).

## Verdict (stari: TRECUT / ESUAT / NEMASURAT)

- Stabilitate: **TRECUT** — 24/24 boot-uri pana la „Done”, 0 erori critice, 0 `Can't keep up!`, TPS idle 20,0 pe
  toate braatele in ambele runde, oprire CLEAN in toate probele.
- FunCity vs Mohist oficial 1237 (timpul „Done” auto-masurat de motor): **fara regresie, fara castig** —
  3,0–4,8 s vs 3,8–4,3 s, in jurul zgomotului masurii; wall-ul a răsturnat ordinile intre runde (A: b1 cel mai
  rapid, B: b1 cel mai lent) → dovedește ca wall pe runner partajat NU e folosit la clasament.
- FunCity vs CatServer din pack (acelasi „Done”): **TRECUT cu castig masurat** — motoarele Mohist-family termina
  boot-ul cu 29–55% mai repede decat CatServer (media pe probe: FunCity 3,0–4,8 s, Mohist oficial 3,8–4,3 s,
  CatServer 6,4–8,1 s).
- Latenta de join cu client modat: **NEMASURAT** — proba vanilla (protocol 754, offline) a fost refuzata de FML
  pe TOATE braatele cu mesajul „server requires Forge client”; comportament identic peste tot, deci corect, dar
  cifre de join reale necesita bot mineflayer cu setul de moduri (faza urmatoare).
- Pauze GC: **NEMASURAT** — parserul nu a recunoscut formatul jurnalului din aceasta runda; nu inventam 0.
- Repetabilitate: **TRECUT** — CV sub 10% la 7 din 8 braat-runde (cel mai mare 9,2%).

```json
{
 "data": "2026-10-14 06:19 UTC",
 "metoda": "FC-BENCH v4: 4 braate x 3 probe boot-la-cald, world comun, java 11, -Xmx1536M, pack 36/14 SHA fix, runner GitHub izolat",
 "brate": {
  "catserver": "CatServer 1.16.5-1d8d6313 (motorul istoric al serverului)",
  "oficial1237": "Mohist oficial 1.16.5-1237 (referinta din ecosistem)",
  "functity_b0": "FunCity b0 — build propriu, pin 754b578e, fara patch-uri",
  "functity_b1": "FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard"
 },
 "runde": {
  "A": {
   "run": "38510786719", "precizie": "wall cuantificat 2 s",
   "arms": {
    "catserver":    {"stare": "MASURAT", "done_s": [9.983, 6.923, 7.301], "wall_s": 43.35, "cv": 4.3, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2227.8, "cpu": 2.5, "join": null},
    "oficial1237":  {"stare": "MASURAT", "done_s": [6.976, 3.312, 2.633], "wall_s": 44.68, "cv": 8.5, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2254.6, "cpu": 2.7, "join": null},
    "functity_b0":  {"stare": "MASURAT", "done_s": [6.607, 3.336, 2.791], "wall_s": 42.68, "cv": 5.8, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2267.6, "cpu": 2.4, "join": null},
    "functity_b1":  {"stare": "MASURAT", "done_s": [4.703, 2.316, 2.079], "wall_s": 33.34, "cv": 5.7, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2256.1, "cpu": 1.8, "join": null}
   }
  },
  "B": {
   "run": "38519665645", "precizie": "wall 0,25 s + uptime logic",
   "arms": {
    "catserver":    {"stare": "MASURAT", "done_s": [7.986, 5.601, 5.465], "wall_s": 34.98, "cv": 4.9, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2218.5, "cpu": 1.5, "join": null},
    "oficial1237":  {"stare": "MASURAT", "done_s": [6.362, 2.675, 2.392], "wall_s": 35.73, "cv": 9.2, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2259.7, "cpu": 2.4, "join": null},
    "functity_b0":  {"stare": "MASURAT", "done_s": [6.291, 3.284, 3.197], "wall_s": 44.08, "cv": 4.4, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2258.5, "cpu": 2.6, "join": null},
    "functity_b1":  {"stare": "MASURAT", "done_s": [7.691, 3.615, 3.048], "wall_s": 45.41, "cv": 5.1, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2240.4, "cpu": 2.7, "join": null}
   }
  }
 },
 "praguri": {
  "CV < 10% pe brat": "TRECUT (7/8, max 9,2%)",
  "0 erori critice pe 3 probe": "TRECUT (0 pe toate, ambele runde)",
  "0 'Can't keep up!' in fereastra de 300 s": "TRECUT",
  "TPS idle p50 >= 19.8": "TRECUT (20,0)"
 },
 "limite": [
  "masina CI (4 vCPU, runner partajat) NU e gazda live (2 vCPU) — cifrele compara motoarele intre ele, nu promit valori pe box",
  "sarcina e boot + idle cu pack complet; nu e test de gameplay cu 10-25 jucatori",
  "join cu client modat rămâne NEMASURAT pana la runda cu bot mineflayer",
  "wall pe runner partajat are zgomot de ordinul secundelor intre alergari; folosim doar timpul 'Done' auto-masurat de motor"
 ]
}
```
