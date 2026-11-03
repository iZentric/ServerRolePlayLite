#!/usr/bin/env python3
"""Strict source/decision gate for the pinned CatServer block-place bridge.

Exhaustive boolean tests are NOT a replacement for runtime mod/plugin tests.
"""
from pathlib import Path
import sys
import unittest

PATCH = Path(__file__).resolve().parents[1] / 'functity/catserver/patches/0002-preserve-forge-block-place-cancellation.patch'
OLD = 'event.setCanceled(bukkitEvent.isCancelled() || !bukkitEvent.canBuild());'
NEW = 'event.setCanceled(forgeCanceled || bukkitEvent.isCancelled() || !bukkitEvent.canBuild());'
SAVE = 'boolean forgeCanceled = event.isCanceled();'


def check_source(source):
    text = Path(source).read_text(encoding='utf-8')
    block = text.split('public void onBlockPlaceEvent(', 1)[1].split('public void onBreakBlockEvent(', 1)[0]
    assert block.count(SAVE) == 1 and block.count(NEW) == 1
    assert OLD not in block
    assert block.index(SAVE) < block.index('if (event instanceof BlockEvent.EntityMultiPlaceEvent)')
    assert block.index(NEW) > block.index('CraftEventFactory.callBlockPlaceEvent(')
    assert 'CraftEventFactory.callBlockMultiPlaceEvent(' in block
    assert 'receiveCanceled = true' in text.split('public void onBlockPlaceEvent(', 1)[0]
    assert block.count('event.setCanceled(') == 1
    return True


class BridgeTest(unittest.TestCase):
    def test_patch_is_only_the_pinned_change(self):
        text = PATCH.read_text()
        self.assertEqual(text.count('diff --git '), 1)
        self.assertIn('src/main/java/catserver/server/CatServerEventHandler.java', text)
        self.assertEqual(text.count('+            ' + SAVE), 1)
        self.assertEqual(text.count('+' + '            ' + NEW), 1)
        self.assertEqual(text.count('-' + '            ' + OLD), 1)

    def test_all_boolean_combinations_and_no_regression_when_forge_allows(self):
        for forge_canceled in (False, True):
            for bukkit_canceled in (False, True):
                for can_build in (False, True):
                    with self.subTest(forge=forge_canceled, bukkit=bukkit_canceled, build=can_build):
                        original = bukkit_canceled or not can_build
                        result = forge_canceled or bukkit_canceled or not can_build
                        if forge_canceled:
                            self.assertTrue(result)
                        else:
                            self.assertEqual(result, original)

    def test_reject_unpatched_or_late_capture(self):
        code = ('@SubscribeEvent(receiveCanceled = true)\n'
                'public void onBlockPlaceEvent(X e) { ' + SAVE + '\n'
                'if (event instanceof BlockEvent.EntityMultiPlaceEvent) {}\n'
                'CraftEventFactory.callBlockMultiPlaceEvent();\n'
                'CraftEventFactory.callBlockPlaceEvent();\n' + NEW + '\n}\n'
                'public void onBreakBlockEvent() {}')
        # Source check also requires no duplicate cancellation setter.
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'handler.java'
            path.write_text(code)
            self.assertTrue(check_source(path))
            path.write_text(code.replace(NEW, OLD))
            with self.assertRaises(AssertionError):
                check_source(path)
            path.write_text(code.replace(SAVE, 'boolean forgeCanceled = false;'))
            with self.assertRaises(AssertionError):
                check_source(path)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--source':
        try:
            check_source(sys.argv[2])
        except (AssertionError, OSError, IndexError) as exc:
            print('BRIDGE_PATCH_SOURCE_INVALID: ' + type(exc).__name__, file=sys.stderr)
            sys.exit(2)
        print('BRIDGE_PATCH_SOURCE_PASS')
    elif len(sys.argv) == 1:
        unittest.main()
    else:
        sys.exit(2)
