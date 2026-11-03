#!/usr/bin/env python3
"""Check CatServer's pinned block-break bridge; not an in-game RP test."""
from pathlib import Path
import re
import sys
import unittest

SAVE = 'boolean forgeCanceled = event.isCanceled();'
SEED = 'bukkitEvent.setCancelled(event.isCanceled());'
CALL = 'Bukkit.getPluginManager().callEvent(bukkitEvent);'
DECIDE = 'event.setCanceled(forgeCanceled || bukkitEvent.isCancelled());'


def check_source(text):
    try:
        _, rest = text.split('public void onBreakBlockEvent(', 1)
        body = rest.split('\n    @SubscribeEvent', 1)[0]
        positions = [body.index(value) for value in (SAVE, SEED, CALL, DECIDE)]
        if not (positions == sorted(positions) and body.count(SAVE) == body.count(DECIDE) == 1
                and body.count('event.setCanceled(') == 1
                and re.search(r'@SubscribeEvent\(receiveCanceled = true\)\s+public void onBreakBlockEvent\(', text)):
            raise ValueError('Forge break veto must survive Bukkit callbacks')
    except (ValueError, IndexError) as exc:
        raise ValueError('Forge break veto must survive Bukkit callbacks') from exc
    return True


class BreakVetoTest(unittest.TestCase):
    def test_uncancelled_upstream_is_rejected(self):
        source = ('@SubscribeEvent(receiveCanceled = true)\n'
                  'public void onBreakBlockEvent(X event) {\n'
                  + SAVE + '\n' + SEED + '\n' + CALL + '\n'
                  + DECIDE.replace('forgeCanceled || ', '') + '\n}\n'
                  '    @SubscribeEvent')
        with self.assertRaises(ValueError):
            check_source(source)
        self.assertTrue(check_source(source.replace(DECIDE.replace('forgeCanceled || ', ''), DECIDE)))

    def test_all_four_cancellation_combinations(self):
        for forge in (False, True):
            for bukkit in (False, True):
                with self.subTest(forge=forge, bukkit=bukkit):
                    result = forge or bukkit
                    self.assertEqual(result, (True if forge else bukkit))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--source':
        try:
            check_source(Path(sys.argv[2]).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            print('BLOCK_BREAK_VETO_REJECTED', file=sys.stderr)
            sys.exit(2)
        print('BLOCK_BREAK_VETO_SOURCE_PASS')
    elif len(sys.argv) == 1:
        unittest.main()
    else:
        sys.exit(2)
