# ENGINE LAB — build izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38091260752

Ultimele linii din compilare (nu sunt cifre de TPS):
```
Downloading https://services.gradle.org/distributions/gradle-7.3.3-bin.zip
...........10%...........20%...........30%...........40%...........50%...........60%...........70%...........80%...........90%...........100%

Welcome to Gradle 7.3.3!

Here are the highlights of this release:
 - Easily declare new test suites in Java projects
 - Support for Java 17
 - Support for Scala 3

For more details see https://docs.gradle.org/7.3.3/release-notes.html

To honour the JVM settings for this build a single-use Daemon process will be forked. See https://docs.gradle.org/7.3.3/userguide/gradle_daemon.html#sec:disabling_the_daemon.
Could not write standard input to Gradle build daemon.
java.io.IOException: Stream closed
	at java.base/java.lang.ProcessBuilder$NullOutputStream.write(ProcessBuilder.java:445)
	at java.base/java.io.OutputStream.write(OutputStream.java:162)
	at java.base/java.io.BufferedOutputStream.flushBuffer(BufferedOutputStream.java:81)
	at java.base/java.io.BufferedOutputStream.flush(BufferedOutputStream.java:142)
	at org.gradle.process.internal.streams.ExecOutputHandleRunner.forwardContent(ExecOutputHandleRunner.java:68)
	at org.gradle.process.internal.streams.ExecOutputHandleRunner.run(ExecOutputHandleRunner.java:53)
	at org.gradle.internal.concurrent.ExecutorPolicy$CatchAndRecordFailures.onExecute(ExecutorPolicy.java:64)
	at org.gradle.internal.concurrent.ManagedExecutorImpl$1.run(ManagedExecutorImpl.java:48)
	at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1136)
	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635)
	at org.gradle.internal.concurrent.ThreadFactoryImpl$ManagedThreadRunnable.run(ThreadFactoryImpl.java:61)
	at java.base/java.lang.Thread.run(Thread.java:840)

FAILURE: Build failed with an exception.

* What went wrong:
Unable to start the daemon process.
This problem might be caused by incorrect configuration of the daemon.
For example, an unrecognized jvm option is used.
Please refer to the User Manual chapter on the daemon at https://docs.gradle.org/7.3.3/userguide/gradle_daemon.html
Process command line: /usr/lib/jvm/temurin-17-jdk-amd64/bin/java -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError --add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.lang.invoke=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED --add-opens java.prefs/java.util.prefs=ALL-UNNAMED --add-opens java.prefs/java.util.prefs=ALL-UNNAMED --add-opens java.base/java.nio.charset=ALL-UNNAMED --add-opens java.base/java.net=ALL-UNNAMED --add-opens java.base/java.util.concurrent.atomic=ALL-UNNAMED -Xmx3G -Dfile.encoding=UTF-8 -Duser.country -Duser.language=en -Duser.variant -cp /home/runner/.gradle/wrapper/dists/gradle-7.3.3-bin/6a41zxkdtcxs8rphpq6y0069z/gradle-7.3.3/lib/gradle-launcher-7.3.3.jar org.gradle.launcher.daemon.bootstrap.GradleDaemon 7.3.3
Please read the following process output to find out more:
-----------------------
Unrecognized VM option 'MaxPermSize=512m'
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.


* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.

* Get more help at https://help.gradle.org
```

Smoke:
```
NU RULAT
```
