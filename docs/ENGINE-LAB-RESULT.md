# ENGINE LAB — build izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38092471792

Ultimele linii din compilare (nu sunt cifre de TPS):
```
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


The system is out of resources.
Consult the following stack trace for details.
java.lang.OutOfMemoryError: GC overhead limit exceeded
	at com.sun.tools.javac.comp.Resolve.resolveQualifiedMethod(Resolve.java:2427)
	at com.sun.tools.javac.comp.Attr.selectSym(Attr.java:3396)
	at com.sun.tools.javac.comp.Attr.visitSelect(Attr.java:3278)
	at com.sun.tools.javac.tree.JCTree$JCFieldAccess.accept(JCTree.java:1897)
	at com.sun.tools.javac.comp.Attr.attribTree(Attr.java:576)
	at com.sun.tools.javac.comp.Attr.visitApply(Attr.java:1825)
	at com.sun.tools.javac.tree.JCTree$JCMethodInvocation.accept(JCTree.java:1465)
	at com.sun.tools.javac.comp.Attr.attribTree(Attr.java:576)
	at com.sun.tools.javac.comp.Attr.attribArgs(Attr.java:674)
	at com.sun.tools.javac.comp.Attr.visitApply(Attr.java:1816)
	at com.sun.tools.javac.tree.JCTree$JCMethodInvocation.accept(JCTree.java:1465)
	at com.sun.tools.javac.comp.Attr.attribTree(Attr.java:576)
	at com.sun.tools.javac.comp.Attr.visitReturn(Attr.java:1686)
	at com.sun.tools.javac.tree.JCTree$JCReturn.accept(JCTree.java:1384)
	at com.sun.tools.javac.comp.Attr.attribTree(Attr.java:576)
	at com.sun.tools.javac.comp.Attr.attribStat(Attr.java:645)
	at com.sun.tools.javac.comp.Attr.attribStats(Attr.java:661)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredAttrNode$StructuralStuckChecker.canLambdaBodyCompleteNormally(DeferredAttr.java:716)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredAttrNode$StructuralStuckChecker.visitLambda(DeferredAttr.java:664)
	at com.sun.tools.javac.tree.JCTree$JCLambda.accept(JCTree.java:1624)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredAttrNode$StructuralStuckChecker.complete(DeferredAttr.java:617)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredType.check(DeferredAttr.java:246)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredType.access$100(DeferredAttr.java:132)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredAttrNode.process(DeferredAttr.java:564)
	at com.sun.tools.javac.comp.DeferredAttr$DeferredAttrContext.complete(DeferredAttr.java:480)
	at com.sun.tools.javac.comp.Resolve.rawInstantiate(Resolve.java:581)
	at com.sun.tools.javac.comp.Resolve.selectBest(Resolve.java:1446)
	at com.sun.tools.javac.comp.Resolve.findMethodInScope(Resolve.java:1633)
	at com.sun.tools.javac.comp.Resolve.findMethod(Resolve.java:1704)
	at com.sun.tools.javac.comp.Resolve.findMethod(Resolve.java:1677)
	at com.sun.tools.javac.comp.Resolve$9.doLookup(Resolve.java:2436)
	at com.sun.tools.javac.comp.Resolve$BasicLookupHelper.lookup(Resolve.java:3097)

> Task :forge:compileJava FAILED

FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':forge:compileJava'.
> Compilation failed; see the compiler error output for details.

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.

* Get more help at https://help.gradle.org

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD FAILED in 10m 53s
14 actionable tasks: 11 executed, 3 up-to-date
```

Smoke:
```
NU RULAT
```
