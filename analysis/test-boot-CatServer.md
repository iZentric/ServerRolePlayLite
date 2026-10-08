# VERDICT CatServer (Thu Oct  8 04:48:06 UTC 2026)
- REZULTAT: **CRAPAT** in 140s | RAM: **n/a**
- Done-line:
- Erori cheie:
          2 	at org.spongepowered.asm.mixin.transformer.MixinProcessor.handleMixinError(MixinProcessor.java:636) ~[mixin-0.8.4.jar:0.8.4+unknown-b0.git-unknown]
          2 	at org.spongepowered.asm.mixin.transformer.MixinProcessor.handleMixinApplyError(MixinProcessor.java:588) ~[mixin-0.8.4.jar:0.8.4+unknown-b0.git-unknown]
          1 org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered
          1 org.spongepowered.asm.mixin.throwables.MixinApplyError: Mixin [radon.mixins.json:chunk.MixinChunkNibbleArray] from phase [DEFAULT] in config [radon.mixins.json] FAILED during APPLY
          1 [04:47:32] [Server thread/ERROR]: Exception stopping the server
          1 [04:47:31] [Server thread/WARN]: Incorrect key server.removeErroringTileEntities was corrected from null to its default, false. 
          1 [04:47:31] [Server thread/WARN]: Incorrect key server.removeErroringEntities was corrected from null to its default, false. 
          1 [04:47:31] [Server thread/FATAL]: Preparing crash report with UUID 2347fb89-1743-4651-ba7a-45046e5eaf4f
          1 [04:47:31] [Server thread/FATAL]: Mixin apply failed radon.mixins.json:chunk.MixinChunkNibbleArray -> net.minecraft.world.chunk.NibbleArray: org.spongepowered.asm.mixin.transformer.throwables.InvalidMixinException PRIVATE @Overwrite method func_177480_a in radon.mixins.json:chunk.MixinChunkNibbleArray cannot reduce visibiliy of PUBLIC target method
          1 [04:47:31] [Server thread/ERROR]: \tCause of unexpected exception was
          1 [04:47:31] [Server thread/ERROR]: This crash report has been saved to: /home/runner/work/ServerRolePlayLite/ServerRolePlayLite/srv/./crash-reports/crash-2026-10-08_04.47.31-server.txt
          1 [04:47:31] [Server thread/ERROR]: Encountered an unexpected exception
- Pluginuri pornite:
    [04:47:19] [Server thread/INFO]: [LuckPerms] Enabling LuckPerms v5.5.71
    [04:47:27] [Server thread/INFO]: [Vault] Enabling Vault v1.7.3-b131
    [04:47:27] [Server thread/INFO]: [ProtocolLib] Enabling ProtocolLib v4.8.0
    [04:47:27] [Server thread/INFO]: [WorldEdit] Enabling WorldEdit v7.2.5+57d5ac9
