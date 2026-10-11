"""独立捕获封存子进程实际码，待所有日志关闭后冻结完整raw与最终receipt。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

WORK=Path(__file__).parent;ROOT=WORK.parents[3]
command=[sys.executable,'-X','utf8','-B',str(WORK/'seal_r02.py')];started=time.monotonic();peak=None;reason=None
with (WORK/'seal.stdout.raw').open('xb') as stdout,(WORK/'seal.stderr.raw').open('xb') as stderr:
 child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr);process=psutil.Process(child.pid);birth=process.create_time()
 while child.poll() is None:
  try:
   if process.create_time()==birth:peak=max(peak or 0,sum(p.memory_info().rss for p in [psutil.Process(),process]+process.children(recursive=True) if p.is_running()))
  except psutil.NoSuchProcess:pass
  if (peak or 0)>128*1024**2 or time.monotonic()-started>180:
   reason='OWNED_NATIVE_LIMIT'
   if child.poll() is None and psutil.Process(child.pid).create_time()==birth:child.terminate()
   break
  time.sleep(.03)
 code=child.wait(timeout=10)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
 """所有输出创建新文件，失败不删除或覆盖。"""
 with (WORK/name).open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
save('seal.native.json',dict(actual_outer_command=sys.orig_argv,command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=code,elapsed_seconds=time.monotonic()-started,sampled_owned_tree_peak_bytes=peak,absolute_peak_bytes=None,failure=reason))
if code or reason:
 print(json.dumps(dict(status='FAIL_PRESERVED',native_exit_code=code),ensure_ascii=False));raise SystemExit(2)
files=sorted(path for path in WORK.rglob('*') if path.is_file());assert sum(path.stat().st_size for path in files)<100*1024**2
rows=[]
for path in files:
 assert not path.is_symlink() and not path.is_junction()
 rows.append(dict(path=path.relative_to(WORK).as_posix(),absolute_path=str(path),sha256=sha(path),bytes=path.stat().st_size))
with (WORK/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
 for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
pre=json.loads((WORK/'preseal_receipt.json').read_text(encoding='utf-8'));native=json.loads((WORK/'native_r02_receipt.json').read_text(encoding='utf-8'))
nested=[row for name in ('validate','harness') for row in json.loads((WORK/(name+'.wrapper.json')).read_text(encoding='utf-8'))['records']]
save('compatibility_delivery_receipt.json',dict(status='STOP_COMPAT_LOGIC_G1_PENDING_G2',task='S12-PH-COMPAT2-R2',entry=str(WORK/'final_draft_binding.json'),preseal_receipt_sha256=sha(WORK/'preseal_receipt.json'),
 total_fixture_checks=pre['total_fixture_checks'],raw_manifest=dict(path=str(WORK/'raw_manifest.jsonl'),sha256=sha(WORK/'raw_manifest.jsonl'),files=len(rows),bytes=sum(row['bytes'] for row in rows)),
 outer_native_codes=[row['native_exit_code'] for row in native['records']]+[code],nested_native_codes=[row['native_exit_code'] for row in nested],head_native_code=0,
 outer_native_elapsed_seconds=sum(row['elapsed_seconds'] for row in native['records']),seal_native_elapsed_seconds=time.monotonic()-started,
 sampled_owned_tree_peak_bytes=max([row['sampled_owned_tree_peak_bytes'] or 0 for row in native['records']]+[peak or 0]),absolute_peak_bytes=None,
 source_commit=None,actual_head_observation=pre['actual_head_observation'],physical_g0='BLOCKED_PENDING_REAL_PINS',compat_g2='NOT_RUN',actual_pins='NOT_PINNED',actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED',g3='NOT_RUN',g5='NOT_RUN',
 initial_derive_native_python_code=None,initial_derive_note='直接工具宿主码0转录不冒称Python独立码；后续逐字节重建核验actual native0。',production_or_old_artifacts_or_git_changed=False,hardware_or_heavy=False))
print(json.dumps(dict(status='STOP',receipt_sha256=sha(WORK/'compatibility_delivery_receipt.json'),raw_manifest_sha256=sha(WORK/'raw_manifest.jsonl'),files=len(rows),bytes=sum(row['bytes'] for row in rows)),ensure_ascii=False))
