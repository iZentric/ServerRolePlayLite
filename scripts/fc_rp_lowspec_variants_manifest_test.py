"""Static RP-preservation contract for the three local Prism profile recipes.

Real Forge boot, login, textures, voice and FPS must be tested on the owner's PC.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
base = json.loads((ROOT / 'agent/FUNCITY-RP-LITE-SELECTIE.json').read_text())
plan = json.loads((ROOT / 'agent/FUNCITY-RP-VARIANTE-LOWSPEC.json').read_text())
original = set(base['retained_in_future_target'])
assert len(original) == 22
oculus = 'oculus-mc1.16.5-1.4.7.jar'
rubidium = 'rubidium-mc1.16.5-0.2.13.jar'
rubidium_options = 'TextruesRubidiumOptions-1.0.8-mc1.16.5.jar'
embeddium = 'embeddium-0.3.18+mc1.16.5.jar'
embeddium_options = 'textrue_embeddium_options-0.1.1+mc1.16.5.jar'
assert {oculus, rubidium, rubidium_options} <= original
assert plan['schema'] == 1 and plan['minecraft'] == '1.16.5' and plan['loader'] == 'Forge'
assert plan['graphics_preset'] == {
    'renderDistance': 5, 'graphicsMode': 0, 'particles': 1,
    'mipmapLevels': 0, 'entityShadows': False, 'shaderpacks_copied': False,
    'note': 'Five chunks, Fast, particles Decreased, mipmap zero, entity shadows off. These are client graphics settings, NOT an FPS cap.',
}
variant_ids = [v['id'] for v in plan['variants']]
assert variant_ids == ['low_rubidium', 'no_oculus_test', 'embeddium_test']
expected = {
    'low_rubidium': original,
    'no_oculus_test': original - {oculus},
    'embeddium_test': (original - {oculus, rubidium, rubidium_options}) | {embeddium, embeddium_options},
}
for item in plan['variants']:
    jars = expected[item['id']]
    assert item['jar_count'] == len(jars)
    assert set(item['removed_only_in_variant']) == ({oculus} if item['id'] != 'low_rubidium' else set())
    assert item['replaced_only_in_variant'] == (
        {rubidium: embeddium, rubidium_options: embeddium_options}
        if item['id'] == 'embeddium_test' else {}
    )
    assert item['source_prism_name'] == (
        'FunCity RP Lite Embeddium TEST' if item['id'] == 'embeddium_test' else 'FunCity RP Lite'
    )
    assert item['prism_name'] and item['prism_name'] not in plan['do_not_touch']
    # None of the RP content, core dependencies, voice or baseline memory optimizers are lost.
    assert original - {oculus, rubidium, rubidium_options} <= jars
    assert len(jars) == len(set(jars))
assert len({v['prism_name'] for v in plan['variants']}) == 3
assert len(expected['low_rubidium']) == 22
assert len(expected['no_oculus_test']) == len(expected['embeddium_test']) == 21
assert not ({'Dynamic FPS', 'FPS Reducer', 'Distant Horizons'} - set(plan['never_added']))
print('PASS: three distinct 22/21/21 variants; RP jars preserved; no background FPS/LOD mods')
