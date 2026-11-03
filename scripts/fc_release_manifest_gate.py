#!/usr/bin/env python3
"""Offline guard for the declared client/server inventory; never touches binaries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'agent'
original = json.loads((ROOT / 'FREEROAM-LISTA-DECLARATA.json').read_text(encoding='utf-8'))
lite = json.loads((ROOT / 'FUNCITY-RP-LITE-SELECTIE.json').read_text(encoding='utf-8'))
server = json.loads((ROOT / 'FUNCITY-SERVER-TARGET-28.json').read_text(encoding='utf-8'))

def unique(names):
    lowered = [x.casefold() for x in names]
    assert len(set(lowered)) == len(lowered), 'duplicate declared JAR name'
    assert all(x.lower().endswith('.jar') and '/' not in x and '\\' not in x for x in names)
    return set(lowered)

assert original['schema'] == lite['schema'] == server['schema'] == 1
full = unique(original['jar_names'])
excluded = unique(lite['removed_from_future_target'])
selected = unique(lite['retained_in_future_target'])
assert len(full) == 28 and len(excluded) == 6 and len(selected) == 22
assert excluded.isdisjoint(selected) and full - excluded == selected
assert lite['ready_for_release'] is False and lite['source_original_and_prism_unchanged'] is True
lab = unique(server['mods'])
assert len(lab) == 28
assert server['status'] == 'PROPOSED_CLIENT_ALIGNED_SERVER_TEST_ONLY_NOT_LIVE'
print('PASS: declared client 28 - approved exclusions 6 = Lite 22; server 28 is lab-only')
