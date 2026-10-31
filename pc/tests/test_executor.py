import tempfile,unittest
from pathlib import Path
from myra_pc.automation.contracts import AutomationResult
from myra_pc.executor import TaskExecutor
from myra_pc.models import RiskLevel,TaskPlan,TaskStatus,TaskStep
from myra_pc.task_store import TaskStore
class FakeRunner:
 def __init__(self,results=None):self.calls=[];self.results=list(results or [])
 def execute(self,action,*,confirmed=False):
  self.calls.append((action,confirmed));return self.results.pop(0) if self.results else AutomationResult(True,"done",True)
class ExecutorTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=TaskStore(Path(self.tmp.name)/"tasks.db")
 def tearDown(self):self.tmp.cleanup()
 def plan(self,*steps):return TaskPlan("test task",tuple(steps))
 def test_safe_actions_and_event_journal(self):
  runner=FakeRunner();p=self.plan(TaskStep("launch","open_app",RiskLevel.BLOCKED,{"app":"notepad"}));r=TaskExecutor(runner,self.store).run(p)
  self.assertEqual(r.status,TaskStatus.COMPLETED);self.assertEqual(self.store.list_events(p.task_id)[0]["event_type"],"task_started")
 def test_controlled_requires_confirmation(self):
  runner=FakeRunner();p=self.plan(TaskStep("type","type_text",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p)
  self.assertEqual(r.status,TaskStatus.NEEDS_CONFIRMATION);self.assertFalse(runner.calls)
 def test_approval_is_passed_to_adapter(self):
  runner=FakeRunner();p=self.plan(TaskStep("type","type_text",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p,confirm=lambda step:True)
  self.assertEqual(r.status,TaskStatus.COMPLETED);self.assertTrue(runner.calls[0][1])
 def test_decline_stops(self):
  runner=FakeRunner();p=self.plan(TaskStep("type","type_text",RiskLevel.SAFE),TaskStep("launch","open_app",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p,confirm=lambda step:False)
  self.assertEqual(r.status,TaskStatus.CANCELLED);self.assertFalse(runner.calls)
 def test_unknown_blocked_even_if_model_marks_safe(self):
  runner=FakeRunner();p=self.plan(TaskStep("unknown","not_registered",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p)
  self.assertEqual(r.status,TaskStatus.BLOCKED);self.assertFalse(runner.calls)
 def test_failure_stops_remaining_steps(self):
  runner=FakeRunner([AutomationResult(False,"failed",False)]);p=self.plan(TaskStep("one","open_app",RiskLevel.SAFE),TaskStep("two","open_app",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p)
  self.assertEqual(r.status,TaskStatus.FAILED);self.assertEqual(len(runner.calls),1)
 def test_cancel_before_start(self):
  runner=FakeRunner();p=self.plan(TaskStep("one","open_app",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p,is_cancelled=lambda:True)
  self.assertEqual(r.status,TaskStatus.CANCELLED);self.assertFalse(runner.calls)
 def test_unverified_is_distinct(self):
  runner=FakeRunner([AutomationResult(True,"launch requested",False)]);p=self.plan(TaskStep("one","open_app",RiskLevel.SAFE));r=TaskExecutor(runner,self.store).run(p)
  self.assertEqual(r.status,TaskStatus.COMPLETED_UNVERIFIED);self.assertFalse(r.verified)
 def test_step_limit(self):
  runner=FakeRunner();p=self.plan(*[TaskStep("x","open_app",RiskLevel.SAFE) for _ in range(3)])
  with self.assertRaises(ValueError):TaskExecutor(runner,self.store,max_steps=2).run(p)
  self.assertFalse(runner.calls)
if __name__=="__main__":unittest.main()
