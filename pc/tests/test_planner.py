import unittest
from myra_pc.planner import TaskPlanner
from myra_pc.models import RiskLevel
class Tests(unittest.TestCase):
    def setUp(self): self.p=TaskPlanner(None)
    def test_policy_overrides_model(self):
        p=self.p.parse('{"title":"Rename","summary":"x","actions":[{"action":"rename_file","description":"rename","parameters":{"from":"a","to":"b"},"risk":"safe"}]}');self.assertEqual(p.actions[0].risk,RiskLevel.CONTROLLED);self.assertTrue(p.needs_confirmation)
    def test_unknown_blocked(self):
        p=self.p.parse('{"title":"bad","actions":[{"action":"run_shell","description":"run"}]}');self.assertEqual(p.actions[0].risk,RiskLevel.BLOCKED)
    def test_bad_json(self):
        with self.assertRaises(ValueError): self.p.parse("not json")
    def test_too_many(self):
        with self.assertRaises(ValueError): TaskPlanner(None,1).parse('{"title":"x","actions":[{"action":"open_app","description":"a"},{"action":"open_app","description":"b"}]}')
    def test_bad_parameters(self):
        with self.assertRaises(ValueError): self.p.parse('{"title":"x","actions":[{"action":"open_app","description":"a","parameters":{"app":3}}]}')
