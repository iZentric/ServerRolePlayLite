#!/usr/bin/env python3
"""Synthetic selection/guard test. No historical JARs, world, PC or runner touched."""
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

import fc_modded_candidate as candidate


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive = root/'fake.zip'
        selected = candidate.CHOSEN + candidate.PERFORMANCE
        extras = tuple(f'unrelated-{n}.jar' for n in range(36 - len(selected)))
        with zipfile.ZipFile(archive, 'w') as dest:
            for name in selected + extras:
                dest.writestr('server/mods/' + name, name.encode())

        def metadata(raw):
            name = raw.decode()
            return {'metadata': 'mods.toml', 'mod_ids': [name],
                    'required_dependencies': {name: []}}

        def stage(_engine, _archive, _core, _guava, output):
            (output/'mods').mkdir(parents=True)
            return {'plugins': [1] * 6}

        actual_sha = candidate.sha

        def sha(path):
            return candidate.ARCHIVE_SHA if path == archive else actual_sha(path)

        with patch.object(candidate, 'inspect_jar', side_effect=metadata), \
                patch.object(candidate, 'stage', side_effect=stage), \
                patch.object(candidate, 'sha', side_effect=sha):
            baseline = candidate.make(None, archive, None, None, root/'baseline')
            trial = candidate.make(None, archive, None, None, root/'trial', with_optimizers=True)
            assert len(baseline['server_mods']) == 15 and baseline['server_optimizers'] == []
            assert len(trial['server_mods']) == 18
            assert trial['server_optimizers'] == list(candidate.PERFORMANCE)
            assert [m['role'] for m in trial['server_mods']].count('server_performance_trial') == 3
            assert {p.name for p in (root/'trial'/'mods').iterdir()} == set(selected)
            assert json.loads((root/'trial'/'stage-report.json').read_text()) == trial
            try:
                candidate.make(None, archive, None, None, root/'trial', with_optimizers=True)
            except ValueError:
                pass
            else:
                raise AssertionError('existing stage overwritten')
        print('PASS: baseline 15, trial 18, exact inventory and no overwrite')


if __name__ == '__main__':
    main()
