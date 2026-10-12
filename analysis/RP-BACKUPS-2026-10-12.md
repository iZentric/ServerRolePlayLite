# RP-BACKUPS — ce conțin cu adevărat backup-rile de server (12 oct 2026)

Acces: pipeline-ul **RP-DROP** (`.github/workflows/rp-drop-inspect.yml`) descarcă arhivele din
Drive pe un runner GitHub, le desface acolo și publică **doar text** pe ramura `rp-drop`
(`rp-drop/<server>/inventar.txt` = lista completă de fișiere, `config/` = configuri + cozi de
loguri, `summary.json` = numărătoare). Lume, `playerdata`, `level.dat`, `.mca`, `.db`,
LuckPerms/Vault și orice nume cu `secret|password|token` **nu părăsesc runner-ul**.
Reîmprospătare: un commit oricare pe `deploy/rp-drop.txt`.

## Ce s-a ingerat

| arhivă | marime | fișiere în arhivă | text publicat pe `rp-drop` (stare finală, 4 ingest-uri) |
|---|---|---|---|
| `cffc205d-…tar.gz` (hypecity, „vibe” mare) | 4,19 GB | 43 742 (5,79 GB despachetat) | 425 fișiere, 72 de configuri-rădăcină, `Chat.txt`+`Commands.txt`, 12 scripturi `.sk` |
| `c8b2d730-…tar.gz` (folder „server/backup”) | 1,16 GB | 19 666 | 394 fișiere, coceni identici (același server, martie 2025) |
| `archive-2024-09-14…tar.gz` („vibe rp”) | 1,58 GB | 20 620 (cu tot cu nested) | 433 fișiere, chat + `latest.log` + `debug.log` |
| `minecity-network.rar` | 2,37 GB | 22 405 (rar → `lobby.tar` + `roleplay.tar` + `velocity.tar`) | 259 fișiere: 225 roleplay, 21 lobby (DeluxeHub/Essentials/ViaVersion), 13 proxy (`velocity.toml`) |

`minecity` nu e un server, e **rețea**: proxy Velocity, lobby separat, server de roleplay
1.16.5 și un al doilea set pe **1.19.4** (`mojang_1.19.4.jar` în inventar) — cu `paper-world-defaults.yml`,
`performant-common.toml`, FAWE, AntiVPN, LuckPerms 127 fișiere. Chat-ul din `Chat.txt` / `Commands.txt`
este citibil pe ramură (ex. 11 sep 2024, ora 12:34 — conversație iRed_/vladutz1lol despre microfon),
exact ce ceream: mesaje reale, nu doar configuri.

Primele trei sunt **același ecosistem de server** (acceleași jare, aceleași crash-uri), la trei
date diferite: `folder-1` = 2025-03, `cffc` = 2024-12, `vibe-rp` = 2024-09. `level-name`:
`hypecity`, `world`, `viberp`; porturi 30004 / 25568 / 25566.

## Igiena secretelor (s-a întâmplat și asta)

La al doilea ingest, pe ramură a ieșit `New Text Document.txt` din minecity cu un șir de tip
parolă, plus `api-key` Minetrax, token JPremium/DiscordSRV în configuri. De la rule-ul
următor **redactarea se face pe runner, înainte de publicare**: orice etichetă de tip
`licență|api-key|token|secret|passw` + cheie ≥12 caractere devine `<REDACTAT>`, hash-urile
de licență în linie de sine <REDACTAT> `<KEY-REDACTAT>`, iar fișierele junk
(`New Text Document.txt`, `notes.txt`, `*.pem`, `id_rsa`) nu mai intră deloc. Țeapă de
urmat: cheia Minetrax și token-ul DiscordSRV au fost pe ramura PUBLICĂ ~15 minute —
recomandare explicită către owneri: **rotate** (Discord Developer Portal → Reset Bot Token).

## Constatări cu greutate pentru motorul nostru

1. **Motorul lor real e Mohist, nu CatServer.** `libraries/com/mohistmc/mohist/1.16.5-1183…1242` —
   au schimbat 5 build-uri Mohist în timp; `latest.log` de pe hypecity rulează
   `mohist-1.16.5-1242-universal.jar`. `server.jar`-ul lor are 8 697 833–8 697 846 B față de
   8 697 940 B cât e build-ul 1237 din Maven (verificat independent) — adică foloseau build-uri
   de develor, neverificate public. **Mohist 1.16.5-1237 de pe scara noastră de performanță
   (25/100, `NoSuchMethodError` la smoke) e exact familia pe care aleargă ei.**
2. **Un singur bug le doboară serverul de 23 de ori.** 37 crash-reports pe hypecity, 8 pe
   vibe-rp, 2 pe folder-1; cauza dominantă (23 din 47) e identică:
   `java.lang.NullPointerException: Ticking block entity` →
   `com.mrcrayfish.vehicle.common.inventory.IStorage.func_70302_i_(IStorage.java:44)` cu
   `HopperTileEntity` dedesubt și `performant.mixins.json:hopper.HopperTileEntityMixin` pe
   traseu. Hopperă + vehicul MrCrayfish.  Asta e exact zona pe care noi am patches-o în
   **CUANTIC** (`VanillaInventoryCodeHooks` + `InventoryMoveItemEvent` + `HopperTileEntity`) —
   dovada că directionarea corectă a mers pe boala reală a serverelor de RP, nu pe benchmark.
3. **Câteva crash-uri sunt SecurityCraft**: `CheckBriefcasePasscode.handle` / `CheckPasscode.handle`
   (3+1 pe hypecity, 2 pe folder-1) — patch-ul de passcode e cunoscut în comunitate;
   `crashutilities-3.13.jar` le ținea serverul în viață după crash de tick (mod de „keep alive”).
4. **Moartea prin RAM, din gafa de configurare**: `hs_err_pid1.log` de pe vibe-rp —
   „mmap failed to map **64 458 063 872 bytes**”: cineva a pus `-Xmx`/reserved heap la ~60 GB.
   JVM-ul crapă la pornire. Pe hypecity, `hs_err_pid55217.log` arată G1 cu ~2 300 regiuni de
   2 MiB (≈4,6 GB). Concluzia noastră din `scripts/jvm-tune.sh` (tavan mai mic = pauze mai scurte)
   e confirmată de production, nu doar de laborator.
5. **Java greșit**: hypecity a dat hs_err cu **OpenJDK 16.0.2+7** — în afara sprijinului pentru
   1.16.5. Noi rămânem pe 11 (staging 30 oct: Java 11 boot 9,8 s, pass).
6. **Scala hărții**: `region` 4,26 GB (625 fișiere) pe hypecity, `GriefDefender` 2 971 fișiere /
   69 MB, `advancements` 1 941 / 66 MB, `playerdata` 3 843 / 9,7 MB. `Chunky-1.2.164` era deja
   folosit (pre-generare), dar `view-distance=6` pe hypecity+folder-1 și 12 pe vibe-rp —
   la 200 de jucători max cu 4,6 GB heap, 6 e singura distanță care mergea.
7. **Mesaje/chat**: `ChatManager/Logs/Chat.txt` **41,8 MB**, `Commands.txt` **55,5 MB**,
   `Swears.txt`, `Signs.txt` + `latest.log` cu chat live și `/command`-uri. Cozile lor intră pe
   `rp-drop` din regula nouă `*.txt`/`*.sk` (rule #6).
8. **Supraîncărcarea de plugini explică totul**: 61–65 plugin-uri + 35–49 moduri pe serverele lor,
   față de 14 plugin-uri + 36 moduri în CUANTIC. Duplicări reale: două versiuni de `Xaeros`
   simultaneous în `mods/`, `DeluxeMenus` 1.13.7 **și** 1.14.0, `PlugManX` de două ori,
   `MyCommand` cu `(2)` în nume, `Multiverse-Core-4.3.1 (2)`. Un server care își dublează
   plugin-urile în folder nu e „lent”, e nediagnosticat.
9. `online-mode=false` peste tot, AuthMe `5.6.0-beta2` (beta!) ca singur zid de autentificare.

## Ce facem cu astea

* Scara de performanță are acum **un caz real de producție** pentru familia Mohist: nu e ipoteză
  că „merge la ei” — rulează cu 23 de crash-uri identice și mor de heap. CUANTIC rămâne
  singura variantă pe care o putem susține cu dovezi, iar patch-ul de hopper/vehicle devine
  punct de vânzare și pentru migrarea lor.
* Pasul următor pe staging (deja agățat de runda 5): redăm **același scenariu hopper+vehicul** pe
  CUANTIC vs CatServer oficial; dacă CUANTIC nu crash-ează, avem primul A/B *calitativ* cu
  semnificație de producție, nu doar ±Milis secunde.
* `analysis/atlas*`/ladder rămân nemodificate — cifrele de mai sus nu schimbă verdicturile,
  le motivează.

## Cum reiau totul oricând

```text
git fetch origin rp-drop && git ls-tree -r --name-only origin/rp-drop   # ce există
deploy/rp-drop.txt: commit oricare → rulează RP-DROP → rescrie rp-drop/ # reîmprospătare
```
