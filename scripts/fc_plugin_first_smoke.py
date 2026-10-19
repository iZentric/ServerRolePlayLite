#!/usr/bin/env python3
"""Disposable one-boot check of the closed plugin-first stage; NEVER public.

Run only in a new hosted runner temp directory. No player joins or benchmarks.
"""
import json
import os
from pathlib import Path
import sys
import time

from fc_bench import JvmRun
from fc_plugin_first_stage import ENGINE_SHA, sha


def check_stage(stage):
    stage = Path(stage).resolve()
    runner_temp = os.environ.get('RUNNER_TEMP')
    if not runner_temp or not stage.is_relative_to(Path(runner_temp).resolve()) or stage.name != 'stage':
        raise ValueError('boot is allowed only in the hosted runner temp stage')
    report = json.loads((stage/'stage-report.json').read_text())
    if (report['server_mods'] != [] or report['engine']['sha256'] != ENGINE_SHA or
            sha(stage/'FunCity-1.16.5-b1.0827.jar') != ENGINE_SHA or
            sorted(p.name for p in (stage/'plugins').glob('*.jar')) !=
            sorted(p['jar'] for p in report['plugins']) or len(report['plugins']) != 6 or
            any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']) or
            list((stage/'mods').glob('*'))):
        raise ValueError('stage JAR inventory drift')
    props = (stage/'server.properties').read_text()
    if not all(line in props.splitlines() for line in (
            'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true')):
        raise ValueError('stage must remain loopback-only with no unauthenticated players')
    if (stage/'eula.txt').exists() or (stage/'lab-world').exists():
        raise ValueError('stage must be new, not an existing world/server')
    return stage


def smoke(stage):
    stage = check_stage(stage)
    # EULA acceptance is confined to this throwaway hosted runner, never published.
    (stage/'eula.txt').write_text('eula=true\n')
    motor = 'FunCity-1.16.5-b1.0827.jar'
    for attempt in (1, 2):
        log = stage/f'boot-attempt-{attempt}.log'
        run = JvmRun(str(stage), motor, ['-Xms512M', '-Xmx2G'], str(log))
        run.port = 25565
        try:
            run.start()
            ready = run.wait_done(420)
            if ready:
                time.sleep(5)
                text = log.read_text(encoding='utf-8', errors='replace')
                # Names inside the JAR need not match filenames. Verify essentials
                # by their declared plugin names in the server log, never by count alone.
                required = ('CoreProtect', 'Essentials', 'LuckPerms', 'Vault')
                missing = [name for name in required if not any(
                    ('Enabling ' + name + ' ') in line or ('Enabling ' + name + ' v') in line
                    for line in text.splitlines())]
                stopped = run.stop(60)
                if missing or stopped != 'CLEAN':
                    raise ValueError(f'booted but missing active plugins={missing}; shutdown={stopped}')
                print('::notice title=Plugin-first closed boot::'
                      f'engine=b1.0827 sha256={ENGINE_SHA} mods=0 staged_plugins=6 '
                      f'active_core={",".join(required)} boot_attempt={attempt} '
                      'loopback_only=true online_mode=true whitelist=true; '
                      'NO player login/auth/voice/RP or capacity claim')
                return True
            text = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
            exited = run.p.poll() if run.p else None
            if exited is None:
                run.stop(15)
            if attempt == 1 and exited == 0 and any(marker in text for marker in (
                    'Successfully installed', 'Server installed', 'install complete')):
                continue  # installer ended cleanly; second run boots server
            print('BOOT_FAILURE tail:', '\n'.join(text.splitlines()[-18:])[-3000:], file=sys.stderr)
            raise ValueError(f'engine did not reach Done marker; exit={exited}, attempt={attempt}')
        finally:
            run.close()
    raise ValueError('installer did not produce a playable boot')


def main():
    try:
        smoke(sys.argv[1])
    except (ValueError, KeyError, OSError, IndexError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
