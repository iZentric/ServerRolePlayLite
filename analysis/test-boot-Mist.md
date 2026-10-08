# VERDICT Mist (Thu Oct  8 08:03:43 UTC 2026)
- REZULTAT: **TIMEOUT** in 1000s | RAM: **806MB**
- Done-line:
- Erori cheie:
          1 [07:47:20 INFO]: [java.lang.Throwable:printStackTrace:671]: Caused by: org.spongepowered.asm.mixin.throwables.MixinApplyError: Mixin [fastbench.mixins.json:MixinWorkbenchContainer] from phase [DEFAULT] in config [fastbench.mixins.json] FAILED during APPLY
          1 [07:47:20 INFO]: [java.lang.Throwable:printStackTrace:671]: 	at org.spongepowered.asm.mixin.transformer.MixinProcessor.handleMixinError(MixinProcessor.java:642)
          1 [07:47:20 INFO]: [java.lang.Throwable:printStackTrace:671]: 	at org.spongepowered.asm.mixin.transformer.MixinProcessor.handleMixinApplyError(MixinProcessor.java:594)
          1 [07:47:20 INFO]: [java.lang.Throwable:printStackTrace:648]: Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered
          1 [07:47:20 FATAL]: Mixin apply failed fastbench.mixins.json:MixinWorkbenchContainer -> net.minecraft.inventory.container.WorkbenchContainer: org.spongepowered.asm.mixin.transformer.throwables.InvalidMixinException Unexpecteded ArrayIndexOutOfBoundsException whilst transforming the mixin class: [INJECT Applicator Phase -> fastbench.mixins.json:MixinWorkbenchContainer -> Apply Injections -> Inject -> fastbench.mixins.json:MixinWorkbenchContainer->@FactoryRedirectWrapper::makeExtInv(Lnet/minecraft/inventory/container/Container;II)Lnet/minecraft/inventory/CraftingInventory;]
          1 [07:47:15 ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
          1 [07:47:11 ERROR]: Zip Error when loading jar file /home/runner/work/ServerRolePlayLite/ServerRolePlayLite/srv/mods/performant-1.16.2-5-4.1m.jar
          1 Exception in thread "main" [07:47:20 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: java.lang.RuntimeException: java.lang.reflect.InvocationTargetException
          1 Downloading file error_prone_annotations-2.1.3.jar with size 13.3828125 KB
          1 Download finished for error_prone_annotations-2.1.3.jar !
          1 	at java.util.zip.ZipFile$Source.zerror(ZipFile.java:1776) ~[?:?]
- Contextul erorilor invalid-dist (vinovatul cu nume):
- Contextul erorii File not found (ultimul mister):
- CANTARUL PE MOD (cei mai scumpi la incarcare, din debug.log):
- Pluginuri pornite:
