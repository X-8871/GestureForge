import json
from pathlib import Path

root = Path.cwd()
base = root / 'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01'
manifest = json.loads((base / 'delivery_manifest_r02.json').read_text(encoding='utf-8'))
print('files', len(manifest['files']))
print('manifest tmp', [f['path'] for f in manifest['files'] if f['path'].startswith('tmp/')])
print('gch', [f['path'] for f in manifest['files'] if f['path'].endswith('.gch')])
for name in ['boundary_r01', 'frozen_r01', 'output_r01', 'feature_r01', 'layer0_r01']:
    val = json.loads((base / name / 'validation.json').read_text(encoding='utf-8'))
    print(name, val.get('status'), val.get('tests'))
    for run in val.get('runs', []):
        print({k:v for k,v in run.items() if k in ['name', 'command', 'exit_code', 'failure', 'cwd', 'log', 'log_sha256']})
    native = json.loads((base / ('native_' + name) / 'native.json').read_text(encoding='utf-8'))
    print('native', {k:v for k,v in native.items() if k not in ['source_pre', 'source_post', 'source_before', 'source_after']})
