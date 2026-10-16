from pathlib import Path
import sys,tempfile
from unittest import mock
from types import SimpleNamespace
repo=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(repo))
import verification.s2b_process_supervisor as supervisor
GIB=1024**3
class Clock:
    value=0.0
    def monotonic(self): return self.value
    def sleep(self,seconds): self.value+=max(0.0,seconds)
clock=Clock()
class FakeJob:
    def __init__(self,**kwargs): self.closed=False; self.pid_queries=0; self.terminated=False
    def pid_list(self):
        self.pid_queries+=1
        if self.pid_queries==1 or clock.value>=10.05: return []
        return [9876]
    def accounting(self): return {'active_processes':0 if self.pid_queries==1 or clock.value>=10.05 else 1,'total_processes':2}
    def terminate_own_job(self,code): self.terminated=True
    def close(self): self.closed=True
class FakeGuard:
    WAIT_OBJECT_0=0; WAIT_TIMEOUT=258; STILL_ACTIVE=259
    def JobObject(self,**kwargs): return FakeJob(**kwargs)
    def launch_suspended_root(self,job,executable,command,**kwargs):
        return SimpleNamespace(pid=456,process_handle=object(),process_info=SimpleNamespace(hProcess=object(),hThread=object()),closed=False)
    def _api_wait(self,handle,milliseconds): return self.WAIT_OBJECT_0
    def _api_get_exit_code(self,handle): return 0
    def _checked_close_handle(self,handle,name): return None
with tempfile.TemporaryDirectory(prefix='s2b-review-drain-cap-') as work:
    with (Path(work)/'output.log').open('w',encoding='utf-8') as output, \
         mock.patch.object(supervisor,'_load_job_guard',return_value=FakeGuard()), \
         mock.patch.object(supervisor.time,'monotonic',clock.monotonic), \
         mock.patch.object(supervisor.time,'sleep',clock.sleep):
        result=supervisor.supervise_process(name='review-drain-override',command=['fixture'],cwd=work,
          environment={},output_stream=output,timeout_seconds=30.0,
          memory_reader=lambda:(12*GIB,16*GIB),sample_interval_seconds=0.25,
          max_sample_gap_seconds=1.0,drain_timeout_seconds=20.0)
print('STATUS',result['status'])
print('DRAIN_TIMEOUT_CONFIGURED',result['cleanup']['natural_drain']['timeout_seconds'])
print('DRAIN_ELAPSED',result['cleanup']['natural_drain']['elapsed_seconds'])
print('MAX_SAMPLE_GAP',result['resource_monitor']['maximum_sample_gap_seconds'])
print('OVERALL_TIMEOUT',result['timeout_seconds'])
assert result['status']=='PASS'
assert result['cleanup']['natural_drain']['elapsed_seconds']>10.0
assert result['resource_monitor']['maximum_sample_gap_seconds']<=1.0