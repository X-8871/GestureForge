"""仅核验root已准备的109真实资产，不准备新数据、不访问设备。"""
from pathlib import Path
import hashlib
import json
import sys
import time

OUT = Path(__file__).absolute().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT))
from verification import s2b_csr_board_acceptance as csr

def check(path, expected):
    """逐组件类型与无重解析核验，原字节流式摘要。"""
    path = Path(path)
    for item in reversed([path, *path.parents]):
        assert not getattr(item.lstat(), 'st_file_attributes', 0) & 0x400, str(item)
    assert path.is_file(), str(path)
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for raw in iter(lambda: handle.read(1048576), b''): digest.update(raw)
    assert digest.hexdigest() == expected, str(path)
    return {'path': str(path), 'sha256': expected, 'bytes': path.stat().st_size}

started = time.perf_counter()
prep_path = ROOT / 'report/evidence/S2B-T18/root_corpus_prepare_20261011_r01/preparation.json'
prepared = check(prep_path, '3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb')
plan = json.loads(prep_path.read_text(encoding='utf-8'))
csr.model.validate_plan(plan)
files = [check(plan['weights']['path'], plan['weights']['sha256'])]
for row in plan['rows']:
    files.append(check(row['input']['path'], row['input']['sha256']))
    files.append(check(row['reference']['path'], row['reference']['sha256']))
    reference = json.loads(Path(row['reference']['path']).read_text(encoding='utf-8'))['samples'][0]
    for tensor in reference['head_tensors'].values():
        files.append(check(tensor['path'], tensor['tensor_sha256']))
sample0 = json.loads(Path(plan['rows'][0]['reference']['path']).read_text(encoding='utf-8'))['samples'][0]
result = {'scope': 'ACTUAL_PREPARED_ASSETS_READ_ONLY_NOT_BOARD', 'native_exit_code': 0,
          'hardware_execution': 'NOT_RUN', 'preparation': prepared, 'rows': len(plan['rows']),
          'sample000': sample0, 'files': files, 'elapsed_seconds': time.perf_counter() - started}
with (OUT / 'prepared_asset_result.json').open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
print(json.dumps({'rows': len(plan['rows']), 'bound_assets': len(files), 'sample000_nonempty_boxes': sample0['nms_output_box_count'],
                  'elapsed_seconds': result['elapsed_seconds']}, ensure_ascii=False))
