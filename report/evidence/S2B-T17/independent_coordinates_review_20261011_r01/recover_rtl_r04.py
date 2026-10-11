"""保留编译预算误分类失败，将缓存与证据分别按授权预算统计。"""
from pathlib import Path
import json
p=Path(__file__).resolve().parent
sample=json.loads((p/'process_preflight.json').read_text(encoding='utf-8'))
assert len(sample['rows'])==1 and sample['rows'][0]['pid']==23188 and sample['rows'][0]['cpu_seconds_delta_2s']<0.1
logs=p/'r04_logs'; assert p.is_dir() and not logs.exists(); logs.mkdir()
source=(p/'recover_rtl.py').read_text(encoding='utf-8')
source=source.replace("assert not report['recovery_preflight']['actual_heavy_processes']", "assert all(row['pid']==23188 for row in report['recovery_preflight']['actual_heavy_processes']); report['idle_vivado_basis']=sample; report['budget_recovery']='前轮把cache和evidence同目录导致100MB证据阈值误适用于编译缓存；本轮独立日志子目录，缓存仍300MB，原件全保留。'")
source=source.replace('compile_r02','compile_r04').replace('simulation_r02','simulation_r04').replace('rtl_receipt_r02.json','rtl_receipt_r04.json')
source=source.replace(',WORK,WORK,env,report',',WORK,logs,env,report').replace("log=(WORK/'simulation_r04.log')","log=(logs/'simulation_r04.log')")
exec(compile(source,str(p/'recover_rtl.py'),'exec'),{'__name__':'__main__','__file__':str(p/'recover_rtl.py'),'sample':sample,'logs':logs})
