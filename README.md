<div align="center">
  <img src="site/assets/funcity-city.webp" alt="Ilustrație FunCity — oraș nocturn în lumini cyan și magenta" width="148" height="148">
  <h1>FunCity RP Lite</h1>
  <p><strong>Un oraș nou. Povestea e a voastră.</strong></p>
  <p>Minecraft Forge 1.16.5 · roleplay · dezvoltare publică, fără promisiuni de performanță inventate</p>
  <p><strong>🧪 În testare · ⛔ Fără release Lite verificat · ⛔ Fără server nou deschis jucătorilor</strong></p>
  <p><a href="START-AICI.md">Start aici</a> · <a href="site/index.html">Pagina proiectului</a> · <a href="agent/INDEX-GITHUB-FUNCITY-2026.md">Tot progresul public</a> · <a href="https://github.com/iZentric/ServerRolePlayLite/pull/2">PR #2</a></p>
</div>

---

> **Stadiu la 22 octombrie 2026:** codul, testele și rapoartele recente sunt pe ramura [PR #2](https://github.com/iZentric/ServerRolePlayLite/pull/2), **nu integrate în `main` și nu publicate automat pe Pages**. PR-ul este deschis și are conflicte. [Indexul public](agent/INDEX-GITHUB-FUNCITY-2026.md) le reunește. Serverul instalat, lumea, profilul original și modpackul convenit **nu au fost modificate** de aceste probe.

## Ce rămâne neschimbat

| Componentă | Situația actuală | Ce NU înseamnă |
|---|---|---|
| **Clientul original** | Profilul Prism **Freeroam 1.0.0**, 28 de nume de JAR, neatins. [Inventarul și limitele verificării](agent/CONTROL-MODURI-ORIGINALE.md). | Numele verificate nu certifică singure SHA-ul surselor ori funcționarea în joc. Nu confundăm vechiul LowSpec sau Freeroam → LowSpec cu un test de paritate reușit. |
| **Clientul Lite** | Profil separat **FunCity RP Lite**, 22 de JAR-uri: șase excluderi aprobate numai din noul profil, inclusiv Not Enough Animations + TRansliterationLib. [Selecția exactă](agent/FUNCITY-RP-LITE-SELECTIE.json). Rubidium rămâne; Embeddium este numai în TEST. | Nu există pachet Lite validat pentru descărcare, FPS comparabil ori login client/server certificat. Nu adăugăm optimizatoare obligatorii pe client. |
| **Serverul real** | Inventarul read-only anterior indica **34 moduri/13 pluginuri**. Nimic nu a fost instalat, scos sau schimbat în lumea existentă. | [Cele 28 de moduri/6 pluginuri](agent/FUNCITY-SERVER-TARGET-28.json) din probe sunt doar o **țintă de laborator**, nu noul inventar al PC-ului. |
| **Hostul final planificat** | Proprietarul a comunicat **2 CPU / 12 GB RAM**. [Plan de test, nu capacitate promisă](agent/CAPACITATE-FUNCITY-RP.md). | Nu cunoaștem modelul CPU, dacă sunt vCPU partajate, uplinkul sau numărul maxim de jucători. |

## Alegerea pentru următoarea copie de test

**CatServer oficial 23.05.26-1** este baza hibridă cea mai defensabilă din probele de laborator. Păstrăm funcțiile RP și, provizoriu, **RoadRunner + ModernFix + FerriteCore**. Nu stivuim moduri noi de „boost” doar ca să bifăm nume. Nu schimbăm motorul instalat: vechiul FunCity b1.0827 este derivat din **Mohist/Tenet**, nu un motor nou independent; atribuirea și licențele upstream rămân obligatorii. [Decizia completă, cu limite](agent/ALEGERE-CONCRETA-MOTOR-MODURI-2026.md) · [arhitectura și proveniența](agent/ARHITECTURA-MOTOR-FUNCITY-HIBRID.md).

| Rezultat de pe copii izolate GitHub | Ce arată — și ce nu |
|---|---|
| [28 vs 22 moduri server](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39710079801) | Reducerea la 22 a pornit mai lent, fără câștig runtime repetat. Nu dovedește că fiecare optimizer existent ajută fiecare jucător. |
| [FerriteCore / ModernFix](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39711748552) | Semnale favorabile de heap post-GC / CPU pe 28/6, lume generată și 80 zombie, **fără clienți**. |
| [RoadRunner vs Performant](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39711647739) | Trialul Performant pe 28/6 a eșuat la marker fatal: nu îl promovăm ca înlocuitor. |
| [Saturn vs FerriteCore](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39713736343) | Saturn a folosit ~448 MiB heap post-GC vs ~322 MiB cu FerriteCore, în substituție pe 28/6. Nu îl adăugăm. |
| [Starlight Forge original 1.16.5](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39768710154) | Semnal CPU pentru **editări luminoase** repetate, dar RSS mai mare; nu este probă de jucători, p95/p99 sau lume RP restaurată. Nu îl adăugăm preventiv. |
| [Chunk Sending canary](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39704706580) și [Smooth Chunk Save canary](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39713299824) | Booturi pe copii, **nu** măsurători de pachete, salvări sub sarcină sau capacitate. |
| [16 mașini staționare](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39708297969) | Numărul a ajuns de la 16 la **0**: testul a fost invalidat; nu avem benchmark valid de condus. |

Pentru surse, versiuni Forge, dependențe client și motivele pentru care alte moduri **nu merită adăugate fără un blocaj real**, vezi [auditul de scalare](agent/AUDIT-PLAYER-SCALING-FORGE-1165-2026.md). Nu pretindem că am testat toate modurile de pe internet.

## Când putem spune câți jucători încap?

**Încă nu putem da un maxim cinstit.** Pentru hostul de 2 CPU / 12 GB, [protocolul](agent/CAPACITATE-FUNCITY-RP.md) propune inițial o copie cu buget de heap prudent, apoi o rampă 5 → 10 → 15 → 20 **ca trepte de probă, nu ca promisiuni**. Trebuie verificate întregul inventar 34/13, login Forge, pluginuri, mașini în mișcare, voice, upload, lumea pregenerată și MSPT p95/p99. Nici `max-players`, nici 80 zombie, nici un boot nu înlocuiesc acești jucători.

## Urmărește lucrările, fără să confunzi testul cu un release

- **[Indexul GitHub](agent/INDEX-GITHUB-FUNCITY-2026.md)** — hartă către cod, workflow-uri, rulări și decizii actuale.
- **[Progresul verificabil](agent/PROGRES.md)** — jurnalul extins, inclusiv rezultate istorice și eșecuri.
- **[Start aici](START-AICI.md)** — explicația simplă; unele probe vechi sunt marcate drept istorice.
- **[Pagina statică](site/index.html)** — prezentare și dovezi, **nu** status live; sursa este `site/template.html` și publicarea Pages rămâne manuală.
- **[PR #2](https://github.com/iZentric/ServerRolePlayLite/pull/2)** — unde sunt postate schimbările. PR-ul nu e îmbinat; rezolvarea conflictelor și orice publicare pe `main`/Pages necesită un pas separat, verificat.

**Nu publicați sau descărcați lumea, loguri brute, conturi, IP-uri ori JAR-uri de la alți autori din acest proiect.** Nu există încă o adresă nouă de server pentru jucători sau un release Lite aprobat. [Drepturi și condiții de publicare](agent/PUBLICARE.md) · [Contribuții](CONTRIBUTING.md).
