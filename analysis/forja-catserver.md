# FORJA CatServer-Custom (Thu Oct  8 07:55:19 UTC 2026)
```
> Task :buildSrc:compileTestJava NO-SOURCE
> Task :buildSrc:compileTestGroovy NO-SOURCE
> Task :buildSrc:processTestResources NO-SOURCE
> Task :buildSrc:testClasses UP-TO-DATE
> Task :buildSrc:test NO-SOURCE
> Task :buildSrc:check UP-TO-DATE
> Task :buildSrc:build UP-TO-DATE

> Configure project :
Java: 1.8.0_504 JVM: 25.504-b01(Temurin) Arch: amd64 Git-Commit: 1c92118

> Configure project :clean
WARNING: This project is configured to use the official obfuscation mappings provided by Mojang. These mapping fall under their associated license, you should be fully aware of this license. For the latest license text, refer below, or the reference copy here: https://github.com/MinecraftForge/MCPConfig/blob/master/Mojang.md, You can hide this warning by running the `hideOfficialWarningUntilChanged` task
WARNING: (c) 2020 Microsoft Corporation. These mappings are provided "as-is" and you bear the risk of using them. You may copy and use the mappings for development purposes, but you may not redistribute the mappings complete and unmodified. Microsoft makes no warranties, express or implied, with respect to the mappings provided here.  Use and modification of this document or the source code (in any form) of Minecraft: Java Edition is governed by the Minecraft End User License Agreement available at https://account.mojang.com/documents/minecraft_eula.

> Configure project :
Forge Version: 1.16.5-36.2.39
Setting up MCP environment
Initializing steps
Executing steps
 > Running 'downloadManifest'
 > Running 'downloadJson'
 > Running 'downloadClient'
 > Running 'downloadServer'
 > Running 'stripClient'
 > Running 'stripServer'
 > Running 'merge'
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

> Task :mcp:downloadConfig UP-TO-DATE
> Task :clean:extractSrg
> Task :clean:createMcp2Srg

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
> Task :forge:createFakeSASPatches
> Task :forge:createMcp2Srg
> Task :clean:compileJava

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

> Task :clean:compileJava
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.

> Task :clean:processResources NO-SOURCE
> Task :clean:classes
> Task :clean:jar
> Task :clean:reobfJar

> Task :forge:compileJava
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
4 warnings

> Task :forge:processResources
> Task :forge:classes
> Task :forge:jar
> Task :clean:genServerBinPatches
> Task :forge:reobfJar
> Task :forge:genServerBinPatches
> Task :forge:filterJarNew
> Task :forge:universalJar
> Task :forge:buildCatServer

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD SUCCESSFUL in 2m 50s
21 actionable tasks: 18 executed, 3 up-to-date
BUILDCATSERVER OK
== jaruri nascute (toate build/libs + nume CatServer):
./buildSrc/build/libs/buildSrc.jar
./projects/forge/build/libs/forge-1.16.5-36.2.39.jar
./projects/forge/build/libs/CatServer-1.16.5-1c92118-server.jar
./projects/forge/build/libs/forge-1.16.5-36.2.39-universal.jar
./projects/clean/build/libs/clean.jar
./projects/forge/build/libs/CatServer-1.16.5-1c92118-server.jar
```
JAR URCAT: catsrc/projects/forge/build/libs/CatServer-1.16.5-1c92118-server.jar
