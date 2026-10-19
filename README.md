<div align="center">
  <img src="site/assets/funcity-city.webp" alt="FunCity — oraș în lumini cyan și magenta" width="190" height="190">
  <h1>FunCity RP Lite</h1>
  <p><strong>Un oraș nou. Povestea e a voastră.</strong></p>
  <p>Minecraft 1.16.5 · pluginuri pentru RP · moduri proprii numai după confirmare</p>
  <p><a href="site/index.html">Pagina proiectului</a> · <a href="agent/SELECTIE-MOTOR-MODURI-CLIENT.md">Motor &amp; moduri</a> · <a href="agent/PROGRES.md">Progres real</a></p>
</div>

---

## Ce construim

FunCity este un proiect de comunitate roleplay cu un **oraș nou, construit de proprietar și de jucători**. **Direcția actuală este plugin-first:** joburile, economia, meniurile și restul RP se proiectează prin pluginuri; conținut modat numai dacă aparține proprietarului și este confirmat exact, optimizări numai dacă probele arată necesitatea. Mobilierul, armele, vehiculele, emotele și vocea sunt **cerințe de evaluat**, nu funcții plugin deja implementate; un resource pack nu garantează mecanicile unui mod. Orașul nu are claims sau protecții preventive; **CoreProtect** este cerut ca jurnal și rollback punctual administrativ, nu ca blocaj la construit. Conturile se autentifică **prin plugin**. [Regula actuală și limitele](agent/PLUGIN-FIRST.md).

[HYPECITY](agent/AUDIT-SERVERE-REFERINTA.md) este reperul practic al proprietarului, care relatează că a avut peste 60 de jucători, posibil spre 100. Este o experiență istorică, nu o măsurătoare a capacității noului FunCity.

## Unde suntem, fără promisiuni inventate

| Stare | Ce înseamnă |
|---|---|
| **ALES ca direcție nouă** | Motorul hibrid FunCity **b1.0827** rămâne referință, RP **plugin-first**; nicio includere automată de moduri terțe. [Whitelisting-ul actual](agent/PLUGIN-FIRST.md) este încă gol până la confirmarea modurilor proprii și a excepției pentru voce. |
| **VALIDAT în laborator** | [Stage izolat 0 moduri / 6 pluginuri](agent/SERVER-PLUGIN-FIRST.md): motorul b1.0827 a pornit cu [toate pluginurile active pe PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39317136133), apoi s-a oprit curat pe loopback; a fost creat un [profil Prism nou, cu zero moduri](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39316848451), dar fără lansare/login. Guava21 rămâne override temporar; **nu** este build de producție, RP testat ori dovadă de performanță maximă. |
| **DE TESTAT** | Pluginurile și funcțiile RP efective, modurile proprii identificate, soluția de voce, apoi boot pe copie, importul clientului dacă e necesar, autentificare, CoreProtect, backup/restaurare și sarcina cu jucători. |
| **LIVE** | Nicio instalare Lite nouă sau capacitate a serverului actual nu este confirmată de acest repo. |

> **Pentru jucători:** încă nu publicăm un pachet Lite nou ori o adresă de intrare verificată. Pagina arată stadiul proiectului, nu un server live.

## Găsești rapid ce te interesează

- **Aspectul proiectului:** [site-ul static](site/index.html) și [sursa paginii](site/template.html). Fără reclame, tracking sau statistici live inventate.
- **Motor, moduri, client:** [decizia și stage-ul plugin-first](agent/SERVER-PLUGIN-FIRST.md) · [regula de includere](agent/PLUGIN-FIRST.md) · [vechea listă 24 + 29, numai comparație](agent/LISTA-MODURI-RP-LITE.md) · [poarta beta](agent/BETA-LITE.md).
- **RP și moderare:** [rolurile pluginurilor](agent/RP-LITE-PLUGINS.md) · [planul comunității](agent/PLAN-COMUNITATE.md).
- **Vrei să continui cu un alt agent?** [Cerința exactă FunCity, gata de copiat](agent/CERINTA-EXACTA-FUNCITY.md) · [instrucțiunile din repo](AGENTS.md).
- **Dovezi și limite:** [comparația HYPECITY/FunCity citită de pe PC](agent/COMPARATIE-HYPECITY-PC.md) · [captura istorică parțială de config](agent/AUDIT-SERVERE-REFERINTA.md) · [progresul](agent/PROGRES.md).

Motorul derivă din Mohist/Tenet, sub GPL-3.0; orice distribuție viitoare de JAR derivat cere verificarea licenței, atribuire și sursa corespunzătoare. Nu publicăm binare sau promisiuni de FPS/jucători numai pe baza selecției din repo.
