from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .automation.contracts import AutomationResult, DesktopAction
from .models import RiskLevel, TaskPlan, TaskStatus, TaskStep
from .safety import classify_action, requires_confirmation
from .task_store import TaskStore
@dataclass(frozen=True, slots=True)
class StepExecution:
    index:int
    action:str
    status:str
    message:str
    verified:bool
@dataclass(frozen=True, slots=True)
class TaskExecutionResult:
    task_id:str
    status:TaskStatus
    steps:tuple[StepExecution,...]
    verified:bool
class TaskExecutor:
    def __init__(self,runner,store:TaskStore,max_steps:int=12):
        if not 1<=max_steps<=50: raise ValueError('max_steps must be between 1 and 50')
        self.runner,self.store,self.max_steps=runner,store,max_steps
    def run(self,plan:TaskPlan,confirm:Callable[[TaskStep],bool]|None=None,is_cancelled:Callable[[],bool]|None=None):
        if not plan.steps or len(plan.steps)>self.max_steps: raise ValueError('empty plan or step limit exceeded')
        self.store.add(plan);self.store.update_status(plan.task_id,TaskStatus.RUNNING);self.store.record_event(plan.task_id,'task_started',{'title':plan.title,'step_count':len(plan.steps)})
        results=[];verified_all=True
        for i,step in enumerate(plan.steps,1):
            if is_cancelled and is_cancelled(): return self._finish(plan.task_id,TaskStatus.CANCELLED,results,False,'task_cancelled')
            risk=classify_action(step.action)
            if risk is RiskLevel.BLOCKED: return self._finish(plan.task_id,TaskStatus.BLOCKED,results,False,'task_blocked')
            approved=False
            if requires_confirmation(step.action):
                if confirm is None: return self._finish(plan.task_id,TaskStatus.NEEDS_CONFIRMATION,results,False,'task_needs_confirmation')
                try: approved=bool(confirm(step))
                except Exception: return self._finish(plan.task_id,TaskStatus.NEEDS_CONFIRMATION,results,False,'confirmation_error')
                if not approved: return self._finish(plan.task_id,TaskStatus.CANCELLED,results,False,'task_cancelled')
            self.store.record_event(plan.task_id,'step_started',{'index':i,'action':step.action,'risk':risk.value})
            try: outcome=self.runner.execute(DesktopAction(step.action,dict(step.parameters)),confirmed=approved)
            except Exception as exc: outcome=AutomationResult(False,f'Action adapter error: {exc}',False)
            results.append(StepExecution(i,step.action,'completed' if outcome.success else 'failed',outcome.message,bool(outcome.verified)))
            self.store.record_event(plan.task_id,'step_completed' if outcome.success else 'step_failed',{'index':i,'action':step.action,'message':outcome.message,'verified':bool(outcome.verified)})
            if not outcome.success: return self._finish(plan.task_id,TaskStatus.FAILED,results,False,'task_failed')
            verified_all=verified_all and bool(outcome.verified)
        status=TaskStatus.COMPLETED if verified_all else TaskStatus.COMPLETED_UNVERIFIED
        return self._finish(plan.task_id,status,results,verified_all,'task_finished')
    def _finish(self,task_id,status,steps,verified,event):
        self.store.update_status(task_id,status);self.store.record_event(task_id,event,{'verified':verified})
        return TaskExecutionResult(task_id,status,tuple(steps),verified)
