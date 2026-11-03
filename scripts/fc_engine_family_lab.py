#!/usr/bin/env python3
"""One SHA-pinned engine at a time against the SAME disposable 15-mod RP stage.

GitHub-hosted loopback only. No world/account/config from live; no raw log upload.
A boot is a compatibility probe, NOT an A/B, player login or engine ranking.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
import zipfile

from fc_bench import JvmRun
from fc_modded_candidate import CHOSEN
from fc_plugin_first_stage import ARCHIVE_SHA, ENGINE_SHA, GUAVA21_SHA, sha

# SHA values previously recorded for EXACT archived 1.16.5 binaries, not families.
ENGINES = {
    'funcity': (None, None, None, ENGINE_SHA),
    'catserver-old': ('zip', ARCHIVE_SHA, 'CatServer-1.16.5-1d8d6313-server.jar',
                      '96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c'),
    'catserver-official': ('jar', None, None,
                           '8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0'),
    'arclight': ('zip', 'd0eed502fd6f45c69f5c887970b938fdc20b13e8e0327bcdeae53b2204a0e1f7',
                 'arclight-forge-1.16.5-1.0.25.jar',
                 'f7615ceb7fbb343aaef7bfc6238b131a28cf9a08190994e94e78e14a6d49ea78'),
    'mist': ('zip', 'ec3da2c161d1754e94f923c73f406410f6d7bf8be1d03b208717d503081fcf65',
             'mist-1.16.5-33-server.jar',
             '1c5554d51ac28d7a101d113387f0ad5023618054a03021515924444d75ff06de'),
}
BOOT_JAR = 'FunCity-1.16.5-b1.0827.jar'


def source_engine(name, source):
    kind, archive_sha, member, expected = ENGINES[name]
    if kind is None:
        return None
    source = Path(source)
    if not source.is_file() or source.is_symlink():
        raise ValueError('source unavailable')
    if kind == 'jar':
        if sha(source) != expected:
            raise ValueError('engine SHA mismatch')
        return source.read_bytes()
    if sha(source) != archive_sha:
        raise ValueError('archive SHA mismatch')
    with zipfile.ZipFile(source) as z:
        entries = [i for i in z.infolist() if i.filename == member and not i.is_dir()]
        if len(entries) != 1 or entries[0].file_size > 200_000_000:
            raise ValueError('unique root engine JAR missing/oversized')
        data = z.read(entries[0])
    import hashlib
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('embedded engine SHA mismatch')
    return data


def validate_stage(stage):
    stage = Path(stage).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or stage.name != 'stage' or not stage.is_relative_to(Path(temp).resolve()):
        raise ValueError('only isolated runner temp stage')
    report = json.loads((stage/'stage-report.json').read_text())
    mods = report['server_mods']
    if (report['scope'] != 'UNRELEASED local modded compatibility experiment; ownership unverified'
            or report['server_optimizers'] != [] or len(mods) != 15
            or {m['jar'] for m in mods} != set(CHOSEN)
            or {p.name for p in (stage/'mods').iterdir()} != set(CHOSEN)
            or any(sha(stage/'mods'/m['jar']) != m['sha256'] for m in mods)
            or len(report['plugins']) != 6
            or any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])
            or sha(stage/BOOT_JAR) != ENGINE_SHA
            or sha(stage/'runtime/guava-21.0.jar') != GUAVA21_SHA):
        raise ValueError('candidate not the exact 15-mod/6-plugin baseline')
    props = (stage/'server.properties').read_text().splitlines()
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true'} <= set(props):
        raise ValueError('stage must be closed to public')
    if (stage/'eula.txt').exists() or (stage/'lab-world').exists():
        raise ValueError('existing world or prior boot not allowed')
    return report


def successful_stop(jvm, log=None):
    """JvmRun's CLEAN means exited; also check code and late fatal log lines."""
    status = jvm.stop(70)
    if status != 'CLEAN' or jvm.p.returncode != 0:
        return False
    if log is not None:
        text = Path(log).read_text(encoding='utf-8', errors='replace')
        if any(marker in text for marker in ('Exception in server tick loop',
                                           'Could not load plugin', 'Error occurred while enabling',
                                           'Failed to start')):
            return False
    return True


def run(stage, name, source):
    stage = Path(stage).resolve()
    if name not in ENGINES:
        raise ValueError('unknown engine choice')
    report = validate_stage(stage)
    replacement = source_engine(name, source)
    if replacement is not None:
        # ONLY the brand-new, validated temporary stage, never an installed engine.
        (stage/BOOT_JAR).write_bytes(replacement)
    if sha(stage/BOOT_JAR) != ENGINES[name][3]:
        raise ValueError('staged engine SHA mismatch')
    (stage/'eula.txt').write_text('eula=true\n')
    log = stage/'engine-boot.log'  # intentionally never published
    j = JvmRun(str(stage), BOOT_JAR,
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
                '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    status = 'BOOT_FAILED'
    plugins_ok = False
    clean = False
    try:
        j.start()
        ready = j.wait_done(420)
        if ready:
            time.sleep(5)
            text = log.read_text(encoding='utf-8', errors='replace')
            plugins_ok = all(re.search(r'Enabling ' + re.escape(p['declared_name']) + r' (?:v|\d)', text)
                             for p in report['plugins'])
            critical = any(token in text for token in
                           ('Exception in server tick loop', 'Could not load plugin',
                            'Error occurred while enabling', 'Failed to start'))
            clean = successful_stop(j, log)
            status = 'BOOT_AND_PLUGINS_OK' if plugins_ok and not critical and clean else 'BOOT_WITH_REGRESSIONS'
        else:
            clean = successful_stop(j) if j.p.poll() is None else False
        # Only categorical evidence is public; bootstrap/install time is NOT a TPS measurement.
        print(f'::notice title=Engine 15-mod isolated test::{name} status={status} '
              f'plugins_ok={str(plugins_ok).lower()} clean_stop={str(clean).lower()} '
              'same_content=15 same_plugins=6 loopback=true player_join=NOT_TESTED '
              'mspt_rss_gain=NOT_MEASURED no_live_write=true', flush=True)
        return status
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(10)
        j.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', type=Path)
    p.add_argument('name', choices=ENGINES)
    p.add_argument('source', type=Path)
    args = p.parse_args()
    try:
        run(args.stage, args.name, args.source)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print('RESPINS: engine trial preflight: ' + str(exc), file=sys.stderr)
        sys.exit(2)
