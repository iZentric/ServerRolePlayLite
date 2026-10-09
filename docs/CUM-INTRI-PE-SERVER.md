# Cum intri pe CUANTIC (Java 1.16.5, **cracked**)

**Adresa:** `92.5.171.150:25565` · **Pack obligatoriu:** `CUANTIC-Client-1.5.9.mrpack` (3 minute de dat)
Release cu toate fișierele: <https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite>

## Regula de aur
**Fără pack = nu intri.** Serverul are ~32 moduri. Dacă ai doar „Minecraft Forge 1.16.5" curat, primești
`Failed to synchronize registry data` și rămâi pe ecranul de login. Packul **se instalează o singură dată**.

## 1. Prism Launcher (gratuit, open source)
<https://prismlauncher.org/downloads/> — alege `.exe` (Windows 64-bit).
La prima pornire: **Settings → Java → iconița de descărcare** → `17 (LTS)` → **Run** (nu instala Java tu).

## 2. Importă packul
**Add Instance → Import →** alege `CUANTIC-Client-1.5.9.mrpack` → **OK**.
Instance noua apare în listă cu numele **CUANTIC**.

## 3. Intră în joc
Lansează **CUANTIC** → **Multiplayer → Add Server** → *Server Address*: `92.5.171.150:25565` → **Done → Join**.
Nu ai cont Premium? Nu contează: serverul e **cracked** (vezi [login fără Premium](login-fara-premium.md)).

## Nu merge — citește mesajul de pe ecran

| Ce scrie | Ce înseamnă | Ce faci |
|---|---|---|
| `Failed to synchronize registry data from server` (clientul stă pe „Downloading and encoding registry data…" și atât) | ai intrat **fără** pack, sau ai un client care nu are aceleași moduri ca serverul | vezi mai jos |
| `Server has additional mods that may be needed on the client: ... clumps@... placebo@...` (în `latest.log`) | serverul are moduri care înregistrează **obiecte/entități** — fără ele id-urile de registru nu se potrivesc | **importă `CUANTIC-Client-1.5.9.mrpack`** (din 1.5.9 jarurile de registru — Clumps, Placebo, FastFurnace, FastWorkbench, AI-Improvements, InControl, bwncr — sunt **și în client**, copiate byte-cu-byte de pe server) |
| `Connection refused` / `timed out` | serverul e jos | `bash ~/c.sh` în Cloud Shell (el singur își ia packul cel mai nou de pe release) |
| `Invalid session` / `Failed to login` | online-mode pornit | pe server: `online-mode=false` în `server.properties` + restart |

### Fix de 30 secunde, fără să reinstalezi nimic (până apuci să-ți faci importul)
Deschide PowerShell și lipește:

```powershell
cd $env:APPDATA\PrismLauncher\instances
Invoke-WebRequest "https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/CUANTIC-Server-CatServer-1.5.9.zip" -OutFile s.zip
Expand-Archive s.zip -DestinationPath s -Force
$m=(dir "CUANTIC*" | dir -d | ?{ test-path "$($_.FullName)\mods" } | select -First 1).FullName
copy "s\mods\Clumps-*.jar" "$m\mods\" -Force; copy "s\mods\Placebo-*.jar" "$m\mods\" -Force
del s.zip; rm -r s
```

După asta dă **Join** iar. (E suficient Clumps — el înregistrează entitatea `clumps:xp_orb_big` care bloca
`minecraft:entity_type`. Restul jarurilor le iei oricum din pack la import.)

## De ce apare `Missing registry data for network connection` (cauza reală, documentată)
Din `latest.log` al unui client 1.5.8 pe server 1.5.8:

```
[Server thread/ERROR]: Server has additional mods that may be needed on the client:
   incontrol@1.16-5.2.12, bwncr@1.16.5-3.10.16, fastfurnace@4.5.0, aiimprovements@0.4.0,
   clumps@6.0.0.28, fastbench@4.6.2, placebo@4.7.1
Unidentified mapping from registry minecraft:entity_type
     clumps:xp_orb_big: 113
Missing registry data for network connection
Failed to load registry, closing connection.
```

Tunelul era **sănătos** (astea trecuseră deja: `Connecting to 92.5.171.150, 25565`,
`Successfully synchronized gun properties from server`). Blocada era la **sync-ul de registre**:
serverul adăugase 7 moduri de performanță pe care clientul nu le avea, iar `clumps` înregistrează o
entitate ⇒ tablele de id-uri diferă ⇒ Forge închide conexiunea înainte de login.
**Reparat în build** (`pack-rules.json → mirror_on_client`): orice mod de pe server care bagă înregistru
intră automat și în mrpack-ul de client, cu **același fișier**. De aceea versiunile de client și server
se instalează mereu din **același release** — altfel riști exact eroarea de mai sus.

## Ai alt launcher?
ATG / MultiMC la fel (Import .mrpack). **CurseForge/Prism-only nu merge**: nu importă `.mrpack`.
NV Launcher: **Import .zip**, **NU** „Import Modrinth modpack". **Vanilla**: nu merge deloc — serverul cere Forge + moduri.
