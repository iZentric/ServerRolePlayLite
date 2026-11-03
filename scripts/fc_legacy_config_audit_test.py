#!/usr/bin/env python3
"""Synthetic privacy/CRC fixtures for the historical snapshot reader."""
import io
import json
import sys
import zipfile

from fc_legacy_config_audit import scan


def main():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('server.properties', 'view-distance=5\nmax-players=200\nrcon.password=NEVER_PRINT_ME\n')
        z.writestr('config.yml', 'token: NEVER_PRINT_ME\npassword: NEVER_PRINT_ME\n')
        z.writestr('bukkit.yml', 'spawn-limits:\n  monsters: 20\n')
    report = '==== cuantic\\server.properties (0 B) ====\n'
    result = scan(buf.getvalue(), report)
    text = json.dumps(result)
    assert 'NEVER_PRINT_ME' not in text and 'token' not in text and 'password' not in text
    assert result['archived_entries_crc_checked'] == 3
    assert result['safe_value_distributions_without_provenance']['server.properties:max-players'] == {'200': 1}
    assert result['report_path_counts'] == {'cuantic': 1}
    try:
        scan(b'bad zip data', report)
    except zipfile.BadZipFile:
        pass
    else:
        raise AssertionError('corrupt archive accepted')
    print('PASS: full-entry CRC, privacy allowlist, historical provenance limits; synthetic only')


if __name__ == '__main__':
    sys.exit(main())
