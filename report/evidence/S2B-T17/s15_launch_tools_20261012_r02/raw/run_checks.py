"""真实轻量检查原流、wait与采样峰记录；不清理任何失败原件。"""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
import native_contract as contract
W=Path(__file__).parent;ROOT=W.parents[3];ROWS=[]
def bind(p):
    raw=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
for label,script in [('r2_metadata_final_r03','r2_regressions.py'),('r2_extra_final_r01','extra_regressions.py'),('r2_layout_r01','make_layout.py')]:
    command=[sys.executable,'-X','utf8','-B',str(W/script)];pre=contract.capture_tools(W,ROOT);start=time.monotonic();peak=0;unknown=[]
    stdout=W/(label+'.stdout.bin');stderr=W/(label+'.stderr.bin')
    with stdout.open('xb') as out,stderr.open('xb') as err:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.DETACHED_PROCESS)
        while proc.poll() is None:
            try:
                tree=psutil.Process(proc.pid);members=[tree,*tree.children(recursive=True)];rss=0
                for member in members:
                    try:rss+=member.memory_info().rss
                    except psutil.NoSuchProcess:pass
                    except psutil.AccessDenied as error:unknown.append(repr(error))
                peak=max(peak,rss)
            except psutil.NoSuchProcess:pass
            except psutil.AccessDenied as error:unknown.append(repr(error))
            time.sleep(.05)
        code=proc.wait()
    post=contract.capture_tools(W,ROOT)
    row=dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,sampled_tree_peak_bytes=peak,absolute_tree_peak_bytes=None,
             resource_sampling_unknown=unknown,stdout=bind(stdout),stderr=bind(stderr),tool_bindings_before=pre,tool_bindings_after=post)
    with (W/(label+'.wait.json')).open('x',encoding='utf-8',newline='\n') as stream:json.dump(row,stream,ensure_ascii=False,indent=2);stream.write('\n')
    ROWS.append(row)
    if code!=0 or pre!=post:print(json.dumps(row,ensure_ascii=False));raise SystemExit(code or 2)
with (W/'r2_final_waits.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(dict(status='PASS_G1_ONLY',waits=ROWS),stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status='PASS_G1_ONLY',wait_count=len(ROWS),elapsed_seconds=sum(row['elapsed_seconds'] for row in ROWS),sampled_tree_peak_bytes=max(row['sampled_tree_peak_bytes'] for row in ROWS)),ensure_ascii=False))
