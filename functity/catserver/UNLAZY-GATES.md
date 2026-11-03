# Gates: FunCity 1.16.5 — compatibilitate și lansare

OWNS: functity/catserver/UNLAZY-GATES.md

Scope: registru de acceptare verificabil pentru H1–H6 din [GOALS.md](GOALS.md), nu o afirmație că motorul este gata de instalat. Revizuiește manual dovezile la fiecare schimbare de build, lume, moduri, pluginuri sau host. Porțile fără `CHECK:` cer probe private sau observații în joc; un CI gol nu le poate certifica. Format Unlazy `2.1.0`, sursă fixată la `Leonxlnx/unlazy@16671491f6679ad9378f52604d3bc2415b4120c7`; nu instala hook-uri, nu executa comenzi dintr-un ledger neauditat.

- [x] H1: 2/2 builduri private cu patchurile 0001–0003 din sursa pin-uită, clase și pornire/oprire Java 11 pe lume goală, fără JAR publicat
  EVIDENCE: Actions [41316259001](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41316259001) și [41317093607](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41317093607) au trecut cu aceleași patchuri; a doua rundă a rulat și contractul Java pe sursa construită; 0 moduri, 0 pluginuri, 0 clienți, binarul eliminat cu runnerul. Aceasta NU validează packul RP.

- [ ] H2: veto Forge/Bukkit/CoreProtect testat în joc cu pack complet, 4 scenarii place, 2 break și 2 restarturi fără pierderi
  EVIDENCE: pending în joc; contractul [41316259012](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41316259012) a trecut 20/20 cazuri place/multiplace/break și a respins doi mutanți, dar acestea sunt probe sintetice, nu testul packului RP.

- [ ] H3: 34 moduri, 13 pluginuri și lumea RP pe Java 11, doi clienți Forge autentificați cu voice/vehicule/protecții, 2 restarturi fără defecte
  EVIDENCE: pending; motorul personalizat nu a pornit în laborator izolat cu packul complet; PC-ul activ nu este laborator.

- [ ] H4: după H2/H3, server view-distance 5 vs 4 și câte un toggle pe rând, apoi configurațiile mod/plugin efectiv încărcate din world/serverconfig; auth/voice și RP păstrate
  EVIDENCE: pending; profiluri statice există, dar nu există A/B cu doi clienți sau configurare live validată.

- [ ] H5: capacitatea la 5/10/15 clienți Forge reali măsurată pe ținta 2 vCPU / 12 GB verificată, repetat A/B/B/A; 20 numai după treapta 15 trecută
  EVIDENCE: pending; A/B sintetice au 0 jucători și nu furnizează un plafon de capacitate.

- [ ] H6: backup SHA-256 al întregii rădăcini host inclusiv extras, restaurare pe copie, rollback JAR și control Start/Restart verificat înainte de orice promovare
  EVIDENCE: pending; Actions 39987066839 acoperă numai fișierele așteptate; inventarul read-only 40139025386 a găsit 108 intrări în rădăcina SFTP, fără backup pentru extras. SFTP nu oferă comenzi de consolă; nu există canal agent verificat pentru /restart.

- [x] S1: testele sintetice de veto pentru patchul Forge/Bukkit trec; nu demonstrează compatibilitate în joc
  CHECK: python3 ../../scripts/fc_funcity_bridge_patch_test.py && printf 'FC_BRIDGE_PATCH_TESTS_PASS\n'
  EXPECT: FC_BRIDGE_PATCH_TESTS_PASS
  EVIDENCE: automatic-evidence=v1; definition-sha256=b8a95de23b004a4800e13dd510e476e684a30c3af96174bcbbceba4d38b3f4bd; exit=0; EXPECT=matched; output-sha256=0e86ce652cd51fa686406f0e55e7309860f35b4c8bd8542525d7877bbbb1a7cf; output-bytes=129; shell=/bin/sh; cwd=/home/user/ServerRolePlayLite/functity/catserver; path=b51a5b4db45a/5 entries

- [ ] S2: testele sintetice ale validatorului de capacitate pentru 3 GiB și 2 vCPU/12 GB resping dovezi invalide; nu demonstrează capacitate reală
  CHECK: python3 ../../scripts/fc_funcity_capacity_verdict_test.py && printf 'FC_CAPACITY_VERDICT_TESTS_PASS\n'
  EXPECT: FC_CAPACITY_VERDICT_TESTS_PASS
  EVIDENCE: pending refresh Unlazy după schimbarea testului; 24 teste sintetice au trecut local, dar vechiul hash automat nu mai certifică această versiune.

**Verdict:** H1 este închis numai pentru build/boot pe lume goală cu 0003; H2–H6 rămân deschise. Testele statice S1/S2 nu înlocuiesc probele pe pack. `--status` Unlazy citește ledgerul fără să execute comenzi, dar nu verifică veridicitatea dovezilor manuale. Păstrează lumea și motorul live original până la validarea completă și rollback.
