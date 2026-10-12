#!/usr/bin/env python3
"""Actual same-pack CatServer branded vs upstream official, A/B/B/A, no live access."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import zipfile
from engine_ab import JAR, prepare, run

EXPECTED_LIVE_SHA = '96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c'


def jar_diff(branded_bytes, official_bytes):
    """Compare uncompressed file contents; ZIP timestamps/recompression aren't code."""
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(branded_bytes)) as a, zipfile.ZipFile(BytesIO(official_bytes)) as b:
        names = set(a.namelist()) | set(b.namelist())
        changed = sorted(n for n in names if n not in a.namelist() or n not in b.namelist()
                         or hashlib.sha256(a.read(n)).digest() != hashlib.sha256(b.read(n)).digest())
    return changed


def main(pack, upstream, out):
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pack) as z:
        branded_bytes = z.read(JAR)
    brand_sha = hashlib.sha256(branded_bytes).hexdigest()
    upstream_bytes = upstream.read_bytes()
    upstream_sha = hashlib.sha256(upstream_bytes).hexdigest()
    if brand_sha != EXPECTED_LIVE_SHA or brand_sha == upstream_sha:
        raise ValueError(f'wrong reference or no binary difference: {brand_sha}, {upstream_sha}')
    result = {
        'method': 'A/B/B/A: branded live JAR vs official exact CatServer 1.16.5-1d8d6313; same 36 mods/14 plugins, Java 17, fresh same-seed world, same GH runner, 64 force-loaded chunks, 40 zombies; 55s warmup then 75s steady window',
        'limits': 'two samples/arm; zero players/vehicles, synthetic workload; no claim of faster real-world RP or client FPS, no live changes',
        'pack_sha256': hashlib.sha256(pack.read_bytes()).hexdigest(),
        'branded_sha256': brand_sha,
        'official_sha256': upstream_sha,
        'uncompressed_jar_entries_different': jar_diff(branded_bytes, upstream_bytes),
    }
    for label, jar in [('branded-A1', None), ('official-B1', upstream),
                       ('official-B2', upstream), ('branded-A2', None)]:
        dest = out / label
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        arm = run(label, dest, out, ticket_workload=True)
        arm['jar_sha256'] = hashlib.sha256((dest / JAR).read_bytes()).hexdigest()
        result[label] = arm
        print(json.dumps(arm, indent=2), flush=True)
        if not arm['valid']:
            result['verdict'] = 'INCOMPLETE: startup/workload/metrics failed; no rank'
            break
    if 'verdict' not in result:
        arms = {'branded': ['branded-A1', 'branded-A2'], 'official': ['official-B1', 'official-B2']}
        summary = {}
        for name, labels in arms.items():
            def metric(key):
                values = [result[label][key] for label in labels]
                return {'values': values, 'median': round(statistics.median(values), 3),
                        'within_arm_range': round(max(values) - min(values), 3)}
            summary[name] = {
                'cpu_steady_s': metric('cpu_seconds_steady_after_55s'),
                'rss_steady_mib': metric('rss_steady_median_mb'),
                'p95_steady_ms': {
                    'values': [result[label]['spark_tick_min_median_p95_max_ms_1m'][2] for label in labels],
                },
                'boot_done_s': metric('boot_done_s'),
                'boot_wall_s': metric('boot_wall_seconds'),
            }
            p95 = summary[name]['p95_steady_ms']['values']
            summary[name]['p95_steady_ms'].update(median=round(statistics.median(p95), 3),
                                                 within_arm_range=round(max(p95) - min(p95), 3))
        result['summary'] = summary
        result['verdict'] = ('TWO-SAMPLE OBSERVATION ONLY: compare within-arm ranges and do not claim 171 MB/6% from historical unpaired minima. No promotion without representative player/vehicle test.')
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return int('summary' not in result)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('usage: engine_native_compare.py <pack.zip> <official.jar> <output-dir>')
    sys.exit(main(*(Path(p).resolve() for p in sys.argv[1:])))
