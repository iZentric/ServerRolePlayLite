#!/usr/bin/env python3
"""Fail-closed *policy* gate for a future plugin-first stage; no installation.

Evidence references in an approval must still be independently verified. An empty
selection is intentional and NOT a bootable server or finished client pack.
"""
import json
from pathlib import Path
import re

POLICY = Path(__file__).resolve().parents[1] / 'agent/PLUGIN-FIRST.json'
SHA = re.compile(r'[a-f0-9]{64}\Z')


def require_jar(record, kind):
    if not isinstance(record, dict):
        raise ValueError(kind + ' approval must be an object')
    name = record.get('filename')
    if (not isinstance(name, str) or not name.endswith('.jar') or '/' in name or
            '\\' in name or '..' in name or not name.strip()):
        raise ValueError(kind + ' approval needs an exact safe JAR filename')
    if not isinstance(record.get('sha256'), str) or not SHA.fullmatch(record['sha256']):
        raise ValueError(kind + ' approval needs a pinned SHA256')
    if kind == 'owner':
        required = ('owner_confirmation', 'licence_and_distribution', 'rp_function')
    else:
        required = ('baseline_evidence', 'ab_evidence', 'measured_hotspot',
                    'no_gameplay_regression')
    if any(not isinstance(record.get(k), str) or len(record[k].strip()) < 8
           for k in required):
        raise ValueError(kind + ' approval lacks independent evidence fields')
    sides = record.get('sides')
    if not isinstance(sides, list) or not set(sides) <= {'client', 'server'} or not sides:
        raise ValueError(kind + ' approval needs explicit client/server sides')
    return name, set(sides)


def validate(policy):
    if (not isinstance(policy, dict) or policy.get('schema') != 1 or
            policy.get('release_blocked') is not True or
            not isinstance(policy.get('voice_status'), str) or
            not policy['voice_status'].startswith('unresolved:')):
        raise ValueError('plugin-first draft cannot be a release or assume working voice')
    approved = {}
    for key, kind in (('owner_content_jar_approvals', 'owner'),
                      ('measured_performance_jar_approvals', 'performance')):
        rows = policy.get(key)
        if not isinstance(rows, list):
            raise ValueError(key + ' must be a list')
        for record in rows:
            name, sides = require_jar(record, kind)
            folded = name.casefold()
            if folded in approved:
                raise ValueError('duplicate JAR approval: ' + name)
            approved[folded] = sides
    for side in ('client', 'server'):
        rows = policy.get(side + '_jar_selection')
        if not isinstance(rows, list) or any(not isinstance(n, str) for n in rows):
            raise ValueError(side + ' selection must list exact JAR names')
        if len(rows) != len({n.casefold() for n in rows}):
            raise ValueError('duplicate JAR in ' + side + ' selection')
        for name in rows:
            if name.casefold() not in approved or side not in approved[name.casefold()]:
                raise ValueError('unapproved ' + side + ' JAR: ' + name)
    return True


def main():
    validate(json.loads(POLICY.read_text(encoding='utf-8')))
    print('PASS: plugin-first whitelist has no unapproved JARs (policy only, not a boot/benchmark)')


if __name__ == '__main__':
    main()
