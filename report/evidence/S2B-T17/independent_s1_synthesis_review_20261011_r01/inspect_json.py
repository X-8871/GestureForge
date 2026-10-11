import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
evidence = Path('report/evidence/S2B-T17/s1_platform_20261011_r01')
for name in sys.argv[1:]:
    data = json.loads((evidence / name).read_text(encoding='utf-8'))
    if name == 'collector_delivery_manifest_r02.json':
        data = {k: v for k, v in data.items() if k != 'files'}
    elif name in ['collector_source_binding.json', 'collector_native_archive_mapping.json', 'source_before.json']:
        data = {k: v if k != 'files' else [v[0], v[-1]] for k, v in data.items()}
    elif name == 'collector_original_inventory.json':
        data = {k: len(v) if isinstance(v, list) else v for k, v in data.items()}
    print(name, json.dumps(data, ensure_ascii=False, indent=2))
