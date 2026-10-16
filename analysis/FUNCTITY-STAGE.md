== SONDA EXTERNA 25565 ==
STATUS FAILED: [Errno 111] Connection refused
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-16 19:14:41 UTC — gazda → artefact → relay

```
mod automat din marker: status port=25566 jar=b1.0827
== FUNCTITY STATUS — 2026-10-16 19:14:24 UTC ==
  staging java: 1459 /home/mndvasi9/funcity-live/jdk11/bin/java -Xms1G -Xmx3G -XX:MaxGCPauseMillis=200 -jar FunCity-1.16.5-b1.0827.jar nogui
  port 25566: da | 25565: nu | 25566: da
  log: Done = 1 | erori = 0 | keep-up = 0
  post-Done (12 linii):
    D [19:11:50 INFO]: Loaded 0 license plates
    D [19:11:50 WARN]: Garagenordner nicht gefunden!
    D [19:11:50 WARN]: Running in offline mode - Voice chat encryption is not secure!
    D [19:11:50 INFO]: Successfully initialized RadioManager
    D [19:11:50 WARN]: Dedicated server took 63.646 seconds to load
    D [19:11:50 INFO]: Server started at port 24454
    D [19:11:50 INFO]: Essentials found a compatible payment resolution method: Vault Compatibility Layer (v1.7.3-b131)!
    D [19:11:50 INFO]: Fetching version information...
    D [19:11:50 INFO]: [Vault] Checking for Updates ... 
    D [19:11:51 INFO]: [33;1m[[32;22mSkinsRestorer[33;1m] [0;39m[32;1m----------------------------------------------[0;39m
    D [19:11:51 INFO]: [33;1m[[32;22mSkinsRestorer[33;1m] [0;39m[32;1m    +===================+[0;39m
    D [19:11:51 INFO]: [33;1m[[32;22mSkinsRestorer[33;1m] [0;39m[32;1m    |   SkinsRestorer   |[0;39m
  pidfile staging: 1459
  linii ERROR:
  bind port:
    B [19:11:17 INFO]: Starting Minecraft server on *:25,566
  primele 12 linii log:
    L 
    L 
    L  __    __   ______   __  __   __   ______   ______  
    L /\ "-./  \ /\  __ \ /\ \_\ \ /\ \ /\  ___\ /\__  _\ 
    L \ \ \-./\ \\ \ \/\ \\ \  __ \\ \ \\ \___  \\/_/\ \/ 
    L  \ \_\ \ \_\\ \_____\\ \_\ \_\\ \_\\/\_____\  \ \_\ 
    L   \/_/  \/_/ \/_____/ \/_/\/_/ \/_/ \/_____/   \/_/ 
    L                                                     
    L 
    L Welcome to Mohist 1.16.5 ! - Mohist Developement Group - 1.16.5-754b578e, Java 55.0
    L Checking libraries, please wait...
    L DownloadSource: MOHIST
  plugini Enabling: 14 | ultimi 6 linii:
    [19:11:51 INFO]: [33;1m[[32;22mSkinsRestorer[33;1m] [0;39m[34;1mWant to support SkinsRestorer or receive priority support? Become a supporter: [33;1mhttps://skinsrestorer.net/pricing[0;39m
    [19:11:51 INFO]: [Vault] No new version available
    [19:11:51 WARN]: There is a new EssentialsX version available for download: 2.22.0.
    [19:11:51 WARN]: Download it here: https://essentialsx.net/downloads.html?branch=stable
    [19:11:52 INFO]: [ProtocolLib] The updater found an update: 5.4.0 (Running 4.8.0). Download at https://www.spigotmc.org/resources/protocollib.1997/
    [19:11:56 INFO]: [ClaimChunk] An update for ClaimChunk is available! Your version: 0.0.21 | Latest version: 0.0.25-FIX1
  frpc: porturi expuse (fara tokenuri):
    T name = "mc"	localPort = 25565	remotePort = 25565
  java staging vie acum: 1
  libertate disc: 670 MiB
  interior jar voicechat (fisiere config citate):
    J assets/voicechat/lang/ca_es.json
    J assets/voicechat/lang/cs_cz.json
    J assets/voicechat/lang/de_de.json
    J assets/voicechat/lang/en_us.json
    J assets/voicechat/lang/es_ar.json
    J assets/voicechat/lang/es_es.json
    J assets/voicechat/lang/es_mx.json
    J assets/voicechat/lang/fr_ca.json
    J assets/voicechat/lang/fr_fr.json
    J assets/voicechat/lang/it_it.json
  moduri voice/chat in pack:
    M voicechat-forge-1.16.5-2.3.23.jar
  configuri voicechat staging:
    C /home/mndvasi9/funcity-live/config/voicechat
    C /home/mndvasi9/funcity-live/config/voicechat/voicechat-server.properties
    C /home/mndvasi9/funcity-live/config/voicechat/voicechat.properties
    C /home/mndvasi9/funcity-live/config/voicechat.properties
    C /home/mndvasi9/funcity-live/config/voicechat-server.properties
    C /home/mndvasi9/funcity-live/config/voicechat-client.properties
    C /home/mndvasi9/funcity-live/config/voicechat-server.toml
    continut /home/mndvasi9/funcity-live/config/voicechat/voicechat-server.properties:
      port=24455
    continut /home/mndvasi9/funcity-live/config/voicechat-server.properties:
      port=24455
  porturi voicechat pe gazda:
    P udp   UNCONN 0      0                  *:24454            *:*    users:(("java",pid=1459,fd=173))
  linii voicechat din log:
    V [19:11:14 INFO]: Reloading ResourceManager: Default, Modernxl 1.16.5.jar, voicechat-forge-1.16.5-2.3.23.jar, getittogetherdrops-1.16.5-v1.2.jar, cgm-1.2.6-1.16.5.jar, player-animation-lib-forge-0.4.0+
    V [19:11:50 WARN]: Running in offline mode - Voice chat encryption is not secure!
(sfarsit rc=0)
RC=0
```
