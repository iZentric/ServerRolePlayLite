#!/usr/bin/env python3
"""Public deterministic specifications for 261 packet differential cases.

Together with the separate 20-case source-extracted bridge contract, this is
281 contract cases, NOT 281 real-client or full-engine differential harnesses.
"""
from pathlib import Path
import sys

PATTERNS = ('zeros', 'repeat', 'random', 'mixed')
# Include every power-of-two boundary +/-1 through 128 KiB plus spread-out
# lengths, including the default 256-byte compression threshold and VarInts.
EXTRA = (6, 10, 24, 40, 80, 160, 250, 300, 768, 1500, 3000, 6000, 12000, 262144)
SIZES = tuple(sorted({x for n in range(1, 18) for x in
                      ((1 << n) - 1, 1 << n, (1 << n) + 1)} | set(EXTRA)))
SPECIAL = ((1, 'zeros', 'heap', 0),       # threshold zero, compressed nonempty
           (0, 'repeat', 'direct', 1),  # zero-length bypass
           (511, 'random', 'heap', 512),
           (512, 'random', 'direct', 512),
           (2097152, 'mixed', 'direct', 256))  # protocol-size edge (public only)


def cases():
    result = []
    for index, size in enumerate(SIZES):
        for pattern_id, pattern in enumerate(PATTERNS):
            source = 'direct' if (index + pattern_id) % 2 else 'heap'
            result.append((f'PKT-{len(result):03d}', size, pattern, source, 256))
    for size, pattern, source, threshold in SPECIAL:
        result.append((f'PKT-{len(result):03d}', size, pattern, source, threshold))
    if len(SIZES) != 64 or len(result) != 261 or len(set(result)) != 261:
        raise ValueError('differential matrix drift')
    return tuple(result)


def write_manifest(path):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError('manifest output must not exist')
    # No private data; only size, pattern and threshold. Never overwrite.
    with path.open('x', encoding='ascii') as output:
        for row in cases():
            output.write('\t'.join(map(str, row)) + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: fc_differential_281.py NEW_PUBLIC_MANIFEST_PATH')
    write_manifest(sys.argv[1])
    print('PUBLIC_PACKET_DIFFERENTIAL_CASES=261')
