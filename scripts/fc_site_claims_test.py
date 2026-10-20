#!/usr/bin/env python3
"""Guard public copy against claiming unverified Freeroam → LowSpec parity.

This checks wording in repository files; it is not a Minecraft or PC inventory test.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
site = (ROOT / 'site' / 'template.html').read_text(encoding='utf-8')
generated = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
readme = (ROOT / 'README.md').read_text(encoding='utf-8')
assert site == generated, 'regenerate site/index.html from site/template.html'
for name, content in (('site', site), ('README', readme)):
    assert 'Freeroam 1.0.0' in content, f'{name}: original pack not named'
    assert 'agent/CONTROL-MODURI-ORIGINALE.md' in content, f'{name}: missing audit source'
    assert 'Conținutul primului pack este în candidatul Lite' not in content, f'{name}: unsupported original parity'
assert '28 de nume JAR' in site and 'confirmate prin inventar PC read-only' in site
assert 'șase nume sunt excluse numai din planul Lite, 22 rămân' in site
assert 'biblioteca sa TRansliterationLib sunt scoase împreună' in site
assert 'Niciun profil nu a fost schimbat' in site
assert 'Freeroam → LowSpec' in readme
print('PASS: site generated from template; Freeroam original and unverified parity disclosed')
