"""只读预检封存的 S6 原件，将初始库存写入新隔离目录。"""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
WORK = Path(__file__).resolve().parent
REPORT = ROOT / 'report/evidence/S2B-T17/s6_platform_20261011_r01'
CACHE = ROOT / 'tmp/2B/S2B-T17/s6_root_run_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s6_source_preflight_20261011_r01'
sys.stdout.reconfigure(encoding='utf-8')

def read(path):
    """只读取已指定的完整 JSON 文件。"""
    assert path.is_file() and not path.is_symlink(), path
    return json.loads(path.read_text(encoding='utf-8'))

def binding(path):
    """保存完整相对路径及原字节哈希。"""
    assert path.is_file() and not path.is_symlink(), path
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}

files = [binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
with (WORK / 'initial_inventory.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump({'files': files, 'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files)}, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
history = [h for b in read(CACHE / 'mcp_history.json')['content'] if b['type'] == 'text' for h in json.loads(b['text']).get('history', [])]
print('INVENTORY', len(files), sum(r['bytes'] for r in files))
for h in history:
    print('HISTORY', json.dumps(h, ensure_ascii=False))
for name in ('resource_preflight.json', 'resource_during_synthesis_01.json', 'source_before.native.json', 'source_after.native.json'):
    print(name, json.dumps(read(CACHE / name), ensure_ascii=False))
after = read(PRE / 'source_after.json')
print('AFTER_KEYS', list(after))
print('SOURCE_COUNT', len(after['source_files']))
print('FREEZE', json.dumps(read(ROOT / after['source_freeze']), ensure_ascii=False)[:1600])
project = Path(after['project_dir'])
for directory in sorted((project / 's2b_inference_candidate.runs').iterdir()):
    if directory.is_dir() and directory.name != '.jobs':
        log = (directory / 'runme.log').read_text(encoding='utf-8')
        print('NATIVE_JOB', directory.name, re.findall(r'(?:Start of session at:|Exiting Vivado at|synth_design:|Time \(s\):).*', log)[-4:], re.findall(r'peak = ([0-9.]+)', log)[-2:])
        print('JOB_FILES', [p.name for p in sorted(directory.iterdir()) if p.is_file()])
for name in ('timing_worst_synth.rpt', 'methodology_synth.rpt', 'drc_synth.rpt', 'constraints_synth.xdc', 'exceptions_synth.rpt'):
    text = (REPORT / name).read_text(encoding='utf-8')
    print('REPORT', name, '\n'.join(text.splitlines()[:55]))
prior = read(ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01/s5_collection_delivery_manifest_r02.json')
print('INTERFACES', json.dumps(prior['interfaces'], ensure_ascii=False))
