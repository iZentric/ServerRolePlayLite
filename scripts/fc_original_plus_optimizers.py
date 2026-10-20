#!/usr/bin/env python3
"""Read-only gate: declared Freeroam names and actual bytes must be preserved.

No Prism, world, accounts, server, installation, archive or release writes.
"""
import json
from pathlib import Path

from fc_freeroam_inventory import inventory

ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT/'agent'/'FUNCITY-RP-LITE-OVERLAY.json'
DECLARED = ROOT/'agent'/'FREEROAM-LISTA-DECLARATA.json'


def assess(original, candidate):
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    declaration = json.loads(DECLARED.read_text(encoding='utf-8'))
    allowed = set(policy['approved_additions'])
    declared = set(declaration['jar_names'])
    baseline = set(policy['performance_candidates_for_active_game'])
    if (policy['project_name'] != 'FunCity RP Lite' or
            policy['declared_original_names'] != 'agent/FREEROAM-LISTA-DECLARATA.json' or
            policy['rule'] != 'preserve_all_original_mods_byte_for_byte_no_unapproved_removals_or_additions' or
            allowed or len(baseline) != 3 or not baseline <= declared or
            len(declared) != 28 or
            any('dynamicfps' in name.casefold().replace(' ', '') for name in allowed | baseline)):
        raise ValueError('invalid overlay policy')
    # inventory() is fail-closed for symlinks, ambiguous folders and unsafe JAR names.
    a, b = inventory(original), inventory(candidate)
    original_names, candidate_names = set(a), set(b)
    missing = sorted(original_names - candidate_names)
    changed = sorted(name for name in original_names & candidate_names if a[name] != b[name])
    added = candidate_names - original_names
    unexpected = sorted(added - allowed)
    declared_missing = sorted(declared - original_names)
    unlisted_original = sorted(original_names - declared)
    matched = not (declared_missing or unlisted_original)
    preserved = bool(a) and not (missing or changed)
    return {
        'original_jar_count': len(a),
        'candidate_jar_count': len(b),
        'declared_missing_in_original': declared_missing,
        'unlisted_original': unlisted_original,
        'declared_matches_disk_names': matched,
        'missing_original': missing,
        'changed_original': changed,
        'unexpected_additions': unexpected,
        'optimizers_added_by_name': sorted(added & allowed),
        'original_preserved_by_sha': preserved,
        'eligible_for_compatibility_testing_only': matched and preserved and not unexpected,
    }
