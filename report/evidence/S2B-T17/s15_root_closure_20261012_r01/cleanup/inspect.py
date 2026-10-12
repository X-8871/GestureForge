import json
from pathlib import Path

root = Path.cwd()
manifest = json.loads((root / 'report/evidence/S2B-T17/s12_timing_cones_20261012_r01/delivery_manifest_r02.json').read_text(encoding='utf-8'))
for row in manifest['files']:
    if 'native_receipt.json' in row['path']:
        print(row['path'])
        value = json.loads((root / row['path']).read_text(encoding='utf-8'))
        print({k:v for k,v in value.items() if k in ['native_exit_code', 'exit_code', 'native_command', 'command', 'state', 'status', 'terminal_state', 'pid', 'root_pid']})
raise SystemExit
names = ['s12_conv_cones_20261012_r01', 's12_conv_cones_20261012_r02', 's12_conv_cones_20261012_r03', 's12_timing_cones_20261012_r01', 's12_root_closure_20261012_r01', 'independent_s12_functional_review_20261012_r01']
for name in names:
    directory = root / 'report/evidence/S2B-T17' / name
    for path in directory.glob('*.json'):
        value = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(value, dict) and 'manifest' in path.name:
            print(str(path.relative_to(root)), 'files', len(value.get('files', [])))
            print('selected', [f['path'] for f in value.get('files', []) if '/s12_conv_layer0_' in f['path'] or '/s12_conv_boundary_' in f['path'] or '/s12_backend_timing_' in f['path'] or '/s12_pool_timing_' in f['path'] or '/s12_route_generic_' in f['path']][:8])
        elif 'recovery' in path.name or 'dependencies' in path.name:
            print(str(path.relative_to(root)), str(value)[:3000])
