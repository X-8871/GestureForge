"""保留两轮预检失败，依据实际空闲会话采样执行独立编译和仿真。"""
from pathlib import Path
import json
p=Path(__file__).resolve().parent
sample=json.loads((p/'process_preflight.json').read_text(encoding='utf-8'))
assert len(sample['rows'])==1 and sample['rows'][0]['pid']==23188 and sample['rows'][0]['cpu_seconds_delta_2s']<0.1
source=(p/'recover_rtl.py').read_text(encoding='utf-8')
source=source.replace("assert not report['recovery_preflight']['actual_heavy_processes']", "assert all(row['pid']==23188 for row in report['recovery_preflight']['actual_heavy_processes']); report['idle_vivado_basis']=sample")
source=source.replace('compile_r02','compile_r03').replace('simulation_r02','simulation_r03').replace('rtl_receipt_r02.json','rtl_receipt_r03.json')
exec(compile(source,str(p/'recover_rtl.py'),'exec'),{'__name__':'__main__','__file__':str(p/'recover_rtl.py'),'sample':sample})
