"""保留首次生成原字节，再生成绑定门禁代码的完整草稿；原生初次结果不覆盖。"""
import hashlib
import json
from pathlib import Path
import generate_drafts as generator

WORK=Path(__file__).parent
initial=WORK/'first_generation'; initial.mkdir()
rows=[]
for path in sorted(WORK.iterdir()):
 if path.is_file() and (path.name in ('collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','input_bindings.json','recovery_resolution.json') or path.name.endswith('.diff')):
  raw=path.read_bytes()
  with (initial/path.name).open('xb') as stream: stream.write(raw)
  rows.append(dict(path=path.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
with (initial/'snapshot.json').open('x',encoding='utf-8',newline='\n') as stream: json.dump(dict(reason='首次草稿未在prepare绑定新增门禁helper，保留原件后加强绑定；不删除/覆盖首次native原件',files=rows),stream,ensure_ascii=False,indent=2); stream.write('\n')
def generated(name,text):
 """仅重建上述已保存初版的生成产物，不改变日志或外部原件。"""
 path=WORK/name
 if path.exists():
  assert (initial/name).is_file()
 with path.open('w' if path.exists() else 'x',encoding='utf-8',newline='') as stream: stream.write(text)
generator.write=generated
generator.main()
