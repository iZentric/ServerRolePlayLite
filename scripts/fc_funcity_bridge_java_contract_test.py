#!/usr/bin/env python3
"""Structural tests; the hosted job compiles/runs the actual Java method."""
import unittest
from fc_funcity_bridge_java_contract import extract_method, extract_break_method


class JavaHarnessTest(unittest.TestCase):
    def setUp(self):
        self.text = '''public void onBlockPlaceEvent(BlockEvent.EntityPlaceEvent event) {
    boolean forgeCanceled = event.isCanceled();
    CraftEventFactory.callBlockPlaceEvent();
    CraftEventFactory.callBlockMultiPlaceEvent();
    event.setCanceled(forgeCanceled || bukkitEvent.isCancelled() || !bukkitEvent.canBuild());
}
    @SubscribeEvent
'''

    def test_extract_exact_patch(self):
        method = extract_method(self.text)
        self.assertIn('boolean forgeCanceled', method)
        self.assertNotIn('@SubscribeEvent', method)

    def test_reject_upstream_without_veto(self):
        with self.assertRaises(ValueError):
            extract_method(self.text.replace('forgeCanceled || ', ''))

    def test_reject_missing_multiplace(self):
        with self.assertRaises(ValueError):
            extract_method(self.text.replace('CraftEventFactory.callBlockMultiPlaceEvent', 'other'))

    def test_break_requires_original_forge_veto(self):
        text = '''@SubscribeEvent(receiveCanceled = true)
public void onBreakBlockEvent(BlockEvent.BreakEvent event) {
    boolean forgeCanceled = event.isCanceled();
    Bukkit.getPluginManager().callEvent(bukkitEvent);
    event.setCanceled(forgeCanceled || bukkitEvent.isCancelled());
}
    @SubscribeEvent
'''
        self.assertIn('forgeCanceled', extract_break_method(text))
        with self.assertRaises(ValueError):
            extract_break_method(text.replace('forgeCanceled || ', ''))


if __name__ == '__main__':
    unittest.main()
