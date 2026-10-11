#!/usr/bin/env python3
"""第三轮独立静态复核，不重复无改动RTL编译。"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).absolute().parents[4]
out = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('checker',root/'verification/check_s2b_inference_platform.py')
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
sources=checker.check_static(root)
reviewed=['src/s2b_inference_top.sv','vivado/s2b_inference_platform.tcl','board/s2b_inference_platform.json','board/s2b_inference_platform.md','verification/check_s2b_inference_platform.py']
frozen={name:checker.sha256(root/name) for name in reviewed}
runs=[]
def run(name,args):
    """原生输出只写独立隔离目录。"""
    p=subprocess.run(args,cwd=root,capture_output=True)
    (out/(name+'.stdout.log')).write_bytes(p.stdout)
    (out/(name+'.stderr.log')).write_bytes(p.stderr)
    runs.append({'name':name,'command':args,'native_exit_code':p.returncode})
    assert p.returncode==0
run('static',[sys.executable,'-B',str(root/'verification/check_s2b_inference_platform.py')])
run('external_void_and_negative',['C:/Program Files/Git/ucrt64/bin/tclsh.exe',str(out/'external_probe.tcl'),root.as_posix()])
original=checker.relative_file
script=(root/'vivado/s2b_inference_platform.tcl').read_text(encoding='utf-8')
negatives=[]
for name,changed in [
 ('invented_list_properties',script.replace('[list_property ','[list_properties ',1)),
 ('wrapper_return_object',script.replace('make_wrapper -files $bd_file -top -import','set wrapper [make_wrapper -files $bd_file -top]')),
 ('missing_wrapper_query',script.replace('set wrapper [get_files */${bd_name}_wrapper.v]','set wrapper {}'))]:
    candidate=out/(name+'.tcl')
    candidate.write_text(changed,encoding='utf-8')
    checker.relative_file=lambda r,v,c=candidate: c if v=='vivado/s2b_inference_platform.tcl' else original(r,v)
    try:
        checker.check_static(root)
        raise AssertionError(name+'负例被接受')
    except ValueError as exc:
        negatives.append({'name':name,'status':'REJECTED','reason':str(exc)})
checker.relative_file=original
manifest_path=root/'report/evidence/S2B-T13/platform_api_audit_20261011_r08/delivery_manifest_complete.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
bindings=[]
for item in manifest['files']:
    actual=checker.sha256(root/item['path'])
    bindings.append({'path':item['path'],'matches':actual==item['sha256'],'actual_sha256':actual})
assert all(x['matches'] for x in bindings)
result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
 'reviewed_source_sha256':frozen,'source_sha256':sources,'runs':runs,'API_regression_negative_cases':negatives,
 'developer_manifest_sha256':checker.sha256(manifest_path),'developer_manifest_files':bindings,
 'sources_stable':sources==checker.check_static(root),
 'limits':['未重复18RTL编译，R2同RTL闭包lint0/162warn复用，T11已正式冻结。','未操作MCP/Vivado/实物。','实际IPI结果另行原件核验。']}
(out/'static_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('R3_STATIC:PASS')
