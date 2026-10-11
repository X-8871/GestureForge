"""核对新r02完整源码及P2回归，旧r01与独审失败原件只读且保持SHA。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import compat_pins as p

WORK=p.WORK;ROOT=p.ROOT;OLD=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
 """只创建新封存元数据，不改被测文件或原失败记录。"""
 with (WORK/name).open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def main():
 """当前HEAD仅只读观察，不作为仍未冻结的源码commit。"""
 inputs=json.loads((WORK/'input_bindings.json').read_text(encoding='utf-8'))
 for row in inputs:
  path=p.exact(Path(row['path']));assert sha(path)==row['sha256']
  if 'bytes' in row:assert path.stat().st_size==row['bytes']
 native=json.loads((WORK/'native_r02_receipt.json').read_text(encoding='utf-8'))
 assert native['status']=='PASS_NATIVE_LIGHTWEIGHT_ONLY'
 old57=json.loads((WORK/'fixture_results.json').read_text(encoding='utf-8'))
 old9=json.loads((WORK/'after_harness_results.json').read_text(encoding='utf-8'))
 new=json.loads((WORK/'r02_regression_results.json').read_text(encoding='utf-8'))
 assert old57['count']==57 and old9['count']==9 and new['old_matrix_accepted']==19 and new['new_matrix_rejected']==25
 for wrapper in ('validate','harness'):
  assert json.loads((WORK/(wrapper+'.wrapper.json')).read_text(encoding='utf-8'))['status']=='PASS_CHEAP_ONLY'
 assert p.SOURCE_COMMIT is None and p.SOURCE_FREEZE_SHA is None and p.FUNCTIONAL_G2_SHA is None
 old_impl=(OLD/'impl_collector.py').read_text(encoding='utf-8');new_impl=(WORK/'impl_collector.py').read_text(encoding='utf-8')
 def function_bytes(text,name):
  node=next(node for node in ast.parse(text).body if isinstance(node,ast.FunctionDef) and node.name==name)
  return ast.get_source_segment(text,node).encode('utf-8')
 assert function_bytes(old_impl,'timing')==function_bytes(new_impl,'timing')
 assert (OLD/'compat_pins.py').read_bytes()==(WORK/'compat_pins.py').read_bytes()
 common=sha(WORK/'collector.py');assert repr(common) in new_impl and repr(common) in (WORK/'source_after_check.py').read_text(encoding='utf-8')
 assert (OLD/'native.py').read_bytes()==(WORK/'native.py').read_bytes()
 assert (OLD/'native_source_after.py').read_bytes()==(WORK/'native_source_after.py').read_bytes()
 files=['collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','compat_pins.py']
 save('final_draft_binding.json',dict(status='FROZEN_COMPAT_LOGIC_G1_ONLY_PENDING_G2',files=[dict(path=name,sha256=sha(WORK/name),bytes=(WORK/name).stat().st_size,diff=name+'.diff') for name in files],
  source_commit=None,EVIDENCE_HEAD_AT_PREPARATION=None,source_freeze_sha=None,functional_g2_sha=None,
  actual_tool_restore=[p.resolve_permanent(p.GUARD,p.GUARD_SHA),p.resolve_permanent(p.SUP,p.SUP_SHA)],
  unchanged_sta_timing_function=True,unchanged_compat_pins=True,unchanged_native_helpers=True,
  required_production_cli=dict(synth=['prepare','source','collect','seal'],pnr=['prepare','collect','classify'],source_after=['--expected-head','--output-dir']),new_production_flags=False))
 command=[r'C:\Program Files\Git\bin\bash.exe','-lc','git -c core.longpaths=true -c maintenance.auto=false rev-parse HEAD']
 started=time.monotonic();process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
 for name,data in (('head.stdout.raw',process.stdout),('head.stderr.raw',process.stderr)):
  with (WORK/name).open('xb') as stream:stream.write(data)
 save('head.native.json',dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=process.returncode,elapsed_seconds=time.monotonic()-started,sampled_peak_bytes=None,absolute_peak_bytes=None))
 assert process.returncode==0
 observed_head=process.stdout.decode('utf-8').strip()
 save('initial_derive_tool_transcription.json',dict(capture_kind='Codex exec_command直接调用结果转录，非独立native stdout/stderr文件',
  command=[r'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe','-X','utf8','-B',str(WORK/'derive_r02.py')],
  tool_host_exit_code=0,native_python_exit_code=None,stdout_stderr_split=None,tool_wall_seconds=0.5780292,
  tool_combined_output='{"status": "R02_MINIMAL_PATCH_GENERATED_BLOCKED", "drafts": 5, "helper_unchanged": true, "common_sha256": "61916205c4993ae856e6ba9afbb198f2cfee1f36b76aff27743e916880beeaad"}\r\n',
  clarification='首次生成未用独立子进程包装，Python独立退出码不追补。后续derive_verify由native_r02独立包装actual0并逐字节核对全部生成产物。'))
 save('preseal_receipt.json',dict(status='COMPAT_LOGIC_G1_COMPLETE_PENDING_REVIEW',task='S12-PH-COMPAT2-R2',actual_seal_command=sys.orig_argv,
  task_baseline_head='891f750045ce141a8152c96025da559ff1d3a321',actual_head_observation=observed_head,source_commit=None,
  legacy_schema_history_recovery_checks=57,legacy_source_after_harness_checks=9,new_p2_regression_checks=new['count'],total_fixture_checks=57+9+new['count'],
  old_r01_bad_matrix_accepted=19,r02_bad_matrix_rejected=25,old_source_pinA_cli_HEAD_B_reproduced=True,new_source_prewrite_rejection_verified=True,
  required_history_codes='五必需labels type(code)is int且0；client非timeout类型和值一致；timeout不能掩盖native非0/未知/类型错误',
  optional_invalid='unique/exact/type int/non0；所有原字节hash闭包真实核验',
  source_commit_checks='source/closed_gate/collect/seal入口CLI==SOURCE pin；freeze/before/after字段同pin；真实HEAD也必须同CLI/pin',
  tests_use_synthetic_Tcl_Git=True,actual_Tcl_calls=0,actual_Git_calls_in_fixtures=0,
  physical_g0_status='BLOCKED_PENDING_REAL_PINS',physical_g0_execution='NOT_RUN',compat_g2='NOT_RUN',actual_pins='NOT_PINNED',actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED',g3='NOT_RUN',g5='NOT_RUN',
  production_old_r01_review_or_git_written=False,heavy_Vivado_ROSS_hardware=False,
  root_next_pins=['ROOT功能G2最终receipt/原始索引/SHA与实际新commit。','真实current43路径及原字节source_freeze/source_commit/SHA、33static/18RTL/8derived/原14；初始852298仅路径参考不沿用旧engine/modified SHA。',
   '新综合/PNR cache/project/evidence/preflight唯一RunIds与精确不存在路径。','最终pins改变后重新冻结common/helper/collector/source_after SHA并串行独审；本次仅兼容逻辑范围。',
   'PNR另绑真实S12综合及独审原件；源码提交与PNR metadata HEAD角色保持分列，目前都不猜填。','真实资源准入/owned ROOT身份/fixed supervisor READY-LIVE-TERMINAL与ROOT约5秒消费/source前后捕获/实际预算另行执行。'],
  limits=['原r01及独审CHANGES_REQUIRED原件保持SHA，不改写旧结果。','模拟Git/Tcl码不是实际运行返回码，生成source状态明确SYNTHETIC；实际物理STA/预算不由mock PASS替代。',
   '首生成独立Python码未采null，真实重建校验native0单列；不能追认历史native字段。','只获得自身离散采样峰；连续绝对峰null。','最终receipt/raw索引由外层包装在本子进程结束后保存，避免日志自哈希循环。']))
 print(json.dumps(dict(status='PRESEAL_COMPLETE',new_checks=new['count'],total_checks=57+9+new['count']),ensure_ascii=False))

if __name__=='__main__':main()
