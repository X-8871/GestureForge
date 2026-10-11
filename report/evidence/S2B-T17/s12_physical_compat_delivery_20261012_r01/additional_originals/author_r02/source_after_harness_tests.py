"""调用完整source-after主函数的隔离模拟；Git返回值不是实际Git或物理运行码。"""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import compat_pins as p

WORK=p.WORK; FIX=WORK/'after_harness'; FIX.mkdir()
results=[]
def module(name,path):
 """只导入待审草稿，不运行CLI。"""
 spec=importlib.util.spec_from_file_location(name,path);item=importlib.util.module_from_spec(spec);spec.loader.exec_module(item);return item
c=module('harness_common',WORK/'collector.py')
after=module('harness_after',WORK/'source_after_check.py')
original_dump=json.dump
def fixture_dump(obj,stream,*args,**kwargs):
 """生成的成功标记和原生码明确改名为合成期望，不能误作真实证据。"""
 if isinstance(obj,dict):
  obj=dict(obj,fixture_test=True,git_commands_not_executed=True)
  if 'status' in obj:obj['synthetic_expected_status']=obj.pop('status');obj['status']='SYNTHETIC_TEST_ONLY'
  if 'native_exit_code' in obj:obj['synthetic_native_exit_code']=obj.pop('native_exit_code')
 original_dump(obj,stream,*args,**kwargs)

def run_case(name,kind=None,expected=None):
 """文件与哈希真实存在，Git/冻结就绪/公共静态闭包为显式测试替身。"""
 base=FIX/name;base.mkdir()
 cache=base/'cache';cache.mkdir()
 pre=base/'pre';pre.mkdir()
 names=['src/FIXTURE_'+str(i)+'.sv' for i in range(43)]
 raw={name:('SYNTHETIC '+name+'\n').encode('utf-8') for name in names}
 for path,data in raw.items():
  target=base/path;target.parent.mkdir(exist_ok=True)
  with target.open('xb') as stream:stream.write(data)
 hashes={path:hashlib.sha256(data).hexdigest() for path,data in raw.items()}
 frozen14={path:hashes[path] for path in names[:14]};static={path:hashes[path] for path in names[:33]}
 freeze=dict(source_commit='0'*40,profile='s2b-inference-platform/0.1.12',source_files=[dict(path=path,sha256=digest) for path,digest in hashes.items()],frozen14=frozen14,fixture_test=True)
 freeze_path=base/'freeze.json'
 with freeze_path.open('x',encoding='utf-8') as stream:original_dump(freeze,stream)
 before=dict(source_commit='0'*40,source_files=freeze['source_files'],frozen14_sha256=frozen14,fixture_test=True)
 if kind=='before_commit':before['source_commit']='1'*40
 with (pre/'source_before.json').open('x',encoding='utf-8') as stream:original_dump(before,stream)
 profile=dict(version='s2b-inference-platform/0.1.12',rtl_sources=names[:18],source_derivation=dict(derived_sources=names[:8]),clock_hz=50000000,visibility_default=0)
 previous=(after.ROOT,after.CACHE,after.COMMIT,c.ROOT,c.FREEZE,c.FREEZE_SHA,c.load_freeze,p.SOURCE_PRE,p.require_ready,sys.argv,after.subprocess.run,after.importlib.util.spec_from_file_location,after.importlib.util.module_from_spec)
 after.ROOT=base;after.CACHE=cache;after.COMMIT='0'*40;c.ROOT=base;c.FREEZE=freeze_path;c.FREEZE_SHA=hashlib.sha256(freeze_path.read_bytes()).hexdigest()
 c.load_freeze=lambda:(freeze,hashes,static,profile);p.SOURCE_PRE=pre;p.require_ready=lambda pnr=False:None
 after.importlib.util.spec_from_file_location=lambda *args:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda value:None))
 after.importlib.util.module_from_spec=lambda spec:c
 calls=[];head_count=0
 def git_fixture(command,**kwargs):
  """提供合成Git输出，不启动git进程，不读取实际Git对象。"""
  nonlocal head_count
  calls.append(command)
  operation=command[3:]
  if kind=='git_failure':return types.SimpleNamespace(returncode=2,stdout=b'',stderr=b'SYNTHETIC_GIT_FAILURE')
  if operation==['rev-parse','HEAD']:
   head_count+=1;head=('1'*40 if kind=='head_start' or (kind=='head_end' and head_count>1) else '0'*40)
   return types.SimpleNamespace(returncode=0,stdout=(head+'\n').encode('ascii'),stderr=b'')
  assert operation[0]=='show'
  path=operation[1].split(':',1)[1];data=raw[path]
  if kind=='git_blob_drift':data=b'SYNTHETIC_BAD_BLOB'
  if kind=='raw_drift_window' and path==names[-1]:
   with (base/names[0]).open('ab') as stream:stream.write(b'CHANGED')
  return types.SimpleNamespace(returncode=0,stdout=data,stderr=b'')
 after.subprocess.run=git_fixture
 out=cache/'source_after_check_r1'
 if kind=='outside':out=base/'source_after_check_r1'
 if kind=='overwrite':
  out.mkdir()
  with (out/'DO_NOT_OVERWRITE').open('xb') as stream:stream.write(b'EXISTING_FIXTURE')
 sys.argv=['source_after_check.py','--expected-head','0'*40,'--output-dir',str(out)]
 captured=io.StringIO();json.dump=fixture_dump
 try:
  with contextlib.redirect_stdout(captured):after.main()
  assert expected is None,'误接受：'+name
  record=json.loads((out/'source_after.json').read_text(encoding='utf-8'))
  assert record['status']=='SYNTHETIC_TEST_ONLY' and record['synthetic_expected_status']=='PASS_SOURCE_AFTER_ONLY'
  assert len(record['source_files'])==43 and len(record['static_source_sha256'])==33 and len(calls)==45
  assert all(hashlib.sha256((base/row['snapshot']).read_bytes()).hexdigest()==row['sha256'] for row in record['source_files'])
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='accepted_synthetic',source_count=43,static_count=33,synthetic_git_calls=len(calls),actual_git_calls=0))
 except (ValueError,AssertionError) as error:
  assert expected is not None and expected in str(error),name+':'+repr(error)
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='rejected',exception=repr(error),synthetic_git_calls=len(calls),actual_git_calls=0))
 finally:
  json.dump=original_dump
  (after.ROOT,after.CACHE,after.COMMIT,c.ROOT,c.FREEZE,c.FREEZE_SHA,c.load_freeze,p.SOURCE_PRE,p.require_ready,sys.argv,after.subprocess.run,after.importlib.util.spec_from_file_location,after.importlib.util.module_from_spec)=previous
run_case('valid_complete_main')
run_case('wrong_initial_HEAD','head_start','实际HEAD不同')
run_case('changed_final_HEAD','head_end','真实HEAD变化')
run_case('git_native_failure_preserved','git_failure','真实Git命令失败')
run_case('wrong_before_commit','before_commit','继承本轮before')
run_case('Git_RAW_blob_drift','git_blob_drift','Git blob与RAW')
run_case('RAW_changed_during_check','raw_drift_window','核验期间RAW变化')
run_case('output_outside_cache','outside','输出必须为本PNR')
run_case('existing_output_kept','overwrite','输出已存在')
with (WORK/'after_harness_results.json').open('x',encoding='utf-8',newline='\n') as stream:original_dump(dict(status='PASS_SOURCE_AFTER_HARNESS_FIXTURES_ONLY',cases=results,count=len(results),actual_git_calls=0,synthetic_exit_codes=True,actual_STA='NOT_RUN',source_commit=None),stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status='PASS_SOURCE_AFTER_HARNESS_FIXTURES_ONLY',cases=len(results),actual_git_calls=0),ensure_ascii=False))
