# ENGINE LAB — build izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38091297299

Ultimele linii din compilare (nu sunt cifre de TPS):
```
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:64: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.SlimeEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:65: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.SpellcastingIllagerEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:66: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.SpiderEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:67: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.StrayEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:68: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.VexEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:69: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.VindicatorEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:70: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.WitchEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:71: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.WitherSkeletonEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:72: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.ZoglinEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:73: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.ZombieEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:74: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.ZombieVillagerEntity;
                                   ^
/tmp/catserver-source/src/main/java/org/bukkit/craftbukkit/v1_16_R3/entity/CraftEntity.java:75: error: package net.minecraft.entity.monster does not exist
import net.minecraft.entity.monster.ZombifiedPiglinEntity;
                                   ^
/tmp/catserver-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/tmp/catserver-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^

> Task :mcp:setupMCP
 > Running 'forgeAccessTransformer'
[22:26:50] [main/INFO]: Access Transformer processor running version 8.0.7+8.0.7+master.43473d43
[22:26:50] [main/INFO]: Command line arguments [--inJar, /tmp/catserver-source/projects/mcp/build/mcp/mcinject/output.jar, --outJar, /tmp/catserver-source/projects/mcp/build/mcp/forgeAccessTransformer/output.jar, --atFile, /tmp/catserver-source/src/main/resources/META-INF/accesstransformer.cfg]
[22:26:50] [main/INFO]: Reading from /tmp/catserver-source/projects/mcp/build/mcp/mcinject/output.jar
[22:26:50] [main/INFO]: Writing to /tmp/catserver-source/projects/mcp/build/mcp/forgeAccessTransformer/output.jar
[22:26:50] [main/INFO]: Transformer file /tmp/catserver-source/src/main/resources/META-INF/accesstransformer.cfg
[22:26:50] [main/WARN]: Found existing output jar /tmp/catserver-source/projects/mcp/build/mcp/forgeAccessTransformer/output.jar, overwriting
[22:26:52] [main/INFO]: JAR transformation complete /tmp/catserver-source/projects/mcp/build/mcp/forgeAccessTransformer/output.jar
 > Running 'forgeSideStripper'
 > Running 'decompile'
 > Running 'inject'
 > Running 'patch'
MCP environment setup is complete

FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':forge:compileJava'.
> java.lang.NullPointerException

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.

* Get more help at https://help.gradle.org

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD FAILED in 3m 44s
16 actionable tasks: 16 executed
```

Smoke:
```
NU RULAT
```
