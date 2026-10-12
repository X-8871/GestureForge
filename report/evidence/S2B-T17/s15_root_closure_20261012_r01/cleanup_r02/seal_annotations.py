import hashlib
import json
from pathlib import Path

root = Path.cwd()
here = root / 'tmp/2B/S2B-T17/s15_cache_cleanup_20261012_r02'

def binding(path):
    return {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}

plan_path = here / 'cleanup_plan.json'
plan = json.loads(plan_path.read_text(encoding='utf-8'))
plan['dependency_reference_audit'] = binding(here / 'dependency_reference_audit.json')
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
index_path = here / 'original_index.json'
rows = [binding(path) for path in here.iterdir() if path.is_file() and path != index_path]
index_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'plan': binding(plan_path), 'index': binding(index_path), 'items': plan['item_count'], 'bytes': plan['total_bytes']}, ensure_ascii=False))
