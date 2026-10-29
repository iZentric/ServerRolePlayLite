#!/usr/bin/env python3
"""Disposable one-boot check of the closed plugin-first stage; NEVER public.

Run only in a new hosted runner temp directory. No player joins or benchmarks.
"""
import json
import os
from pathlib import Path
import re
import sys
import time

from fc_bench import JvmRun
from fc_plugin_first_stage import ENGINE_SHA, GUAVA21_SHA, sha


def check_stage(stage):
    stage = Path(stage).resolve()
    runner_temp = os.environ.get('RUNNER_TEMP')
    if not runner_temp or not stage.is_relative_to(Path(runner_temp).resolve()) or stage.name != 'stage':
        raise ValueError('boot is allowed only in the hosted runner temp stage')
    report = json.loads((stage/'stage-report.json').read_text())
    if (report['server_mods'] != [] or report['engine']['sha256'] != ENGINE_SHA or
            report['runtime_lab_dependency']['path'] != 'runtime/guava-21.0.jar' or
            report['runtime_lab_dependency']['sha256'] != GUAVA21_SHA or
            sorted(p.name for p in (stage/'runtime').iterdir()) != ['guava-21.0.jar'] or
            sha(stage/'runtime/guava-21.0.jar') != GUAVA21_SHA or
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
    guava21 = stage/'runtime/guava-21.0.jar'  # packaged and verified by the stage builder
    # EULA acceptance is confined to this throwaway hosted runner, never published.
    (stage/'eula.txt').write_text('eula=true\n')
    motor = 'FunCity-1.16.5-b1.0827.jar'
    for attempt in (1, 2):
        log = stage/f'boot-attempt-{attempt}.log'
        run = JvmRun(str(stage), motor,
                     ['-Xbootclasspath/a:' + str(guava21), '-Xms512M', '-Xmx2G'], str(log))
        run.port = 25565
        try:
            run.start()
            ready = run.wait_done(420)
            if ready:
                time.sleep(5)
                text = log.read_text(encoding='utf-8', errors='replace')
                # Verify ALL six by exact plugin.yml name, not just JAR presence.
                report = json.loads((stage/'stage-report.json').read_text())
                required = tuple(p['declared_name'] for p in report['plugins'])
                missing = [name for name in required if not any(
                    ('Enabling ' + name + ' ') in line or ('Enabling ' + name + ' v') in line
                    for line in text.splitlines())]
                critical = [line for line in text.splitlines() if any(
                    token in line for token in ('Could not load plugin', 'Error occurred while enabling',
                                               'Exception in server tick loop', 'Failed to start'))]
                stopped = run.stop(60)
                versions = sorted(set(re.findall(r'(?<!\d)36\.2\.\d+(?!\d)', text)))
                print('::notice title=Forge versions mentioned in boot log::' +
                      (','.join(versions[:8]) if versions else 'NOT_FOUND'))
                if missing or critical or stopped != 'CLEAN':
                    details = (f'booted but missing active plugins={missing}; '
                               f'critical_log_lines={len(critical)}; shutdown={stopped}')
                    print('::error title=Closed FunCity boot check::' + details)
                    raise ValueError(details)
                print('::notice title=Plugin-first closed boot::'
                      f'engine=b1.0827 sha256={ENGINE_SHA} mods=0 staged_plugins=6 '
                      f'active_plugins={",".join(required)} boot_attempt={attempt} '
                      f'guava21_lab_override_sha256={GUAVA21_SHA} '
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
            relevant = [line for line in text.splitlines() if any(
                token in line.lower() for token in ('guava', 'install', 'immutablemap',
                                                    'nosuchmethoderror', 'classpath', 'fatal'))]
            excerpt = re.sub(r'[^A-Za-z0-9 ._+/():=,-]', '_',
                             ' | '.join(relevant[-12:]))[-1400:]
            print(f'::error title=Closed FunCity boot diagnosis::exit={exited} '
                  f'attempt={attempt} clues={excerpt}')
            guava = [p.relative_to(stage).as_posix() for p in (stage/'libraries').rglob('*guava*.jar')]
            print('::notice title=Installed Guava JAR paths::' +
                  ','.join(guava[:8])[:550] if guava else
                  '::notice title=Installed Guava JAR paths::none')
            tail = re.sub(r'[^A-Za-z0-9 ._+/():=,-]', '_',
                          ' | '.join(text.splitlines()[-15:]))[-1600:]
            print(f'::error title=Closed FunCity boot::exit={exited} attempt={attempt} tail={tail}')
            raise ValueError(f'engine did not reach Done marker; exit={exited}, attempt={attempt}')
        finally:
            run.close()
    raise ValueError('installer did not produce a playable boot')


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError('expected isolated stage with bundled pinned Guava21')
        smoke(sys.argv[1])
    except (ValueError, KeyError, OSError, IndexError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        reason = re.sub(r'[^A-Za-z0-9 ._+/():=,-]', '_', str(exc))[:400]
        print('::error title=Closed FunCity smoke rejected::' + reason)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
