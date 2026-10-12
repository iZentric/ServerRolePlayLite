# Inventar real al pack-ului CUANTIC 1.7.7 — numai citire

Arhivă: [release public `lite`](https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite), SHA-256 `fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15`.
Inventar exact: **36 moduri / 14 pluginuri**. Citit din ZIP, nu dedus din `pack-rules.json`.
**Prezența unui mod NU dovedește un câștig de FPS/RAM**, iar eliminarea lui fără test poate strica loginul/vehiculele.
Nicio modificare la live, JAR, lume sau pack. Nu am citit/pus în raport chei de acces sau setări sensibile.

## Ce optimizări/funcții apar deja în arhivă

| Componentă urmărită | Fișier găsit (sau lipsa lui) |
| --- | --- |
| `ferritecore` | `ferritecore-2.1.1-forge.jar` |
| `modernfix` | `modernfix-forge-5.18.0+mc1.16.5.jar` |
| `roadrunner` | `RoadRunner-mc1.16.5-1.5.2.jar` |
| `lazydfu` | `lazydfu-0.1.3.jar` |
| `spark` | `spark-1.9.1-forge.jar` |
| `voicechat` | `voicechat-forge-1.16.5-2.3.23.jar` |
| `vehicle` | `vehicle-mod-0.45.2-1.16.5 (1).jar` |
| `smoothchunk` | `smoothchunk1.16.5-2.0.jar` |
| `ksyxis` | `Ksyxis-1.4.6.jar` |

## Configuri existente și câteva setări publice

Configuri detectate: `server.properties`, `spigot.yml`, `bukkit.yml`, `catserver.yml`, `config/modernfix-mixins.properties`, `config/ferritecore-mixin.toml`.

| Setare (server.properties) | Valoare în arhivă |
| --- | --- |
| `use-native-transport` | `true` |
| `view-distance` | `4` |
| `online-mode` | `false` |
| `network-compression-threshold` | `512` |
| `max-players` | `25` |

**Atenție:** arhiva nu garantează că gazda live rulează aceeași configurație chiar acum; verificarea gazdei necesită runnerul self-hosted. Nu adăugăm FerriteCore/ModernFix/RoadRunner încă o dată fără a verifica fișierele de mai sus. RoadRunner/ModernFix au mecanisme care pot intra în conflict cu alte mixin-uri; logurile și testele de compatibilitate contează mai mult decât lista de moduri.

<details><summary>Toate cele 36 de moduri din arhivă</summary>

- `AI-Improvements-1.16.5-0.5.0.jar`
- `Clumps-6.0.0.28.jar`
- `FastFurnace-1.16.5-4.5.0.jar`
- `FastSuite-1.16.4-1.1.1.jar`
- `FastWorkbench-1.16.5-4.6.2.jar`
- `Ksyxis-1.4.6.jar`
- `Modernxl 1.16.5.jar`
- `Pizzaland_v68.jar`
- `Placebo-1.16.5-4.7.1.jar`
- `RoadRunner-mc1.16.5-1.5.2.jar`
- `SpawnerFix-1.16.2-1.0.0.3.jar`
- `additional-guns-0.7.1-1.16.5.jar`
- `bwncr-1.16.5-3.10.16.jar`
- `cfm-7.0.0pre22-1.16.3.jar`
- `cgm-1.2.6-1.16.5.jar`
- `connectivity-2.4-1.16.5.jar`
- `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar`
- `ferritecore-2.1.1-forge.jar`
- `getittogetherdrops-1.16.5-v1.2.jar`
- `incontrol-1.16-5.2.12.jar`
- `lazydfu-0.1.3.jar`
- `letmedespawn-forge-1.16-1.0.2a.jar`
- `mapperbase-1.16.5-2.4.0.0.jar`
- `memoryleakfix-forge-pre1.17-1.1.5.jar`
- `modernfix-forge-5.18.0+mc1.16.5.jar`
- `modernlife-1.16.5-1.15.jar`
- `obfuscate-0.6.3-1.16.5.jar`
- `pamhc2foodcore-1.16.3-1.0.2.jar`
- `player-animation-lib-forge-0.4.0+1.16.5.jar`
- `roadstuff-1.16.5-4.3.0.jar`
- `selene-1.16.5-1.9.0.jar`
- `smoothchunk1.16.5-2.0.jar`
- `spark-1.9.1-forge.jar`
- `supplementaries-1.16.5-0.18.4b.jar`
- `vehicle-mod-0.45.2-1.16.5 (1).jar`
- `voicechat-forge-1.16.5-2.3.23.jar`
</details>

<details><summary>Toate cele 14 pluginuri din arhivă</summary>

- `Chunky-1.2.217.jar`
- `Cuantic-Brand-1.7.7.jar`
- `EssentialsX-2.19.7.jar`
- `EssentialsXAntiBuild-2.19.7.jar`
- `EssentialsXChat-2.19.7.jar`
- `EssentialsXProtect-2.19.7.jar`
- `EssentialsXSpawn-2.19.7.jar`
- `LuckPerms-Bukkit-5.5.71.jar`
- `ProtocolLib.jar`
- `SkinsRestorer.jar`
- `Vault.jar`
- `claimchunk-0.0.22.jar`
- `worldedit-bukkit-7.2.5-dist.jar`
- `worldguard-bukkit-7.0.5-dist.jar`
</details>
