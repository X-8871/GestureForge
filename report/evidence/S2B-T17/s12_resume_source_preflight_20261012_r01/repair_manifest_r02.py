"""按检查器schema分列真实入口拒绝native1与未执行依赖BLOCKED/null，保存前两次包装失败。"""
from pathlib import Path
import sys
import seal_resume as seal

original_write = seal.write

def write(path, value):
    if path.name.startswith('delivery_manifest'):
        gate = [row for row in value['checks'] if row['name']=='pnr_pending_negative_gate']
        assert len(gate)==1 and gate[0]['exit_code']==1
        gate[0]['status'] = 'FAIL'
        gate[0]['reason'] = '实际PNR prepare因未冻结依赖拒绝native1；这是保留的真实拒绝运行，预期拒绝断言在logic_tests native0通过。'
        value['checks'].append({'name': 'pnr_synth_dependency', 'status': 'BLOCKED', 'command': None, 'exit_code': None,
            'reason': 'SYNTH_MANIFEST/SYNTH_G2为None/PENDING，未执行综合，不伪造退出码。'})
        value['limitations'].append('两代包装失败原件保留：PASS/native1以及BLOCKED/native1都违反schema；新版本以实际入口FAIL/native1及依赖BLOCKED/null分列，不改六工具。')
    original_write(path, value)

seal.write = write

if sys.argv[1]=='repair':
    seal.copy(Path(__file__).absolute(), seal.OUT/'repair_manifest_r02.py')
    seal.close(('append',), 'delivery_manifest_r03.json')
elif sys.argv[1]=='seal':
    seal.close(('repair_r02', 'r03_evidence', 'r03_inputs'), 'delivery_manifest_r04.json')
