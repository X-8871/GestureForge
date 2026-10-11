"""只通过冻结supervise函数注入轻量替身，绝不调用生产main或真实guard。"""
from pathlib import Path
import importlib.util,json,sys
WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[3]
spec=importlib.util.spec_from_file_location('frozen_supervisor',ROOT/'tmp/2B/S2B-T17/s10_guard_supervisor_20261012_r01/supervisor.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
config=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
raise SystemExit(m.supervise(config['command'],config['binding'],Path(config['out']),config['input_rows']))
