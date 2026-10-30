import os
import unittest
from unittest.mock import patch

from myra_pc.config import RunMode, Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_select_hybrid_and_hindi_english(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.run_mode, RunMode.HYBRID)
        self.assertEqual(settings.primary_language, "hi-IN")
        self.assertEqual(settings.secondary_language, "en-IN")

    def test_invalid_mode_is_rejected(self):
        with patch.dict(os.environ, {"MYRA_RUN_MODE": "magic"}, clear=True):
            with self.assertRaises(ValueError):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()
