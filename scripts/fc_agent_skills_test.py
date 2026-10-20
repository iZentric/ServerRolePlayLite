#!/usr/bin/env python3
"""Static audit of six newly copied project-local Markdown skills; no execution."""
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
BASELINE = {'brainstorming', 'find-skills', 'skill-creator', 'task-observer', 'using-superpowers'}
assert LOCK['version'] == 1
assert set(LOCK['skills']) == BASELINE | set(ADDED)
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
    assert {p.name for p in folder.iterdir()} == expected_files
    for f in folder.iterdir():
        assert f.is_file() and not f.is_symlink() and not (f.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    skill = (folder/'SKILL.md').read_bytes()
    assert skill.startswith(b'---\n')
    assert f'name: {name}'.encode() in skill.split(b'---', 2)[1]
    assert hashlib.sha256(skill).hexdigest() == record['computedHash']
print('PASS: six pinned local Markdown skills, licenses and hashes; no runtime install or execution')
