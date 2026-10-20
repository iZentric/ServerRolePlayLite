#!/usr/bin/env python3
"""Hosted-only fixture proving we emit counts/IDs, never raw client log text."""
import subprocess
import tempfile
from pathlib import Path

script = str(Path(__file__).with_name('fc_lite_join_log_diagnostic.ps1'))
with tempfile.TemporaryDirectory(prefix='fc-join-log-') as temp:
    profile = Path(temp) / 'PrismLauncher' / 'instances' / 'FunCity RP Lite'
    logs = profile / '.minecraft' / 'logs'
    logs.mkdir(parents=True)
    (logs / 'latest.log').write_text(
        'START secret-user-name token=PRIVATE_VALUE 203.0.113.1\n'
        'Incomplete mod data: missing mod placebo\n'
        'Unvollständige Moddaten\n', encoding='utf-8')
    result = subprocess.run(['pwsh', '-File', script, '-Profile', str(profile)],
                            capture_output=True, text=True)
    assert result.returncode == 0, 'fixture must parse synthetic log'
    assert 'MOD_MISMATCH_LINES=2' in result.stdout, 'missing mismatch indicators'
    assert 'SERVER_ONLY_IDS_IN_HINTS=placebo' in result.stdout, 'ID not detected'
    for secret in ('secret-user-name', 'PRIVATE_VALUE', '203.0.113.1', temp):
        assert secret not in result.stdout + result.stderr, 'raw client data leaked'
    print('PASS: Lite log symptoms sanitized; no paths/names/IP/secrets emitted')
