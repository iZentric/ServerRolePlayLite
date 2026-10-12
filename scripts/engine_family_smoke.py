#!/usr/bin/env python3
"""Run compatibility gate for hybrid server JARs with the IDENTICAL CUANTIC pack.

All processes are isolated on GitHub-hosted runner. No live server access.
A successful smoke is NOT modded login, vehicle gameplay or speed superiority.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile
from engine_lab import smoke
import engine_lab

JAR = 'CatServer-1.16.5-1d8d6313-server.jar'
REQUIRED_PLUGINS = {
    'LuckPerms', 'Vault', 'ProtocolLib', 'WorldEdit', 'Chunky', 'Cuantic-Brand',
    'SkinsRestorer', 'Essentials', 'EssentialsChat', 'EssentialsAntiBuild',
    'EssentialsSpawn', 'WorldGuard', 'ClaimChunk', 'EssentialsProtect',
}


def inventory(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith('.jar')]
        items = {n: hashlib.sha256(z.read(n)).hexdigest() for n in names
                 if n.startswith(('mods/', 'plugins/')) and n.count('/') == 1}
        roots = [n for n in names if '/' not in n]
    return items, roots


def main(root, report):
    report.mkdir(parents=True, exist_ok=True)
    pack = root / 'CUANTIC-Server-CatServer-1.7.7.zip'
    inventory_live, roots = inventory(pack)
    mods = {k: v for k, v in inventory_live.items() if k.startswith('mods/')}
    plugins = {k: v for k, v in inventory_live.items() if k.startswith('plugins/')}
    if len(mods) != 36 or len(plugins) != 14 or JAR not in roots:
        raise ValueError(f'baseline archive differs from expected 36/14 pack: {len(mods)}/{len(plugins)} {roots}')
    output = {
        'method': 'same exact 36 mod + 14 plugin JAR files and same configs/seed; one isolated smoke per hybrid JAR; no production access',
        'limits': 'no modded-client login, vehicle gameplay, player load or A/B performance result; successful boot alone is not an upgrade',
        'baseline_zip': pack.name,
        'baseline_jar_sha256': None,
        'inventory_sha256': hashlib.sha256(json.dumps(inventory_live, sort_keys=True).encode()).hexdigest(),
        'candidates': {},
    }
    with zipfile.ZipFile(pack) as z:
        output['baseline_jar_sha256'] = hashlib.sha256(z.read(JAR)).hexdigest()
    mapping = [
        ('live-CatServer', None, None),
        ('own-ticket-JAR', root / 'CUANTIC-CatServer-ticket-experimental.jar', None),
        ('Arclight', root / 'CUANTIC-Server-Arclight-1.7.7.zip', 'arclight'),
        ('Mist', root / 'CUANTIC-Server-Mist-EXPERIMENTAL-1.7.7.zip', 'mist'),
    ]
    engine_lab.BOOT_TIMEOUT = 180
    only = set(filter(None, os.environ.get('ENGINE_FAMILY_ONLY', '').split(',')))
    for label, source, hint in mapping:
        if only and label not in only:
            continue
        row = {'same_mod_plugin_payload_sha256': True, 'smoke': None, 'candidate_pack_inventory': None}
        output['candidates'][label] = row
        try:
            dest = report / label
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(pack) as z:
                z.extractall(dest)
            if hint:
                inv, names = inventory(source)
                row['candidate_pack_inventory'] = {
                    'mods': sum(n.startswith('mods/') for n in inv),
                    'plugins': sum(n.startswith('plugins/') for n in inv),
                    'identical_to_baseline': inv == inventory_live,
                    'differences': sorted(n for n in set(inv) | set(inventory_live)
                                          if inv.get(n) != inventory_live.get(n))[:30],
                    'root_jars': names,
                }
                available = [n for n in names if hint.lower() in n.lower()]
                if len(available) != 1:
                    raise ValueError(f'{label}: expected exactly one {hint} engine in release ZIP, got {names}')
                with zipfile.ZipFile(source) as z:
                    (dest / JAR).write_bytes(z.read(available[0]))
                row['source_engine'] = available[0]
            elif source is not None:
                shutil.copyfile(source, dest / JAR)
            row['jar_sha256'] = hashlib.sha256((dest / JAR).read_bytes()).hexdigest()
            # Strict: an isolated smoke cannot run against altered assets.
            inv_dir = {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for section in ('mods', 'plugins') for p in (dest / section).glob('*.jar')}
            if inv_dir != inventory_live:
                raise ValueError(f'{label}: mod/plugin mismatch on disk')
            smoke_log = report / (label + '-smoke') / 'smoke.log'
            ok = smoke(dest, smoke_log)
            result = json.loads((smoke_log.parent / 'smoke-result.json').read_text())
            row['smoke'] = result
            row['required_plugins_enabled'] = sorted(REQUIRED_PLUGINS - set(result['plugin_names'])) == []
            row['qualified_for_performance_A_B'] = bool(ok and row['required_plugins_enabled'])
            # Short diagnostic excerpts, not full log, user or world data.
            if not row['qualified_for_performance_A_B']:
                text = smoke_log.read_text(errors='replace')
                row['diagnostic_key_lines'] = [line[-360:] for line in text.splitlines()
                    if re.search(r'Caused by:|Exception in thread|IllegalAccessError|MixinApplyError|InjectionError|InvalidInjection|failed injection|critical injection|Fail to launch|Mod loading error|NoClassDefFoundError|UnsupportedClassVersion', line, re.I)][:25]
                row['diagnostic_tail'] = text[-1800:]
        except Exception as e:
            row['error'] = f'{type(e).__name__}: {e}'
        finally:
            (report / 'result.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
            print(f'{label}: {json.dumps(row, ensure_ascii=False)[:500]}', flush=True)
    return output


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: engine_family_smoke.py <release-and-artifact-dir> <report-dir>')
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
