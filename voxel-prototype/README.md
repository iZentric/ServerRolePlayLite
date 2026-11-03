# FunCity Voxel Lab — etapa 1/9

Prototip vizual **separat**: fereastră WebGL2, buclă `requestAnimationFrame`, cameră first-person, mișcare normalizată la diagonală și scenă statică de orientare. `WASD` mișcare, mouse/săgeți privire, `Space`/`E` sus, `Q` jos, `Shift` sprint, `Esc` pauză. Dacă preview-ul nu permite pointer lock, ține apăsat mouse-ul pe scenă și deplasează-l ori folosește săgețile. Scena nu este încă teren generat, chunkuri, fizică sau multiplayer.

```sh
cd voxel-prototype
npm ci
npm test
npm run build
npm run dev
```

Deschide adresa locală afișată de Vite. `npm test` verifică direcția mișcării, independența de framerate, diagonala și limitele privirii; `npm run build` verifică TypeScript și construiește pagina. FPS-ul afișat este **al prototipului din browser**, nu TPS sau număr de jucători ai serverului.

[Presupus] Pentru a păstra modurile Forge 1.16.5 și pluginurile Bukkit, serverul RP trebuie să rămână pe o bază JVM compatibilă, nu să fie mutat în acest renderer WebGL2. Acest folder nu încarcă moduri, pluginuri sau lumea privată, nu comunică cu serverul live și nu demonstrează 30/60/100 de jucători pe 2 vCPU/12 GB. Etapa 2 poate adăuga stocare blocuri/chunkuri **numai după validarea etapei 1**; compatibilitatea RP și capacitatea rămân la porțile [H2–H6](../functity/catserver/GOALS.md) ale serverului pe copia TEST.
