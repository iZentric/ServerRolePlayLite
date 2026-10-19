#!/usr/bin/env python3
"""Policy-only tests: forbid carrying the historical modpack into the new target."""
import copy
import json
from fc_plugin_first_gate import POLICY, validate


def reject(data):
    try:
        validate(data)
    except ValueError:
        return
    raise AssertionError('unjustified JAR selection accepted')


def main():
    source = json.loads(POLICY.read_text(encoding='utf-8'))
    assert validate(source)
    assert source['client_jar_selection'] == source['server_jar_selection'] == []
    assert source['owner_content_jar_approvals'] == []
    assert source['measured_performance_jar_approvals'] == []
    for key, value in (('client_jar_selection', ['Pizzaland_v68.jar']),
                       ('server_jar_selection', ['RoadRunner-mc1.16.5-1.5.2.jar']),
                       ('release_blocked', False), ('voice_status', 'working')):
        changed = copy.deepcopy(source)
        changed[key] = value
        reject(changed)
    changed = copy.deepcopy(source)
    changed['owner_content_jar_approvals'] = [
        {'filename': 'Pizzaland_v68.jar', 'sha256': 'a' * 64,
         'sides': ['client', 'server']}]
    changed['client_jar_selection'] = ['Pizzaland_v68.jar']
    reject(changed)  # name and hash alone do not establish ownership/licence
    changed = copy.deepcopy(source)
    changed['measured_performance_jar_approvals'] = [
        {'filename': 'RoadRunner-mc1.16.5-1.5.2.jar', 'sha256': 'b' * 64,
         'sides': ['server']}]
    changed['server_jar_selection'] = ['RoadRunner-mc1.16.5-1.5.2.jar']
    reject(changed)  # no hotspot or A/B evidence
    print('PASS: unknown content/performance JAR, undocumented owner and unmeasured optimization rejected')


if __name__ == '__main__':
    main()
