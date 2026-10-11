import json
from pathlib import Path

root = Path.cwd()
origin = root / 'tmp/2B/S2B-T17/independent_s11_implementation_review_20261012_r01'
rows = [json.loads(line) for line in (origin / 'raw_manifest.jsonl').read_text(encoding='utf-8').splitlines()]
sizes = [(row['path'], (root / row['path']).stat().st_size) for row in rows]
print(json.dumps({'rows': len(rows), 'unique': len(set(row['path'] for row in rows)),
                  'bound_bytes': sum(size for _, size in sizes),
                  'largest': sorted(sizes, key=lambda row: row[1], reverse=True)[:5],
                  'selected': [path for path, _ in sizes if any(word in path for word in ('source_binding', 'source_after.json', 'mapping', 'snapshot', 'raw_copy'))]}, ensure_ascii=False))
main = root / 'report/evidence/S2B-T17/s11_implementation_20261012_r01'
for name in ('s11_implementation_source_binding.json', 'pnr_closed_binding.json'):
    path = main / name
    if path.is_file():
        value = json.loads(path.read_text(encoding='utf-8'))
        print(name, list(value))
        for key, item in value.items():
            if isinstance(item, list):
                print(key, len(item), item[:1] if key in ('source_files',) else [])
        if name == 's11_implementation_source_binding.json':
            print('restoration_mapping', str(value['restoration_mapping'])[:2200])
            source_rows = value['source_files']
            known = {row['sha256'] for row in rows}
            print('additional_snapshot_bytes', sum((root / row['snapshot']).stat().st_size for row in source_rows if row['sha256'] not in known))
