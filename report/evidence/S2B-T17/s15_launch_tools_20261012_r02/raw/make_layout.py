"""22字段运行配置的布局说明；不是可执行配置或批准记录。"""
import json
from pathlib import Path
import compat_pins as pins
import native_contract as contract
W=Path(__file__).parent;ROOT=W.parents[3]
D=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r02'
template={key:None for key in pins._CONFIG_FIELDS}
layout=dict(SYNTH_CACHE=W,PNR_CACHE=W/'pnr_s15_r01',PROJECT=W/'project_s15_r01',SYNTH_REPORT=ROOT/'report/evidence/S2B-T17/s15_platform_20261012_r01',PNR_REPORT=ROOT/'report/evidence/S2B-T17/s15_postroute_20261012_r01',SOURCE_PRE=ROOT/'report/evidence/S2B-T17/s15_source_preflight_20261012_r01')
for key,value in layout.items():template[key]=str(value)
for key in pins._CONFIG_PATHS-set(layout)-{'SYNTH_MANIFEST','SYNTH_G2'}:template[key]=str(ROOT/('__PENDING_S15_'+key+'__'))
guide=dict(status='REFERENCE_ONLY_PENDING_ALL_REAL_APPROVALS',field_count=22,template_fields=template,
 layout_verified_parent=str(W.parent),source_files_count='ROOT最终实际闭包；不固定45，新增runner可能46',
 production_tool_closure=list(contract.TOOL_NAMES),review_receipt_contract='实际独立PASS receipt的reviewed_tools必须含完整13生产工具的精确repo-POSIX path、SHA256、bytes；每项唯一。可另列被审回归工具。',
 field_usage={key:('真实原字节SHA256，未知必须null' if key.endswith('_SHA') else '真实独立PASS状态字符串，未知必须null' if key.endswith('_EXPECTED_STATUS') else 'ROOT实际冻结40位commit，未知必须null' if key=='SOURCE_COMMIT' else '精确绝对路径，仅manifest相对identifier转POSIX') for key in pins._CONFIG_FIELDS},
 creation_order=['ROOT在实际SOURCE/功能G1-G2/工具G2冻结后materialize新的runtime_pins_synth_rN.json；通过S15_RUNTIME_CONFIG指定实际原件并绑定SHA。',
 'native.py --prefix s15_runtime_prepare_rN -- prepare；真实准备receipt只写WORK。',
 'native.py --prefix s15_runtime_source_before_rN -- source --commit 实际SOURCE --phase before；PRE/REPORT/PROJECT须未存在，source-before新建PRE和REPORT供builder使用。',
 'ROOT实际source→builder→setup→launch→wait→open_run→reports→query_xdc→close九标签；reports批次可追加methodology JSON附件绑定。',
 'native.py --prefix s15_runtime_source_after_rN -- source --commit 实际SOURCE --phase after；闭合SOURCE与static。',
 'ROOT关闭gate_r01列已闭合SOURCE/config/MCP九标签/附件/native source记录，保持原字节不改。',
 'native.py --prefix s15_runtime_collect_rN -- collect --commit 实际SOURCE --gate 旧gate_r01精确绝对路径。',
 'collect真实wait完成后新建gate_r02，仅扩展native_wrappers加入collect实际原件；native.py --prefix s15_runtime_seal_rN -- seal --commit 实际SOURCE --gate 新gate_r02精确绝对路径。'],
 constraints=['旧gate和既有RunId禁止覆写。seal重新校验collect实际消费旧gate bytehash，SOURCE/config/MCP9及闭合附件与新gate全部相同。',
 '预算/未知、缺身份、PID复用采样、exe/cwd/cmdline/ppid漂移、工具集合前后漂移、错commit/gate、重复额外参数均阻断。',
 '本说明不创建真实runtime_pins.json，不伪造SOURCE/功能G2/工具G2。',
 'TREE RSS6GiB/available512MiB/Cfree8GiB；1s/SUP5s/consumer5s硬10s；连续两轮活集合完全相同、max3不变；4.5GiB启动阈值用户已豁免。'])
with (D/'runtime_pin_layout.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(guide,stream,ensure_ascii=False,indent=2);stream.write('\n')
print('REFERENCE_ONLY_PENDING_ALL_REAL_APPROVALS 22')
