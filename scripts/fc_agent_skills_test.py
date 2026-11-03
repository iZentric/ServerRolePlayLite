#!/usr/bin/env python3
"""Static audit of pinned project-local skills; no execution."""
import hashlib
import json
import re
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = json.loads((ROOT/'skills-lock.json').read_text(encoding='utf-8'))
ADDED = {
    'verification-before-completion': ('obra/superpowers', 'skills/verification-before-completion/SKILL.md'),
    'systematic-debugging': ('obra/superpowers', 'skills/systematic-debugging/SKILL.md'),
    'writing-for-agents': ('mattpocock/skills', 'skills/productivity/writing-for-agents/SKILL.md'),
    'change-impact': ('affaan-m/ECC', 'skills/change-impact/SKILL.md'),
    'ponytail-review': ('DietrichGebert/ponytail', 'skills/ponytail-review/SKILL.md'),
    'frontend-design': ('anthropics/skills', 'skills/frontend-design/SKILL.md'),
}
SUPERPOWERS = {
    'brainstorming', 'diagnosing-superpowers', 'dispatching-parallel-agents',
    'executing-plans', 'finishing-a-development-branch', 'receiving-code-review',
    'requesting-code-review', 'subagent-driven-development', 'systematic-debugging',
    'test-driven-development', 'using-git-worktrees', 'using-superpowers',
    'verification-before-completion', 'writing-plans', 'writing-skills',
}
OTHERS = {'find-skills', 'skill-creator', 'task-observer', 'writing-for-agents',
          'change-impact', 'ponytail-review', 'frontend-design'}
assert LOCK['version'] == 1
assert set(LOCK['skills']) == SUPERPOWERS | OTHERS
assert {p.name for p in (ROOT/'.agents/skills').iterdir() if p.is_dir()} == set(LOCK['skills'])
for name, (repo, source_path) in ADDED.items():
    record = LOCK['skills'][name]
    assert record['source'] == repo and record['sourceType'] == 'github'
    assert record['skillPath'] == source_path
    assert re.fullmatch(r'[0-9a-f]{40}', record['sourceCommit'])
    folder = ROOT/'.agents/skills'/name
    expected_files = {'SKILL.md'}
    if name == 'writing-for-agents':
        expected_files.add('SKILL-MECHANICS.md')
        extra = (folder/'SKILL-MECHANICS.md').read_bytes()
        assert hashlib.sha256(extra).hexdigest() == record['supplementaryFiles']['SKILL-MECHANICS.md']
    if repo != 'obra/superpowers':
        expected_files.add('LICENSE.txt')
        assert (folder/'LICENSE.txt').read_text(encoding='utf-8').lstrip().startswith(('MIT License', 'Apache License'))
        assert record['licensePath'] == str((folder/'LICENSE.txt').relative_to(ROOT))
    else:
        assert record['licensePath'] == 'agent/SKILLURI-LICENSES.txt'
        assert 'obra/superpowers' in (ROOT/record['licensePath']).read_text(encoding='utf-8')
    if name != 'systematic-debugging':
        assert {p.name for p in folder.iterdir()} == expected_files
    for f in folder.iterdir():
        assert f.is_file() and not f.is_symlink()
        if name != 'systematic-debugging':
            assert not (f.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    skill = (folder/'SKILL.md').read_bytes()
    assert skill.startswith(b'---\n')
    assert f'name: {name}'.encode() in skill.split(b'---', 2)[1]
    assert hashlib.sha256(skill).hexdigest() == record['computedHash']
for name in sorted(SUPERPOWERS):
    folder = ROOT/'.agents/skills'/name
    record = LOCK['skills'][name]
    assert record['source'] == 'obra/superpowers' and record['sourceType'] == 'github'
    assert record['sourceCommit'] == '2ce8aa15d05bd57213e6f746f953aafb7ded7a8b'
    assert record['skillPath'] == f'skills/{name}/SKILL.md'
    assert record['licensePath'] == 'agent/SKILLURI-LICENSES.txt'
    assert (folder/'SKILL.md').read_bytes().startswith(b'---\n')
    assert hashlib.sha256((folder/'SKILL.md').read_bytes()).hexdigest() == record['computedHash']
    digest = hashlib.sha256()
    for f in sorted(folder.rglob('*')):
        assert not f.is_symlink()
        if f.is_file():
            digest.update(f.relative_to(folder).as_posix().encode('utf-8') + b'\0')
            digest.update(f.read_bytes() + b'\0')
    assert digest.hexdigest() == record['treeHash'], name

find = LOCK['skills']['find-skills']
assert find['source'] == 'vercel-labs/skills'
assert find['sourceCommit'] == 'a80e4c9d12d607631249d4d7d059f835d4b2f13a'
assert find['licensePath'] == 'agent/SKILLURI-LICENSES.txt'
assert hashlib.sha256((ROOT/'.agents/skills/find-skills/SKILL.md').read_bytes()).hexdigest() == find['computedHash']
licenses = (ROOT/'agent/SKILLURI-LICENSES.txt').read_text(encoding='utf-8')
assert 'Copyright (c) 2026 Vercel, Inc.' in licenses
assert 'Copyright (c) 2025 Jesse Vincent' in licenses
print('PASS: 15 pinned superpowers skills (complete trees), pinned find-skills, existing 5 other skills; no remote code executed')
