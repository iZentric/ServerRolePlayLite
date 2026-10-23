#!/usr/bin/env python3
"""Disposable, loopback-only Java 11 boot/stop of a built CatServer launcher.

Zero mods/plugins/players. It is NOT proof of hybrid RP compatibility or
capacity. Never uploads or prints raw boot logs, world data or binaries.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

DONE = re.compile(r'\bDone \([^\n]*\)! For help, type "help"')
FATAL = re.compile(r'\[(?:[^\n]*?/)?(?:ERROR|FATAL)\]|Exception in thread', re.I)
PROPERTIES = '''server-ip=127.0.0.1
server-port=25565
online-mode=false
white-list=true
enable-rcon=false
enable-query=false
enable-command-block=false
max-players=1
view-distance=4
max-tick-time=60000
level-name=lab-world
'''


def inspect(text):
    """Only report derived flags; logs remain private on the disposable VM."""
    return bool(DONE.search(text)), bool(FATAL.search(text))


def smoke(java, jar, deadline_seconds=420):
    jar = Path(jar).resolve(strict=True)
    if not jar.is_file() or not Path(java).is_file() or deadline_seconds < 1:
        raise ValueError('missing Java/JAR or invalid deadline')
    with tempfile.TemporaryDirectory(prefix='funcity-java11-smoke-') as tmp:
        work = Path(tmp)
        (work / 'eula.txt').write_text('eula=true\n')
        (work / 'server.properties').write_text(PROPERTIES)
        logpath = work / 'private-boot.log'
        with logpath.open('wb') as logfile:
            process = subprocess.Popen([str(java), '-Xms256m', '-Xmx2G', '-jar', str(jar), 'nogui'],
                                       cwd=work, stdin=subprocess.PIPE, stdout=logfile,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            started = time.monotonic()
            reached_done = fatal = False
            try:
                while time.monotonic() - started < deadline_seconds:
                    text = logpath.read_text(encoding='utf-8', errors='replace')
                    reached_done, fatal = inspect(text)
                    if fatal or reached_done or process.poll() is not None:
                        break
                    time.sleep(1)
                if process.poll() is None:
                    if reached_done and not fatal:
                        process.stdin.write(b'stop\n')
                        process.stdin.flush()
                    else:
                        process.terminate()
                process.stdin.close()
                try:
                    process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=10)
                # Inspect the final segment as well; startup success is not a clean stop.
                final_done, final_fatal = inspect(logpath.read_text(encoding='utf-8', errors='replace'))
                return final_done and not final_fatal and process.returncode == 0
            finally:
                if not process.stdin.closed:
                    process.stdin.close()
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(2)
    try:
        ok = smoke(sys.argv[1], sys.argv[2])
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print('JAVA11_LOOPBACK_SMOKE_REJECTED: ' + type(exc).__name__, file=sys.stderr)
        sys.exit(2)
    print('JAVA11_LOOPBACK_BOOT_CLEAN_STOP=' + str(ok).lower() +
          ' world=generated mods=0 plugins=0 players=0 client_login=NOT_TESTED')
    sys.exit(0 if ok else 2)
