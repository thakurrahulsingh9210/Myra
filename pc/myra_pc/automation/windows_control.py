import os,platform,shutil,subprocess
from pathlib import Path
from urllib.parse import urlparse
from .contracts import AutomationResult,DesktopAction
from ..safety import classify_action,requires_confirmation
from ..models import RiskLevel
class WindowsControl:
 APP_ALLOWLIST={"notepad":("notepad.exe",),"calculator":("calc.exe",),"paint":("mspaint.exe",),"explorer":("explorer.exe",),"file explorer":("explorer.exe",),"edge":("msedge.exe",),"chrome":("chrome.exe",),"firefox":("firefox.exe",)}
 def __init__(self,workspace,*,system=None,popen=subprocess.Popen):
  self.workspace=Path(workspace).expanduser().resolve();self.workspace.mkdir(parents=True,exist_ok=True);self.system=system or platform.system();self._popen=popen
 def _path(self,raw):
  p=(self.workspace/raw).resolve()
  if p!=self.workspace and self.workspace not in p.parents: raise PermissionError("Path escapes Myra's approved workspace")
  return p
 def execute(self,action:DesktopAction,*,confirmed=False):
  risk=classify_action(action.name)
  if risk is RiskLevel.BLOCKED:return AutomationResult(False,"Action is blocked by Myra safety policy.")
  if requires_confirmation(action.name) and not confirmed:return AutomationResult(False,"User confirmation is required.")
  try:
   p=action.parameters
   handlers={"open_app":lambda:self.open_app(p.get("app","")),"open_url":lambda:self.open_url(p.get("url","")),"type_text":lambda:self.type_text(p.get("text","")),"mouse_click":lambda:self.mouse_click(int(p["x"]),int(p["y"])),"press_hotkey":lambda:self.press_hotkey(p.get("keys","")),"search_files":lambda:self.search_files(p.get("pattern","*")),"read_file":lambda:self.read_file(p["path"]),"create_file":lambda:self.create_file(p["path"],p.get("content","")),"rename_file":lambda:self._move(p["source"],p["destination"],True),"move_file":lambda:self._move(p["source"],p["destination"],False),"delete_file":lambda:self.delete_file(p["path"])}
   return handlers[action.name]() if action.name in handlers else AutomationResult(False,"Action not implemented yet.")
  except (KeyError,ValueError,OSError,PermissionError) as e:return AutomationResult(False,str(e))
 def open_app(self,name):
  if self.system!="Windows":return AutomationResult(False,"Windows-only action.")
  cmd=self.APP_ALLOWLIST.get(name.strip().lower())
  if not cmd:return AutomationResult(False,"Application is not on the approved launch list.")
  self._popen(list(cmd),shell=False,close_fds=True);return AutomationResult(True,"Launch requested; window verification pending.")
 def open_url(self,url):
  u=urlparse(url)
  if u.scheme not in {"https","http"} or not u.netloc:return AutomationResult(False,"Only valid HTTP/HTTPS URLs are allowed.")
  if self.system!="Windows":return AutomationResult(False,"Windows-only action.")
  os.startfile(url);return AutomationResult(True,"URL launch requested.")
 def search_files(self,pattern):
  if not pattern or len(pattern)>128 or Path(pattern).is_absolute() or ".." in Path(pattern).parts:return AutomationResult(False,"Invalid search pattern.")
  found=sorted(str(p.relative_to(self.workspace)) for p in self.workspace.rglob(pattern) if p.is_file())[:200]
  return AutomationResult(True,"\\n".join(found) if found else "No matching files.",verified=True)
 def read_file(self,raw):
  p=self._path(raw)
  if not p.is_file():return AutomationResult(False,"File not found.")
  if p.stat().st_size>1_000_000:return AutomationResult(False,"File exceeds 1 MB limit.")
  return AutomationResult(True,p.read_text(encoding="utf-8"),verified=True)
 def create_file(self,raw,content):
  p=self._path(raw)
  if len(content.encode())>1_000_000:return AutomationResult(False,"Content exceeds 1 MB limit.")
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("x",encoding="utf-8") as f:f.write(content)
  return AutomationResult(True,"File created.",verified=p.is_file())
 def _move(self,src_raw,dst_raw,rename):
  src,dst=self._path(src_raw),self._path(dst_raw)
  if not src.exists():return AutomationResult(False,"Source does not exist.")
  if dst.exists():return AutomationResult(False,"Destination already exists.")
  dst.parent.mkdir(parents=True,exist_ok=True)
  src.rename(dst) if rename else shutil.move(str(src),str(dst))
  return AutomationResult(True,"File moved.",verified=dst.exists())
 def delete_file(self,raw):
  p=self._path(raw)
  if not p.is_file():return AutomationResult(False,"File not found or not a regular file.")
  p.unlink();return AutomationResult(True,"File deleted.",verified=not p.exists())
 @staticmethod
 def _pyautogui():
  try:import pyautogui
  except ImportError as e:raise RuntimeError("Install desktop extra for mouse and keyboard") from e
  return pyautogui
 def type_text(self,text):
  if len(text)>2000:return AutomationResult(False,"Text exceeds 2000 character limit.")
  self._pyautogui().write(text,interval=.01);return AutomationResult(True,"Text typed; result verification pending.")
 def mouse_click(self,x,y):
  if x<0 or y<0 or x>20000 or y>20000:return AutomationResult(False,"Mouse coordinates outside allowed bounds.")
  self._pyautogui().click(x=x,y=y);return AutomationResult(True,"Mouse click sent; result verification pending.")
 def press_hotkey(self,keys):
  allowed={"ctrl","alt","shift","win","enter","tab","esc","space","up","down","left","right","home","end","pageup","pagedown",*(f"f{i}" for i in range(1,13))}
  parts=[x.strip().lower() for x in keys.split("+") if x.strip()]
  if not parts or len(parts)>4 or any(x not in allowed for x in parts):return AutomationResult(False,"Hotkey contains unsupported keys.")
  self._pyautogui().hotkey(*parts);return AutomationResult(True,"Hotkey sent; result verification pending.")
