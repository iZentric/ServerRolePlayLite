#!/usr/bin/env python3
"""Read-only, privacy-preserving aggregate of the pathless historical config snapshot.

Every archived entry is counted and CRC-checked. Only an explicit whitelist of
numeric/boolean *server* settings is summarized, never raw plugin/player files.
A basename-only ZIP cannot establish which reference server a setting belongs to.
"""
import base64
from collections import Counter, defaultdict
import io
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WHITELIST = {
    'server.properties': {'view-distance', 'network-compression-threshold',
                          'entity-broadcast-range-percentage', 'max-players',
                          'spawn-protection', 'online-mode', 'sync-chunk-writes'},
    'bukkit.yml': {'monsters', 'animals', 'water-animals'},
    'spigot.yml': {'nerf-spawner-mobs', 'item-despawn-rate', 'mob-spawn-range'},
}
OPT_CONFIGS = ('aiimprovements-common.toml', 'ferritecore-mixin.toml',
               'modernfix-mixins.properties', 'performant-common.toml',
               'smoothchunk-common.toml', 'fastbench.cfg',
               'connectivity-common.toml', 'voicechat-server.toml')
REPORT = re.compile(r'^==== (.*?) \((\d+) B\) ====$', re.M)
LINE = re.compile(r'^\s*([a-z][a-z0-9_-]+)\s*[:=]\s*(-?\d+|true|false)\s*(?:#.*)?$', re.I)


def scan(blob, report):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        infos = z.infolist()
        if (len(infos) > 20_000 or sum(i.file_size for i in infos) > 100_000_000 or
                any(i.file_size > 1_000_000 for i in infos)):
            raise ValueError('snapshot exceeds safe read-only limits')
        if z.testzip() is not None:
            raise ValueError('corrupt entry in snapshot')
        names = Counter(i.filename for i in infos)
        if any(i.is_dir() for i in infos):
            raise ValueError('unexpected directory entry')
        values = defaultdict(Counter)
        for info in infos:
            if info.filename not in WHITELIST:
                continue
            for line in z.read(info).decode('utf-8', 'replace').splitlines():
                match = LINE.fullmatch(line)
                if match and match[1] in WHITELIST[info.filename]:
                    values[info.filename + ':' + match[1]][match[2].lower()] += 1
    paths = REPORT.findall(report)
    provenance = Counter()
    for path, _ in paths:
        if path.startswith('cuantic\\'):
            provenance['cuantic'] += 1
        elif path.startswith('servere referinta\\HYPECITY BK vechi nostalgic pentru cei de pe mooncraft\\'):
            provenance['HYPECITY BK'] += 1
        else:
            provenance['other'] += 1
    return {
        'scope': 'historical selected files only; no live config, paths lost in ZIP; NOT a per-server audit',
        'archived_entries_crc_checked': len(infos),
        'total_uncompressed_bytes': sum(i.file_size for i in infos),
        'unique_basenames': len(names),
        'duplicate_basename_entries': len(infos) - len(names),
        'empty_entries': sum(i.file_size == 0 for i in infos),
        'extension_counts': dict(Counter(Path(i.filename).suffix.lower() for i in infos)),
        'report_entries_with_paths': len(paths),
        'report_path_counts': dict(provenance),
        'config_name_counts': {k: names[k] for k in (*WHITELIST, *OPT_CONFIGS)},
        'safe_value_distributions_without_provenance': {k: dict(v) for k, v in sorted(values.items())},
    }


def main():
    folder = ROOT / 'diag'
    meta = (folder / 'oldcfg-meta.txt').read_text()
    sizes = dict(re.findall(r'(zip|b64|parts)=(\d+)', meta))
    if not all(k in sizes for k in ('zip', 'b64', 'parts')) or int(sizes['parts']) > 50:
        raise ValueError('invalid snapshot metadata')
    joined = ''.join((folder / f'oc_part{i}.txt').read_text().strip()
                     for i in range(int(sizes['parts'])))
    if len(joined) != int(sizes['b64']):
        raise ValueError('fragment size mismatch')
    blob = base64.b64decode(joined, validate=True)
    if len(blob) != int(sizes['zip']):
        raise ValueError('ZIP size mismatch')
    result = scan(blob, (folder / 'oldcfg-report.txt').read_text(errors='replace'))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        sys.exit(2)
