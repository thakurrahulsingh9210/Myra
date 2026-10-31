import tempfile,unittest
from pathlib import Path
from myra_pc.automation.windows_control import WindowsControl
from myra_pc.automation.contracts import DesktopAction
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.c=WindowsControl(self.root,system="Windows",popen=lambda *a,**k:None)
 def tearDown(self):self.tmp.cleanup()
 def test_app_allowlist(self):self.assertTrue(self.c.execute(DesktopAction("open_app",{"app":"notepad"})).success)
 def test_unknown_app(self):self.assertFalse(self.c.execute(DesktopAction("open_app",{"app":"powershell"})).success)
 def test_create_confirmation(self):
  a=DesktopAction("create_file",{"path":"n/a.txt","content":"hello"});self.assertIn("confirmation",self.c.execute(a).message);self.assertTrue(self.c.execute(a,confirmed=True).success)
 def test_delete_confirmation(self):
  (self.root/"a").write_text("x");a=DesktopAction("delete_file",{"path":"a"});self.assertFalse(self.c.execute(a).success);self.assertTrue((self.root/"a").exists());self.assertTrue(self.c.execute(a,confirmed=True).success)
 def test_path_traversal(self):
  with self.assertRaises(PermissionError):self.c._path("../outside")
 def test_read_search(self):
  (self.root/"a.txt").write_text("hello");self.assertEqual(self.c.read_file("a.txt").message,"hello");self.assertIn("a.txt",self.c.search_files("*.txt").message)
 def test_shell_blocked(self):self.assertFalse(self.c.execute(DesktopAction("run_arbitrary_shell",{"command":"whoami"})).success)
 def test_linux_refuses_launch(self):self.assertFalse(WindowsControl(self.root,system="Linux").open_app("notepad").success)
 def test_bad_url(self):self.assertFalse(self.c.open_url("javascript:alert(1)").success)
 def test_hotkey_allowlist(self):self.assertFalse(self.c.press_hotkey("ctrl+alt+delete").success)
