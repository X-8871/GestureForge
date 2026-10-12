"""R2工具恢复映射，只创建新证据，不恢复覆盖任何原件。"""
from pathlib import Path
import hashlib,json
W=Path(__file__).parent;ROOT=W.parents[3]
D=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r02'
assert D.is_dir() and not (D/'tools').exists()
(D/'tools').mkdir();rows=[];tools=[]
for name in ['guard.py','supervisor.py']:
    p=W/name;raw=p.read_bytes();target=D/'tools'/name
    with target.open('xb') as stream:stream.write(raw)
    digest=hashlib.sha256(raw).hexdigest()
    rows.append(dict(original_absolute_path=str(p),sha256=digest,archived_repo_path=target.relative_to(ROOT).as_posix(),bytes=len(raw)))
    tools.append(dict(destination_absolute_path=str(p),sha256=digest,artifact_repo_path=target.relative_to(ROOT).as_posix()))
for name,value in [('archive_mapping.json',dict(binding_rows=rows,production_source_commit=None)),('recovery_entry.json',dict(fixed_project_root=str(ROOT),fixed_guard_sha256=rows[0]['sha256'],fixed_supervisor_sha256=rows[1]['sha256'],tool_files=tools,restore_performed=False))]:
    with (D/name).open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(name,hashlib.sha256((D/name).read_bytes()).hexdigest())
