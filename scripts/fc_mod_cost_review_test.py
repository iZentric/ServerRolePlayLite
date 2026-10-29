#!/usr/bin/env python3
"""Verify every chosen Lite mod has exactly one cost/role review (static only)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r'^\| ([CS]\d\d) \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS(?: din runtime normal)?) \|', re.M)
REVIEW_ROW = re.compile(r'^\| `([^`]+\.jar)` \|', re.M)


def check(decisions, review):
    client_block = decisions.split('## Client —', 1)[1].split('## Server —', 1)[0]
    server_block = decisions.split('## Server —', 1)[1].split('## Pluginurile', 1)[0]
    client = {name for _, name, state in ROW.findall(client_block) if state == 'PĂSTRAT'}
    server = {name for _, name, state in ROW.findall(server_block) if state == 'PĂSTRAT'}
    if len(client) != 24 or len(server) != 29 or len(client & server) != 20:
        raise ValueError('decision inventory drift (24 client / 29 server / 20 shared)')
    rows = REVIEW_ROW.findall(review.split('## Ce am scos deja', 1)[0])
    expected = client | server
    if len(rows) != 33 or len(set(rows)) != 33 or set(rows) != expected:
        raise ValueError('cost review must list each chosen mod exactly once (20+4+9)')
    return True


def main():
    decisions = (ROOT / 'agent/DECIZII.md').read_text(encoding='utf-8')
    review = (ROOT / 'agent/AUDIT-COST-MODURI.md').read_text(encoding='utf-8')
    assert check(decisions, review)
    first = REVIEW_ROW.findall(review)[0]
    try:
        check(decisions, review.replace(f'| `{first}` |', '| `not-in-pack.jar` |', 1))
    except ValueError:
        pass
    else:
        raise AssertionError('unknown mod in review not rejected')
    try:
        check(decisions, review.replace(f'| `{first}` |', '', 1))
    except ValueError:
        pass
    else:
        raise AssertionError('missing mod in review not rejected')
    print('PASS: 24 client + 29 server (20 shared); 33 exact cost/role rows, static only')


if __name__ == '__main__':
    main()
