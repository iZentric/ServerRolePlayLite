# inbox — ce arunci aici ajunge la mine și pe boxă

**Cum încarci:** github.com → `iZentric/ServerRolePlayLite` → branch `arena/9bbcb24f-serverroleplaylite` → folderul `inbox/` → *Add file → Upload files* (merge și drag & drop direct pe pagină). De pe PC: `git add inbox/fisier && git push`.

**Ce pun aici:** jar-uri de moduri/plugin-uri de testat, configuri, preseturi de world, scripturi — orice fișier.

**Ce fac eu cu ele:** le am în workspace (le citesc, le decompil/analizez), le duc prin staging (boot + 60s keep-up + sha) și pe producie NUMAI dacă: (1) trec testul pe staging, (2) au proveniență verificabilă (repo + commit/tag sau etag + sha). Fără (2) = rămân pe staging, nu pe serverul cu jucători.

**Cum ajung pe boxă:** rulez markerul `inbox` → fișierele se oglindeste în `~/functity/inbox/` de pe mașina cu FunCity (compară sha, nu recopiază identicele).

**Limite:** ~100 MB/fișier (maximul Git). Arhive mai mari: sparge-le sau dă-mi un link.
