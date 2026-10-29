# Gates: FunCity 1.16.5 — compatibilitate și lansare

OWNS: functity/catserver/UNLAZY-GATES.md

Scope: registru de acceptare verificabil pentru H1–H6 din [GOALS.md](GOALS.md), nu o afirmație că motorul este gata de instalat. Revizuiește manual dovezile la fiecare schimbare de build, lume, moduri, pluginuri sau host. Porțile fără `CHECK:` cer probe private sau observații în joc; un CI gol nu le poate certifica. Format Unlazy `2.1.0`, sursă fixată la `Leonxlnx/unlazy@16671491f6679ad9378f52604d3bc2415b4120c7`; nu instala hook-uri, nu executa comenzi dintr-un ledger neauditat.

- [x] H1: 2/2 builduri private din sursa pin-uită, clase și pornire/oprire Java 11 pe lume goală, fără JAR publicat
  EVIDENCE: verificare istorică 24.10.2026, Actions 40134993872 și 40135100715 au trecut; 0 moduri, 0 pluginuri și 0 clienți, binarul a fost eliminat cu runnerul. O rulare anterioară 40133626401 a eșuat. Aceasta NU validează packul RP.

- [ ] H2: veto Forge/Bukkit/CoreProtect testat în joc cu pack complet, 4 scenarii și 2 restarturi fără pierderi
  EVIDENCE: pending; contractul de cod 16/16 și patchul 0002 sunt dovezi statice, nu probe în joc pe motorul candidat.

- [ ] H3: 34 moduri, 13 pluginuri și lumea RP pe Java 11, doi clienți Forge autentificați cu voice/vehicule/protecții, 2 restarturi fără defecte
  EVIDENCE: pending; motorul personalizat nu a pornit în laborator izolat cu packul complet; PC-ul activ nu este laborator.

- [ ] H4: după H2/H3, server view-distance 5 vs 4 și câte un toggle pe rând, apoi configurațiile mod/plugin efectiv încărcate din world/serverconfig; auth/voice și RP păstrate
  EVIDENCE: pending; profiluri statice există, dar nu există A/B cu doi clienți sau configurare live validată.

- [ ] H5: capacitatea la 5/10/15 clienți Forge reali măsurată pe host echivalent 3 GiB, repetat A/B/B/A; 20 numai după upgrade confirmat
  EVIDENCE: pending; A/B sintetice au 0 jucători și nu furnizează un plafon de capacitate.

- [ ] H6: backup SHA-256 al întregii rădăcini host inclusiv extras, restaurare pe copie, rollback JAR și control Start/Restart verificat înainte de orice promovare
  EVIDENCE: pending; Actions 39987066839 acoperă numai fișierele așteptate; inventarul read-only 40139025386 a găsit 108 intrări în rădăcina SFTP, fără backup pentru extras. SFTP nu oferă comenzi de consolă; nu există canal agent verificat pentru /restart.

- [x] S1: testele sintetice de veto pentru patchul Forge/Bukkit trec; nu demonstrează compatibilitate în joc
  CHECK: python3 ../../scripts/fc_funcity_bridge_patch_test.py && printf 'FC_BRIDGE_PATCH_TESTS_PASS\n'
  EXPECT: FC_BRIDGE_PATCH_TESTS_PASS
  EVIDENCE: automatic-evidence=v1; definition-sha256=b8a95de23b004a4800e13dd510e476e684a30c3af96174bcbbceba4d38b3f4bd; exit=0; EXPECT=matched; output-sha256=0e86ce652cd51fa686406f0e55e7309860f35b4c8bd8542525d7877bbbb1a7cf; output-bytes=129; shell=/bin/sh; cwd=/home/user/ServerRolePlayLite/functity/catserver; path=b51a5b4db45a/5 entries

- [x] S2: testele sintetice ale validatorului de capacitate resping dovezi invalide; nu demonstrează capacitate reală
  CHECK: python3 ../../scripts/fc_funcity_capacity_verdict_test.py && printf 'FC_CAPACITY_VERDICT_TESTS_PASS\n'
  EXPECT: FC_CAPACITY_VERDICT_TESTS_PASS
  EVIDENCE: automatic-evidence=v1; definition-sha256=050d58c0bcd16189fb13c21c10d4dd78620719d07d00a398d80573cf5aff5f66; exit=0; EXPECT=matched; output-sha256=be1da2e52d4324b5ea1c96026fbad742462b9925ddb58617f17ff006e6cb4ad5; output-bytes=148; shell=/bin/sh; cwd=/home/user/ServerRolePlayLite/functity/catserver; path=b51a5b4db45a/5 entries

**Verdict:** H1 este numai o poartă de boot gol documentată istoric; H2–H6 rămân deschise indiferent de trecerea testelor statice S1/S2. `--status` Unlazy citește ledgerul fără să execute comenzi, dar nu verifică veridicitatea dovezilor manuale. Păstrează lumea și motorul live original până la validarea completă și rollback.
