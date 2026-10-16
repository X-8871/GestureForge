from pathlib import Path
import sys, time, tempfile
from types import SimpleNamespace
from unittest import mock
repo=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(repo))
import verification.s2b_process_supervisor as supervisor
GIB=1024**3
class FakeJob:
    def __init__(self,**kwargs): self.closed=False; self.terminated=False
    def pid_list(self): return []
    def accounting(self): return {'active_processes':0,'total_processes':1}
    def terminate_own_job(self,code): self.terminated=True
    def close(self): self.closed=True
class FakeGuard:
    WAIT_OBJECT_0=0; WAIT_TIMEOUT=258; STILL_ACTIVE=259
    def __init__(self): self.exit_reads=0
    def JobObject(self,**kwargs): return FakeJob(**kwargs)
    def launch_suspended_root(self,job,executable,command,**kwargs):
        return SimpleNamespace(pid=123,process_handle=object(),
          process_info=SimpleNamespace(hProcess=object(),hThread=object()),closed=False)
    def _api_wait(self,handle,milliseconds): return self.WAIT_OBJECT_0
    def _api_get_exit_code(self,handle):
        self.exit_reads+=1
        if self.exit_reads==1: time.sleep(1.15)
        return 0
    def _checked_close_handle(self,handle,name): return None
guard=FakeGuard()
with tempfile.TemporaryDirectory(prefix='s2b-review-fake-job-') as work:
    log=Path(work)/'out.log'
    with log.open('w',encoding='utf-8') as stream, mock.patch.object(supervisor,'_load_job_guard',return_value=guard):
        result=supervisor.supervise_process(name='review-override-gap',command=['fixture'],cwd=work,
          environment={},output_stream=stream,timeout_seconds=5.0,
          memory_reader=lambda:(12*GIB,16*GIB),sample_interval_seconds=0.25,
          max_sample_gap_seconds=2.0,drain_timeout_seconds=10.0)
print('STATUS',result['status'])
print('MAX_SAMPLE_GAP',result['resource_monitor']['maximum_sample_gap_seconds'])
print('CONFIGURED_MAX_GAP',result['resource_monitor']['max_sample_gap_seconds'])
print('SAMPLE_COUNT',result['resource_monitor']['sample_count'])
print('EXIT_READS',guard.exit_reads)
assert result['status']=='PASS'
assert result['resource_monitor']['maximum_sample_gap_seconds']>1.0