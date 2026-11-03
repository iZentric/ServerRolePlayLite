#!/usr/bin/env python3
"""Rank private JFR execution samples on Minecraft's main server thread.

Reads only a LOCAL JSON export of jdk.ExecutionSample; never uploads a profile.
A sample count is not a player-capacity result or proof of wall-time savings.
"""
import json
from collections import Counter
from pathlib import Path
import re
import sys


class ProfileRejected(ValueError):
    pass


def summarize(data, minimum=100, thread='Server thread'):
    if thread not in ('Server thread', 'netty'):
        raise ProfileRejected('unsupported thread group')
    try:
        events = data['recording']['events']
    except (KeyError, TypeError) as exc:
        raise ProfileRejected('JFR recording events missing') from exc
    if not isinstance(events, list):
        raise ProfileRejected('invalid JFR event list')
    counts = Counter()
    for event in events:
        if not isinstance(event, dict) or event.get('type') != 'jdk.ExecutionSample':
            continue
        values = event.get('values')
        if not isinstance(values, dict):
            raise ProfileRejected('invalid execution sample')
        sampled = values.get('sampledThread')
        name = sampled.get('javaName') if isinstance(sampled, dict) else None
        if not isinstance(name, str) or not (name.startswith('Netty ') if thread == 'netty'
                                               else name == thread):
            continue
        try:
            method = values['stackTrace']['frames'][0]['method']
            owner, function = method['type']['name'], method['name']
        except (KeyError, IndexError, TypeError) as exc:
            raise ProfileRejected('selected thread sample without Java top frame') from exc
        if (not isinstance(owner, str) or not isinstance(function, str)
                or not owner or not function or len(owner) + len(function) > 249
                or not re.fullmatch(r'[A-Za-z0-9_$./<>-]+', owner)
                or not re.fullmatch(r'[A-Za-z0-9_$./<>-]+', function)):
            raise ProfileRejected('invalid Java frame identifier')
        name = owner + '.' + function
        counts[name] += 1
    total = counts.total()
    if minimum < 1 or total < minimum:
        raise ProfileRejected(f'fewer than {minimum} {thread} CPU samples; profile longer under load')
    return total, counts.most_common()


def main(path):
    raw = Path(path).absolute()
    repo = Path(__file__).resolve().parents[1]
    if raw.is_symlink() or raw.resolve().is_relative_to(repo) or not raw.is_file():
        raise ProfileRejected('require a private profile file outside the repository')
    if raw.stat().st_size > 64 * 1024 * 1024:
        raise ProfileRejected('JSON export exceeds 64 MiB; capture a shorter interval')
    with raw.open(encoding='utf-8') as source:
        recording = json.load(source)
    for thread in ('Server thread', 'netty'):
        try:
            total, ranking = summarize(recording, thread=thread)
        except ProfileRejected as exc:
            if thread == 'Server thread' or not str(exc).startswith('fewer than'):
                raise
            print('Netty CPU samples <100; capture longer during real packet traffic.')
            continue
        print(f'{thread} execution samples: {total}; top Java frames (not wall time):')
        for name, count in ranking[:12]:
            print(f'{100 * count / total:5.1f}%  {count:5d}  {name}')
    print('PRIVATE diagnostic only; no real-player capacity or engine winner inferred.')


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ProfileRejected('usage: python3 scripts/fc_funcity_jfr_hotspots.py PRIVATE_JFR_JSON')
        main(sys.argv[1])
    except (ProfileRejected, OSError, json.JSONDecodeError) as exc:
        print(f'Profile rejected: {exc}', file=sys.stderr)
        sys.exit(2)
