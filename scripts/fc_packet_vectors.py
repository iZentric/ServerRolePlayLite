#!/usr/bin/env python3
"""Generate PUBLIC fixed inputs for a protocol-compatible compression experiment."""
import hashlib
from pathlib import Path

SIZES = ((1024, 2500), (32768, 800), (262144, 200))


def random_bytes(length):
    return b''.join(hashlib.sha256(i.to_bytes(4, 'little')).digest()
                    for i in range((length + 31) // 32))[:length]


def write_vectors(root):
    root = Path(root)
    root.mkdir()  # Never overwrite or read an existing/private dataset.
    vectors = []
    for size, loops in SIZES:
        for mode in ('mixed', 'random'):
            name = f'packet-{size}-{mode}.bin'
            data = random_bytes(size) if mode == 'random' else b'\0' * (size // 2) + random_bytes(size // 2)
            (root/name).write_bytes(data)
            vectors.append((name, loops))
    return vectors


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('usage: fc_packet_vectors.py NEW_PUBLIC_OUTPUT_DIR')
    for name, loops in write_vectors(sys.argv[1]):
        print(name, loops)
