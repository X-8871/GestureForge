"""轻量窄回归真实原流及direct wait记录；禁止重跑覆写既有RunId。"""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
HERE=Path(__file__).parent;ROOT=HERE.parents[3];RUN='r03'
def bind(p):
    raw=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
pre=bind(HERE/'source_closure.py');start=time.monotonic();peak=0;unknown=[]
command=[sys.executable,'-X','utf8','-B',str(HERE/'regressions.py')]
with (HERE/('regressions_'+RUN+'.stdout.bin')).open('xb') as out,(HERE/('regressions_'+RUN+'.stderr.bin')).open('xb') as err:
    env=dict(os.environ,SOURCE_FALLBACK_TEST_RUN=RUN)
    child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.DETACHED_PROCESS,env=env)
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
row=dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,sampled_tree_peak_bytes=peak,absolute_tree_peak_bytes=None,resource_sampling_unknown=unknown,tool_before=pre,tool_after=bind(HERE/'source_closure.py'),stdout=bind(HERE/('regressions_'+RUN+'.stdout.bin')),stderr=bind(HERE/('regressions_'+RUN+'.stderr.bin')))
with (HERE/('regressions_'+RUN+'.wait.json')).open('x',encoding='utf-8',newline='\n') as stream:json.dump(row,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(row,ensure_ascii=False));raise SystemExit(code)
