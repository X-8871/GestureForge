"""保留首包装失败；新清单将实际拒绝码1列为BLOCKED，20条断言通过另判。"""
import sys
from pathlib import Path
import seal_resume as seal

original_write = seal.write

def write(path, value):
    if path.name.startswith('delivery_manifest'):
        gate = [row for row in value['checks'] if row['name']=='pnr_pending_negative_gate']
        assert len(gate)==1 and gate[0]['exit_code']==1
        gate[0]['status'] = 'BLOCKED'
        gate[0]['reason'] = '现成PNR prepare实际因缺SYNTH_MANIFEST/G2依赖拒绝，native1；预期拒绝断言已在20条logic_tests native0中通过。'
        value['limitations'].append('首precheck把预期拒绝native1列PASS违反包装schema，真实evidence2与inputs2原件保留；新版本只修正该状态为BLOCKED，不改六工具。')
    original_write(path, value)

seal.write = write

if sys.argv[1] == 'repair':
    seal.copy(Path(__file__).absolute(), seal.OUT/'repair_manifest.py')
    seal.close(('seal',), 'delivery_manifest_r02.json')
elif sys.argv[1] == 'append':
    seal.close(('repair', 'final_evidence', 'final_inputs'), 'delivery_manifest.json')
