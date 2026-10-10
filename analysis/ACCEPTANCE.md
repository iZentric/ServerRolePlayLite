# ACCEPTANCE CUANTIC — 2026-10-10 11:58:33 UTC (live.log: 434 linii)
[CADE] T1 proces java + port: java=nil port25565=0
[TRECE] T2 boot: Done (19.605s) | Dedicated server took 69.838 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 5
      [11:52:02] [Server thread/INFO]: [SkinsRestorer] Renaming SkinErrorCooldown to commands.skinErrorCooldown
      [11:52:11] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
      [11:52:28] [Craft Scheduler Thread - 5/WARN]: [AuthMe] Could not download GeoLiteAPI database [FileNotFoundException]: plugins/AuthMe/GeoLite2-Country.mmdb (No such file or directory)
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 30
[VERIFICA] T5 plugini: pe disk: 15 jar; 0 linii de incarcare | esuati: 1
[CADE] T6 punte console: niciun raspuns la 'list' in 24 s
[VERIFICA] T7 salvare lume: 'Saved the game'=NU | level.dat mtime 1791633105->1791633105 | regiuni 12->12
[INFO] T8 resurse: disc liber 1750MB (ocupat 66%), MemAvailable 7918MB, RSS java ?MB, swap 5111MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.

SCOR: TRECE=2 VERIFICA=3 CADE=2 din 9 teste
