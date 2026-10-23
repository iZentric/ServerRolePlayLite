#!/usr/bin/env python3
"""Stage ONLY the 29 chosen server mod JARs from a pinned historical ZIP.

Local, isolated candidate only: no plugins, configs, worlds, engine, install,
client, or release are copied. The ZIP is never unpacked onto a server. It does
NOT prove the archived mods match a running HYPECITY or FunCity instance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile

from fc_lite_repack import selection as client_selection

HISTORICAL_SHA256 = 'fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15'
ROWS = re.compile(r'^\| (S\d\d) \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS(?: din runtime normal)?) \|', re.M)
MAX_JAR_BYTES = 350_000_000
MAX_TOTAL_BYTES = 1_000_000_000


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def decisions(path, client_decisions, historical, voice_metadata):
    text = Path(path).read_text(encoding='utf-8')
    block = text.split('## Server —', 1)[1].split('## Pluginurile', 1)[0]
    rows = ROWS.findall(block)
    if len(rows) != 36 or len({id for id, _, _ in rows}) != 36:
        raise ValueError('expected 36 distinct historical server mod decisions')
    names = [name for _, name, _ in rows]
    if len({n.casefold() for n in names}) != 36:
        raise ValueError('duplicate server JAR name')
    keep = {name.casefold() for _, name, state in rows if state == 'PĂSTRAT'}
    removed = {name.casefold() for _, name, state in rows if state != 'PĂSTRAT'}
    if len(keep) != 29 or len(removed) != 7:
        raise ValueError('expected 29 kept and 7 excluded server mods')
    client, _, voice = client_selection(client_decisions, historical, voice_metadata)
    if client_decisions != path:
        raise ValueError('client and server decisions must be in the same file')
    if len(keep & client) != 20 or len(keep - client) != 9 or len(client - keep) != 4:
        raise ValueError('client/server selection mismatch: expected 20 shared, 9 server-only, 4 client-only')
    if voice['filename'].casefold() not in keep & client:
        raise ValueError('voice is required on client and server')
    return {name.casefold(): name for name in names}, keep, removed


def stage(source, expected_sha256, destination, decisions_path, historical,
          voice_metadata=Path('agent/voicechat-1.16.5-2.3.23.json'),
          without_pizzaland=False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError('destination must be new and distinct from source')
    if not re.fullmatch('[a-f0-9]{64}', expected_sha256) or digest(source) != expected_sha256:
        raise ValueError('server source SHA256 mismatch; no output written')
    names, keep, removed = decisions(decisions_path, decisions_path, historical, voice_metadata)
    keep, removed = set(keep), set(removed)
    if without_pizzaland:
        optional = 'pizzaland_v68.jar'
        if optional not in keep:
            raise ValueError('Pizzaland missing from baseline selection')
        keep.remove(optional)
        removed.add(optional)
    target_count = 28 if without_pizzaland else 29
    with zipfile.ZipFile(source) as archive:
        matches = []
        for item in archive.infolist():
            parts = item.filename.split('/')
            if (len(parts) >= 2 and parts[-2].casefold() == 'mods' and
                    parts[-1].casefold().endswith('.jar')):
                matches.append(item)
        actual = [item.filename.split('/')[-1].casefold() for item in matches]
        if len(matches) != 36 or set(actual) != set(names) or len(set(actual)) != 36:
            raise ValueError('historical 36-mod inventory missing, duplicated or changed')
        if (any(item.is_dir() or item.file_size > MAX_JAR_BYTES or
                (item.external_attr >> 16) & 0o170000 == 0o120000 for item in matches) or
                sum(item.file_size for item in matches) > MAX_TOTAL_BYTES):
            raise ValueError('server mod is a symlink, directory, or exceeds size cap')
        chosen = {item.filename.split('/')[-1].casefold(): item for item in matches}
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(prefix='.fc-server-lite-', suffix='.zip',
                                             dir=destination.parent, delete=False) as f:
                tmp = Path(f.name)
            jar_digests = {}
            with zipfile.ZipFile(tmp, 'w', allowZip64=True) as output:
                for name in sorted(keep):
                    info = zipfile.ZipInfo('mods/' + names[name], (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_STORED  # JARs are already ZIP files
                    info.external_attr = 0o100644 << 16
                    h = hashlib.sha256()
                    with archive.open(chosen[name]) as src, output.open(info, 'w') as dst:
                        for data in iter(lambda: src.read(1024 * 1024), b''):
                            h.update(data)
                            dst.write(data)
                    jar_digests[names[name]] = h.hexdigest()
            with zipfile.ZipFile(tmp) as output:
                if {i.filename for i in output.infolist()} != {
                        'mods/' + names[n] for n in keep} or len(output.infolist()) != target_count:
                    raise ValueError('output differs from selected mods')
                if output.testzip() is not None:
                    raise ValueError('output CRC failure')
            result = {'scope': 'isolated server mods-only ZIP, NOT an installed/booted server',
                      'source_sha256': expected_sha256, 'candidate_sha256': digest(tmp),
                      'candidate_bytes': tmp.stat().st_size, 'server_mod_count': target_count,
                      'shared_client_server_names': 19 if without_pizzaland else 20,
                      'server_only': 9, 'client_only': 4,
                      'removed': sorted(names[n] for n in removed),
                      'kept_sha256': jar_digests}
            tmp.rename(destination)
            return result
        finally:
            if tmp is not None and tmp.exists():
                tmp.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path, help='pinned CUANTIC 1.7.7 historical ZIP; NOT HYPECITY')
    p.add_argument('--output', required=True, type=Path, help='new local mods-only ZIP; never deploy automatically')
    p.add_argument('--source-sha256', default=HISTORICAL_SHA256)
    p.add_argument('--decisions', type=Path, default=Path('agent/DECIZII.md'))
    p.add_argument('--historical-client', type=Path, default=Path('diag/pc-client.txt'))
    p.add_argument('--without-pizzaland', action='store_true',
                   help='isolated 28-mod comparison only; never touches a server or world')
    p.add_argument('--voice-metadata', type=Path, default=Path('agent/voicechat-1.16.5-2.3.23.json'))
    a = p.parse_args()
    try:
        report = stage(a.source, a.source_sha256, a.output, a.decisions,
                       a.historical_client, a.voice_metadata,
                       without_pizzaland=a.without_pizzaland)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, IndexError, TypeError, zipfile.BadZipFile,
            json.JSONDecodeError) as exc:
        print(f'RESPINS: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
