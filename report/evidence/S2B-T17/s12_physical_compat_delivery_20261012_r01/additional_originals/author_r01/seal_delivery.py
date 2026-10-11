"""只读复核本任务输入与最终草稿后封存，真实物理pins与准入仍阻断。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import compat_pins as p

WORK=p.WORK; ROOT=p.ROOT

def write(name,value):
 """创建封存原件，不覆盖成功或失败输出。"""
 with (WORK/name).open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def sha(path):
 """原字节SHA绑定，不进行换行规范化。"""
 return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 """保存真实HEAD观察与原件索引；当前观察不能替代未来源码冻结。"""
 started=time.monotonic()
 bindings=json.loads((WORK/'input_bindings.json').read_text(encoding='utf-8'))
 for row in bindings:
  file=p.pinned(Path(row['absolute_path']),row['sha256']);assert file.stat().st_size==row['bytes']
 fixtures=json.loads((WORK/'fixture_results.json').read_text(encoding='utf-8'))
 harness=json.loads((WORK/'after_harness_results.json').read_text(encoding='utf-8'))
 assert fixtures['count']==57 and harness['count']==9
 wrappers=[json.loads((WORK/(name+'.wrapper.json')).read_text(encoding='utf-8')) for name in ('generate','refresh','validate','harness')]
 assert all(wrapper['status']=='PASS_CHEAP_ONLY' for wrapper in wrappers)
 drafts=['collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','compat_pins.py']
 for name in drafts:ast.parse((WORK/name).read_text(encoding='utf-8'))
 common=sha(WORK/'collector.py')
 assert repr(common) in (WORK/'impl_collector.py').read_text(encoding='utf-8')
 assert repr(common) in (WORK/'source_after_check.py').read_text(encoding='utf-8')
 assert p.SOURCE_COMMIT is None and p.SOURCE_FREEZE_SHA is None and p.FUNCTIONAL_G2_SHA is None
 command=[r'C:\Program Files\Git\bin\bash.exe','-lc','git -c core.longpaths=true -c maintenance.auto=false rev-parse HEAD']
 git_started=time.monotonic();native=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
 for name,raw in (('head.stdout.bin',native.stdout),('head.stderr.bin',native.stderr)):
  with (WORK/name).open('xb') as stream:stream.write(raw)
 actual_head=native.stdout.decode('utf-8').strip() if native.returncode==0 else None
 write('head.native.json',dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=native.returncode,elapsed_seconds=time.monotonic()-git_started,sampled_peak_bytes=None,absolute_peak_bytes=None,actual_head_observation=actual_head,source_baseline_freeze=False))
 assert native.returncode==0
 write('final_draft_binding.json',dict(status='FROZEN_COMPAT_DRAFT_ONLY_NOT_PHYSICAL_APPROVAL',files=[dict(path=name,sha256=sha(WORK/name),bytes=(WORK/name).stat().st_size) for name in drafts],source_commit=None,helper_pins_all_pending=True,
   fixed_tool_restore=p.resolve_permanent(p.GUARD,p.GUARD_SHA),fixed_supervisor_restore=p.resolve_permanent(p.SUP,p.SUP_SHA)))
 write('pending_pins.json',dict(status='BLOCKED_PENDING_ROOT_REAL_FREEZE',source_commit=None,source_freeze_path=None,source_freeze_sha256=None,
   functional_g1_path=None,functional_g1_sha256=None,functional_g2_path=None,functional_g2_sha256=None,functional_g2_expected_status=None,
   synth_g2_path=None,synth_g2_sha256=None,synth_g2_expected_status=None,synth_manifest_path=None,synth_manifest_sha256=None,
   unique_run_ids=None,required_source_counts=dict(source=43,static=33,rtl=18,derived=8,original_frozen=14),profile='s2b-inference-platform/0.1.12',clock_hz=50000000,visibility=0,part='xc7z020clg400-2',
   root_next_steps=['功能G2完成后ROOT实际重新捕获current43 source SHA并提交，再绑定source_commit/source_freeze路径/SHA和真实G1/G2原件。',
    '初始source_freeze_prepare只能参考43路径清单；其继承旧S10的modified_files/engine字段不能作为本轮实际SHA pin。',
    'ROOT精确批准综合/PNR各新cache/project/evidence/preflight唯一路径，不能复用旧S11 RunId/PID/birth或旧source_before。',
    '最终改pins后所有草稿SHA须重新冻结；impl/source_after的COMMON_SHA、prepare scripts/helper与正式映射绑定须同步，再作串行独审。',
    'PNR必须另绑真实S12综合manifest与独立综合G2原件；兼容逻辑G2不授予physicalG0、heavy准入或实际budget批准。',
    '真实source_before/after、fixed supervisor READY/LIVE/TERMINAL、ROOT约5秒消费、owned退出与实际预算另行执行/核对。'],
   unchanged_cli=dict(synth=['prepare','source','collect','seal'],pnr=['prepare','collect','classify'],source_after=['--expected-head','--output-dir']),
   production_cli_fixture_flags_added=False,actual_sta='NOT_RUN',new_budget='NOT_RUN',old_s11_budget='BLOCKED'))
 files=sorted(path for path in WORK.rglob('*') if path.is_file())
 assert sum(path.stat().st_size for path in files)<100*1024**2
 rows=[]
 for path in files:
  assert not path.is_symlink() and not path.is_junction()
  rows.append(dict(path=path.relative_to(WORK).as_posix(),absolute_path=str(path),sha256=sha(path),bytes=path.stat().st_size))
 with (WORK/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
  for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
 records=[record for wrapper in wrappers for record in wrapper['records']]
 write('compatibility_delivery_receipt.json',dict(status='STOP_G1_COMPAT_DRAFT_PENDING_INDEPENDENT_REVIEW',created_at_timezone='UTC+8',actual_outer_command=sys.orig_argv,
   source_commit=None,task_baseline_head='891f750045ce141a8152c96025da559ff1d3a321',actual_head_observation=actual_head,source_freeze=None,
   entry=str(WORK/'final_draft_binding.json'),pending_entry=str(WORK/'pending_pins.json'),input_count=len(bindings),draft_count=5,additional_fail_closed_helper=True,
   schema_history_recovery_checks=57,source_after_full_main_harness_checks=9,fixture_git_native_codes_are_synthetic=True,actual_git_calls_in_harness=0,
   native_calls=[dict(label=record['label'],native_exit_code=record['native_exit_code'],expected_code=record['expected_native_code'],elapsed_seconds=record['elapsed_seconds']) for record in records]+[dict(label='head_read_only',native_exit_code=native.returncode,expected_code=0)],
   native_wall_seconds=sum(record['elapsed_seconds'] for record in records),sampled_owned_parent_plus_direct_child_peak_bytes=max(record['sampled_own_parent_plus_direct_child_peak_bytes'] or 0 for record in records),absolute_peak_bytes=None,
   raw_manifest=dict(path=str(WORK/'raw_manifest.jsonl'),sha256=sha(WORK/'raw_manifest.jsonl'),files=len(rows),bytes=sum(row['bytes'] for row in rows)),
   finalize_elapsed_seconds=time.monotonic()-started,production_or_git_modified=False,hardware_or_vivado_or_ross=False,
   physical_g0='BLOCKED_PENDING_REAL_PINS',compat_g2='NOT_RUN',actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED',g3='NOT_RUN',g5='NOT_RUN',
   limitations=['独审只能批准兼容逻辑；未取得真实pins与准入时不能实际collect/source-after或派发heavy。',
    '模拟history中的Tcl从未执行，模拟Git返回值不属于真实退出码；source_after输出均标SYNTHETIC并把成功标记/原生码改为合成期望字段。',
    '正式恢复入口仅只读核验，没有恢复/覆盖工具或修改旧G2原件。',
    '首次生成5份草稿与diff已保留在first_generation/；后续增加prepare对新增helper绑定，原首次native原件保留。',
    '原wrapper当时自身源码SHA未在启动时采集；最终源码与生成产物哈希在本索引冻结，不把最终HASH冒称历史实时采样。',
    '资源峰仅当前native包装及直接自有子进程离散采样，连续绝对峰未测。',
    '没有正式evidence包装CHECKS_OK或接口/STA/G3/G5通过声明；正式清单仍复用现有schema1，待实际运行闭合后生成。']))
 print(json.dumps(dict(status='STOP',receipt_sha256=sha(WORK/'compatibility_delivery_receipt.json'),raw_manifest_sha256=sha(WORK/'raw_manifest.jsonl'),files=len(rows),bytes=sum(row['bytes'] for row in rows)),ensure_ascii=False))

if __name__=='__main__':main()
