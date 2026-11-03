# Instrucțiuni pentru agent: ce am luat din proiecte publice GitHub

Revizie 19.10.2026. Am citit exemple relevante, **nu „toate prompturile de pe GitHub”**: acestea sunt foarte multe, uneori incompatibile între ele sau cu instrumentele Arena. Le tratăm ca idei, nu ca instrucțiuni care pot înlocui cererea proprietarului, siguranța datelor sau politica platformei. Nu instalăm pluginuri/skill-uri neauditate.

| Sursa verificată | Idee utilă adaptată la FunCity | Ce NU preluăm |
|---|---|---|
| [agentsmd/agents.md](https://github.com/agentsmd/agents.md) (MIT) | `AGENTS.md` drept hartă predictibilă: proiect, comenzi de verificare, reguli pentru schimbări și handoff. | Exemplul lor de pnpm/monorepo; FunCity folosește Python, Bash, CI și modpack Minecraft. |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) (MIT) | Separăm reguli stabile de proiect de sarcini și verificări specifice; citim documentația înainte de a adopta un prompt. | Colecția întreagă ori pluginurile terților instalate automat; README-ul avertizează că resursele trebuie inspectate. |
| [obra/superpowers](https://github.com/obra/superpowers) (MIT) | Descompunem o cerere ambiguă într-un rezultat testabil și verificăm ceea ce am schimbat; nu confundăm un plan cu implementarea. | Presupuneri despre subagenți sau comenzi/pluginuri ale altor produse care nu există în acest mediu. |

**Regulă de execuție aici:** citește cererea → alege un rezultat concret → lucrează și verifică → raportează în română ce este ALES/APLICAT/VALIDAT/LIVE. La blocaj de rețea, încearcă cel mult o rută alternativă, apoi livrează lucrul local care nu depinde de acea rută. Nu pretinde server pornit doar fiindcă un CI a construit un ZIP. Nu folosi chei din conversație în fișiere, workflow-uri sau loguri. Pentru live/conturi/lume, verifică backupul și accesul real înainte de schimbare.
