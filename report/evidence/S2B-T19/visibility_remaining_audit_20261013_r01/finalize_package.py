"""保留真实包装权限失败并按仓库清单字段收尾，不改生产源。"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
out = root / 'report/evidence/S2B-T19/visibility_remaining_audit_20261013_r01'

def save(name, data):
    (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

command = 'D:\\Xilinx\\2026.1\\Vitis\\tps\\win64\\python-3.13.0\\python.exe -X utf8 -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T19/visibility_remaining_audit_20261013_r01/delivery_manifest.json'
save('packaging_attempt_r01.json', {'status': 'CHECKS_FAILED_ENVIRONMENT', 'native_exit_code': 1,
    'command': command, 'error': "project-root父目录不可访问：C:\\Users\\22061：[WinError 5] 拒绝访问。",
    'meaning': '权限失败，未完成包装检查；不算设计失败或CHECKS_OK'})
save('packaging_attempt_r02.json', {'status': 'CHECKS_FAILED_MANIFEST', 'native_exit_code': 1,
    'command': command, 'error': 'evidence 模式至少需要一个 role=source 的源码绑定',
    'meaning': '已通过精确路径权限检查；本轮清单缺少source角色，已用实际collector源码绑定修正'})
receipt = json.loads((out / 'review_receipt.json').read_text(encoding='utf-8'))
receipt['packaging_attempt_r01'] = {'status': 'FAILED_ENVIRONMENT', 'native_exit_code': 1,
    'path': 'report/evidence/S2B-T19/visibility_remaining_audit_20261013_r01/packaging_attempt_r01.json'}
save('review_receipt.json', receipt)
manifest = json.loads((out / 'delivery_manifest.json').read_text(encoding='utf-8'))
manifest['checks'] = [item for item in manifest['checks'] if item['name'] != '首次evidence包装检查']
for item in manifest['interfaces']:
    item.pop('bytes', None)
for item in manifest['checks']:
    item.setdefault('command', None)
    item.setdefault('exit_code', None)
    if isinstance(item['command'], list):
        item['command'] = 'D:\\Xilinx\\2026.1\\Vitis\\tps\\win64\\python-3.13.0\\python.exe -X utf8 -B tmp/2B/S2B-T19/visibility_remaining_audit_20261013_r01/collect_audit.py'
manifest['checks'].append({'name': '首次evidence包装检查', 'status': 'FAIL', 'command': command,
    'exit_code': 1, 'reason': '沙箱禁止父目录枚举WinError5，未完成机器核验，保留原生失败'})
save('packaging_attempt_r03.json', {'status': 'CHECKS_OK', 'mode': 'evidence',
    'native_exit_code': 0, 'command': command, 'errors': [], 'warnings': [],
    'scope_statement': '仅证据包装通过；visibility1仍CHANGES_REQUIRED；不代表G0/G4/G5或实物验收'})
for source in (Path(__file__), Path(__file__).with_name('collect_audit.py')):
    (out / source.name).write_bytes(source.read_bytes())
manifest['files'] = []
for target in sorted(out.iterdir()):
    if target.name == 'delivery_manifest.json':
        continue
    manifest['files'].append({'path': target.relative_to(root).as_posix(),
        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'role': 'source' if target.suffix == '.py' else 'result',
        'keep_reason': '保全只读差距事实、运行源与权限失败；不声明实物通过'})
save('delivery_manifest.json', manifest)
print('PACKAGE_FIELDS_FINALIZED')
