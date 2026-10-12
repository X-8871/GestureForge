"""保留初版包装错误并按既有任务目录生成新版清单；生产源码保持STOP。"""
from pathlib import Path
import sys,json,subprocess,time,hashlib,shutil

repo=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
run='s14_arithmetic_fix_20261012_r01'
evidence=repo/'report/evidence/S2B-T17'/run
work=repo/'tmp/2B/S2B-T17'/run

def sha(path):
    """绑定原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,data):
    """旧运行和旧清单不覆盖。"""
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    """重现初版包装失败的实际原生码，再仅纠正清单任务编号。"""
    target=evidence/'delivery_manifest_r02.json'
    if target.exists():raise ValueError('r02已存在')
    source=evidence/'delivery_manifest.json'
    command=[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',source.relative_to(repo).as_posix()]
    start=time.monotonic();child=subprocess.Popen(command,cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout,stderr=child.communicate(timeout=30);code=child.wait(timeout=30)
    assert code==2
    result=json.loads(stdout.decode('utf-8'))
    assert result['status']=='CHECKS_FAILED' and result['errors']==['evidence_dir 必须精确等于 report/evidence/S2B-T17-S14/'+run]
    for name,data in [('packaging_failure_replay.stdout.log',stdout),('packaging_failure_replay.stderr.log',stderr)]:
        with (evidence/name).open('xb') as f:f.write(data)
    save(evidence/'packaging_failure_replay.native.json',dict(command=command,cwd=str(repo),pid=child.pid,native_exit_code=code,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-start,terminal_state='EXITED_DIRECT_CHILD_WAIT',first_tool_host_exit_code=1,first_tool_native_exit_code='NOT_CAPTURED',note='初次PowerShell宿主归一化为1；本次原生重现2仅用于闭合包装错误证据，不改变功能G1。'))
    shutil.copyfile(Path(__file__),evidence/'g1_packaging_source_r02.py')
    manifest=json.loads(source.read_text(encoding='utf-8'))
    manifest['task_id']='S2B-T17'
    manifest['limitations'].append('初版清单task_id误写S2B-T17-S14与既有S2B-T17目录不符，实际包装失败及原生重现2保留；r02仅纠正目录绑定编号。')
    manifest['files']=[i for i in manifest['files'] if not i['path'].startswith(evidence.relative_to(repo).as_posix()+'/')]
    for path in sorted(evidence.rglob('*')):
        if not path.is_file():continue
        role='source' if 'source_snapshot' in path.parts or path.suffix=='.py' else 'log' if path.suffix=='.log' else 'input' if path.suffix in ['.txt','.dat','.sv'] else 'result'
        manifest['files'].append(dict(path=path.relative_to(repo).as_posix(),sha256=sha(path),role=role))
    save(target,manifest)
    print(json.dumps(dict(status='PACKAGING_R02_READY_FUNCTIONAL_G1_UNCHANGED',manifest_sha256=sha(target),receipt_sha256=sha(evidence/'final_receipt.json'),files=len(manifest['files']),native_failure_replay_exit_code=code),ensure_ascii=False))

if __name__=='__main__':main()
