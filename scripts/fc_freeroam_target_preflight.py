#!/usr/bin/env python3
"""Read-only, fail-closed inventory gate for the OWNER-CHOSEN Freeroam Prism profile.

Never writes to Prism. No paths, filenames, hashes, logs or account data are
printed. A passing inventory is NOT an installation or a boot/login result.
"""
import argparse
import json
from pathlib import Path
import sys

from fc_freeroam_inventory import inventory

ROOT = Path(__file__).resolve().parent.parent
DECLARED = ROOT/'agent'/'FREEROAM-LISTA-DECLARATA.json'
SELECTION = ROOT/'agent'/'FUNCITY-RP-LITE-SELECTIE.json'
EXPECTED_EXCLUSIONS = frozenset({
    'CTM-MC1.16.1-1.1.2.6.jar',
    'DynamicSurroundings-1.16.5-4.0.5.0.jar',
    'InGameAccountSwitcher-Forge-1.16-8.0.1.jar',
    'lightfallclient-1.0.0.jar',
    'notenoughanimations-1.2.4.jar',
    'TRansliterationLib-1.0.4.jar',
})


def check(profile):
    """Return redacted counts; never delete or mutate a JAR."""
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    declared = json.loads(DECLARED.read_text(encoding='utf-8'))['jar_names']
    excluded = set(selection['removed_from_future_target'])
    kept = set(selection['retained_in_future_target'])
    if (len(declared) != len(set(declared)) or len(declared) != 28 or
            excluded != EXPECTED_EXCLUSIONS or len(selection['removed_from_future_target']) != 6 or
            kept != set(declared) - excluded or len(kept) != 22 or
            len(selection['retained_in_future_target']) != 22 or
            selection['ready_for_release'] is not False):
        raise ValueError('invalid target selection')
    if Path(profile).name != 'Freeroam 1.0.0':
        raise ValueError('wrong profile')
    original = inventory(profile)  # Rejects links, ambiguous folders, unsafe JARs.
    names = set(original)
    missing = set(declared) - names
    unexpected = names - set(declared)
    return {
        'pass': not (missing or unexpected),
        'original_jar_count': len(original),
        'declared_missing_count': len(missing),
        'unexpected_jar_count': len(unexpected),
        'approved_exclusions_present_count': len(names & excluded),
        'remaining_target_count_if_inventory_matches': len(kept) if not (missing or unexpected) else None,
        'installation_performed': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, type=Path,
                        help='Exact Freeroam 1.0.0 profile directory; do not pass another instance')
    args = parser.parse_args(argv)
    try:
        result = check(args.profile)
    except (OSError, ValueError, KeyError, TypeError):
        print('FREEROAM_PREFLIGHT_BLOCKED; no installation performed', file=sys.stderr)
        return 2
    if not result['pass']:
        print('FREEROAM_INVENTORY_MISMATCH ' +
              f"original={result['original_jar_count']} missing={result['declared_missing_count']} " +
              f"unexpected={result['unexpected_jar_count']} READ_ONLY=true")
        return 1
    print('FREEROAM_INVENTORY_MATCH ' +
          f"original={result['original_jar_count']} target_declared={result['remaining_target_count_if_inventory_matches']} " +
          'READ_ONLY=true INSTALLATION=false')
    return 0


if __name__ == '__main__':
    sys.exit(main())
