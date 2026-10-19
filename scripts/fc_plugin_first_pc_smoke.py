#!/usr/bin/env python3
"""One-shot, closed PC lab boot. Never touches any existing server or player data."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from fc_plugin_first_smoke import check_stage


def boot(stage, verify=check_stage):
    stage = verify(stage)  # requires a new runner-temp stage with verified SHA/JARs
    # Do not steal an already used port; this process must remain local to the PC.
    import socket
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', 25565))
        except OSError as exc:
            raise ValueError('loopback port already in use; existing server untouched') from exc
    (stage / 'eula.txt').write_text('eula=true\n', encoding='ascii')
    jar = stage / 'FunCity-1.16.5-b1.0827.jar'
    args = ['java', '-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
            '-Xms512M', '-Xmx2G', '-jar', str(jar), 'nogui']
    log = stage/'pc-boot.log'
    p = None
    try:
        with log.open('wb') as output:
            p = subprocess.Popen(args, cwd=stage, stdin=subprocess.PIPE,
                                 stdout=output, stderr=subprocess.STDOUT)
            end = time.monotonic() + 450
            ready = False
            while time.monotonic() < end:
                text = log.read_text(encoding='utf-8', errors='replace')
                if re.search(r'Done \([0-9.]+s\)', text):
                    ready = True
                    break
                if p.poll() is not None:
                    break
                time.sleep(2)
            if not ready:
                text = log.read_text(encoding='utf-8', errors='replace')
                indicators = [word for word in ('NoSuchMethodError', 'UnsupportedClassVersionError',
                                                'Failed to start', 'Could not load plugin') if word in text]
                raise ValueError('PC lab did not boot; exit=' + str(p.poll()) +
                                 ' indicators=' + ','.join(indicators))
            report = json.loads((stage/'stage-report.json').read_text(encoding='utf-8'))
            names = [plugin['declared_name'] for plugin in report['plugins']]
            missing = [name for name in names if not re.search(
                r'Enabling ' + re.escape(name) + r' (?:v|\d)', text)]
            critical = [line for line in text.splitlines() if any(
                marker in line for marker in ('Could not load plugin', 'Error occurred while enabling',
                                               'Exception in server tick loop', 'Failed to start'))]
            if missing or critical:
                raise ValueError('PC lab booted but plugin failure: missing=' + ','.join(missing) +
                                 ' critical_log_lines=' + str(len(critical)))
            print('::notice title=FunCity PC CLOSED boot::Done=true mods=' +
                  str(len(report['server_mods'])) + ' active_plugins=' + ','.join(names) +
                  ' loopback=true; no client login, auth plugin, voice, RP or capacity tested', flush=True)
            p.stdin.write(b'stop\n')
            p.stdin.flush()
            try:
                code = p.wait(timeout=70)
            except subprocess.TimeoutExpired as exc:
                raise ValueError('PC lab did not stop cleanly') from exc
            if code != 0:
                raise ValueError('PC lab stop exit=' + str(code))
            print('::notice title=FunCity PC CLOSED stop::clean=true', flush=True)
    finally:
        if p is not None and p.poll() is None:
            p.kill()  # only the process started here, never a pre-existing server
            p.wait(timeout=20)
        if p is not None and p.stdin is not None:
            p.stdin.close()


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('expected runner-temp new stage')
        boot(sys.argv[1])
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print('RESPINS: PC lab boot: ' + str(exc), file=sys.stderr)
        sys.exit(2)
