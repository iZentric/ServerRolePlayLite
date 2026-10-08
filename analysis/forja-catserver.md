# FORJA CatServer-Custom (Thu Oct  8 07:27:38 UTC 2026)
```
> Run with --scan to get full insights.

* Get more help at https://help.gradle.org

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD FAILED in 6s
2 actionable tasks: 2 up-to-date
To honour the JVM settings for this build a single-use Daemon process will be forked. See https://docs.gradle.org/7.3.3/userguide/gradle_daemon.html#sec:disabling_the_daemon.
Daemon will be stopped at the end of the build 
Configuration on demand is an incubating feature.
> Task :buildSrc:compileJava NO-SOURCE
> Task :buildSrc:compileGroovy UP-TO-DATE
> Task :buildSrc:processResources NO-SOURCE
> Task :buildSrc:classes UP-TO-DATE
> Task :buildSrc:jar UP-TO-DATE
> Task :buildSrc:assemble UP-TO-DATE
> Task :buildSrc:compileTestJava NO-SOURCE
> Task :buildSrc:compileTestGroovy NO-SOURCE
> Task :buildSrc:processTestResources NO-SOURCE
> Task :buildSrc:testClasses UP-TO-DATE
> Task :buildSrc:test NO-SOURCE
> Task :buildSrc:check UP-TO-DATE
> Task :buildSrc:build UP-TO-DATE

> Configure project :clean
WARNING: This project is configured to use the official obfuscation mappings provided by Mojang. These mapping fall under their associated license, you should be fully aware of this license. For the latest license text, refer below, or the reference copy here: https://github.com/MinecraftForge/MCPConfig/blob/master/Mojang.md, You can hide this warning by running the `hideOfficialWarningUntilChanged` task
WARNING: (c) 2020 Microsoft Corporation. These mappings are provided "as-is" and you bear the risk of using them. You may copy and use the mappings for development purposes, but you may not redistribute the mappings complete and unmodified. Microsoft makes no warranties, express or implied, with respect to the mappings provided here.  Use and modification of this document or the source code (in any form) of Minecraft: Java Edition is governed by the Minecraft End User License Agreement available at https://account.mojang.com/documents/minecraft_eula.

> Configure project :
Java: 1.8.0_504 JVM: 25.504-b01(Temurin) Arch: amd64 Git-Commit: 1c92118
Forge Version: 1.16.5-36.2.39

> Task :forge:compileFmllauncherJava
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/fmllauncher/java/foxlaunch/legacy/LegacyLauncher.java:42: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/fmllauncher/java/foxlaunch/legacy/LegacyLauncher.java:42: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
2 warnings

> Task :forge:processFmllauncherResources
> Task :forge:fmllauncherClasses
> Task :clean:compileJava
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.

> Task :forge:compileJava
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/main/java/moe/loliserver/utils/EnumHelper.java:171: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
        private static sun.misc.Unsafe unsafe = null;
                               ^
/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/catsrc/src/main/java/moe/loliserver/utils/EnumHelper.java:188: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                  ^

> Task :clean:processResources NO-SOURCE
> Task :clean:classes
> Task :clean:jar
> Task :clean:assemble
> Task :clean:check
> Task :clean:build
> Task :mcp:compileJava NO-SOURCE
> Task :mcp:processResources NO-SOURCE
> Task :mcp:classes UP-TO-DATE
> Task :mcp:jar
> Task :mcp:assemble
> Task :mcp:check
> Task :mcp:build

> Task :forge:compileJava
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
4 warnings

> Task :forge:processResources
> Task :forge:classes
> Task :forge:jar
> Task :forge:assemble
> Task :forge:check
> Task :forge:build

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD SUCCESSFUL in 1m 7s
10 actionable tasks: 8 executed, 2 up-to-date
BUILD OK
== jaruri nascute:
./projects/mcp/build/mcp/merge/output.jar
./projects/mcp/build/mcp/forgeAccessTransformer/output.jar
./projects/mcp/build/mcp/mcinject/output.jar
./projects/mcp/build/mcp/downloadClient/client.jar
./projects/mcp/build/mcp/forgeSideStripper/output.jar
./projects/mcp/build/mcp/downloadServer/server.jar
./projects/mcp/build/mcp/rename/output.jar
./projects/mcp/build/mcp/stripClient/output.jar
./projects/mcp/build/mcp/stripServer/output.jar
./projects/forge/build/libs/forge-1.16.5-36.2.39.jar
```
JAR URCAT: catsrc/projects/mcp/build/mcp/downloadServer/server.jar
