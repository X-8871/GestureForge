"""仅机械适配既有轻量预检的隔离输出名，保留首轮原件。"""
import hashlib,json
from pathlib import Path
WORK=Path(__file__).parent
source=WORK/'precheck.py'; raw=source.read_bytes(); code=raw.decode('utf-8')
replacements=[("name+'.stdout.log'","name+'_r02.stdout.log'"),("name+'.stderr.log'","name+'_r02.stderr.log'"),("name+'.native.json'","name+'_r02.native.json'"),('prepared_receipt.json','prepared_receipt_r02.json'),('unclosed_gate.json','unclosed_gate_r02.json'),('precheck_result.json','precheck_result_r02.json'),('raw_manifest.jsonl','raw_manifest_r02.jsonl')]
for old,new in replacements:
 assert old in code; code=code.replace(old,new)
target=WORK/'precheck_adapted_r02.py'; assert not target.exists()
with target.open('xb') as f: f.write(code.encode('utf-8'))
with (WORK/'precheck_r02_derivation.json').open('x',encoding='utf-8',newline='\n') as f:
 json.dump(dict(source=source.name,source_sha256=hashlib.sha256(raw).hexdigest(),target=target.name,target_sha256=hashlib.sha256(code.encode('utf-8')).hexdigest(),replacements=replacements,actual_collect_executed=False,first_collector_snapshot='collector_first_preparation.py',supersedes_first_preparation_reason='静态检查发现common/当前collector同名保存，收集尚未执行；修复只在本隔离代码，首轮源及所有结果保留。'),f,ensure_ascii=False,indent=2); f.write('\n')
exec(compile(code,str(target),'exec'),dict(__name__='__main__',__file__=str(target)))
