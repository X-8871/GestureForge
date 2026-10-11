#!/usr/bin/env python3
"""独立核验恢复原件后冻结候选平台G2收据，不批准可见性启用。"""
import hashlib
import json
import tkinter
import zipfile
from pathlib import Path

out=Path(__file__).absolute().parent
root=out.parents[3]
recovery=root/'report/evidence/S2B-T13/artifact_recheck_20261011_r01'
static=json.loads((out/'static_result.json').read_text(encoding='utf-8'))
artifact=json.loads((out/'actual_artifact_result.json').read_text(encoding='utf-8'))
interp=tkinter.Tcl()
def digest(path):
    """串行读取实际文件原字节。"""
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def dictionary(text):
    values=interp.splitlist(text)
    assert len(values)%2==0
    return dict(zip(values[::2],values[1::2]))

manifest_path=recovery/'delivery_manifest.json'
assert digest(manifest_path)=='4893b94d19cc81919164d3c8b49c435d90daca771fbbe0557c3f4e8493e15e79'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
verified=[]
for item in manifest['files']:
    assert digest(root/item['path'])==item['sha256'],item['path']
    verified.append(item)
audit=dictionary(dictionary((recovery/'audit.tcldict').read_text(encoding='utf-8'))['data'])
assert audit['status']=='OK' and audit['code']=='0' and audit['raw']=='AUDIT:OK'
assert all(audit[key]=='0' for key in ['warning_count','critical_count','error_count'])
history=json.loads((recovery/'mcp_history_calls.json').read_text(encoding='utf-8'))['history']
assert {item['id'] for item in history}=={44,45,46}
assert all(item['code']==0 for item in history)
removal=next(item for item in history if item['id']==44)
assert 'remove_files $accidental_wrapper' in removal['command'] and 'file delete' not in removal['command']
closure=dictionary(removal['output'].strip())
wrapper_list=interp.splitlist(closure['remaining_wrappers'])
assert len(wrapper_list)==1 and closure['top']=='s2b_inference_wrapper'
assert '/sources_1/imports/hdl/s2b_inference_wrapper.v' in wrapper_list[0]
compile_order=interp.splitlist(closure['compile_order'])
assert len(set(compile_order))==len(compile_order)
rtl=json.loads((root/'board/s2b_inference_platform.json').read_text(encoding='utf-8'))['rtl_sources']
for name in rtl:
    assert (root/name).as_posix() in compile_order,name
assert sum(path.endswith('/s2b_inference_wrapper.v') for path in compile_order)==1
wrapper_path=Path(wrapper_list[0])
assert digest(wrapper_path)==digest(recovery/'s2b_inference_wrapper.v')=='57fa5e3417ad5c492513d3f3ba0a32a723dc7427d775d08211ddfeefe851dd43'
xsa_path=recovery/'s2b_inference_no_bit.xsa'
assert digest(xsa_path)==artifact['xsa_sha256']=='6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7'
with zipfile.ZipFile(xsa_path) as z:
    assert z.testzip() is None
    for name in ['ps7_init.c','ps7_init.h','ps7_init.tcl','s2b_inference.hwh']:
        assert hashlib.sha256(z.read(name)).hexdigest()==digest(recovery/name),name
assert digest(recovery/'s2b_inference.bd')==artifact['bd_sha256']
before=json.loads((recovery/'source_snapshot/source_before.json').read_text(encoding='utf-8'))
after=json.loads((recovery/'source_after.json').read_text(encoding='utf-8'))
assert before['source_sha256']==after['source_sha256']
for path,value in before['source_sha256'].items():
    assert digest(root/path)==value,path
    assert digest(recovery/'source_snapshot'/Path(path).name)==value,path
for path,value in static['reviewed_source_sha256'].items(): assert digest(root/path)==value,path

recovery_result={'status':'PASS','manifest_sha256':digest(manifest_path),'manifest_files_verified':verified,
 'actual_mcp_ids':[44,45,46],'actual_mcp_exit_codes':[item['code'] for item in history],
 'wrapper_sha256':digest(wrapper_path),'compile_order':list(compile_order),'source_before_after_count':len(before['source_sha256']),
 'source_before_after_stable':True,'original_entry_status':'FAIL_CAPTURE_COUNTER_RESET_UNCHANGED',
 'limits':['rootpartial首次store记录原样保留；实际退出码来自真实history恢复原件。','仅精确产物恢复，未把原::run返回改为成功。']}
(out/'recovery_result.json').write_text(json.dumps(recovery_result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt={'schema_version':1,'task_id':'S2B-T13','role':'INDEPENDENT_REVIEWER','status':'PASS',
 'scope':'候选visibility0平台生成与精确产物恢复G2；五被审源固定；不批准visibility1，不代表G3/G4/G5或综合/实现/时序通过。',
 'source_commit':static['source_commit'],'reviewed_source_sha256':static['reviewed_source_sha256'],
 'closed_findings':[{'id':'R13-01','status':'CLOSED','basis':'R2真实junction/精确名称/重叠入口负例通过；本轮path函数不变。'},
  {'id':'R13-02','status':'CLOSED','basis':'IDLE未START未LOAD的CPU↔DAP先验与HP实际路径分开绑定，参数1须真实Reviewer原件及来源核查；模型golden仍G3。'},
  {'id':'R13-03','status':'CLOSED','basis':'外口voidAPI改真实网查唯一新增端点；独立void成功/六负例通过；真实IPIconnect0、DDR/FIXED_IO21成员、validate0/audit0闭合。'},
  {'id':'R13-API-ENUM-WRAPPER','status':'CLOSED','basis':'官方list_property、全部cell intf枚举、wrapper-import后get_files查询；真实BD/HWH/uniqueimportwrapper和完整18源码compileorder闭合。'}],
 'findings':[],
 'checks':{'r3_static':'PASS','independent_external_cases':7,'independent_API_regression_negative_cases':3,
  'developer_r08_file_hash_binding':'PASS','actual_interface_bd_hwh_and_ps_profile':'PASS',
  'actual_capture_recovery_and_source_freeze':'PASS','xsa_zip_crc_and_no_bit':'PASS','18_source_compile_order':'PASS',
  'rtl_lint':'R2_REUSED_0_WITH_162_WARNINGS_NO_RERUN','synthesis':'NOT_RUN','implementation_timing':'NOT_RUN','hardware':'NOT_RUN'},
 'delivery':{'xsa_sha256':artifact['xsa_sha256'],'bd_sha256':artifact['bd_sha256'],
  'wrapper_sha256':digest(wrapper_path),'recovery_manifest_sha256':digest(manifest_path)},
 'bootstrap_compatibility':'编译XSA0上形成的同一ELF可供最终XSA1仅visibility变更时复用，但必须另行实际核验PS配置/软件ABI/BSP/MMU/初始化与运行参数兼容、分别绑定两XSA；当前机器checker不要求编译XSA等于最终XSA，本收据不声称兼容实证或参数1已批准。',
 'limitations':['原ipi_full_r05入口仍FAIL_CAPTURE_COUNTER_RESET；products原生code0/PRODUCTS:OK且产物完整，恢复后独立原件核验通过，未重写FAIL。',
  'root重复调用非幂等products引入双wrapper失败完整保留；仅撤销其额外generated文件对象，未删除磁盘，恢复后唯一importwrapper与源码闭包真实查询。',
  'validate存在7条未打印普通WARNING，原capture记录保留；不能称零warning。恢复audit0/零warning/critical/error。',
  '工业I及板卡身份不由canonicalpart证明；未操作实物。',
  '不承诺一条::run命令无需包装恢复就正常返回；提供冻结恢复recipe。',
  '未修改被审源、未提交、没有MCP/重型作业；原native/store失败和历史版本均保留。'],
 'evidence_files':[]}
for path in sorted(out.iterdir()):
    if path.is_file() and path.name!='review_receipt.json': receipt['evidence_files'].append({'path':path.relative_to(root).as_posix(),'sha256':digest(path)})
(out/'review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('R3_FINAL:PASS_CANDIDATE_PLATFORM_GENERATION_ONLY')
print('RECEIPT_SHA256:'+digest(out/'review_receipt.json'))
