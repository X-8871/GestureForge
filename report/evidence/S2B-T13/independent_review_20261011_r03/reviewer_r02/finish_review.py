#!/usr/bin/env python3
"""冻结第二轮独立结论与原件绑定。"""
import hashlib
import json
from pathlib import Path

out = Path(__file__).absolute().parent
root = out.parents[3]
def digest(path):
    """按真实原字节计算哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = json.loads((out / 'probe_results.json').read_text(encoding='utf-8'))
manifest_path = root / 'report/evidence/S2B-T13/platform_revision_20261011_r04/delivery_manifest_complete.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest_checks = []
for item in manifest['files']:
    path = root / item['path']
    manifest_checks.append({'path': item['path'], 'actual_sha256': digest(path), 'matches': digest(path) == item['sha256']})
(out / 'developer_manifest_verification.json').write_text(json.dumps({'manifest_sha256':digest(manifest_path),
    'checks':manifest_checks}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert all(x['matches'] for x in manifest_checks if x['path'] != 'src/s2b_control_csr.sv')
assert result['reviewed_sources_stable']
connect_path = root / 'report/evidence/S2B-T13/ipi_full_20261011_r01/connect.tcldict'
assert 'set_property name DDR {}' in connect_path.read_text(encoding='utf-8')
receipt = {
 'schema_version':1, 'task_id':'S2B-T13', 'role':'INDEPENDENT_REVIEWER', 'status':'CHANGES_REQUIRED',
 'reviewed_source_sha256':result['reviewed_source_sha256'], 'source_commit':result['source_commit'],
 'scope':'平台5文件完整静态复审、独立路径/绑定负例；追加root实际IPI失败原件只读核验。未审T11未冻结功能，无重型/实物/提交。',
 'closed_findings':[
  {'id':'R13-01','status':'CLOSED','reason':'逐组件精确名称/链接/reparse与输出互不重叠核验已实现，独立真实junction及10路径负例正确拒绝；运行入口拒绝在source/创建前。'},
  {'id':'R13-02','status':'CLOSED','reason':'visibility0全程IDLE_PS/epoch0/未START未LOAD的CPU0↔DAP先验入口明确，BSP/MMU/宏及原件绑定明确，HP模型golden仍G3；机器只报BINDINGS_VERIFIED并固定真实Reviewer receipt原件hash。'}],
 'findings':[{'id':'R13-03','priority':1,'file':'vivado/s2b_inference_platform.tcl','location':'connect：make_bd_intf_pins_external后set_property name DDR/FIXED_IO',
  'problem':'实际Vivado外口创建命令已创建对象但返回空；脚本将空返回值当对象设置名称，Common17-161使真实IPI停止。',
  'evidence':{'path':connect_path.relative_to(root).as_posix(),'sha256':digest(connect_path)},
  'closure':'调用外口创建后按实际创建对象独立查询且断言唯一，再设置DDR/FIXED_IO名称；真实connect、validate、audit和products通过，保存原失败并新Run重建。'}],
 'checks':{'static_paths_and_bindings':'PASS','path_negative_cases':10,'visibility_negative_cases':15,
  'valid_preflight_and_create_project_stub':'PASS','native_junction_rejection':'PASS','18_rtl_lint_native_exit_code':0,
  'lint_warnings':162,'developer_manifest_files_hashes':'ALL_MATCH_EXCEPT_ACTIVE_T11_CONTROLLER',
  'reviewed_five_source_stability':'PASS',
  'actual_ipi_r01_connect':'FAIL_NATIVE_COMMON_17_161','synthesis_implementation':'NOT_RUN','hardware':'NOT_RUN'},
 'observations':['T11活动controller已更新，D1 r04旧清单绑定不再匹配该依赖；其余文件哈希相符，T13五文件始终稳定；controller功能不在此冻结范围。新平台证据须绑定最终T11。',
  '实际IP_Flow日志clk ASSOCIATED_BUSIF仅S_AXI，RTL属性含S_AXI:M_AXI；后续实际读回核验M_AXI关联，不据此猜测语义失败。',
  '虚构合格fixture可返回BINDINGS_VERIFIED，只证明机器binding，禁止用其启用实际平台；批准来源由总控核查真实Reviewer交付。'],
 'limitations':['静态子项PASS不等于实际平台G1/G2通过；R13-03阻断未关闭。','没有操作root Vivado会话、板卡或用户源码。','临时证据由root正式归档绑定。'],
 'evidence_files':[]
}
for path in sorted(out.iterdir()):
    if path.is_file() and path.name != 'review_receipt.json':
        receipt['evidence_files'].append({'path':path.relative_to(root).as_posix(),'sha256':digest(path)})
(out / 'review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('R2_RECEIPT:CHANGES_REQUIRED R13-01/02=CLOSED R13-03=OPEN')
