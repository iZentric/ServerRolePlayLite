#!/usr/bin/env python3
"""Closed hosted canary: exact 28-mod RP baseline, then ONE optional server-only JAR.

This proves only two isolated boots with six plugins; NO clients, concurrent
players, actual network sending, live PC or capacity/performance claims.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_full_rp_engine_boot import main as full_boot
from fc_mod_binary_evidence import inspect_jar
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

CANDIDATE = 'chunksending-1.16.5-2.5.jar'


def validate_candidate(root, candidate):
    root, candidate = Path(root).resolve(), Path(candidate).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if (not temp or root != Path(temp).resolve()/'fc-full-rp-catserver-official' or
            candidate != root/CANDIDATE or candidate.is_symlink() or
            not candidate.is_file() or not 1000 < candidate.stat().st_size < 100_000):
        raise ValueError('source not exact, new hosted runner temp path')
    data = inspect_jar(candidate.read_bytes())
    if (data['metadata'] != 'mods.toml' or data['mod_ids'] != ['chunksending'] or
            any(dep not in ('forge', 'minecraft')
                for deps in data['required_dependencies'].values() for dep in deps)):
        raise ValueError('not isolated Forge 1.16.5 chunk-sending candidate')
    return sha(candidate)


def main(root, source, archive, motor, core, guava, candidate):
    root = Path(root).resolve()
    candidate_sha = validate_candidate(root, candidate)
    # The upstream harness verifies SHA-pinned official motor and historical
    # JARs, dependency metadata, exact mod/plugin inventory, loopback/whitelist
    # and clean baseline boot before any experimental candidate is staged.
    full_boot(root, 'catserver-official', source, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name for p in (template/'mods').iterdir()}
    if len(baseline) != 28 or len(report['plugins']) != 6:
        raise ValueError('baseline changed')
    for trial in (1, 2):
        stage = root/f'chunk-sending-trial-{trial}'
        shutil.copytree(template, stage, symlinks=False)
        if (stage/'mods'/CANDIDATE).exists() or (stage/'mods'/CANDIDATE).is_symlink():
            raise ValueError('candidate already in baseline')
        shutil.copyfile(candidate, stage/'mods'/CANDIDATE)
        if ({p.name for p in (stage/'mods').iterdir()} != baseline | {CANDIDATE} or
                sha(stage/'mods'/CANDIDATE) != candidate_sha):
            raise ValueError('stage inventory or candidate hash drift')
        # Do not reuse the baseline log; no raw logs leave the disposable VM.
        (stage/'private-benchmark.log').unlink(missing_ok=True)
        run_one(stage, report, generate=True)
    print('::notice title=Chunk Sending Forge 1.16.5 canary::baseline=28/6 clean; '
          'candidate=29/6 clean_twice=true file_id=4583202 sha256=' + candidate_sha +
          ' world=GENERATED client_login=NO packet_load=NO players=0 '
          'p95=UNMEASURED capacity=UNMEASURED no_artifact_uploaded=true', flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 8:
            raise ValueError('wrong number of hosted runner inputs')
        main(*sys.argv[1:])
    except (ValueError, OSError, AssertionError, KeyError, zipfile.BadZipFile):
        print('::error title=Chunk Sending canary rejected::No promotion; private diagnostic remains on disposable runner',
              file=sys.stderr)
        sys.exit(2)
