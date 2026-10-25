# Tutorial: Claude Code + Arena Quickstart A

Ghid pentru configurația recomandată în acest repo: **Claude Code conectat la Arena prin Quickstart-ul oficial (Opțiunea A)**, cu skills și pluginurile proiectului. În modul CLI local, agentul citește/scrie fișierele și rulează comenzile pe calculatorul tău, iar cererile de model ajung la Arena. Tutorialul nu configurează o cheie API portabilă și nu unește Arena Agent de pe site cu Claude Code.

> Quickstart-ul se rulează pe calculatorul tău. În sandboxul repo-ului, clientul `claude` nu era instalat, iar autentificarea ta Arena nu a fost verificată.

## 1. Deschide un terminal potrivit

- **macOS / Linux:** Terminal.
- **Windows:** folosește **WSL 2** și rulează pașii în terminalul distribuției Linux, nu amesteca instalarea WSL cu un Claude Code instalat separat în Windows. `scripts/agent` este un launcher Bash.

## 2. Instalează Claude Code

Urmează instrucțiunile oficiale curente: [Claude Code — Setup](https://code.claude.com/docs/en/setup).

Pentru macOS, Linux sau WSL, instalarea nativă recomandată este:

```sh
curl -fsSL https://claude.ai/install.sh | bash
```

Închide și redeschide terminalul, apoi verifică:

```sh
claude --version
```

Dacă nu apare versiunea, oprește-te și repară instalarea înainte să rulezi Quickstart-ul Arena.

## 3. Configurează Arena numai cu Quickstart A

Deschide pagina oficială [Connect Claude Code to Arena](https://platform.arena.ai/docs/claude-code) și urmează **Option A: Quickstart**. Pentru instalarea standard, scriptul oficial este:

```sh
curl -fsSL https://platform.arena.ai/setup.sh | bash
```

Urmează prompturile și folosește contul/workspace-ul Arena care ți-a fost acordat. Quickstart-ul detectează Claude Code și salvează setările de conectare și meniul de modele.

- Nu alege configurarea manuală Opțiunea B dacă singurul tău acces este Quickstart A.
- Nu copia tokenul în repo, într-un mesaj, OpenCode, un proxy sau alt client.
- Quickstart-ul poate modifica **setările personale** Claude Code din home-ul tău (`~/.claude/`). Acestea sunt diferite de `.claude/settings.json` din repo, unde sunt declarate extensiile proiectului.

## 4. Verifică legătura cu Arena

Pornește Claude Code:

```sh
claude
```

În sesiune:

1. Rulează `/model`.
2. Verifică dacă apare **Arena Coding Router** sau modelul Arena oferit de workspace-ul tău.
3. Trimite o cerere scurtă, fără cod sau date sensibile, de exemplu: `Spune salut și confirmă că poți răspunde.`

Dacă primești `403`, modelul nu apare sau autentificarea eșuează, verifică accesul workspace-ului cu administratorul Arena. Nu încerca să muți tokenul în alt client și nu-l trece printr-un proxy.

## 5. Deschide repo-ul și pornește agentul

Intră în folderul local al proiectului în care vrei să lucreze agentul. Pentru un repo privat, poți folosi [GitHub CLI](https://cli.github.com/) și autentificarea prin browser (`gh auth login`); nu trimite tokenuri în chat.

> Atenție: launcherul `./scripts/agent hybrid` și acest ghid sunt schimbări din branch-ul activ al sesiunii și nu au fost împinse pe GitHub. Un `gh repo clone` al branch-ului implicit poate să nu le conțină. Până când folosești copia actualizată a branch-ului, poți porni clientul direct cu `claude` în rădăcina repo-ului, după Quickstart A.

Apoi rulează:

```sh
./scripts/agent doctor
./scripts/agent                  # Arena Quickstart A, implicit
./scripts/agent hybrid           # meniu: Arena, Antigravity sau OpenCode gratuit
```

`./scripts/agent` pornește Claude Code cu profilul Arena implicit. `hybrid` te lasă să alegi pentru sesiunea curentă:

1. **Arena Quickstart A + Claude Code** — ruta Arena, în clientul permis.
2. **Google Antigravity CLI (`agy`)** — contul și modelele Google, separat de Arena.
3. **OpenCode + free-router** — ruta cu modele Zen listate gratuit, instalată separat conform `docs/CUSTOM-AGENT.md`.

Acestea sunt clienți diferiți care pot lucra în același repo local. Skills-urile din `.agents/skills/` sunt formatul comun folosit de mai mulți clienți; setările și pluginurile specifice rămân separate. Nu există fallback automat și nu se amestecă credențialele.

### Instalare opțională Antigravity CLI

Dacă vrei a doua rută, instalează clientul oficial în același mediu/terminal în care vei deschide repo-ul:

```sh
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy --version
```

Pe Windows PowerShell:

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
agy --version
```

Pornește `agy` o dată pentru autentificarea Google și verifică `/usage` pentru limitele contului. Antigravity are plan individual gratuit, dar cotele sunt limitate și diferă după model/plan; nu promitem rulare nelimitată. Vezi [instrucțiunile oficiale Antigravity](https://antigravity.google/docs/getting-started).

Pentru prima încercare, cere ceva mic și sigur, de exemplu:

> Analizează structura repo-ului și spune-mi ce teste ai rula. Nu modifica fișiere încă.

După ce confirmi că funcționează, cere o schimbare mică și spune-i agentului să ruleze testele relevante. Revizuiește diff-ul înainte să păstrezi schimbările.

### Antigravity ca al doilea reviewer în aceeași sesiune Arena

Meniul `./scripts/agent hybrid` alege un singur client pentru sesiunea respectivă. Separat, există și un bridge mic pentru situația în care vrei să rămâi în Claude Code + Arena, dar să ceri o **a doua părere** de la Antigravity:

1. Instalează și autentifică `agy` cu contul Google, conform pașilor de mai sus.
2. Deschide Claude Code prin Arena, în rădăcina repo-ului.
3. Cere explicit skill-ul `/antigravity-second-opinion`.
4. Skill-ul îți arată ce modificări urmărește să trimită și cere aprobarea ta înainte de orice transmitere.

Bridge-ul trimite doar un diff mic, la cererea ta, către Antigravity/Google. Nu dă repo-ul întreg agentului, rulează `agy` dintr-un director temporar gol, în mod plan/sandbox, iar procesul `agy` nu primește variabilele `ANTHROPIC_*`, `CLAUDE_CODE_*` sau `ARENA_*`. **Cheia Quickstart A rămâne în Claude Code; nu este trecută printr-un gateway și nu este folosită de Antigravity.** Un filtru caută câteva tipare comune de secrete și refuză diff-uri mai mari de 16 KB, dar nu este un scanner perfect: verifică și tu ce aprobi. Diff-ul poate apărea în istoricul normal Antigravity/Google. Înainte de prima folosire, verifică și extensiile/MCP-urile globale Antigravity (`/mcp`, `/plugin`, `/permissions`): wrapperul nu le dezactivează pe toate.

Aceasta este delegare pentru review, nu un router care unește modelele și nici editare automată de către Antigravity. Providerii viitori se pot adăuga separat, fiecare cu propriul CLI/API și autentificare; nu adăuga cheia Arena într-un router general. Integrarea nu a fost testată pe calculatorul tău; aici `agy` nu este instalat, deci verificarea s-a limitat la codul bridge și testele locale.

## 6. Activează skills și plugins

Repo-ul include skills locale în `.agents/skills/` și adaptoare în `.claude/skills/`. Superpowers este declarat ca plugin fixat în `.claude/settings.json`; prima pornire poate cere aprobarea/instalarea lui.

- În Claude Code, rulează `/plugin` pentru marketplace și gestionarea pluginurilor.
- Acceptă numai extensii pe care le-ai ales și a căror sursă ai verificat.
- Începe cu Superpowers și skills locale; nu instala o listă mare de plugins dintr-un foc.
- Poți folosi modul **Plan** pentru analiză înainte de modificări. Lasă aprobările normale activate; nu folosi `bypassPermissions` implicit.

## 7. Despre mods

Un mod se instalează ca plugin și poate rula JavaScript/TypeScript cu permisiunile utilizatorului: poate interacționa cu fișiere, procese și rețeaua. De aceea, **nu instala mods aleatorii**. Înainte de activare, verifică repo-ul autorului, codul, comenzile/hooks, accesul de rețea și politica de actualizare. Probele oficiale Anthropic din [claude-code-playground](https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods) sunt exemple, nu garanții de suport sau audit.

## 8. Ce se combină și ce nu

- **Arena Agent de pe site** rămâne produs separat; nu devine un plugin Claude Code.
- Meniul `./scripts/agent hybrid` pornește un singur client ales de tine. În schimb, skill-ul `/antigravity-second-opinion` poate chema `agy` pentru un review separat din sesiunea Claude Code + Arena, după aprobarea ta.
- **OpenCode + free-router** este încă o rută separată, fără cheia Arena Quickstart. În repo o pornește `./scripts/agent auto`, dar necesită instalarea și verificarea separată a OpenCode/free-router.
- Agenții delegați nu devin un singur provider: fiecare folosește aplicația/CLI-ul și autentificarea proprie. Un gateway care interceptează traficul Claude/Arena nu face parte din această soluție.
- Nu este confirmată o cotă fixă de 100 de rulări pe zi pentru Quickstart. Arena Agent de pe site documentează un buget de credite care se reînnoiește după 24 de ore; nu presupune că limita lui este identică cu limita cheii Quickstart. Vezi [sistemul de credite Arena](https://help.arena.ai/articles/5476762589-credit-sytem) și [documentația Quickstart](https://platform.arena.ai/docs/claude-code).

## Proiecte GitHub cercetate și alegerea noastră

| Proiect | Ce este | Decizie |
|---|---|---|
| [Claude Code oficial](https://code.claude.com/docs/en/setup) + [Arena Quickstart](https://platform.arena.ai/docs/claude-code) | Clientul suportat și providerul permis pentru accesul tău actual. | **Ruta principală.** Păstrăm binarul oficial; nu îl modificăm și nu punem cheia Arena într-un proxy. |
| [Superpowers](https://github.com/obra/superpowers) | Plugin open-source cu skills/workflow-uri; repo-ul fixează o revizie specifică în `.claude/settings.json`. | **Păstrăm**, după promptul de trust/instalare al Claude Code. |
| [Anthropic Claude Code plugins](https://github.com/anthropics/claude-code/tree/main/plugins) și [sample mods](https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods) | Pluginuri/mods și exemple oficiale. Mods sunt cod, nu simple instrucțiuni. | Marketplace/pluginuri selectate; mods doar după inspecție. |
| [simplybychris/antigravity-plugin-cc](https://github.com/simplybychris/antigravity-plugin-cc) | Plugin comunitar care cheamă Antigravity CLI din Claude Code. | **Nu l-am instalat.** Wrapperul modifică temporar setări globale Antigravity pentru model, cu lock/backup/restore; auditul sursei nu a fost complet. |
| [et-Celestosapien/antigravity-delegate](https://github.com/et-Celestosapien/antigravity-delegate) | Delegă sarcini către `agy`, cu worktree și review. | **Nu l-am instalat.** Proiect foarte nou; installerul poate schimba permisiuni globale și autorul avertizează că workerul rulează cu privilegii locale. |
| [greenpolo/cc-multi-cli-plugin](https://github.com/greenpolo/cc-multi-cli-plugin) | Gateway local pentru mai mulți provideri, inclusiv Anthropic passthrough. | **Nu îl folosim cu Arena Quickstart A.** Gateway-ul s-ar afla pe traseul credențialelor Arena; compatibilitatea și permisiunea nu sunt verificate. |
| [opencode-free-router](https://github.com/dweee/opencode-free-router) | Rutare OpenCode spre modele Zen listate gratuit; profilul e separat de Arena și whitelist-uit în repo. | **Opțional, rută separată.** Testele repo-ului au trecut 76/76 în auditul anterior, dar asta nu e audit formal; compatibilitatea OpenCode V2.1 nu a fost confirmată și proiectul e foarte nou. |
| [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) | Proiect separat cu proxy local și mulți provideri; autorii pretind peste 60 provideri. Nu este un Claude Code oficial „deblocat”. | **Nu îl instalăm acum.** Are o suprafață mare de cod/configurare și nu i-am făcut audit complet; nu introduce Arena Quickstart în el. Poate fi reevaluat separat, fără secrete, pe o copie temporară. |
| [nilupulk/claude-code-free](https://github.com/nilupulk/claude-code-free) | Fork mic care se descrie în README ca versiune „leaked”; GitHub nu raportează o licență recunoscută. | **Evităm.** Nu avem motiv să rulăm un binar/fork neoficial când extensiile oficiale acoperă nevoia. |
| [9Router](https://github.com/decolua/9router) | Router terț care promite mulți provideri și fallback automat. | **Nu e default.** Există advisories istorice de securitate; nu am validat complet release-ul curent. Faptul că un README promite „free/unlimited” nu e dovadă de cotă sau siguranță. |

Așadar, **hibridul are două niveluri**, nu o versiune piratată de Claude Code și nu un proxy cu Arena:

- `./scripts/agent` sau `./scripts/agent arena` → Claude Code oficial + Arena Quickstart A ca agent principal.
- În acea sesiune, `/antigravity-second-opinion` → review opțional de la Antigravity, prin CLI-ul Google și autentificarea lui proprie, cu aprobarea ta.
- `./scripts/agent auto` → OpenCode + free-router, ca rută separată, fără Arena.
- `./scripts/agent hybrid` → meniu pentru a porni unul dintre clienții disponibili ca aplicație principală.

Astfel poți ține Arena „la cârmă” și cere altui agent o părere, fără să-i dai cheia Arena. Pentru editare delegată sau alți provideri, adăugăm câte un adaptor nativ separat și îl audităm înainte; nu presupunem că un router comun este permis. Dacă Arena refuză accesul, nu facem failover prin copierea tokenului.

## Probleme frecvente

- **`claude: command not found`:** Claude Code nu este instalat sau terminalul nu a reîncărcat `PATH`-ul. Repornește terminalul și verifică din nou instalarea.
- **Arena nu apare în `/model`:** rulează din nou Quickstart-ul oficial și folosește opțiunea de actualizare a modelelor dacă este oferită; apoi repornește Claude Code.
- **`403 organization_client_restricted`:** poate indica un client sau mod nepermis pentru cheia ta. Rămâi în aplicația Claude Code și verifică accesul/eligibilitatea cu administratorul workspace-ului.
- **Pluginul nu s-a încărcat:** acceptă promptul de trust numai dacă recunoști repo-ul; verifică `/plugin` și repornește sesiunea dacă e nevoie.

## Surse oficiale

- [Arena Quickstart pentru Claude Code](https://platform.arena.ai/docs/claude-code)
- [Instalare și configurare Claude Code](https://code.claude.com/docs/en/setup)
- [Plugins Claude Code](https://code.claude.com/docs/en/plugins)
- [Mods Claude Code](https://code.claude.com/docs/en/plugins/mods/overview)
