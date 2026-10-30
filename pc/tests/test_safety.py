import unittest

from myra_pc.models import RiskLevel
from myra_pc.safety import can_auto_execute, classify_action, requires_confirmation


class SafetyTests(unittest.TestCase):
    def test_read_only_action_is_safe(self):
        self.assertEqual(classify_action("open_app"), RiskLevel.SAFE)
        self.assertTrue(can_auto_execute("open_app"))
        self.assertFalse(requires_confirmation("open_app"))

    def test_mutation_requires_confirmation(self):
        self.assertEqual(classify_action("rename_file"), RiskLevel.CONTROLLED)
        self.assertTrue(requires_confirmation("rename_file"))
        self.assertFalse(can_auto_execute("rename_file"))

    def test_critical_and_unknown_actions_fail_closed(self):
        self.assertEqual(classify_action("delete_file"), RiskLevel.CRITICAL)
        self.assertEqual(classify_action("made_up_action"), RiskLevel.BLOCKED)
        self.assertEqual(classify_action("run_arbitrary_shell"), RiskLevel.BLOCKED)


if __name__ == "__main__":
    unittest.main()
