"""核对公共接口、守卫、精确差异及最后真实包装检查。"""
import json,hashlib,re,subprocess,time,sys,ctypes
from pathlib import Path
ROOT=Path.cwd();MAIN=ROOT/'report/evidence/S2B-T17/s12_timing_cones_20261012_r01';OUT=ROOT/'tmp/2B/S2B-T17/independent_s12_functional_review_20261012_r01';started=time.monotonic();checks=[];commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def check(ok,name,detail=None):
 assert ok,(name,detail)
 checks.append(dict(name=name,result='PASS',detail=detail))
freeze=load(MAIN/'source_freeze.json'); baseline=freeze['source_commit']
head=subprocess.check_output(['git','-c','core.longpaths=true','-c','maintenance.auto=false','rev-parse','HEAD'],text=True).strip();check(head==baseline,'实际观测HEAD891')
diff=subprocess.check_output(['git','-c','core.longpaths=true','-c','maintenance.auto=false','diff','--no-ext-diff',baseline,'--',*sorted(freeze['modified_files'])]);check(hashlib.sha256(diff).hexdigest()==freeze['source_diff_sha256'],'16当前待审Git差异等同冻结patch')
for path in ['src/s2b_conv_tile_engine.sv','src/s2b_maxpool_engine.sv','src/s2b_route_engine.sv','src/s2b_route_query.sv','src/s2b_network_backend.sv']:
 old=subprocess.check_output(['git','-c','core.longpaths=true','-c','maintenance.auto=false','show',baseline+':'+path]).decode('utf-8').replace('\r\n','\n');cur=(ROOT/path).read_text(encoding='utf-8')
 # 公开端口只比较从首input/output到关闭括号，允许私有默认参数头。
 oldhead=old[:old.index(');')];newhead=cur[:cur.index(');')]
 oldports=oldhead[oldhead.index('    input'):];newports=newhead[newhead.index('    input'):]
 check(oldports==newports,'全部公开端口逐字节不变 '+path)
 if path in ['src/s2b_conv_tile_engine.sv','src/s2b_route_engine.sv','src/s2b_route_query.sv']:
  check(re.search(r'parameter bit FROZEN_(?:CONV_DESCRIPTOR|ROUTE_SHAPES) = 1\'b0',cur) is not None,'私有参数默认0 '+path)
 if path.endswith('s2b_conv_tile_engine.sv'):
  suffix='        start_ready = (state == ST_IDLE) && !hard_reset && !abort;'
  check(cur[cur.index(suffix):cur.index('    always_ff')]==old[old.index(suffix):old.index('    always_ff')],'CONV公开握手/reset/abort组合输出不变')
  check('if (compute_read_enable) begin\n                feature_read_in_bounds <=' in cur and 'if (compute_read_enable && (weight_bank_index < group_lane_count)) begin' in cur,'特征权重实际FF读统一守卫')
  check('compute_read_enable = !compute_bad_argument && !compute_overflow;' in cur,'MAC ARG/溢出仍禁止实际下一读')
  check('reduction_count_bad = !frozen_conv_descriptor[97];' in cur,'完整字段miss受验证首分支拒绝')
profile=load(ROOT/'board/s2b_inference_platform.json')
print('PROFILEKEYS',list(profile))
check(profile['version']=='s2b-inference-platform/0.1.12','profile0.1.12')
check(profile['clock_hz']==50000000 and profile['visibility_default']==0,'50MHz visibility0')
check(profile['requested_part_literal']=='XC7Z020-2CLG400I' and profile['vivado_part']=='xc7z020clg400-2','Vivado -2精确part')
check(len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8,'18active 8derived')
repair=load(ROOT/'tmp/2B/S2B-T17/s12_remaining_prepare_20261012_r01/delivery_repair_capture_r01/native_receipt.json')
check([r['native_returncode'] for r in repair['runs']]==[0,0,2],'真实repair/evidence/inputs0/0/2')
check(repair['source16_pre']==repair['source16_post']==freeze['modified_files'] and repair['source16_stable'] is True,'修复前后16source不动')
for f in repair['files']:check(sha(Path(f['path']))==f['sha256'],'修复实际log '+Path(f['path']).name)
failed=load(MAIN/'manifest_schema_repair_r01/failed_execution_state.json');check((failed['finalize_native_returncode'],failed['evidence_native_returncode'],failed['wrapper_outer_native_returncode'],failed['inputs'])==(0,2,1,'NOT_RUN'),'原r05失败事实保留')
# 本独审首次checker在精确祖先枚举时被环境拒绝，保留原失败且不覆盖重跑。
environment_failure=load(OUT/'evidence_checker.stdout.log')
check(environment_failure['status']=='CHECKS_FAILED' and any('WinError 5' in e for e in environment_failure['errors']),'独审checker环境失败原件保留')
commands.append(dict(command=[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',str(MAIN/'delivery_manifest_r02.json')],native_exit_code=2,outer_reviewer_driver_exit_code=1,status='ENVIRONMENT_FAILED',basis='finalchecks_execution_r02.log及evidence_checker.stdout.log；未进入清单核验，fresh inputs NOT_RUN'))
evidence_raw=(ROOT/'tmp/2B/S2B-T17/s12_remaining_prepare_20261012_r01/delivery_repair_capture_r01/evidence.stdout.log').read_text(encoding='utf-8')
inputs_raw=(ROOT/'tmp/2B/S2B-T17/s12_remaining_prepare_20261012_r01/delivery_repair_capture_r01/inputs.stdout.log').read_text(encoding='utf-8')
check('CHECKS_OK' in evidence_raw and 'CHECKS_FAILED' in inputs_raw,'已执行真实包装0/2原stdout一致')
class Counters(ctypes.Structure):
 _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ('peak_working','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
c=Counters();c.cb=ctypes.sizeof(c);ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p;ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
check(bool(ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(c),c.cb)) and c.peak_working<=134217728,'独审实际自进程峰<=128MiB',c.peak_working)
receipt=dict(status='PASS_FINAL_STATIC_AND_RAW_PACKAGING_ONLY',checks=checks,commands=commands,source_baseline=baseline,actual_head=head,seconds=time.monotonic()-started,peak_self_working_bytes=c.peak_working,limitations=['本独审fresh evidence checker因祖先枚举WinError5原生2/driver1；fresh inputs NOT_RUN。独立731及119逐RAW核验与已执行原checker0/2原件用于包装判断，不冒称fresh CHECKS_OK。','stage checker子进程绝对峰未测；仅轻量读包，未执行RTL/Vivado。','inputs2为真实未冻结物理/G2时点及历史FAIL状态；不篡改原G1包装。'])
(OUT/'finalchecks_raw_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=receipt['status'],checks=len(checks),seconds=receipt['seconds'],peak_self_bytes=c.peak_working),ensure_ascii=False))
