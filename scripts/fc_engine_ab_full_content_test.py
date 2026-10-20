#!/usr/bin/env python3
"""No Minecraft: rejects non-runner paths and validates PID-scoped resource sample."""
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from fc_engine_ab_full_content import check_env, proc_sample


def main():
    rss, cpu = proc_sample(os.getpid())
    assert rss > 0 and cpu >= 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with patch.dict(os.environ, {'RUNNER_TEMP': str(root)}):
            for bad in (root/'old-world', root/'fc-engine-ab'/'trial-1'):
                try:
                    check_env(bad, bad/'stage')
                except ValueError:
                    pass
                else:
                    raise AssertionError('unsafe AB root accepted')
    print('PASS: PID-scoped RSS/CPU and new runner-temp AB root guards')


if __name__ == '__main__':
    main()
