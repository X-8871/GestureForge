"""保留清单格式失败，补充原因后重新执行只读证据检查。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

root = Path.cwd()
run = root / 'report/evidence/S2B-T19/pc_nvlist_20261013_r01'
audit = root / 'report/evidence/S2B-T19/pc_nvlist_packaging_20261013_r01'
audit.mkdir(exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
original = run / 'delivery_manifest.json'
manifest = json.loads(original.read_text(encoding='utf-8'))
# 原始失败清单不覆盖，修订清单同时绑定旧清单字节。
reasons = {'initial_r01': '沙箱拒绝精确父目录路径核验，离线回归环境失败；原始日志保留。',
           'retry_permissions_r02': '新增模拟测试错误要求对已停止CPU调用stop；修正测试后final_r03通过，失败日志保留。',
           'consumers_r04': '消费者环境缺cv2：78通过、1 ERROR；r05显式借用已安装Python312依赖后79通过。'}
for check in manifest['checks']:
    if check['status'] == 'FAIL':
        check['reason'] = reasons[check['name']]
manifest['files'].append({'path': original.relative_to(root).as_posix(), 'sha256': sha(original),
                          'role': 'result', 'keep_reason': '原始包装失败清单，缺少历史FAIL原因，不覆盖。'})
corrected = run / 'delivery_manifest_r02.json'
assert not corrected.exists()
corrected.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
shutil.copyfile(Path(__file__), audit / Path(__file__).name)
rows = []
for mode in ('inputs', 'evidence'):
    command = [sys.executable, '-X', 'utf8', '-B', 'verification/check_stage_delivery.py', '--mode', mode,
               '--manifest', corrected.relative_to(root).as_posix()]
    result = subprocess.run(command, cwd=root, capture_output=True)
    (audit / (mode + '.stdout.log')).write_bytes(result.stdout)
    (audit / (mode + '.stderr.log')).write_bytes(result.stderr)
    rows.append({'mode': mode, 'command': command, 'exit_code': result.returncode})
(audit / 'execution.json').write_text(json.dumps({'original_manifest_sha256': sha(original),
    'corrected_manifest_sha256': sha(corrected), 'checks': rows,
    'prior_tool_observation': '普通沙箱拒绝用户目录祖先；首次提权检查发现3个历史FAIL缺reason。原始清单保留。',
    'meaning': 'evidence应0；inputs仍因真实历史失败及实板NOT_RUN返回2，不代表G3。'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(rows))
assert rows[0]['exit_code'] == 2 and rows[1]['exit_code'] == 0
