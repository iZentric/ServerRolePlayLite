#!/usr/bin/env python3
"""Read-only metadata audit of the already-published funcity server ZIP.

Do not extract, run, upload, or repackage any entry. Output category counts only.
A clean ZIP directory is NOT proof of a safe or licensed server release.
"""
import argparse
import hashlib
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


def audit(path, expected_sha=HISTORIC_SHA256):
    path = Path(path)
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha):
        raise ValueError('expected SHA-256 must be a 64-character lowercase hex string')
    if path.is_symlink() or not path.is_file():
        raise ValueError('archive must be a regular file')
    if sha256(path) != expected_sha:
        raise ValueError('archive SHA-256 does not match pinned published asset')
    counts = dict(entries=0, mod_jars=0, plugin_jars=0, other_jars=0,
                  java_runtime_entries=0, world_entries=0, sensitive_entries=0,
                  nested_archives=0, scripts=0, symlinks=0, encrypted=0,
                  unsafe_paths=0, duplicate_paths=0, uncompressed_bytes=0)
    seen = set()
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
            if len(parts) >= 2 and dirs[-1] == 'mods' and leaf.endswith('.jar'):
                counts['mod_jars'] += 1
            elif len(parts) >= 2 and dirs[-1] == 'plugins' and leaf.endswith('.jar'):
                counts['plugin_jars'] += 1
            elif leaf.endswith('.jar'):
                counts['other_jars'] += 1
            if leaf.endswith(('.zip', '.tar', '.gz', '.7z', '.rar')):
                counts['nested_archives'] += 1
            if leaf.endswith(('.bat', '.ps1', '.sh', '.exe')):
                counts['scripts'] += 1
            if 'java' in dirs or 'jre' in dirs or 'jdk' in dirs:
                counts['java_runtime_entries'] += 1
    # In particular, do not turn this into an "OK to publish" verdict.
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--expected-sha', default=HISTORIC_SHA256)
    args = parser.parse_args()
    print('HISTORIC_SERVER_ZIP_METADATA ' + json.dumps(audit(args.archive, args.expected_sha),
                                                    sort_keys=True))
    print('NOT_A_RELEASE_GATE: names/content/rights/gameplay not audited; nothing extracted or uploaded')


if __name__ == '__main__':
    main()
