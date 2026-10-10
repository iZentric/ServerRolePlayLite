# ENGINE LAB — build izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38093403726

Ultimele linii din compilare (nu sunt cifre de TPS):
```
 > Running 'rename'
Stopping at requested step: /home/runner/.gradle/caches/forge_gradle/mcp_repo/de/oceanlabs/mcp/mcp_config/1.16.5-20210115.111550/joined/rename/output.jar
Setting up MCP environment
Initializing steps
Executing steps
 > Running 'downloadManifest'
 > Running 'downloadJson'
 > Running 'downloadServer'
 > Running 'strip'
 > Running 'rename'
Stopping at requested step: /home/runner/.gradle/caches/forge_gradle/mcp_repo/de/oceanlabs/mcp/mcp_config/1.16.5-20210115.111550/server/rename/output.jar

> Task :forge:compileFmllauncherJava
/tmp/catserver-source/src/fmllauncher/java/foxlaunch/legacy/LegacyLauncher.java:42: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/tmp/catserver-source/src/fmllauncher/java/foxlaunch/legacy/LegacyLauncher.java:42: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
2 warnings

> Task :forge:processFmllauncherResources
> Task :forge:fmllauncherClasses
> Task :mcp:downloadConfig UP-TO-DATE
> Task :clean:extractSrg
> Task :clean:createMcp2Srg
> Task :clean:compileJava
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.

> Task :clean:processResources NO-SOURCE
> Task :clean:classes
> Task :clean:jar
> Task :clean:reobfJar
> Task :clean:genServerBinPatches
> Task :forge:createFakeSASPatches
> Task :forge:createMcp2Srg

> Task :forge:compileJava
/tmp/catserver-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/tmp/catserver-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^
/tmp/catserver-source/src/main/java/moe/loliserver/utils/EnumHelper.java:171: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
        private static sun.misc.Unsafe unsafe = null;
                               ^
/tmp/catserver-source/src/main/java/moe/loliserver/utils/EnumHelper.java:188: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                  ^
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
4 warnings

> Task :forge:processResources
> Task :forge:classes
> Task :forge:jar
> Task :forge:reobfJar
> Task :forge:genServerBinPatches
> Task :forge:filterJarNew
> Task :forge:universalJar
> Task :forge:buildCatServer

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD SUCCESSFUL in 2m 31s
21 actionable tasks: 18 executed, 3 up-to-date
```

Smoke:
```
{
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "done_seconds": "9.944",
  "enabled_plugins": 0,
  "plugin_names": [],
  "critical_lines": [
    "[23:05:49] [Server thread/WARN]: Could not load any license plate"
  ],
  "timed_out": false,
  "exit_code_after_stop": 0,
  "handshake_with_real_client": "NOT TESTED",
  "performance_under_players": "NOT TESTED",
  "passed_smoke": false
}
```
