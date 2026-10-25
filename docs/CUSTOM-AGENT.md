# Agentul FunCity: verdictul de cercetare și configurarea

Actualizat la **25 octombrie 2026**. Accesul confirmat acum este Arena Quickstart Opțiunea A; nu avem Arena API access generic/Opțiunea B. Scopul este un agent de coding cu skills locale și un traseu Arena permis, fără a pretinde fallback gratuit nelimitat.

## Verdict actualizat: avem doar Arena Quickstart A

**Pentru accesul pe care l-ai confirmat, recomandarea principală este Claude Code + Arena Quickstart (Opțiunea A), cu Superpowers fixat și skill-urile locale ale repo-ului.** Quickstart-ul oficial configurează Claude Code pentru Arena; nu înseamnă că ai primit o cheie API generală, un plan gratuit nelimitat sau acces la alți clienți.

Documentația Arena spune explicit că free-router keys funcționează numai în aplicația Claude Code; Cowork, print mode și Agent SDK pot primi 403 `organization_client_restricted`. Așadar **nu copia `ANTHROPIC_AUTH_TOKEN` din configurarea Quickstart în Roo Code, Cline, OpenCode, Claw Code sau un proxy**. Nu îl trecem prin CCR, OmniRoute ori alt router. Dacă ulterior workspace-ul primește API access separat, reevaluăm integrarea conform permisiunilor acelui API.

Arena Coding Router este providerul/modelul `coding-router-preview` din clientul autorizat. Nu am dovadă că utilizatorul poate controla pool-ul de modele, că fiecare prompt primește „cel mai bun model”, sau că ofertele/cotele sunt nelimitate. Modelul efectiv disponibil, accesul și limitele depind de cont și workspace. Arena Agent Mode este un produs separat de acest API local.

`OpenCode + opencode-free-router` rămâne **o alternativă separată**, fără Arena: poate automatiza alegerea între modele Zen disponibile, cu oferte și cote schimbătoare. Nu avem o rută verificată și permisă care să unească Arena Quickstart A cu ceilalți provideri într-un singur fallback automat. Nu folosim integrarea neoficială `lmarena` cu cookies.

Superpowers și skill-urile pot îmbunătăți procedura și contextul agentului, nu modelul de bază și nu garantează calitatea. Am pregătit configurarea locală, dar nu am instalat clientul, rulat Quickstart-ul în mediul tău sau autentificat contul.

## Ce am cercetat și de ce a ieșit acest verdict

Am dat prioritate documentației și codului primar; repo/fork counts și social media sunt doar semnale de adopție și experiență. Am comparat routere multi-provider, adaptoare OpenCode, pluginuri/hooks și privacy/session capture. Eșantionarea GitHub/fork-urilor și a discuțiilor sociale este amplă și țintită, dar nu reprezintă literalmente fiecare fork, issue sau post existent.

### Alternativa free-first separată: `opencode-free-router`

- Sursă: [repo-ul și release-ul v0.1.7](https://github.com/dweee/opencode-free-router). Am inspectat sursa, installerul și wrapperul; testele repo-ului au trecut **76/76**, typecheck-ul a trecut, iar `npm audit --audit-level=high` a raportat 0 vulnerabilități în instalarea de test. Aceste verificări nu sunt audit formal de securitate și nu dovedesc compatibilitate end-to-end cu orice OpenCode V2.
- Pluginul schimbă modelul la hook-urile `prompt`/`retry`. În codul inspectat, hook-ul citește metadate de sesiune/model, nu textul promptului; rankerul descarcă date de leaderboard/catalog (inclusiv rezultate LMArena), nu trimite promptul la aceste surse. Menționarea LMArena descrie semnale de clasament, **nu** conectare la Arena API și nu acces la Arena Agent Mode.
- Starea locală ține ID-uri de sesiune, modele și cooldown-uri; mesajele de log pot include fragmente din erorile providerilor. Wrapperul citește `providers.env` și exportă valorile în procesul OpenCode; procesele copil/tool-urile pot moșteni variabilele. De aceea configurația recomandată lasă acel fișier fără chei și nu activează Artificial Analysis.
- Tagul pin-uiește API-ul de plugin OpenCode 2.0.32; OpenCode V2.1 nu a fost validat efectiv cu acest plugin. Pentru setup-ul utilizatorului trebuie verificat `./scripts/agent doctor`, apoi o sesiune de test fără cod sensibil.
- Routerul nu oferă modele sau credite; consumă catalogul și accesul contului OpenCode/providerilor conectați. Limitele gratuite sunt server-side și se pot schimba. OpenCode a atribuit erori recente de rate-limit limitelor Zen, nu unei instalări corupte ([issue #55136](https://github.com/anomalyco/opencode/issues/55136)).

### De ce whitelist-ul include doar trei modele

[Documentația OpenCode Zen](https://opencode.ai/docs/zen/) listează în prezent **Space Bunny Free**, **LongCat 2.5 Preview Free** și **Step 5 Preview Free** ca gratuite pentru o perioadă limitată, iar pentru acești provideri declară zero retention și că datele nu sunt folosite la training. De aceea `.opencode/free-router-config.json` permite doar aceste ID-uri și exclude OpenRouter, Google, Groq, NVIDIA, Mistral, OpenCode Go și ceilalți provideri din pool-ul automat. Declarațiile de privacy sunt cele publicate de OpenCode/provideri, nu un audit independent al infrastructurii lor. Ofertele pot expira ori se pot schimba.

Nu includem Big Pickle sau alte modele Zen doar fiindcă afișează preț zero: pagina Zen avertizează că unele modele gratuite pot folosi datele pentru îmbunătățire. Nu echivalăm „$0” cu „private”, „fără limită” sau „ZDR”.

### Alternative comparate, dar nerecomandate ca default acum

- **OmniRoute** — funcționalități de rutare bogate și compatibilitate cu mai mulți clienți, dar scanarea rezoluției din manifestul npm 3.8.52 a raportat 1 critical și 11 high, iar auditul executorilor outbound/SSRF și al logurilor nu este închis. Advisory-ul ACP are discrepanțe între metadatele și fixul observat în tarball; asta nu certifică restul. Modul `auto/coding` poate rută și spre surse facturabile dacă sunt configurate. Rămâne blocat ca default; detaliile verificării anterioare sunt păstrate în istoricul repo.
- **Claude Code Router (CCR)** — adopție GitHub mare și integrare/fallback multi-provider, dar tagul v3.1.3 inspectat stochează API keys cu marker `plain` (permisiunile restrictive pe fișiere nu înseamnă criptare), iar request pipeline are payload în calea de logging; default-ul și retenția exactă nu au fost confirmate. Există și raport recent de fallback cross-provider care eșuează cu 401 ([issue #1831](https://github.com/musistudio/claude-code-router/issues/1831)). Nu l-am instalat și nu îl recomand implicit pentru chei sensibile.
- **9Router** — adopție GitHub foarte mare și OpenCode-compatible, dar advisories istorice descriu expuneri de chei/conversații, RCE, bypass-uri de auth și SSRF: [GHSA-vjc7-jrh9-9j86](https://github.com/decolua/9router/security/advisories/GHSA-vjc7-jrh9-9j86), [GHSA-qvfm-67h2-2qfx](https://github.com/decolua/9router/security/advisories/GHSA-qvfm-67h2-2qfx). Acestea afectează versiuni istorice; nu afirm că release-ul curent rămâne vulnerabil. Nu am corelat toate fixurile cu artefactul cel mai nou, deci nu îl facem default înaintea unui audit curent.
- **Weave Router** — interesant ca gateway/abstracție, dar nu free-first garantat: oferta comercială are abonamente/fee, iar self-hosting-ul cere chei provider. Benchmarkurile proprii și comentariile [Show HN](https://news.ycombinator.com/item?id=48688700) nu sunt validare independentă.
- **OpenRouter `openrouter/free`** — opțiune simplă, dar selecția dintre modelele gratuite este dinamică/aleatorie după capabilități, cu cote proprii și schimbări de catalog; nu rezolvă includerea oficială Arena în fallback și nu oferă, de unul singur, clasamentul/switching-ul task-aware dorit.
- **Forkul `soficis/opencode-free-model-router`** — declară mod ZDR-only, însă are adopție publică foarte mică și declarațiile upstream/ZDR nu au fost verificate independent. Nu oferă un motiv suficient să îl preferăm față de proiectul cu teste și sursă auditată aici.

### Semnale sociale

Am eșantionat Reddit, Hacker News, X și issues publice, inclusiv rapoarte de 429/limitări la modelele gratuite și experiențe mixte cu gateway-uri. Exemplele [OpenRouter/free pe Reddit](https://www.reddit.com/r/opencodeCLI/comments/1ryngev/used_opencode_free_openrouter_models_to_do/), [rate limits pe Reddit](https://www.reddit.com/r/opencodeCLI/comments/1rewp99/i_got_tired_of_rate_limits_so_i_wired_80_free/) și discuțiile HN despre Weave sunt anecdote/declarații, nu dovezi de SLA, ToS ori securitate. În eșantionul X, majoritatea postărilor despre 9Router erau promoționale; un raport despre 403 la OpenCode Free observă că free-tier-ul trebuie folosit din clientul OpenCode, dar este doar experiență individuală ([post X, 16 octombrie](https://x.com/MatinSenPai/status/2111200797916639547)). Restricția de client este susținută separat de documentația OpenCode V2, care spune că free-tier chat models cer OpenCode. Nu am găsit o bază credibilă pentru promisiunea „gratis nelimitat”.

## Configurația din repo

- `scripts/agent` pornește implicit Claude Code cu setările din Quickstart A. Launcherul nu citește, nu afișează și nu validează credențialele Arena.
- `.claude/settings.json` fixează Superpowers la un commit verificat; `.claude/skills/` conectează skill-urile locale. Prima pornire poate cere instalarea/încrederea pluginului. Skill-urile și pluginul îmbunătățesc workflow-ul, nu transformă Arena într-un pool multi-provider.
- `.opencode/free-router-config.json` păstrează un profil opțional OpenCode-only, whitelist-uit la modele Zen selectate. `./scripts/agent auto` este separat și nu folosește cheia Arena.
- Am eliminat configul de provider Arena pentru OpenCode: ar fi sugerat în mod greșit că tokenul Quickstart A este o cheie API generală. Nu am copiat cheia în repo și nu am modificat configurația din home-ul tău.

### Instalare manuală a routerului (nu a fost executată)

Rulează din rădăcina repo-ului, pe sistemul tău, doar după ce ai revizuit upstream-ul. Necesită OpenCode V2 și Node 22.18+ (sau Bun, dacă Node nu este primul în `PATH`). Nu copia nicio cheie în repo.

```sh
git clone --depth 1 --branch v0.1.7 \
  https://github.com/dweee/opencode-free-router.git \
  /tmp/opencode-free-router
/tmp/opencode-free-router/scripts/install.sh --no-rank
```

Installerul upstream copiază codul în `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/free-router`, creează wrapperul `opencode-free` și fișiere de configurare locale. Inspectează diff-ul și folderul creat. **Pe instalare nouă**, copiază whitelist-ul repo-ului în configul routerului; dacă ai deja un `config.json`, fă backup și îmbină manual în loc să îl suprascrii:

```sh
cfg="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/free-router"
cp .opencode/free-router-config.json "$cfg/config.json"
chmod 600 "$cfg/config.json"
```

Lasă `providers.env` și `ranker.env` fără secrete. Autentifică-te separat în OpenCode numai dacă modelul/providerul cere cont; nu am testat eligibilitatea sau limita contului tău.

## Rulare

```sh
./scripts/agent doctor
./scripts/agent             # implicit: Claude Code cu setările Arena Quickstart A
./scripts/agent hybrid      # alege între Arena, Antigravity CLI și ruta OpenCode gratuită
./scripts/agent arena       # profilul Arena, explicit
./scripts/agent antigravity # Google Antigravity CLI, cu propriul login/provider
./scripts/agent auto        # profil separat OpenCode + free-router; fără Arena
```

Rulează mai întâi Quickstart-ul oficial Arena pe calculatorul tău, apoi verifică în Claude Code că `/model` arată Arena Coding Router. Dacă primești 403 sau modelul nu apare, nu copia tokenul într-un alt client și nu încerca să-l treci prin proxy; verifică accesul și eligibilitatea cu administratorul/workspace-ul Arena.

`auto` este o rută alternativă, nu un fallback automat din Arena. Pluginul free-router pin-uiește API-ul OpenCode 2.0.32, iar compatibilitatea cu OpenCode V2.1 nu a fost confirmată. Limitele Zen se schimbă, iar rate limits pot opri o sarcină până la resetare.

## Limite de cost, privacy și routing

- Cele trei modele din whitelist sunt listate acum ca gratuite; disponibilitatea, limitele, perioada promoțională și calitatea se pot schimba. Nu este cost zero garantat în viitor și nici acces nelimitat.
- Free-router-ul alege dintre candidații whitelist-uiți și poate schimba modelul la erori; nu alege Arena și nu poate garanta că un model clasat bine pe leaderboard va folosi corect tool-urile proiectului.
- Ranking-ul LMArena din plugin este numai sursă de scor. Nu este `api.arena.ai`, Arena Coding Router, Arena Agent Mode sau acces la Max.
- Pentru modelele Zen selectate, pagina OpenCode declară ZDR/no training în prezent; providerii externi pot avea reguli diferite. Verifică din nou pagina Privacy/Zen înainte de cod sensibil.
- Pluginul păstrează local metadate de sesiune/cooldown și loguri cu posibile fragmente de erori. Nu am găsit transmiterea textului promptului din hook către ranker; promptul este însă transmis providerului ales pentru generare, conform funcției serviciului.
- Nu adăuga API keys în `providers.env`, `ranker.env`, fișiere versionate sau prompturi. Env-ul poate fi moștenit de unelte copil. Costul de provider rămâne responsabilitatea contului respectiv.

## Extensii, skills, subagenți și moduri

Claude Code are extensiile pe care le cauți:

- **Skills**: directoare cu `SKILL.md`; pot fi invocate cu `/nume-skill` sau folosite automat când sunt relevante. Skill-urile locale ale repo-ului sunt în `.agents/skills/`, cu adaptoare în `.claude/skills/`.
- **Plugins**: pachete instalabile din marketplace, care pot grupa skills, subagenți, hooks și servere MCP. Superpowers v7.0.1 este deja declarat în `.claude/settings.json`, fixat la o versiune; la pornire, Claude Code poate cere aprobarea/instalarea lui. În sesiune poți folosi `/plugin` pentru marketplace-ul oficial și pluginurile aprobate.
- **Subagenți**: fișiere `.claude/agents/*.md` cu roluri specializate, set propriu de instrucțiuni, unelte, skills și permisiuni. Sunt o cale potrivită pentru, de exemplu, „review Paper”, „debug Java” sau „audit securitate”.
- **Moduri de lucru**: Claude Code are moduri de permisiuni precum Plan, Default/Manual și Accept Edits; Auto poate apărea în versiunile/mediile care îl oferă. Acestea controlează ce poate face agentul, nu îi schimbă modelul și nu adaugă automat providerii. Nu activăm `bypassPermissions` implicit.
- **Mods**: funcționalitate nouă împachetată ca plugin, cu handler-e JavaScript/TypeScript care rulează în procesul Claude Code și pot modifica interfața sau interveni în evenimente/tool calls. Un mod rulează cu permisiunile utilizatorului și poate citi/scrie fișiere, porni procese sau accesa rețeaua; nu instalez unul fără să alegem și să audităm sursa.

Skill-urile pot fi folosite și separat; nu trebuie transformate toate în pluginuri. Un plugin este util când vrei să instalezi/actualizezi un pachet unitar. Nu instalăm automat MCP-uri, observatoare de sesiune sau extensii de marketplace neverificate. Pentru pluginuri Paper/Minecraft, verificăm sursa, licența, permisiunile și artefactul înainte de instalare.

Confirmarea umană rămâne necesară pentru chei noi, permisiuni MCP de scriere, instalarea pluginurilor/JAR-urilor, modificări la server live/backup, commit/push, PR merge, release și deploy.

## Surse primare și verificări

- Arena: [OpenCode setup](https://platform.arena.ai/docs/opencode), [Claude Code](https://platform.arena.ai/docs/claude-code), [Max/API access](https://arena.ai/blog/max-router-tops-agent-arena).
- Claude Code: [plugins and marketplace](https://code.claude.com/docs/en/plugins), [skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents), [permission modes](https://code.claude.com/docs/en/interactive-mode), [mods](https://code.claude.com/docs/en/plugins/mods/overview), [plugin security](https://code.claude.com/docs/en/plugins/security).
- Google Antigravity: [CLI install](https://antigravity.google/docs/getting-started), [skills](https://antigravity.google/docs/skills/), [plugins](https://antigravity.google/docs/plugins/), [plans/quotas](https://antigravity.google/docs/plans/), [pricing](https://antigravity.google/pricing/).
- OpenCode: [Zen/pricing/privacy](https://opencode.ai/docs/zen/), [providers și custom provider](https://opencode.ai/v2/docs/providers), [CLI/model selection](https://opencode.ai/v2/docs/models), [skills discovery](https://opencode.ai/v2/docs/skills/).
- Free router: [dweee/opencode-free-router](https://github.com/dweee/opencode-free-router), [source/tag v0.1.7](https://github.com/dweee/opencode-free-router/tree/v0.1.7).
- Superpowers/OpenCode: [pin v7.0.1 install notes](https://raw.githubusercontent.com/obra/superpowers/v7.0.1/.opencode/INSTALL.md), [issue #2583](https://github.com/obra/superpowers/issues/2583).
- 9Router advisories: [GHSA-vjc7-jrh9-9j86](https://github.com/decolua/9router/security/advisories/GHSA-vjc7-jrh9-9j86), [GHSA-qvfm-67h2-2qfx](https://github.com/decolua/9router/security/advisories/GHSA-qvfm-67h2-2qfx).
- CCR: [release v3.1.3](https://github.com/musistudio/claude-code-router/tree/v3.1.3), [fallback issue #1831](https://github.com/musistudio/claude-code-router/issues/1831).
- Experiențe comunitare: [OpenCode free limits](https://github.com/anomalyco/opencode/issues/55136), [Reddit 429/free models](https://www.reddit.com/r/opencodeCLI/comments/1ryngev/used_opencode_free_openrouter_models_to_do/), [Reddit multi-router](https://www.reddit.com/r/opencodeCLI/comments/1rewp99/i_got_tired_of_rate_limits_so_i_wired_80_free/), [Weave Show HN](https://news.ycombinator.com/item?id=48688700).
