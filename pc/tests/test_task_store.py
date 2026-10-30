import tempfile
import unittest
from pathlib import Path

from myra_pc.models import RiskLevel, TaskPlan, TaskStatus, TaskStep
from myra_pc.task_store import TaskStore


class TaskStoreTests(unittest.TestCase):
    def test_persists_plan_and_updates_status(self):
        with tempfile.TemporaryDirectory() as temp:
            store = TaskStore(Path(temp) / "tasks.sqlite3")
            plan = TaskPlan(
                title="Open Notepad",
                steps=(TaskStep("Open Notepad", "open_app", RiskLevel.SAFE),),
            )
            store.add(plan)
            saved = store.get(plan.task_id)
            self.assertIsNotNone(saved)
            self.assertEqual(saved["title"], "Open Notepad")
            self.assertTrue(store.update_status(plan.task_id, TaskStatus.COMPLETED))
            self.assertEqual(store.get(plan.task_id)["status"], "completed")
            self.assertFalse(store.update_status("missing", TaskStatus.FAILED))

    def test_rejects_unbounded_list_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            store = TaskStore(Path(temp) / "tasks.sqlite3")
            with self.assertRaises(ValueError):
                store.list_recent(0)


if __name__ == "__main__":
    unittest.main()
