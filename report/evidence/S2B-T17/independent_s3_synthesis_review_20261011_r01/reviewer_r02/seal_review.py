"""封存独立审查原件，仅写两次专用审查目录的新文件。"""
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
root=Path.cwd().resolve()
parent=root/'tmp/2B/S2B-T17'
dirs=[parent/'independent_s3_synthesis_review_20261011_r01',parent/'independent_s3_synthesis_review_20261011_r02']
assert all(d.is_dir() and not d.is_symlink() for d in dirs)

def save(path,value):
    """只创建新封存文件，保留原审查失败字节。"""
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)
        stream.write('\n')

def digest(path):
    raw=path.read_bytes()
    return {'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'role':'input' if path.suffix=='.py' else 'result'}

for index,d in enumerate(dirs):
    save(d/'review.native.json',dict(command=['python','-B',str(d/'review_s3.py')],cwd=str(root),
         native_exit_code=1 if index==0 else 0,
         observation_source='functions.exec tools.exec_command Git Bash调用返回的实际exit_code',
         stdout=digest(d/'review.stdout.log'),stderr=digest(d/'review.stderr.log'),
         business_status='FAIL_TIMING',scope='原生码为Reviewer审查脚本码，不是综合/业务成功码。'))

save(dirs[0]/'diagnostic_observations.json',dict(
    prior_inspection_attempts=[
        dict(status='FAILED_BEFORE_EXECUTION',native_exit_code=1,reason='PowerShell嵌套引号解析错误，初次只读inspect未执行。'),
        dict(status='PARTIAL_STDOUT_INSPECTION_FAILED',native_exit_code=1,reason='Python stdout默认GBK不能输出原件中的字符，改用UTF-8输出；未写被审证据。'),
        dict(status='PASS_READ_ONLY_INSPECTION',native_exit_code=0,reason='UTF-8结构化读取正常，原始工具输出在调用记录中；不捏造缺失stdout文件。')],
    review_failure=dict(native_exit_code=1,reason='1713项PASS；超时文本错误期待TIMEOUT，真实原件timed out after300s。原脚本/检查日志/receipt仍保留。')))

for d in dirs:
    files=[digest(p) for p in sorted(d.rglob('*')) if p.is_file()]
    assert not (d/'raw_delivery_manifest.json').exists()
    save(d/'raw_delivery_manifest.json',dict(schema_version=1,role='INDEPENDENT_REVIEWER_RAW_ARCHIVE',
         files=files,source_commit='f3a0b0514c90983c41c8729b93f18d627bfc1bb5',
         reviewed_manifest=dict(path='report/evidence/S2B-T17/s3_platform_20261011_r01/s3_collection_delivery_manifest_r03.json',sha256='86d9aff8dcda7161bc5027b5906824a59748e1439ed6e87e76637d086409bcd0'),
         business_status='FAIL_TIMING',self_binding='本清单不自绑定，SHA通过最终回传固定。',
         prior_attempt=digest(dirs[0]/'raw_delivery_manifest.json') if d==dirs[1] else None))
    print(json.dumps(dict(directory=str(d),raw_manifest=digest(d/'raw_delivery_manifest.json'),receipt=digest(d/'receipt.json'),files=len(files),bytes=sum(v['bytes'] for v in files)),ensure_ascii=False))
