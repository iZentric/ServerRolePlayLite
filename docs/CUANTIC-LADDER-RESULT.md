# Scara CUANTIC — candidați hibrid 1.16.5: SHA, smoke 36/14 și A/B

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38272459943

Runner GitHub izolat, Java 17, pack neschimbat (36 moduri + 14 pluginuri). Serverul live nu a fost atins.
Un candidat care nu ajunge la `Done` este INCOMPATIBIL, nu mai lent; fără 3 probe valide pe braț nu există verdict.

```json
{
  "method": "scară CUANTIC: descărcare cu SHA, smoke pe pack identic 36/14, A/B sintetic cu N probe pe braț, pe un runner GitHub izolat",
  "limits": "nu ating serverul live; nu declară compatibilitate cu clientul modat; un motor care nu pornește e INCOMPATIBIL, nu mai lent",
  "baseline_pack": {
    "mods": 36,
    "plugins": 14,
    "pack_sha256": "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
  },
  "candidates": {
    "Mohist 1.16.5-1237": {
      "url": "https://repo1.maven.org/maven2/com/mohistmc/mohist/1.16.5-1237/mohist-1.16.5-1237-server.jar",
      "licence_declared": "GPL-3.0",
      "sha256_expected": "17d08ed544aab50f0c9c0281507a44d765cfeb371289a10d47e2143146255bff",
      "sha256_actual": "17d08ed544aab50f0c9c0281507a44d765cfeb371289a10d47e2143146255bff",
      "baseline_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
      "candidate_jar_sha256": "17d08ed544aab50f0c9c0281507a44d765cfeb371289a10d47e2143146255bff",
      "smoke_passed": false,
      "boot_done_s": null,
      "plugins_enabled": 0,
      "key_lines": [
        "Exception in thread \"main\" [15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: java.lang.RuntimeException: java.lang.reflect.InvocationTargetException",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat cpw.mods.modlauncher.LaunchServiceHandlerDecorator.launch(LaunchServiceHandlerDecorator.java:39)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat cpw.mods.modlauncher.LaunchServiceHandler.launch(LaunchServiceHandler.java:54)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat cpw.mods.modlauncher.LaunchServiceHandler.launch(LaunchServiceHandler.java:72)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat cpw.mods.modlauncher.Launcher.run(Launcher.java:82)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat cpw.mods.modlauncher.Launcher.main(Launcher.java:66)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat net.minecraftforge.server.ServerMain$Runner.runLauncher(ServerMain.java:105)",
        "[15:45:19 INFO]: [java.lang.ThreadGroup:uncaughtException:1077]: \tat net.minecraftforge.server.ServerMain.main(ServerMain.java:86)"
      ],
      "root_cause": "java.lang.NoSuchMethodError: 'java.util.stream.Collector com.google.common.collect.ImmutableMap.toImmutableMap(java.util.function.Function, java.util.function.Function)'",
      "ab": {
        "verdict": "NEAVĂGAT",
        "reason": "nu a ajuns la `Done` cu pack-ul intact: fără scor de performanță"
      }
    },
    "Magma 1.16.5-36.2.39-c1c5a946": {
      "url": "https://git.magmafoundation.org/api/v4/projects/8/packages/maven/org/magmafoundation/Magma/1.16.5-36.2.39-c1c5a946/Magma-1.16.5-36.2.39-c1c5a946-server.jar",
      "licence_declared": "GPL-3.0 (de reconfirmat pe tag)",
      "sha256_expected": null,
      "error": "HTTPError: HTTP Error 522: <none>"
    },
    "LoliServer 1.16.5 (fără sursă oficială; repository-ul GitHub Loli-Server/LoliServer a intors 404 (stins); nu luam binare de pe oglinzi neoficiale)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    }
  }
}
```
