#!/usr/bin/env python3
"""Fail closed on stale home-page claims and unpublished-document links.

Purely static public-copy checks; not a PC, Minecraft or Pages deployment test.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
site = (ROOT/'site/template.html').read_text(encoding='utf-8')
generated = (ROOT/'site/index.html').read_text(encoding='utf-8')
readme = (ROOT/'README.md').read_text(encoding='utf-8')
start = (ROOT/'START-AICI.md').read_text(encoding='utf-8')
assert site == generated, 'site/index.html must be generated from site/template.html'

for name, content in (('site', site), ('README', readme)):
    for fragment in ('Freeroam 1.0.0', '22', '28', '34', '13', '2 CPU', '12 GB',
                     'CatServer oficial', 'RoadRunner', 'ModernFix', 'FerriteCore',
                     'agent/INDEX-GITHUB-FUNCITY-2026.md', 'ServerRolePlayLite/pull/2'):
        assert fragment in content, f'{name}: missing present-day claim/link: {fragment}'
    for stale in ('FunCity b1.0827 este motorul de laborator',
                  'FunCity b1.0827 rămâne motorul pentru copia de test',
                  'Conținutul primului pack este în candidatul Lite'):
        assert stale not in content, f'{name}: obsolete or unsupported claim: {stale}'

assert 'originalul cu 28 este intact' in site or 'Freeroam 1.0.0 rămâne neatins' in site
assert 'original' in readme and 'neatins' in readme
assert 'maxim' in site and 'necunoscut' in site
assert ('PR-ul nu e îmbinat' in readme or 'PR-ul nu este îmbinat' in readme) and 'Pages' in readme
assert 'nu sunt încă disponibile' in site or 'server nou deschis pentru jucători' in site
assert 'agent/CONTROL-MODURI-ORIGINALE.md' in site
assert 'agent/CONTROL-MODURI-ORIGINALE.md' in readme
assert 'originalul Freeroam 1.0.0 (28 de nume)' in start
assert 'FunCity RP Lite separat (22 JAR-uri)' in start
assert 'FunCity RP Lite = toate cele 28 de JAR-uri' not in start

# Local README links and branch-blob links embedded in the static site should
# resolve in this checkout. Page deployment still requires a separate decision.
for match in re.findall(r'\]\(([^)]+)\)', readme):
    if not match.startswith(('http:', 'https:', '#', 'mailto:')):
        assert (ROOT/match.split('#', 1)[0]).is_file(), f'broken README link: {match}'
branch_prefix = ('https://github.com/iZentric/ServerRolePlayLite/blob/'
                 'arena/9bbcb24f-serverroleplaylite/')
for match in re.findall(r'href="([^"]+)"', site):
    if match.startswith(branch_prefix):
        assert (ROOT/match.removeprefix(branch_prefix).split('#', 1)[0]).is_file(), (
            f'broken site branch link: {match}')
print('PASS: generated static page, current RP/host/PR status, source links, no fake live capacity')
