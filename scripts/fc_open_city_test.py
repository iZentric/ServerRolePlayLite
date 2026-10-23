#!/usr/bin/env python3
"""Static policy regression for a player-built open city; NOT a Minecraft test."""
from pathlib import Path
import re
import sys

NO_PREVENTION = {'P04': 'EssentialsXAntiBuild', 'P06': 'EssentialsXProtect',
                 'P12': 'claimchunk', 'P14': 'WorldGuard'}
TOOLS_NOT_RUNTIME = {'P01': 'Chunky', 'P13': 'WorldEdit'}
REQUIRED = {'P03': 'EssentialsX', 'P05': 'EssentialsXChat',
            'P07': 'EssentialsXSpawn', 'P08': 'LuckPerms', 'P15*': 'CoreProtect'}


def check(decisions, properties):
    block = decisions.split('## Pluginurile arhivei vechi;', 1)[1]
    rows = re.findall(r'^\| (P\d\d\*?) \| ([^|]+) \| ([^|]+) \|', block, re.M)
    found = {id: (name.strip(), state.strip()) for id, name, state in rows}
    if len(rows) != len(found) or len(rows) != 15:
        raise ValueError('expected 15 distinct plugin decisions (14 historical plus CoreProtect)')
    for id, name in NO_PREVENTION.items():
        if found.get(id) != (name, 'SCOS'):
            raise ValueError(f'{name} would restrict the open city')
    for id, name in TOOLS_NOT_RUNTIME.items():
        if found.get(id) != (name, 'SCOS din runtime normal'):
            raise ValueError(f'{name} must be absent in normal runtime')
    for id, name in REQUIRED.items():
        if not found.get(id, ('', ''))[0] == name or not found[id][1].startswith('PĂSTRAT'):
            raise ValueError(f'{name} unexpectedly absent from target')
    if not re.search(r'^\| A1 \| autentificarea \*\*contului prin plugin\*\*; JAR/versiune încă nealese \|', decisions, re.M):
        raise ValueError('player account authentication via a plugin must remain explicit and unverified')
    props = re.findall(r'^spawn-protection=(\S+)$', properties, re.M)
    if props != ['0']:
        raise ValueError('repo spawn-protection must be 0; live still unverified')
    return {'static_policy_only': True,
            'protection_plugins_removed_from_target': sorted(NO_PREVENTION.values()),
            'tools_outside_normal_runtime': sorted(TOOLS_NOT_RUNTIME.values()),
            'coreprotect_required_not_present_in_historical_zip': True}


def main():
    source = Path('agent/DECIZII.md').read_text()
    props = Path('functity-config/server.properties').read_text()
    report = check(source, props)
    for id in (*NO_PREVENTION, *TOOLS_NOT_RUNTIME, *REQUIRED):
        wrong = source.replace(f'| {id} |', f'| {id}-DUP |', 1)
        try:
            check(wrong, props)
        except ValueError:
            pass
        else:
            raise AssertionError(f'fail-closed ID fixture {id}')
    try:
        check(source.replace('| A1 |', '| A1-DELETED |', 1), props)
    except ValueError:
        pass
    else:
        raise AssertionError('plugin account authentication requirement dropped')
    try:
        check(source, props.replace('spawn-protection=0', 'spawn-protection=16'))
    except ValueError:
        pass
    else:
        raise AssertionError('spawn protection drift not rejected')
    print('PASS: open-city target, plugin authentication required but not installed/tested, CoreProtect, spawn-protection=0; static only')
    return report


if __name__ == '__main__':
    sys.exit(0 if main() else 2)
