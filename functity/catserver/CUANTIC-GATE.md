# Cuantic — CatServer 1.16.5 compatibil, candidat TEST, nu live

[Presupus] „Cuantic” desemnează **identitatea motorului** pentru serverul RP existent, nu un joc/browser nou și nici schimbarea numelui ramurii Git. Păstrăm lumea, 34 moduri, 13 pluginuri, auth, voice, vehiculele și survivalul. Sursa este CatServer LGPL-3.0 la SHA `1d8d63138be77a606df2a5e940b960065948f983`, fără copierea altui motor și fără JAR redistribuit. Patchul [`0004`](patches/0004-cuantic-operator-identity.patch) înlocuiește **doar** `0001` la buildul Cuantic: schimbă numele din API-ul Bukkit și loggerul, dar lasă `catserver.yml`, clasele și ABI-ul Forge/Bukkit în loc. Păstrează separat patchurile de corectitudine [`0002`](patches/0002-preserve-forge-block-place-cancellation.patch) și [`0003`](patches/0003-preserve-forge-block-break-cancellation.patch). Builderul istoric FunCity rămâne neschimbat implicit; `--cuantic` este opt-in.

## Alegere între trei direcții

| Opțiune | Avantaj | Cost/risc pentru pack | Decizie |
|---|---|---|---|
| Rescriere Rust/Paper | Libertate de performanță | Nu încarcă direct 34 JAR-uri Forge + 13 pluginuri Bukkit 1.16.5 | Nu înlocui serverul RP. |
| Transplant mare de ticking/chunkuri | Posibil câștig | Riscul de ordine a evenimentelor, vehicule și moduri; hopper/tickets au regresat ori au fost neconcludente public | Nu intră înainte de profil privat. |
| **CatServer pin-uit + identitate Cuantic + veto-uri** | Compatibilitatea API-urilor rămâne, schimbările sunt mici și reversibile | Brandingul nu aduce FPS/TPS; e obligatoriu A/B față de oficial | Candidat **numai în laborator**; nu-l numim mai rapid până trece porțile. |

## Plafonul cerut de proprietar, fail-closed

Reperele **2,515 s CPU median / ~30 s** și **1,50 / 1,52 ms tick mediu sortat** au fost **observațiile oficialului** într-un singur [job public 41573354240](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41573354240), pe runner GitHub, lume generată, **18 moduri/6 pluginuri/80 mobi/0 clienți**; nu sunt o limită fizică universală. [Screeningul Cuantic](../../.github/workflows/cuantic-catserver-synthetic-screen.yml) reconstruiește sursa, verifică bytecode-ul din JAR-ul universal, pornește/oprește Java 11 fără pack, apoi rulează **O/Q/Q/O** pe copii identice ale scenei publice. [Verificatorul](../../scripts/fc_cuantic_synthetic_ab.py) refuză candidatul dacă **oricare** condiție e falsă: median CPU Cuantic `≤2,515`; cele două valori tick mediu Cuantic sortate `≤1,50` și `≤1,52`; median CPU Cuantic `≤` oficial **în același job**; ambele tickuri Cuantic sortate `≤` ale oficialului **în același job**. 0 clienți, 18/6 și 80 mobi sunt obligatorii. Nicio toleranță sau comparație numerică între joburi nu poate ascunde o regresie; valorile complete ale brațelor se afișează **numai după 4 trialuri**. Un eșec înseamnă **necalificat**, nu „motorul e rău în producție”; dacă runnerul variază, repetarea cere o nouă rulare controlată, nu relaxarea pragului fără acord.

**Important:** acesta este screening pe **media** tickului, nu p95/p99 cu jucători. Chiar dacă trece, nu dovedește „nu urcă” pe 2 vCPU/12 GB, pachetul privat 34/13, autentificare, voce, condus sau capacitate 30/60. Acestea cer TEST izolat + A/B/B/A [H2–H6](GOALS.md), inclusiv backup/restaurare. Dacă nu trece screeningul, nu se promovează și nu se atinge live-ul. Nu există încă niciun patch de performanță Cuantic integrat, iar brandingul nu este revendicat ca optimizare.

Build **numai pe Linux privat izolat** cu JDK 17 activ, Java 11 separat și director de ieșire nou în afara repo-ului; binarele și `runtime-seed/` rămân private:

```sh
bash scripts/fc_funcity_build_private.sh /cale/privata/cuantic-build-NOU /cale/java11/bin/java --cuantic
# Rezultatul local, doar după build, verificare a claselor și boot pe lume goală:
sha256sum /cale/privata/cuantic-build-NOU/CuanticEngine-private-trial.jar
```

Acest script **nu** instalează Cuantic pe host și nu redenumește/restaurează lumea. Pentru prima probă RP reală se adaptează doar stagingul pe o copie TEST inactivă, cu SHA, seed și izolare; până atunci folosiți instrucțiunile de siguranță din [README](README.md), fără substituirea nevalidată a căilor FunCity.
