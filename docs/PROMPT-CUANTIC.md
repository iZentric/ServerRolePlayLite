# PROMPT-CUANTIC — profilul permanent al proiectului

> Versiunea scurtă, păstrată ca lege de proiect. Textul integral primit de la proprietar este spec-ul de mai jos,
> cu aceleași obligații; acest fișier e versiunea pe care o aplică agenții.

## Scop
Server hybrid **Roleplay Lite** + survival cât de cât vanilla, pe orice PC, cu modpack-ul și pluginurile lui VII
sacre (cerință de compatibilitate). Baza tehnică, planul, uneltele și pații îi alege agentul.

## Reguli de neclintit
1. Maximezi performanța reală și funcționalitatea; iau baza upstream matură și o îmbunătățesc, nu reinventez.
2. Optimizez consumul total (CPU, RAM, GC, I/O, rețea, MSPT) și sub sarcină, nu doar la pornire goală.
3. Zero cost: numai software liber, fără billing, fără licențe plătite.
4. Fără „cel mai bun/10x" fără baseline + benchmark măsurat, cu variație raportată.
5. Fiecare componentă trebuie să bată echivalentul public cu dovezi, altfel se taie (LEGEA-RUST art.5).
6. Nu șterg și nu înlocuiesc conținut din modpack fără să declar efectul.
7. Numele oricărui produs/config/raport nou este **Cuantic**.
8. Nu pretind că am verificat o pagină/agent/build pe care nu l-am rulat. Declari limitările.

## Echipa (când ai suport real; altfel declară că simulezi rolurile)
Coordonator · Cercetători · Compatibilitate · Performanță/profilare · Build · Critic adversarial,
cu task board comun (responsabil, stare, surse, fișiere, blocaje).

## Livrabile obligatorii
jar Cuantic + surse/patch-uri · pași de build și instalare · lista de compatibilități confirmate ·
inventar tehnologii și licențe · config-urile optimizate + lista schimbărilor · raport baseline vs candidat
(loguri + valori brute) · uneltele gratuite instalate cu versiuni și comenzi · puntea live (chat/loguri +
start/stop/restart) cu pași de salvare și rollback · limitări, regresiuni, teste nereușite, următorul experiment.

## stare_project_vs_profil (2026-10-09)
| Cerință | Stare | Unde |
|---|---|---|
| jar Cuantic (CatServer + Arclight 1.5.8) | livrat, build reproducible | `scripts/build_lite.py`, release `lite` |
| pași build/instalare | livrat | `docs/PRIMA-PORNIRE.md`, `deploy/INSTALEAZA-PACK.bat` |
| compatibilități confirmate | 32 moduri + 15 plugini, audit `missing 0` | `analysis/viteza/`, `docs/ANATOMIA-SERVERULUI.md` |
| config optimizat + schimbări | livrat | `docs/VITEZA-CUANTIC.md`, `docs/CONSUM-DETALIAT.md` |
| baseline vs candidat | parțial: idle + load sintetic, `Done 14-83s`, vârf RAM 4185 MB | `analysis/viteza*` |
| benchmark **cu jucători reali** | **NELIVRAT** — necesita clienți reali, mineflayer nu trece de handshake-ul FML | — |
| punte live (chat/loguri + start/stop/restart) | **NOU**: `~/cuantic-live/cmd.in` → consola serverului, loguri citite din home; RCON ramâne inutilizabil pe 1.16.5 (MC-12864) | `scripts/cuantic-live.sh` |
| 24/7 pe Cloud Shell | **IMPOSIBIL fizic**: containerul unui job moare la final; persistă numai home-ul | `analysis/up.md`, `analysis/chk.md` |
| expunere publică | frps pe VPS-ul proprietarului + frpc în Cloud Shell, adresă fixă `92.5.171.150:25565` | `scripts/frps-install.sh`, `scripts/cuantic-live.sh` |
| cost | 0 lei (free tier OCI/Evovv, GitHub Actions, binare open-source) | — |

## Următorul experiment cu cel mai mare potențial
Trei clienți reali cu `CUANTIC-Client-1.5.8.mrpack` intrați deodată, măsurați 10 min: MSPT p50/p95/p99, TPS,
RAM steady vs peak, pauze GC — pe CatServer vs Arclight, aceeasi lume/seed. Baseline-ul e packul nemodificat
din release-ul `lite`.
