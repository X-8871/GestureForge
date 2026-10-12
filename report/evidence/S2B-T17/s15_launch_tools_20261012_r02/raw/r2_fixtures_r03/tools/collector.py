"""轻量逻辑fixture；不表示真实SOURCE、MCP或G2。"""
import hashlib,json,sys,time
from pathlib import Path
arguments=sys.argv[1:];mode=arguments[0];options=dict(zip(arguments[1::2],arguments[2::2]))
root=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition');pre=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s15_launch_prepare_20261012_r02\\r2_fixtures_r03\\pre');report=Path('C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\s15_launch_prepare_20261012_r02\\r2_fixtures_r03\\report')
def binding(path):
 raw=path.read_bytes();return dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
if mode=='source':
 value=dict(source_commit=options['--commit'],fixture_test=True,source_files=[])
 path=pre/('source_'+options['--phase']+'.json')
elif mode=='collect':
 gate=Path(options['--gate']);raw=gate.read_bytes()
 value=dict(source_commit=options['--commit'],root_gate=binding(gate),closed_gate_inputs=json.loads(raw),fixture_test=True,limitations=['逻辑fixture'],timing=dict(status='FIXTURE_ONLY'))
 path=report/'s15_collection_summary.json'
else:raise ValueError('fixture模式不同')
with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False)
print('仅逻辑fixture实际捕获');time.sleep(.25)
