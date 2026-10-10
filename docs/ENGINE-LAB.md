# CUANTIC ENGINE LAB — candidat izolat, nu deploy

Motorul live CUANTIC 1.7.7 este CatServer `1d8d6313` (26 mai 2023), rebranduit
prin `scripts/brand_engine.py`. Această modificare a literalei de branding NU
accelerează tick-urile. Nu revendicăm câștiguri de performanță din branding.

Codul public upstream `Luohuayu/CatServer`, ramura `1.16.5`, conține după
versiunea noastră un fix cu optimizarea construcției evenimentului de mutare în
hopper (`98eabb0e1985`, 3 august 2023) și corecții pentru respawn
(`1c92118fcca6`, 21 aprilie 2024):
- https://github.com/Luohuayu/CatServer/commit/98eabb0e198532804162949df311bea20dacd5cd
- https://github.com/Luohuayu/CatServer/commit/1c92118fcca69ffac97a48c8e1f6e1bb861b41d1
- licență upstream: LGPL-3.0; https://github.com/Luohuayu/CatServer/tree/1.16.5

Workflow-ul `ENGINE LAB` compilează *pinned* commitul nou într-un runner GitHub
separat, aplică brandingul local, descarcă **același pack 1.7.7** și face
smoke-test cu modurile și pluginurile reale. Artifactul e doar un **candidat**.
Nu actualizează `lite`, nu schimbă jarul live, nu atinge lumea, nu declară
handshake-ul ori TPS-ul cu jucători drept testate. O compilare reușită nu
dovedește că serverul nou este mai rapid.

Pornește prin modificarea fișierului `deploy/engine-lab.txt` pe ramura sesiunii,
sau prin workflow_dispatch dacă ai drepturi. După test: inspectează
`smoke-result.json`, `boot.log`, verifică loginul cu clientul modat pe o copie
a lumii și compară *același workload*, `spark` MSPT p95 și RSS, față de
motorul vechi. Doar după această etapă s-ar putea discuta despre deploy.

Nota: Dacă ForgeGradle/upstream nu mai compilează reproductibil pe CI, buildul
eșuează în loc să înlocuiască tăcut motorul live.
