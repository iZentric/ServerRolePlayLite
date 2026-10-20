#!/usr/bin/env python3
"""Static target consistency; never reads Prism, installs mods or benchmarks FPS."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = json.loads((ROOT/'agent'/'LOW-SPEC-TINTA.json').read_text(encoding='utf-8'))
assert p['status'] == 'REFERINTA_ISTORICA_NU_TINTA_FINALA'
assert (p['minecraft'], p['forge']) == ('1.16.5', '36.2.42')
content = p['client_content_and_dependencies']
extras = p['client_optimization_and_compatibility']
excluded = p['absent_versus_historical_funcity_only']
assert (len(content), len(extras), len(excluded)) == (15, 6, 4)
assert len(set(content + extras + excluded)) == 25
assert 'Dynamic FPS' not in ' '.join(content + extras)
# This verifies consistency with the *historical FunCity* capture, not Freeroam.
captures = [line.removeprefix('lista: ').split(', ') for line in
            (ROOT/'diag'/'pc-client.txt').read_text(encoding='utf-8').splitlines()
            if line.startswith('lista: ')]
assert len(captures) == 2 and set(captures[0]) == set(captures[1])
assert set(captures[0]) == set(content + extras + excluded)
assert all('Freeroam' in line for line in (p['source_scope'], p['constraints'][0]))
assert p['settings_for_test']['render_distance_chunks'] == 5
print('PASS: historical 21-name LowSpec inventory matches FunCity capture only; NOT final Freeroam pack')
