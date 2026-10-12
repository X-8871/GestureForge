"""补充核实ROOT九条未执行命令及IP库绑定，绝不执行Tcl。"""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).absolute().parent
spec=importlib.util.spec_from_file_location('review',HERE/'review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
path=review.RUN/'execution_commands.json'
value=review.load(path)
assert value['source_commit']==review.HEAD and value['executed'] is False
assert value['session_id']=='vivado-20261012-085253-f212aec3'
assert [x['label'] for x in value['commands']]==['source','products','setup','launch','wait','open_run','reports','query_xdc','close']
library=review.exact(Path(value['ipcfg']['path']))
assert review.sha(library.read_bytes())==value['ipcfg']['sha256']=='c49edb337c430c244653bb4aa66e624146d2492e053cc7385561867224feb26a'
text='\n'.join(x['command'] for x in value['commands'])
assert 's12_launch_prepare_20261012_r01/project' in text and 's12_platform_20261012_r03' in text
assert 'set_param general.maxThreads 1' in text and value['commands'][3]['command']=='launch_runs synth_1 -jobs 1'
assert 'CONFIG.PROFILE_VISIBILITY_PROVEN' in text and 'xc7z020clg400-2' in text and '0.1.12' in text
assert not (review.WORK/'project').exists() and not (review.ROOT/'report/evidence/S2B-T17/s12_platform_20261012_r03').exists()
receipt=dict(status='PASS_LAUNCH_PINS_G2_ONLY', main_receipt=review.bind(HERE/'final_review_receipt.json'),
    execution_commands=review.bind(path),ipcfg=dict(path=str(library),sha256=review.sha(library.read_bytes())),
    scope='静态核九labels、路径、单jobs/threads及IP库原字节；未执行Tcl，不批准实际综合结果。')
review.write('commands_supplement_receipt.json',receipt)
print(json.dumps(dict(status=receipt['status'],receipt=review.bind(HERE/'commands_supplement_receipt.json')),ensure_ascii=False))
