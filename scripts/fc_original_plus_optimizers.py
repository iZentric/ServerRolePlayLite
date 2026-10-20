#!/usr/bin/env python3
"""Read-only gate for a prospective Lite client; never edits original or candidate.

The declared 28 names are NOT a disk inventory. Only explicitly owner-approved
exclusions are allowed, and even an eligible candidate is NOT release-ready.
"""
import json
from pathlib import Path

from fc_freeroam_inventory import inventory

ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT/'agent'/'FUNCITY-RP-LITE-OVERLAY.json'
DECLARED = ROOT/'agent'/'FREEROAM-LISTA-DECLARATA.json'
SELECTION = ROOT/'agent'/'FUNCITY-RP-LITE-SELECTIE.json'


def assess(original, candidate):
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    declaration = json.loads(DECLARED.read_text(encoding='utf-8'))
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    allowed = set(policy['approved_additions'])
    excluded = set(policy['approved_exclusions_from_future_lite'])
    blocked = set(policy['blocked_exclusion_awaiting_owner'])
    declared = set(declaration['jar_names'])
    baseline = set(policy['performance_candidates_for_active_game'])
    if (policy['project_name'] != 'FunCity RP Lite' or
            policy['declared_original_names'] != 'agent/FREEROAM-LISTA-DECLARATA.json' or
            policy['rule'] != 'retain_original_bytes_except_exact_owner_approved_target_exclusions' or
            allowed or len(baseline) != 3 or not baseline <= declared or
            len(declared) != 28 or len(declaration['jar_names']) != 28 or
            len(excluded) != 4 or len(policy['approved_exclusions_from_future_lite']) != 4 or
            blocked != {'TRansliterationLib-1.0.4.jar'} or
            not excluded <= declared or excluded & blocked or
            set(selection['removed_from_future_target']) != excluded or
            set(selection['retained_in_future_target']) != declared - excluded or
            len(selection['retained_in_future_target']) != 24 or
            not {'notenoughanimations-1.2.4.jar', *blocked} <= set(selection['retained_in_future_target']) or
            any('dynamicfps' in name.casefold().replace(' ', '') for name in allowed | baseline)):
        raise ValueError('invalid overlay policy/selection')
    # inventory() rejects symlinks, ambiguous folders and unsafe JAR names.
    a, b = inventory(original), inventory(candidate)
    original_names, candidate_names = set(a), set(b)
    missing = original_names - candidate_names
    changed = sorted(name for name in original_names & candidate_names if a[name] != b[name])
    added = candidate_names - original_names
    unexpected = sorted(added - allowed)
    declared_missing = sorted(declared - original_names)
    unlisted_original = sorted(original_names - declared)
    matched = not (declared_missing or unlisted_original)
    retained_unchanged = bool(a) and not (missing - excluded or changed)
    exactly_excluded = missing == excluded
    return {
        'original_jar_count': len(a),
        'candidate_jar_count': len(b),
        'declared_missing_in_original': declared_missing,
        'unlisted_original': unlisted_original,
        'declared_matches_disk_names': matched,
        'missing_original': sorted(missing),
        'unapproved_missing_original': sorted(missing - excluded),
        'approved_target_exclusions_present': sorted(missing & excluded),
        'changed_original': changed,
        'unexpected_additions': unexpected,
        'optimizers_added_by_name': sorted(added & allowed),
        'retained_original_sha_unchanged': retained_unchanged,
        'exactly_four_approved_exclusions': exactly_excluded,
        'eligible_for_compatibility_testing_only': matched and retained_unchanged and exactly_excluded and not unexpected,
        'ready_for_release': False,
    }
