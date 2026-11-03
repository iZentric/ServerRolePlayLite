# HANDOFF — predare către un alt agent (2026-10-17, dimineața)

Citește întâi astea trei: `INVENTAR.md` (ce binare există, unde), `MIGREAZA.md` (cum se mută pe alt GitHub), prezentul fișier (cum se operează).

## Ce e proiectul
Server Minecraft **FunCity** (fostul Cuantic) pe un **ARM Oracle free tier** — 2 core, ~3.8 GB RAM, HDD, IP `92.5.171.150:25565`. Motor **Mohist 1.16.5** (forge+sponge, GPL-3.0, păstrează atribuirea), jar custom FunCity b1.0827, 36 moduri + 14 pluginuri RP. Site public cu benchmark-uri măsurate: Pages pe `main` (workflow `site.yml`, autofișare prin `site-auto.yml` la `17 */6`).

## Cum se ajunge pe boxă — singurul canal
**NU există SSH de la agent.** Agentul comandă boxa PRIN GitHub:
1. Scrii markerul în `deploy/funcity-stage.txt`: format exact `MODE port jar` (ex. `migpack x x # comentariu`), un singur marker o dată.
2. Push pe branchul arena (`arena/9bbcb24f-serverroleplaylite` sau ce branch e activ) → workflow-ul `functity-stage.yml` (job `s`, `runs-on: [ self-hosted ]`) rulează PE BOXĂ `scripts/functity-stage.sh auto`, care citește markerul și alege modul.
3. Raportul apare în `analysis/FUNCTITY-STAGE.md` (cap = cel mai nou; include și SONDA EXTERNĂ 25565 = dovada că serverul e viu, făcută de un job hosted din rețea).
4. Atepți cu `gh run watch <id>` pe id — **fără sleep-poll loops, fără markere în lanț** (coada încurcată a produs deja 3 rapoarte deșarte).

Moduri în kit (`scripts/functity-stage.sh`): `host-info backup assemble test expose install prune snap restart up down status persist stats tune bootcheck tuneprod packtest packpromote site-sync inbox migpack unclog`. Fiecare e documentat cu comentariu în script.

## STAREA DE ACUM (verificată, nu presupusă)
- Serverul: **SUS**, ultima confirmare externă 01:25 UTC (Mohist 1.16.5, 0/25). Boot mediu 4.2 s, keep-up 0, RSS 3.1 GB.
- **Runnerul de pe boxă a murit** (joburi `queued` la nesfârșit) — cauza cea mai probabilă: disc plin (erau 179 MiB libere). Primul tău lucru, prin user:
  `df -h ~ && pgrep -af "svc.sh|run.sh" | head` în consola GCP SSH, apoi repornire runner (svc.sh run / systemd) și curățare `_work`. După aceea rulezi marker `unclog x x`, apoi `migpack x x`.
- Producția are **configul vechi, stabil**. Tunarea de config a fost testată pe staging (4.251s vs 4.2s) și-a fost retrasă in mod explicit — nu o reaplica pe producie fără cerere noua.
- PC-ul userului e al doilea runner (`KERNELOS-PC`, Windows 10): **doar banc de test**. Are powershell 5.1, fără pwsh/bash. Scripturile au garda `RUNNER_OS` — dacă un marker cade pe PC, refuză și atâta tot; rulezi marker din nou.

## Reguli puse de user (nenegociabile)
1. **Niciodată un jar netestat pe producție.** Traseul: `packtest` (staging, port 25566, boot + 60s keep-up) → `packpromote` (montare cu rollback automat dacă serverul nu urcă în 300 s).
2. **Proveniență verificabilă sau refuz**: jar doar dacă poate fi potrivit cu sursa (repo + commit/tag + sha). Starlight-forge 1.16.5 = refuzat definitiv; krypton = refuzat după ce build-ul din source a eșuat pe maven mort (doar arhivă CF = nu).
3. **Cifre doar măsurate** (site, rapoarte, benchmark). Ce n-ai măsurat, scrii explicit „—".
4. Răspunsuri scurte, un pas concret pe tură, fără așteptări lungi degeaba. Nu promite „gata" fără proba ei (id run / raport / asset).
5. Nu ștergi și nu atingi `cuantic-live/` (producția) din alte moduri ale kitului; `worlds` se arhivează DOAR prin `snap`/`migpack`.
6. Ambiguitate de acces/credentiale → te oprești și întrebi userul. Nu cere parole, nu instala nimic pe PC-ul lui în afara runner-ului existent.

## Ce e deja postat pentru mutare
- Release `jars-20261017-0952`: `functity-jare-toate.tar.gz` 132 MB (12 jare FunCity + mohist-1237) + `CUANTIC-Server-CatServer-1.7.7.zip` 49 MB + `SHA256SUMS.txt`.
- Release `lite`: client .mrpack 86 MB + variantă Arclight + engine jar. Release `world-live`: worldsync.tar.gz 88 MB (snapshot de ieri).
- Branchul `functity-out` = artefactele (builds/, pack/, bench). Clonare cu `git clone -b functity-out`.

## Ce urmează (în ordinea asta)
1. Repornire runner boxă (comanda de diagnostic mai sus, userul o rulează în consolă GCP).
2. Marker `unclog` → marker `migpack` → verifică pe release `world-live` că au apărut `functity-live.tar.gz` (+ world dacă încape) și dă-i userului link-urile.
3. Opțional la cerere: `packtest` pentru orice candidat nou, altfel **nu inventezi modificări** — userul a refuzat deja bench-uri sintetice contaminat; cifrele se iau din loguri (`stats`).

## Contact cu realitatea
- Sonda 25565 din `analysis/FUNCTITY-STAGE.md` e singura dovadă de „viu" ce ai tu; tu nu poți accesa portul direct din sandbox.
- Boot real pe HDD poate depăși 240 s: SLP-wait = minim 30×10s, iar verdict final DOAR după sonda externă din raport (o buclă prea scurtă a dat deja un „CRITIC" fals).
