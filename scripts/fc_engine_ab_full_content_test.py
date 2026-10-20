#!/usr/bin/env python3
"""No Minecraft: rejects non-runner paths and validates PID-scoped resource sample."""
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from fc_engine_ab_full_content import check_env, proc_sample, verify_trial_stop


class FakeProcess:
    def __init__(self, code):
        self.returncode = code


class FakeJvm:
    def __init__(self, stop_result, code):
        self.stop_result = stop_result
        self.p = FakeProcess(code)

    def stop(self, _grace):
        return self.stop_result


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
        log = root/'private.log'
        log.write_text('Server stopped normally\n')
        verify_trial_stop(FakeJvm('CLEAN', 0), log)
        for jvm, lines in ((FakeJvm('CLEAN', 1), 'Server stopped normally'),
                           (FakeJvm('KILLED_DUPA_GRACE', -9), 'Server stopped normally'),
                           (FakeJvm('CLEAN', 0), 'Exception in server tick loop')):
            log.write_text(lines)
            try:
                verify_trial_stop(jvm, log)
            except ValueError:
                pass
            else:
                raise AssertionError('invalid trial was reported clean')
    print('PASS: PID-scoped metrics, new runner-temp path, JVM exit code and post-workload critical checks')


if __name__ == '__main__':
    main()
