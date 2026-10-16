# Migrare pe „bossu” (Xeon X5860) — ce mutăm, în ce ordine, și ce nu se mută până nu trec porțile

Cifrele de mai jos sunt dintr-o singură fotografie a panoului (13 oct. ora ~18:33 EEST), nu din probe. Nu sunt
date de benchmark; le-am transcris ca să știu la ce ne uităm.

## Ce am citit de pe gazda nouă

| | |
|---|---|
| Masină | LXC/container pe nod Proxmox „bossu”, panou „vladutz dedicated”, uptime 41 min |
| CPU | Intel Xeon **X5860** @ 2.80 GHz, 8 fire afișate, 25 °C, 2 % medie, un firing de 100 % la 09:48 |
| RAM (interior) | 4,86 GiB folosiți din 58,9 GiB · swap 1,06 GiB |
| RAM (panou) | 3,64 / 13,7 GiB |
| Disc | 1,39 GiB din 1,1 T · boot 973 M · **54 GiB liber în container** |
| Rețea | 30,42 MiB intrare / 54,55 MiB ieșire |
| Procese java | `java -Xms128M -XX:M…` (PID 5833) — **nu** serverul nostru (al nostru e `-Xmx6G` + `@unix_args.txt`) |
| Semnal de alarmă | 3 rânduri `[Mines] Miner Incepator a fost resetata` (09:26:03, 09:26:43, 09:27:04) + un contor roșu „86…” |

**Concluzia mea, ca strateg:** mașina asta nu e un upgrade de viteză, e un upgrade de **resurse**. Tick-ul de
Minecraft stă pe un singur fir, iar X5860 e Nehalem-EX din 2010 (fără AVX2, IPC mic). Gazda actuală e
Oracle `VM.Standard.E2.1.Micro` (1 OCPU EPYC Naples, frânat la 50 % baseline) — are un fir modern, dar
îi taie timpul. Ce câștigăm sigur: **54 GiB disc** (live-ul stă pe 5,0 GB, acum la 67 % = 3,4 GB, unde un
world + log-uri + backup-uri se îneacă) și **RAM** (10 GB liberi vs 5,1 GB). Ce nu știm: dacă pierde la tick.

De-asta nu mut „pe ochelari”. Porțile sunt în `scripts/cuantic_migrate.py`.

## Porțile (toate 6 verzi = mutăm; oricare roșie = rămânem)

1. **identitate** — pack-ul umbrei are același sha256 cu cel de pe live;
2. **CPU** — micro-benchmark (aceeași expresie pe ambele gazde) ≥ 95 % din gazda actuală;
3. **pornire** — umbra ajunge la `Done` cu 36 moduri + 14 pluginuri, sub 1,25× din boot-ul live;
4. **RAM** — RSS sub 105 % din live;
5. **vecini** — steal de la hipervizor < 3 %; pe container unde contorul e ascuns, poarta **nu** trece (0 fals e mai periculos decât fără măsurătoare);
6. **pack intact** — 36/36 moduri și 14/14 pluginuri încărcate în umbra.

## Ordinea efectivă (nimic de pe live nu se atinge până la pasul 6)

1. **Află ce e „Miner Incepator”.** Un proces care se resetează la fiecare ~30 s pe mașina pe care vrem să mutăm
   serverul e exact genul de vecin care îți omoară tick-ul. Trebuie oprit/înțeles înainte de orice.
2. **Java 17 + utilitare**, pe gazda nouă: `apt-get install -y openjdk-17-jre-headless unzip curl python3`.
3. **Runner GitHub, etichetat:** `./config.sh --url https://github.com/iZentric/ServerRolePlayLite --labels self-hosted,cuantic-new --unattended_configuration disabled`.
   Eticheta `cuantic-new` e obligatorie — `migrate-shadow.yml` **nu** are fallback, deci măsurătoarea nu poate nimeri
   din greșeală pe gazda live. (Token-ul de runner îl generezi tu din panou; eu n-am acces la el și nici nu trebuie.)
4. **Măsurătoarea-umbră:** eu dau push la `deploy/migrate.txt`, workflow-ul aleargă pe bossu, ridică serverul
   **pe portul 25599, în /tmp, fără frpc, fără world real**, și publică `docs/CUANTIC-MIGRATE-RESULT.md`.
5. **Referința live** vine singură: `scripts/chk.sh` a primit un pas care aleargă `cuantic_migrate.py baseline`
   (doar citește `/proc` + `live.log`) și îi scrie output-ul în `analysis/chk.md`. Fără al doilea server pe live.
6. **`compare` = verdict.** Doar cu „MIGREAZĂ” scris în raport deschidem pasul 7.
7. **Ce se mută, de fapt:** tot ce e în `~/cuantic-live` pe gazda veche — `world/`, `world_nether/`, `world_the_end/`,
   `mods/` (36), `plugins/` (14), `config/`, `ops.json`, `server.properties`, `unix_args.txt`, **JAR-ul
   `CatServer-1.16.5-1d8d6313-server.jar` exact așa cum e** (sha `96f82479…`), `live.log`. Plus `frpc.toml`
   (tunelul care face public 92.5.171.150:25565) și `cuantic-wake.py` (reperul de „cost 0”: portul 25565 răspunde
   mereu, serverul se trezește la primul contact și se oprește după 15 min fără jucători).
8. **Comutarea:** se schimba **tunelul**, nu IP-ul: `frpc` de pe mașina nouă rezervă aceeasi proximitate
   `92.5.171.150:25565`, iar pe gazda veche se oprește `frpc` (nu și serverul — rămâne pornit ca rezervă pană
   confirmi ca joci 10 minute fara spike). Adresa din joc rămâne neschimbata.
9. **Rollback:** un singur drum — repornești `frpc` pe gazda veche. Datele de pe nou rămân neatinse, nu pierzi nimic.

## Ce **nu** se mută și ce **nu** se schimbă

- **Nu** urc JAR-ul pe `CatServer 1c92118f` în același timp cu mutarea. Două schimbări odată = nu mai știi ce ți-a stricat tick-ul.
- Release-ul `lite` și pack-ul `fe1e2610…8a15` rămân exact ele.
- `online-mode=false` rămâne (e ce face clientul tău modat să poată intra).
- **Nu** ating `scripts/net.py` și nici `deploy/net.txt`: ele eliberează IP-uri și opresc instanțe CUANTIC — adică chiar serverul ăsta.

## Comenzi, pe rand

Pe gazda nouă (pas 4 pregătitor):
```bash
python3 scripts/cuantic_migrate.py measure --out /tmp/cuantic-migrate/new
python3 scripts/cuantic_migrate.py measure --out /tmp/cuantic-migrate/new --use-live-pack   # daca ai deja pack-ul pe masina
```

Pe gazda veche, prin CHK (rulează deja; eu doar adaug pasul în `chk.sh`):
```bash
python3 scripts/cuantic_migrate.py baseline --out /tmp/cuantic-baseline
```

Verdictul:
```bash
python3 scripts/cuantic_migrate.py compare --live /tmp/cuantic-baseline/live.json \
  --new /tmp/cuantic-migrate/new/measure.json --out /tmp/cuantic-migrate/verdict.json
```

## Ce am nevoie de la tine, ca să nu stăm degeaba

1. Ce e „Miner Incepator” pe bossu și îl pot opri?
2. Are bossu port 25565 (sau 25599 pentru umbră) expus/redirectat, și are acces la `api.github.com`?
3. Îmi dai ție runner-ul de pe bossu cu eticheta `cuantic-new` (eu nu pot instala runner-ul de aici; e singurul pas care are nevoie de mâna ta).
