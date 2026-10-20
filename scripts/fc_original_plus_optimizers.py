#!/usr/bin/env python3
"""Read-only gate for FunCity RP Lite: Freeroam bytes retained, no surprise mods.

Synthetic tests only until the owner's Freeroam profile is actually accessible.
Never walks Prism worlds, logs, config, accounts, or reads/modifies the server.
"""
import json
from pathlib import Path

from fc_freeroam_inventory import compare

POLICY = Path(__file__).resolve().parent.parent/'agent'/'FUNCITY-RP-LITE-OVERLAY.json'


def assess(original, candidate):
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    allowed = set(policy['performance_candidates_for_active_game'])
    if (policy['project_name'] != 'FunCity RP Lite' or
            policy['rule'] != 'copy_all_original_mods_byte_for_byte_then_add_only_compatible_client_optimizers' or
            len(allowed) != 4 or 'Dynamic FPS' in ' '.join(allowed)):
        raise ValueError('invalid overlay policy')
    result = compare(original, candidate)  # original and candidate are read-only
    unexpected = set(result['lowspec_only']) - allowed
    return {
        'original_jar_count': result['original_count'],
        'candidate_jar_count': result['lowspec_count'],
        'missing_original': result['original_only'],
        'changed_original': result['changed_sha'],
        'unexpected_additions': sorted(unexpected),
        'compatible_optimizers_added_by_name': sorted(set(result['lowspec_only']) & allowed),
        'original_preserved_by_sha': result['original_count'] > 0 and not (result['original_only'] or result['changed_sha']),
        'eligible_for_compatibility_testing_only': result['original_count'] > 0 and not (result['original_only'] or result['changed_sha'] or unexpected),
    }
