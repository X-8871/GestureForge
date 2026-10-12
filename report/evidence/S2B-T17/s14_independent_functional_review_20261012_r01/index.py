"""给已完成隔离审查补充真实工具版本和输入/日志绑定，不改原回执。"""
from pathlib import Path
import os, sys, json, hashlib, subprocess
from datetime import datetime, timezone, timedelta
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def digest(path):
    """绑定真实文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
receipt=json.loads((HERE/'final_review_receipt.json').read_text(encoding='utf-8'))
assert receipt['status']=='PASS_G2_FUNCTIONAL_ONLY'
assert digest(HERE/'review.py')==receipt['reviewer_source_sha256']
assert receipt['source_sha256_pre']==receipt['source_sha256_post']
for p,h in receipt['source_sha256_post'].items():assert digest(ROOT/p)==h
for test in receipt['tests']:
    for run in test['runs']:
        assert run['direct_wait_exit_code']==run['native_exit_code']==0
        for stream in ('stdout','stderr'):assert digest(ROOT/run[stream]['path'])==run[stream]['sha256']
tool=Path('D:/FPGA_S2A_MSYS2_20261001/env')
env=dict(os.environ,PATH=str(tool/'usr/bin')+os.pathsep+str(tool/'mingw64/bin')+os.pathsep+os.environ.get('PATH',''))
tools=[]
for name,exe in [('g++',tool/'mingw64/bin/g++.exe'),('make',tool/'usr/bin/make.exe')]:
    result=subprocess.run([str(exe),'--version'],cwd=HERE,env=env,capture_output=True,timeout=30)
    assert result.returncode==0
    (HERE/(name+'.version.stdout.log')).write_bytes(result.stdout)
    (HERE/(name+'.version.stderr.log')).write_bytes(result.stderr)
    tools.append({'name':name,'command':[str(exe),'--version'],'native_exit_code':result.returncode,
        'stdout':name+'.version.stdout.log','stderr':name+'.version.stderr.log',
        'version':result.stdout.decode('utf-8').splitlines()[0]})
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file() and 'obj_dir' not in p.parts and '__pycache__' not in p.parts:
        files.append({'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'size_bytes':p.stat().st_size})
index={'schema_version':1,'status':'PASS_G2_FUNCTIONAL_ONLY','source_commit':receipt['source_commit'],
    'final_review_receipt':{'path':(HERE/'final_review_receipt.json').relative_to(ROOT).as_posix(),'sha256':digest(HERE/'final_review_receipt.json')},
    'source_sha256':receipt['source_sha256_post'],'files':files,'tool_versions_supplement':tools,
    'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'command_transcript':[sys.executable,'-X','utf8','-B',str(HERE/'review.py')],
    'review_launch_tool_host_exit_code':0,'review_launch_direct_native_exit_code':'NOT_SEPARATELY_CAPTURED',
    'limitations':['audit_pre.json为测试前临时状态；最终结论仅final_review_receipt.json。','obj_dir为可重建编译缓存，不列长期证据；保留原始bench/向量/源副本/日志。','只审查功能G2；STA、PNR、G3–G5未批准。']}
with (HERE/'artifact_hash_index.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'status':index['status'],'files':len(files),'receipt_sha256':digest(HERE/'final_review_receipt.json'),'index_sha256':digest(HERE/'artifact_hash_index.json')},ensure_ascii=True))
