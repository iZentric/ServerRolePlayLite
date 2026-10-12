#!/usr/bin/env python3
"""Generic isolated ABBA comparison for two Forge+Bukkit 1.16.5 engines.

No player login, real-world claims, or automatic promotion. The caller must
first gate both JARs with all 36 mods and 14 plugins on the same Java version.
"""
import hashlib
import json
from pathlib import Path
import statistics
import sys
from engine_ab import JAR, prepare, run


def main(pack, other_jar, label, output):
    output.mkdir(parents=True, exist_ok=True)
    result = {
        'method': f'A/B/B/A on same GitHub VM and Java version: live CatServer vs {label}, original pack + 256 FILLED hoppers + 40 zombies',
        'limits': '2 samples per arm; zero players, no vehicles, modded login, production world or live deployment; observed boot/CPU/p95 are not universal speed rankings',
        'candidate_name': label,
    }
    for name, jar in [('live-A1', None), ('candidate-B1', other_jar),
                      ('candidate-B2', other_jar), ('live-A2', None)]:
        dest = output / name
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        arm = run(name, dest, output, hopper_workload=True)
        arm['jar_sha256'] = hashlib.sha256((dest / JAR).read_bytes()).hexdigest()
        result[name] = arm
        print(json.dumps(arm, ensure_ascii=False, indent=2), flush=True)
        if not arm['valid']:
            result['verdict'] = 'INCOMPLETE: pack or workload did not pass verification; no promotion'
            break
    if 'verdict' not in result:
        def median(arms, get):
            return round(statistics.median(get(result[arm]) for arm in arms), 3)
        result['summary'] = {
            key: {
                'p95_ms': median(arms, lambda x: x['spark_tick_min_median_p95_max_ms_1m'][2]),
                'cpu_s': median(arms, lambda x: x['cpu_seconds_during_command_and_warmup']),
                'rss_mb': median(arms, lambda x: x['rss_median_mb']),
            } for key, arms in [('live', ('live-A1', 'live-A2')),
                               ('candidate', ('candidate-B1', 'candidate-B2'))]
        }
        a, b = result['summary']['live'], result['summary']['candidate']
        result['verdict'] = ('better CPU and p95 only in this synthetic test; still NOT validated for production' if
                             b['cpu_s'] < a['cpu_s'] and b['p95_ms'] < a['p95_ms'] else
                             'NOT PROVEN BETTER than live CatServer; do not promote')
    (output / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    return not all(result.get(x, {}).get('valid') for x in
                   ('live-A1', 'candidate-B1', 'candidate-B2', 'live-A2'))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit('usage: engine_family_compare.py <server-pack.zip> <other.jar> <engine-label> <out-dir>')
    sys.exit(int(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(),
                      sys.argv[3], Path(sys.argv[4]).resolve())))
