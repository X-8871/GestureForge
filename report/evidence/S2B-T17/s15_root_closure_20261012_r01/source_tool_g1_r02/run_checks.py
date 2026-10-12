"""R2真实subprocess/direct wait正反向；所有输出只在本轮TMP。"""
import json,subprocess,sys,time
from pathlib import Path
import psutil
import source_closure as c
HERE=Path(__file__).parent;ROWS=[]
for label,tail,expected in [
 ('regressions_r02',[str(HERE/'regressions.py')],0),
 ('actual_closure_r02',[str(HERE/'source_closure.py'),'--request',str(HERE/'actual_request_r01.json'),'--output-dir',str(HERE/'s15_source_closure_actual_r02')],0),
 ('reject_existing_r02',[str(HERE/'source_closure.py'),'--request',str(HERE/'actual_request_r01.json'),'--output-dir',str(HERE/'s15_source_closure_actual_r02')],1)]:
    command=[sys.executable,'-X','utf8','-B',*tail];start=time.monotonic();peak=0;unknown=[];pre=c.binding(HERE/'source_closure.py')
    with (HERE/(label+'.stdout.bin')).open('xb') as out,(HERE/(label+'.stderr.bin')).open('xb') as err:
        child=subprocess.Popen(command,cwd=c.ROOT,stdout=out,stderr=err,creationflags=subprocess.DETACHED_PROCESS)
        while child.poll() is None:
            try:
                root=psutil.Process(child.pid);rss=0
                for item in [root,*root.children(recursive=True)]:
                    try:rss+=item.memory_info().rss
                    except psutil.NoSuchProcess:pass
                    except psutil.AccessDenied as error:unknown.append(repr(error))
                peak=max(peak,rss)
            except psutil.NoSuchProcess:pass
            except psutil.AccessDenied as error:unknown.append(repr(error))
            time.sleep(.05)
        code=child.wait()
    record=dict(command=command,native_exit_code=code,expected_exit_code=expected,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,sampled_tree_peak_bytes=peak,absolute_tree_peak_bytes=None,resource_sampling_unknown=unknown,tool_before=pre,tool_after=c.binding(HERE/'source_closure.py'),stdout=c.binding(HERE/(label+'.stdout.bin')),stderr=c.binding(HERE/(label+'.stderr.bin')))
    c.save(HERE/(label+'.wait.json'),record);ROWS.append(record)
    assert code==expected and record['tool_before']==record['tool_after'],record
c.save(HERE/'real_waits_r02.json',dict(status='PASS_G1_ONLY',waits=ROWS))
print(json.dumps(dict(status='PASS_G1_ONLY',wait_count=len(ROWS),elapsed_seconds=sum(row['elapsed_seconds'] for row in ROWS),sampled_tree_peak_bytes=max(row['sampled_tree_peak_bytes'] for row in ROWS)),ensure_ascii=False))
