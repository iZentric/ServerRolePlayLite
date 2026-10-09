# ⚛️ TABLOUL DE VITEZĂ — 1.5.7 vs 1.5.6-fără-noutăți
_2026-10-09 11:58:04 UTC — acelasi hardware, acelasi jar campion, diferenta = DOAR ferritecore + spigot.yml CUANTIC_

## CUANTIC-1.5.7
- 1.5.7: ferritecore PREZENT: ferritecore-2.1.1-forge.jar | jar da534986e7b3 | mods: 31
- STATUS: **Done (10.706s)** in 145s | RAM varf 4085MB | STABIL@+90s 4077MB | plugini 0 | linii ERROR 3

## REF-fara-noveluri
- REF: feritecore+spigotyml scoase: ferritecore-2.1.1-forge.jar | jar da534986e7b3 | mods: 30
- STATUS: **Done (11.257s)** in 151s | RAM varf 3362MB | STABIL@+90s 3403MB | plugini 0 | linii ERROR 3

Criterii: boot (Done), RAM stabil@+90s, zero erori noi.

## VERDICT (critic adversarial)
- Boot: 10.71s vs 11.26s = **in zgomot** (tribunalul a aratat deja ±20% intre runuri) — ferritecore NU incetineste, dar NU aduce niciun castic masurabil **pe server idle** (el taie memorie la modele de mesh = client-side).
- RAM idle: diferenta 674MB intre randuri **nu e atribuibila** — acelasi server a cantat 3403/4077/4440/4613 MB la 4 probe identice = variatie naturala de ~700MB.
- Zero erori noi, 3 linii ERROR = aceleasi ca la tribunal.
- CE ADUCE 1.5.7 CU VORBĂ (pentru jucatori activi, nu idle): player-idle-timeout 0 = **fix de bug real** (copiii nu mai erau dati afara dupa 10 min in statie), compressie 512 = mai putini pacheti/min pe calculatoare slabe, nerf-spawner-mobs false = mob farm-urile functionale inapoi.
- CONCLUZIE: 1.5.7 = egalitate de viteza + 3 fixuri functionale. Fara regressie. Ramane montat.

