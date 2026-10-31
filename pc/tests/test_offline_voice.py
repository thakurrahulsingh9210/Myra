import unittest
from unittest.mock import patch
from myra_pc.providers.offline_voice import WindowsTextToSpeech

class OfflineVoiceTests(unittest.TestCase):
    @patch("myra_pc.providers.offline_voice.platform.system", return_value="Linux")
    def test_windows_tts_refuses_non_windows(self, _system):
        with self.assertRaisesRegex(RuntimeError, "Windows 10/11"):
            WindowsTextToSpeech()

if __name__ == "__main__":
    unittest.main()
