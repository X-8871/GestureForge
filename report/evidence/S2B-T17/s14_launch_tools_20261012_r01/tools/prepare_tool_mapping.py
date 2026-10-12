"""仅绑定新guard/SUP实际原件和未来本正式包恢复位置，不做SOURCE冻结。"""
import json
from pathlib import Path
import hashlib
import compat_pins as p

D=p.exact(p.ARCHIVE,True)
rows=[]; tools=[]
for path,expected in ((p.GUARD,p.GUARD_SHA),(p.SUP,p.SUP_SHA)):
    path=p.exact(path); raw=path.read_bytes(); actual=hashlib.sha256(raw).hexdigest()
    assert actual==expected
    repo=(D/"tools"/path.name).relative_to(p.ROOT).as_posix()
    rows.append(dict(original_absolute_path=str(path),sha256=actual,bytes=len(raw),archived_repo_path=repo))
    tools.append(dict(destination_absolute_path=str(path),sha256=actual,artifact_repo_path=repo))
items={"archive_mapping.json":dict(binding_rows=rows), "recovery_entry.json":dict(fixed_project_root=str(p.ROOT),fixed_guard_sha256=p.GUARD_SHA,fixed_supervisor_sha256=p.SUP_SHA,tool_files=tools,scope="S14工具恢复，不是生产SOURCE冻结；新工具G2/源码/资源入口仍PENDING。")}
for name,row in items.items():
    path=D/name; assert not path.exists()
    with path.open("x",encoding="utf-8",newline="\n") as stream: json.dump(row,stream,ensure_ascii=False,indent=2); stream.write("\n")
    print(json.dumps(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),ensure_ascii=False))
