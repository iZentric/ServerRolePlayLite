#!/usr/bin/env python3
"""Sequential, fail-closed A/B on disposable pack copies. Never edits a live server.

Example: python3 scripts/fc_spawner_ab.py --pack /path/pack.zip --pack-sha256 SHA \
  --engine /path/FunCity.jar --engine-sha256 SHA --run-dir /tmp/fc-smoke/my-run
Requires Java 11, installed pack/bootstrap dependencies, and a spare local server port.
Results are idle/server probes, NOT client Forge login, player FPS or capacity proof.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

MOD = 'mods/SpawnerFix-1.16.2-1.0.0.3.jar'
SANDBOX = Path('/tmp/fc-smoke')


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def compare(a, b, mod_sha):
    """Structural comparability only; this does not award a performance verdict."""
    same = (a.get('status') == b.get('status') == 'MASURAT'
            and a.get('probate_reusite') == b.get('probate_reusite') == 3
            and a.get('critice_total') == b.get('critice_total') == 0
            and a.get('pack_sha256_actual') == b.get('pack_sha256_actual') == a.get('pack_sha256_asteptat')
            and a.get('world_start_identical_each_trial') is True
            and b.get('world_start_identical_each_trial') is True
            and bool(a.get('world_snapshot_sha256'))
            and a.get('world_snapshot_sha256') == b.get('world_snapshot_sha256')
            and isinstance(a.get('pack_mods'), int) and isinstance(b.get('pack_mods'), int)
            and a['pack_mods'] == b['pack_mods'] + 1
            and a.get('pack_plugins') == b.get('pack_plugins')
            and a.get('overrides') == b.get('overrides')
            and a.get('excluded_mods_test_only') == {}
            and b.get('excluded_mods_test_only') == {MOD: mod_sha})
    return {'structural_pair_valid': bool(same),
            'world_sha256': a.get('world_snapshot_sha256') if same else None,
            'pack_sha256': a.get('pack_sha256_actual') if same else None,
            'mod_removed_only_in_test_sha256': mod_sha,
            'baseline': {k: a.get(k) for k in ('status', 'pack_mods', 'pack_plugins', 'boot_medie_s', 'rss_medie_mb', 'cpu_medie_pct', 'tps_p50')},
            'without_spawnerfix': {k: b.get(k) for k in ('status', 'pack_mods', 'pack_plugins', 'boot_medie_s', 'rss_medie_mb', 'cpu_medie_pct', 'tps_p50')},
            'performance_verdict': 'NEDECIS: idle probes alone cannot establish a player-workload benefit or justify rollout',
            'forge_client_login_fps': 'NEMASURAT; protocol probe is not Forge client login',
            'rollout': 'INTERZIS: no live/release change from this test'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('pack', 'pack-sha256', 'engine', 'engine-sha256', 'run-dir'):
        p.add_argument('--' + arg, required=True)
    args = p.parse_args()
    run = Path(args.run_dir).resolve()
    sandbox = SANDBOX.resolve()
    if run == sandbox or not run.is_relative_to(sandbox) or run.exists():
        p.error('--run-dir must be a NEW directory strictly inside /tmp/fc-smoke (results preserved)')
    for label, value in (('pack', args.pack), ('engine', args.engine)):
        path = Path(value)
        if not path.is_file() or path.is_symlink():
            p.error(f'{label} must be a regular readable file')
        expected = getattr(args, label + '_sha256')
        if not re.fullmatch('[a-fA-F0-9]{64}', expected) or sha_file(path) != expected.lower():
            p.error(f'{label} SHA256 mismatch or invalid; no Java process launched')
    with zipfile.ZipFile(args.pack) as z:
        members = [i for i in z.infolist() if i.filename == MOD and not i.is_dir()]
        if len(members) != 1:
            p.error(f'pack must contain exactly one {MOD}')
        mod_sha = hashlib.sha256(z.read(members[0])).hexdigest()
    run.mkdir(parents=True)  # no pre-existing results or stages may be overwritten
    config = {'pack_zip': str(Path(args.pack).resolve()), 'pack_sha256': args.pack_sha256.lower(),
              'boot_jar': 'FunCity.jar', 'install_timeout': 480, 'boot_timeout': 600,
              'java_args': ['-Xms1G', '-Xmx3G'],
              'props': {'server-ip': '127.0.0.1', 'server-port': '25565',
                        'online-mode': 'false', 'view-distance': '5', 'level-seed': '20261018'}}
    bench = Path(__file__).with_name('fc_bench.py')
    snapshot = run / 'world-reference'
    reports = []
    for arm, mode in (('baseline', 'save'), ('without-spawnerfix', 'restore')):
        cfg = dict(config, arm=arm)
        if mode == 'restore':
            cfg['exclude'] = [MOD]
        config_path = run / (arm + '.config.json')
        config_path.write_text(json.dumps(cfg, indent=2) + '\n')
        env = dict(os.environ, FC_JAR=str(Path(args.engine).resolve()),
                   FC_STAGE=str(run / arm / 'stage'), FC_OUT=str(run / arm / 'results'),
                   FC_WORLD_MODE=mode, FC_WORLD_SNAPSHOT=str(snapshot),
                   FC_TRIALS='3', FC_RUN_SECONDS='90')
        print(f'Running {arm} on a disposable isolated stage; no live modification', flush=True)
        rc = subprocess.run([sys.executable, str(bench), '--arm-conf', str(config_path)],
                            env=env, check=False).returncode
        report_path = run / arm / 'results' / (arm + '.json')
        if rc != 0 or not report_path.exists():
            print(f'BLOCAT: {arm} failed (rc={rc}); logs/stage kept at {run}; no next arm or verdict', file=sys.stderr)
            return 2
        reports.append(json.loads(report_path.read_text()))
        if (reports[-1].get('status') != 'MASURAT' or reports[-1].get('probate_reusite') != 3
                or reports[-1].get('critice_total') != 0):
            print(f'BLOCAT: {arm} incomplete or critical errors; see {report_path}; no next arm or verdict', file=sys.stderr)
            return 2
    baseline_mod = run / 'baseline' / 'stage' / MOD
    if not baseline_mod.is_file() or sha_file(baseline_mod) != mod_sha:
        print('BLOCAT: original mod not intact in baseline test stage', file=sys.stderr)
        return 2
    result = compare(*reports, mod_sha)
    (run / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['structural_pair_valid'] else 2


if __name__ == '__main__':
    sys.exit(main())
