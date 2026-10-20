#!/usr/bin/env python3
"""Validate per-JAR owner choices against the declared names; no PC access."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
original = json.loads((ROOT/'agent'/'FREEROAM-LISTA-DECLARATA.json').read_text(encoding='utf-8'))
answers = json.loads((ROOT/'agent'/'FREEROAM-RASPUNSURI-28.json').read_text(encoding='utf-8'))
policy = json.loads((ROOT/'agent'/'FUNCITY-RP-LITE-OVERLAY.json').read_text(encoding='utf-8'))
keep = set(answers['keep'])
review = set(answers['conditional_review_for_removal_not_removed'])
delegated = set(answers['performance_delegated_preserve_now'])
assert (len(keep), len(review), len(delegated)) == (18, 5, 5)
assert not (keep & review or keep & delegated or review & delegated)
assert keep | review | delegated == set(original['jar_names'])
assert len(original['jar_names']) == 28
assert answers['current_action'] == 'FOUR_EXCLUSIONS_IN_LITE_TARGET_ONLY_NO_PROFILE_OR_JAR_CHANGED'
assert set(answers['latest_request']['requested_exclusions_from_future_lite']) == review
assert set(answers['latest_request']['target_exclusions_now']) == set(policy['approved_exclusions_from_future_lite'])
assert set(answers['latest_request']['pending_conflict']) == {'TRansliterationLib-1.0.4.jar'}
assert set(policy['approved_exclusions_from_future_lite']) == review - set(answers['latest_request']['pending_conflict'])
assert answers['latest_request']['actual_pc_profile_or_original_modified'] is False
assert not policy['approved_additions']
assert policy['owner_choices'] == 'agent/FREEROAM-RASPUNSURI-28.json'
assert set(answers['new_mods_deferred']) == set(policy['deferred_not_installed'])
assert 'voicechat-forge-1.16.5-2.3.23.jar' in keep
assert 'mapperbase-1.16.5-2.4.0.0.jar' in keep and 'roadstuff-1.16.5-4.3.0.jar' in keep
assert 'selene-1.16.5-1.9.0.jar' in keep and 'supplementaries-1.16.5-0.18.4b.jar' in keep
assert 'rubidium-mc1.16.5-0.2.13.jar' in delegated
print('PASS: 28 answers; four excluded in Lite target, dependency conflict pending; no profile/JAR edit')
