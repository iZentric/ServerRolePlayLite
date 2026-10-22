#!/usr/bin/env python3
"""Read-only metadata audit of the already-published funcity server ZIP.

Do not extract to disk, run, upload, or repackage any entry. A bounded nested
ZIP may be read into memory to inspect its directory only; never open its files.
Output counts plus missing names only from the already-public 28-mod manifest.
A clean ZIP directory is NOT proof of a release.
"""
import argparse
import hashlib
import io
import json
import re
import stat
import zipfile
from pathlib import Path
from pathlib import PurePosixPath

HISTORIC_SHA256 = '0752393616e898ede7f1b68f3bb2c68c063235581eca4af6b6d9d02d3cfbb289'
SENSITIVE_DIRS = {'playerdata', 'stats', 'advancements', 'logs', 'crash-reports',
                  'accounts', 'userdata', 'saves', 'backups', 'backup', 'usercache'}
SENSITIVE_FILES = {'ops.json', 'whitelist.json', 'banned-players.json',
                   'banned-ips.json', 'usercache.json', 'server.properties',
                   'eula.txt', 'credentials.json'}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def audit(path, expected_sha=HISTORIC_SHA256, target=None):
    """Count ZIP directory categories, optionally compare public target mod names.

    Nested ZIP directory indexes are inspected in memory with bounded input;
    no inner file content is opened, extracted, executed, or published.
    """
    expected = set()
    public_names = {}
    if target is not None:
        manifest = json.loads(Path(target).read_text(encoding='utf-8'))
        names = manifest.get('mods', [])
        if (manifest.get('schema') != 1 or len(names) != 28 or
                not all(isinstance(n, str) and n.lower().endswith('.jar') and
                        '/' not in n and '\\' not in n and
                        not any(ord(ch) < 32 for ch in n) for n in names)):
            raise ValueError('invalid public 28-mod target manifest')
        public_names = {n.casefold(): n for n in names}
        expected = set(public_names)
        if len(expected) != 28:
            raise ValueError('duplicate public mod target')
    path = Path(path)
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha):
        raise ValueError('expected SHA-256 must be a 64-character lowercase hex string')
    if path.is_symlink() or not path.is_file():
        raise ValueError('archive must be a regular file')
    if sha256(path) != expected_sha:
        raise ValueError('archive SHA-256 does not match pinned published asset')
    counts = dict(entries=0, mod_jars=0, plugin_jars=0, other_jars=0,
                  mod_jars_in_deeper_folders=0, plugin_jars_in_deeper_folders=0,
                  library_jars=0, runtime_jars=0,
                  java_runtime_entries=0, world_entries=0, sensitive_entries=0,
                  nested_archives=0, nested_archive_bytes=0, nested_archive_large=0,
                  nested_zip_inspected=0, nested_zip_skipped=0, nested_mod_jars=0,
                  nested_plugin_jars=0, target_outer_matches=0, target_nested_matches=0,
                  target_combined_matches=0, target_missing_count=0,
                  scripts=0, symlinks=0, encrypted=0,
                  unsafe_paths=0, duplicate_paths=0, uncompressed_bytes=0)
    seen = set()
    outer_matches = set()
    nested_matches = set()
    nested_zips = []
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > 100_000:
            raise ValueError('too many ZIP entries')
        for item in members:
            counts['entries'] += 1
            counts['uncompressed_bytes'] += item.file_size
            raw = item.filename.replace('\\', '/')
            segments = raw.split('/')
            parts = PurePosixPath(raw).parts
            unsafe = (not raw or raw.startswith('/') or re.match(r'^[a-zA-Z]:', raw)
                      or any(p in {'.', '..'} for p in segments) or '' in segments[:-1]
                      or (segments[-1] == '' and not item.is_dir())
                      or any(ord(ch) < 32 for ch in raw) or not parts)
            if unsafe:
                counts['unsafe_paths'] += 1
                continue
            normalized = '/'.join(parts).casefold()
            if normalized in seen:
                counts['duplicate_paths'] += 1
            seen.add(normalized)
            mode = item.external_attr >> 16
            if item.create_system == 3 and stat.S_IFMT(mode) == stat.S_IFLNK:
                counts['symlinks'] += 1
            if item.flag_bits & 0x1:
                counts['encrypted'] += 1
            if item.is_dir():
                continue
            dirs = [p.casefold() for p in parts[:-1]]
            leaf = parts[-1].casefold()
            if any(p.startswith('world') or p in SENSITIVE_DIRS for p in dirs):
                counts['world_entries'] += int(any(p.startswith('world') or p == 'saves' for p in dirs))
                counts['sensitive_entries'] += 1
            elif (leaf in SENSITIVE_FILES or any(word in leaf for word in
                    ('password', 'secret', 'token', 'credential', 'private')) or
                  leaf.endswith(('.pem', '.key', '.p12', '.log'))):
                counts['sensitive_entries'] += 1
            if leaf.endswith('.jar') and 'mods' in dirs and leaf in expected:
                outer_matches.add(leaf)
            if len(parts) >= 2 and dirs[-1] == 'mods' and leaf.endswith('.jar'):
                counts['mod_jars'] += 1
            elif len(parts) >= 2 and dirs[-1] == 'plugins' and leaf.endswith('.jar'):
                counts['plugin_jars'] += 1
            elif leaf.endswith('.jar'):
                counts['other_jars'] += 1
                if 'mods' in dirs:
                    counts['mod_jars_in_deeper_folders'] += 1
                elif 'plugins' in dirs:
                    counts['plugin_jars_in_deeper_folders'] += 1
                elif 'libraries' in dirs or 'lib' in dirs:
                    counts['library_jars'] += 1
                elif any(d in {'java', 'jre', 'jdk', 'runtime'} for d in dirs):
                    counts['runtime_jars'] += 1
            if leaf.endswith(('.zip', '.tar', '.gz', '.7z', '.rar')):
                counts['nested_archives'] += 1
                counts['nested_archive_bytes'] += item.file_size
                counts['nested_archive_large'] += int(item.file_size > 64 * 1024 * 1024)
                if leaf.endswith('.zip'):
                    nested_zips.append(item)
            if leaf.endswith(('.bat', '.ps1', '.sh', '.exe')):
                counts['scripts'] += 1
            if 'java' in dirs or 'jre' in dirs or 'jdk' in dirs:
                counts['java_runtime_entries'] += 1
        # Nested ZIP files can be backups; inspect their indexes separately, never
        # treat their JARs as validated runtime files. No inner payload is opened.
        for item in nested_zips:
            if (item.flag_bits & 1 or item.file_size > 100 * 1024 * 1024 or
                    item.compress_size == 0 or item.file_size > item.compress_size * 200):
                counts['nested_zip_skipped'] += 1
                continue
            try:
                with zipfile.ZipFile(io.BytesIO(archive.read(item))) as inner:
                    if len(inner.infolist()) > 100_000:
                        counts['nested_zip_skipped'] += 1
                        continue
                    counts['nested_zip_inspected'] += 1
                    for member in inner.infolist():
                        if member.is_dir():
                            continue
                        parts = member.filename.replace('\\', '/').split('/')
                        if (any(p in {'', '.', '..'} for p in parts) or
                                any(ord(ch) < 32 for ch in member.filename) or
                                re.match(r'^[a-zA-Z]:', parts[0]) or
                                (member.create_system == 3 and
                                 stat.S_IFMT(member.external_attr >> 16) == stat.S_IFLNK)):
                            continue
                        dirs = [p.casefold() for p in parts[:-1]]
                        leaf = parts[-1].casefold()
                        if leaf.endswith('.jar') and 'mods' in dirs:
                            counts['nested_mod_jars'] += 1
                            if leaf in expected:
                                nested_matches.add(leaf)
                        if leaf.endswith('.jar') and 'plugins' in dirs:
                            counts['nested_plugin_jars'] += 1
            except (zipfile.BadZipFile, RuntimeError, EOFError):
                counts['nested_zip_skipped'] += 1
    counts['target_outer_matches'] = len(outer_matches)
    counts['target_nested_matches'] = len(nested_matches)
    counts['target_combined_matches'] = len(outer_matches | nested_matches)
    missing = expected - (outer_matches | nested_matches)
    counts['target_missing_count'] = len(missing)
    counts['target_missing_public_names'] = sorted((public_names[n] for n in missing), key=str.casefold)
    # In particular, do not turn this into an "OK to publish" verdict.
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--expected-sha', default=HISTORIC_SHA256)
    parser.add_argument('--target', default=str(Path(__file__).resolve().parents[1] /
                                                 'agent/FUNCITY-SERVER-TARGET-28.json'))
    args = parser.parse_args()
    print('HISTORIC_SERVER_ZIP_METADATA ' + json.dumps(audit(args.archive, args.expected_sha, args.target),
                                                    sort_keys=True))
    print('NOT_A_RELEASE_GATE: names/content/rights/gameplay not audited; nothing extracted or uploaded')


if __name__ == '__main__':
    main()
