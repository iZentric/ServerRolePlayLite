#!/usr/bin/env python3
"""Windows PC closed compatibility boot for old-pack content, NEVER public."""
import json
import os
from pathlib import Path
import sys

from fc_modded_candidate import CHOSEN, PERFORMANCE
from fc_plugin_first_pc_smoke import boot
from fc_plugin_first_stage import ENGINE_SHA, GUAVA21_SHA, sha


def validate(stage):
    stage = Path(stage).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or not stage.is_relative_to(Path(temp).resolve()) or stage.name != 'stage':
        raise ValueError('only new PC runner temp stage allowed')
    report = json.loads((stage/'stage-report.json').read_text(encoding='utf-8'))
    mods = report['server_mods']
    expected = set(CHOSEN + tuple(report['server_optimizers']))
    if report['server_optimizers'] not in ([], list(PERFORMANCE)):
        raise ValueError('unknown performance selection')
    if (report['scope'] != 'UNRELEASED local modded compatibility experiment; ownership unverified' or
            len(mods) != len(expected) or {m['jar'] for m in mods} != expected or
            {p.name for p in (stage/'mods').iterdir()} != expected or
            any(sha(stage/'mods'/m['jar']) != m['sha256'] for m in mods) or
            sha(stage/'FunCity-1.16.5-b1.0827.jar') != ENGINE_SHA or
            sha(stage/'runtime/guava-21.0.jar') != GUAVA21_SHA or
            len(report['plugins']) != 6 or
            any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('unverified modded PC stage')
    props = (stage/'server.properties').read_text(encoding='ascii').splitlines()
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true'} <= set(props):
        raise ValueError('PC stage must stay on loopback')
    if (stage/'eula.txt').exists() or (stage/'lab-world').exists():
        raise ValueError('existing world/server cannot be used')
    return stage


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('expected new PC runner temp stage')
        boot(sys.argv[1], validate)
    except (ValueError, OSError, KeyError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        sys.exit(2)
